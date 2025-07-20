import logging
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, date
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def extract_credit_cards(oltp_db: Session, last_processed_id: int) -> List[Dict[str, Any]]:
    """
    Extract credit cards from OLTP database that have an ID greater than the last processed ID.
    """
    logger.info(f"Extracting credit cards with ID > {last_processed_id}")
    
    # SQL query to extract credit cards
    query = text("""
        SELECT 
            c.card_id, c.member_id, c.card_number, c.card_type, c.credit_limit, 
            c.current_balance, c.apr_rate, c.minimum_payment, c.payment_due_date, 
            c.card_status, c.issue_date, c.expiry_date, c.created_at, c.updated_at,
            m.member_key
        FROM credit_cards c
        JOIN dim_member m ON c.member_id = m.member_id AND m.is_current = TRUE
        WHERE c.card_id > :last_id
        ORDER BY c.card_id
    """)
    
    try:
        # Execute query
        result = oltp_db.execute(query, {"last_id": last_processed_id})
        
        # Convert result to list of dictionaries
        credit_cards = []
        for row in result:
            credit_card = {
                "card_id": row.card_id,
                "member_id": row.member_id,
                "member_key": row.member_key,
                "card_number": row.card_number,
                "card_type": row.card_type,
                "credit_limit": row.credit_limit,
                "current_balance": row.current_balance,
                "apr_rate": row.apr_rate,
                "minimum_payment": row.minimum_payment,
                "payment_due_date": row.payment_due_date,
                "card_status": row.card_status,
                "issue_date": row.issue_date,
                "expiry_date": row.expiry_date,
                "created_at": row.created_at,
                "updated_at": row.updated_at
            }
            credit_cards.append(credit_card)
        
        logger.info(f"Extracted {len(credit_cards)} credit cards")
        return credit_cards
    
    except Exception as e:
        # If the join fails (e.g., dim_member doesn't exist yet), try without the join
        logger.warning(f"Error extracting credit cards with join: {str(e)}. Trying without join.")
        
        # SQL query without join
        query = text("""
            SELECT 
                card_id, member_id, card_number, card_type, credit_limit, 
                current_balance, apr_rate, minimum_payment, payment_due_date, 
                card_status, issue_date, expiry_date, created_at, updated_at
            FROM credit_cards
            WHERE card_id > :last_id
            ORDER BY card_id
        """)
        
        # Execute query
        result = oltp_db.execute(query, {"last_id": last_processed_id})
        
        # Convert result to list of dictionaries
        credit_cards = []
        for row in result:
            credit_card = {
                "card_id": row.card_id,
                "member_id": row.member_id,
                "member_key": None,  # Will be looked up during transformation
                "card_number": row.card_number,
                "card_type": row.card_type,
                "credit_limit": row.credit_limit,
                "current_balance": row.current_balance,
                "apr_rate": row.apr_rate,
                "minimum_payment": row.minimum_payment,
                "payment_due_date": row.payment_due_date,
                "card_status": row.card_status,
                "issue_date": row.issue_date,
                "expiry_date": row.expiry_date,
                "created_at": row.created_at,
                "updated_at": row.updated_at
            }
            credit_cards.append(credit_card)
        
        logger.info(f"Extracted {len(credit_cards)} credit cards (without join)")
        return credit_cards

def calculate_credit_limit_tier(credit_limit: float) -> str:
    """
    Calculate credit limit tier based on credit limit.
    """
    if not credit_limit:
        return "Unknown"
    
    if credit_limit < 1000:
        return "Low"
    elif credit_limit < 5000:
        return "Medium"
    elif credit_limit < 10000:
        return "High"
    else:
        return "Premium"

def calculate_apr_category(apr_rate: float) -> str:
    """
    Calculate APR category based on APR rate.
    """
    if not apr_rate:
        return "Unknown"
    
    if apr_rate < 0.10:
        return "Low"
    elif apr_rate < 0.20:
        return "Medium"
    else:
        return "High"

