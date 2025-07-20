import logging
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, date
from typing import List, Dict, Any
import decimal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def extract_payment_history(oltp_db: Session, last_processed_id: int) -> List[Dict[str, Any]]:
    """
    Extract payment history from OLTP database that have an ID greater than the last processed ID.
    """
    logger.info(f"Extracting payment history with ID > {last_processed_id}")
    
    # SQL query to extract payment history with dimension keys
    query = text("""
        SELECT 
            p.payment_id, p.member_id, p.card_id, p.payment_date, p.payment_amount, 
            p.minimum_due, p.payment_status, p.days_late, p.late_fee, 
            p.statement_balance, p.payment_method, p.created_at,
            m.member_key, c.card_key, d.date_key as payment_date_key, pm.payment_method_key
        FROM payment_history p
        JOIN dim_member m ON p.member_id = m.member_id AND m.is_current = TRUE
        JOIN dim_credit_card c ON p.card_id = c.card_id AND c.is_current = TRUE
        JOIN dim_date d ON p.payment_date = d.date_value
        JOIN dim_payment_method pm ON p.payment_method = pm.payment_method
        WHERE p.payment_id > :last_id
        ORDER BY p.payment_id
    """)
    
    try:
        # Execute query
        result = oltp_db.execute(query, {"last_id": last_processed_id})
        
        # Convert result to list of dictionaries
        payments = []
        for row in result:
            payment = {
                "payment_id": row.payment_id,
                "member_id": row.member_id,
                "card_id": row.card_id,
                "payment_date": row.payment_date,
                "payment_amount": row.payment_amount,
                "minimum_due": row.minimum_due,
                "payment_status": row.payment_status,
                "days_late": row.days_late,
                "late_fee": row.late_fee,
                "statement_balance": row.statement_balance,
                "payment_method": row.payment_method,
                "created_at": row.created_at,
                "member_key": row.member_key,
                "card_key": row.card_key,
                "payment_date_key": row.payment_date_key,
                "payment_method_key": row.payment_method_key
            }
            payments.append(payment)
        
        logger.info(f"Extracted {len(payments)} payment history records")
        return payments
    
    except Exception as e:
        # If the join fails, try without the joins
        logger.warning(f"Error extracting payment history with joins: {str(e)}. Trying without joins.")
        
        # SQL query without joins
        query = text("""
            SELECT 
                payment_id, member_id, card_id, payment_date, payment_amount, 
                minimum_due, payment_status, days_late, late_fee, 
                statement_balance, payment_method, created_at
            FROM payment_history
            WHERE payment_id > :last_id
            ORDER BY payment_id
        """)
        
        # Execute query
        result = oltp_db.execute(query, {"last_id": last_processed_id})
        
        # Convert result to list of dictionaries
        payments = []
        for row in result:
            payment = {
                "payment_id": row.payment_id,
                "member_id": row.member_id,
                "card_id": row.card_id,
                "payment_date": row.payment_date,
                "payment_amount": row.payment_amount,
                "minimum_due": row.minimum_due,
                "payment_status": row.payment_status,
                "days_late": row.days_late,
                "late_fee": row.late_fee,
                "statement_balance": row.statement_balance,
                "payment_method": row.payment_method,
                "created_at": row.created_at,
                "member_key": None,  # Will be looked up during transformation
                "card_key": None,    # Will be looked up during transformation
                "payment_date_key": None,  # Will be looked up during transformation
                "payment_method_key": None  # Will be looked up during transformation
            }
            payments.append(payment)
        
        logger.info(f"Extracted {len(payments)} payment history records (without joins)")
        return payments

def transform_payment_history(payments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transform payment history data to fit the DW schema.
    """
    logger.info(f"Transforming {len(payments)} payment history records")
    
    transformed_payments = []
    for payment in payments:
        # Calculate derived measures
        payment_ratio = None
        excess_payment = None
        
        if payment["minimum_due"] and payment["minimum_due"] > 0 and payment["payment_amount"]:
            payment_ratio = float(payment["payment_amount"] / payment["minimum_due"])
        
        if payment["payment_amount"] and payment["minimum_due"]:
            excess_payment = float(payment["payment_amount"] - payment["minimum_due"])
        
        # Calculate flags
        is_on_time = payment["payment_status"] == "on_time"
        is_full_payment = False
        is_minimum_payment = False
        is_over_payment = False
        
        if payment["payment_amount"] and payment["statement_balance"]:
            is_full_payment = payment["payment_amount"] >= payment["statement_balance"]
            is_over_payment = payment["payment_amount"] > payment["statement_balance"]
        
        if payment["payment_amount"] and payment["minimum_due"]:
            is_minimum_payment = payment["payment_amount"] >= payment["minimum_due"]
        
        # Create transformed payment
        transformed_payment = {
            "member_key": payment["member_key"],
            "card_key": payment["card_key"],
            "payment_date_key": payment["payment_date_key"],
            "payment_method_key": payment["payment_method_key"],
            "payment_amount": payment["payment_amount"],
            "minimum_due": payment["minimum_due"],
            "statement_balance": payment["statement_balance"],
            "late_fee": payment["late_fee"],
            "days_late": payment["days_late"],
            "payment_ratio": payment_ratio,
            "excess_payment": excess_payment,
            "is_on_time": is_on_time,
            "is_full_payment": is_full_payment,
            "is_minimum_payment": is_minimum_payment,
            "is_over_payment": is_over_payment,
            "payment_status": payment["payment_status"],
            "created_datetime": datetime.now()
        }
        
        transformed_payments.append(transformed_payment)
    
    logger.info(f"Transformed {len(transformed_payments)} payment history records")
    return transformed_payments

def load_payment_history(dw_db: Session, transformed_payments: List[Dict[str, Any]]) -> int:
    """
    Load transformed payment history into the DW database.
    """
    if not transformed_payments:
        logger.info("No payment history to load")
        return 0
    
    logger.info(f"Loading {len(transformed_payments)} payment history records into DW")
    
    # For each payment, look up any missing dimension keys
    records_loaded = 0
    for payment in transformed_payments:
        # Skip if any required dimension key is missing
        missing_keys = []
        
        if payment["member_key"] is None:
            missing_keys.append("member_key")
            # Try to look up the member_key
            query = text("""
                SELECT member_key
                FROM dim_member
                WHERE member_id = :member_id AND is_current = TRUE
            """)
            
            result = dw_db.execute(query, {"member_id": payment["member_id"]})
            member = result.fetchone()
            
            if member:
                payment["member_key"] = member.member_key
            else:
                logger.warning(f"No member_key found for member_id {payment['member_id']}")
        
        if payment["card_key"] is None:
            missing_keys.append("card_key")
            # Try to look up the card_key
            query = text("""
                SELECT card_key
                FROM dim_credit_card
                WHERE card_id = :card_id AND is_current = TRUE
            """)
            
            result = dw_db.execute(query, {"card_id": payment["card_id"]})
            card = result.fetchone()
            
            if card:
                payment["card_key"] = card.card_key
            else:
                logger.warning(f"No card_key found for card_id {payment['card_id']}")
        
        if payment["payment_date_key"] is None:
            missing_keys.append("payment_date_key")
            # Try to look up the payment_date_key
            query = text("""
                SELECT date_key
                FROM dim_date
                WHERE date_value = :date_value
            """)
            
            result = dw_db.execute(query, {"date_value": payment["payment_date"]})
            date_record = result.fetchone()
            
            if date_record:
                payment["payment_date_key"] = date_record.date_key
            else:
                logger.warning(f"No date_key found for date {payment['payment_date']}")
        
        if payment["payment_method_key"] is None:
            missing_keys.append("payment_method_key")
            # Try to look up the payment_method_key
            query = text("""
                SELECT payment_method_key
                FROM dim_payment_method
                WHERE payment_method = :payment_method
            """)
            
            result = dw_db.execute(query, {"payment_method": payment["payment_method"]})
            payment_method = result.fetchone()
            
            if payment_method:
                payment["payment_method_key"] = payment_method.payment_method_key
            else:
                logger.warning(f"No payment_method_key found for payment_method {payment['payment_method']}")
        
        # Skip if any required dimension key is still missing
        if payment["member_key"] is None or payment["card_key"] is None or \
           payment["payment_date_key"] is None or payment["payment_method_key"] is None:
            logger.warning(f"Skipping payment - missing dimension keys: {missing_keys}")
            continue
        
        # Insert new record
        insert_query = text("""
            INSERT INTO fact_payment (
                member_key, card_key, payment_date_key, payment_method_key,
                payment_amount, minimum_due, statement_balance, late_fee, days_late,
                payment_ratio, excess_payment, is_on_time, is_full_payment,
                is_minimum_payment, is_over_payment, payment_status, created_datetime
            ) VALUES (
                :member_key, :card_key, :payment_date_key, :payment_method_key,
                :payment_amount, :minimum_due, :statement_balance, :late_fee, :days_late,
                :payment_ratio, :excess_payment, :is_on_time, :is_full_payment,
                :is_minimum_payment, :is_over_payment, :payment_status, :created_datetime
            )
        """)
        
        dw_db.execute(insert_query, payment)
        records_loaded += 1
    
    # Commit the transaction
    dw_db.commit()
    
    logger.info(f"Loaded {records_loaded} payment history records into DW")
    return records_loaded