def calculate_card_age_months(issue_date: date) -> int:
    """
    Calculate card age in months.
    """
    if not issue_date:
        return 0
    
    today = datetime.now().date()
    months = (today.year - issue_date.year) * 12 + (today.month - issue_date.month)
    
    return max(0, months)

def transform_credit_cards(credit_cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transform credit cards data to fit the DW schema.
    """
    logger.info(f"Transforming {len(credit_cards)} credit cards")
    
    transformed_credit_cards = []
    for card in credit_cards:
        # Calculate derived fields
        credit_limit_tier = calculate_credit_limit_tier(card["credit_limit"])
        apr_category = calculate_apr_category(card["apr_rate"])
        card_age_months = calculate_card_age_months(card["issue_date"])
        
        # Create transformed credit card
        transformed_card = {
            "card_id": card["card_id"],
            "member_key": card["member_key"],
            "card_type": card["card_type"],
            "credit_limit": card["credit_limit"],
            "credit_limit_tier": credit_limit_tier,
            "apr_rate": card["apr_rate"],
            "apr_category": apr_category,
            "card_status": card["card_status"],
            "issue_date": card["issue_date"],
            "expiry_date": card["expiry_date"],
            "card_age_months": card_age_months,
            "effective_date": datetime.now().date(),
            "expiry_date_scd": None,
            "is_current": True
        }
        
        transformed_credit_cards.append(transformed_card)
    
    logger.info(f"Transformed {len(transformed_credit_cards)} credit cards")
    return transformed_credit_cards

def load_credit_cards(dw_db: Session, transformed_credit_cards: List[Dict[str, Any]]) -> int:
    """
    Load transformed credit cards into the DW database.
    """
    if not transformed_credit_cards:
        logger.info("No credit cards to load")
        return 0
    
    logger.info(f"Loading {len(transformed_credit_cards)} credit cards into DW")
    
    # For each credit card, check if it already exists in the DW
    records_loaded = 0
    for card in transformed_credit_cards:
        # Skip if member_key is None (can't load without a valid member_key)
        if card["member_key"] is None:
            # Try to look up the member_key
            query = text("""
                SELECT member_key
                FROM dim_member
                WHERE member_id = :member_id AND is_current = TRUE
            """)
            
            result = dw_db.execute(query, {"member_id": card["member_id"]})
            member = result.fetchone()
            
            if member:
                card["member_key"] = member.member_key
            else:
                logger.warning(f"Skipping credit card {card['card_id']} - no member_key found")
                continue
        
        # Check if credit card already exists
        query = text("""
            SELECT card_key, card_id
            FROM dim_credit_card
            WHERE card_id = :card_id AND is_current = TRUE
        """)
        
        result = dw_db.execute(query, {"card_id": card["card_id"]})
        existing_card = result.fetchone()
        
        if existing_card:
            # Update existing credit card (SCD Type 2)
            # First, expire the current record
            update_query = text("""
                UPDATE dim_credit_card
                SET is_current = FALSE, expiry_date_scd = :effective_date
                WHERE card_key = :card_key
            """)
            
            dw_db.execute(update_query, {
                "effective_date": card["effective_date"],
                "card_key": existing_card.card_key
            })
        
        # Insert new record
        insert_query = text("""
            INSERT INTO dim_credit_card (
                card_id, member_key, card_type, credit_limit, credit_limit_tier,
                apr_rate, apr_category, card_status, issue_date, expiry_date,
                card_age_months, effective_date, expiry_date_scd, is_current
            ) VALUES (
                :card_id, :member_key, :card_type, :credit_limit, :credit_limit_tier,
                :apr_rate, :apr_category, :card_status, :issue_date, :expiry_date,
                :card_age_months, :effective_date, :expiry_date_scd, :is_current
            )
        """)
        
        dw_db.execute(insert_query, card)
        records_loaded += 1
    
    # Commit the transaction
    dw_db.commit()
    
    logger.info(f"Loaded {records_loaded} credit cards into DW")
    return records_loaded