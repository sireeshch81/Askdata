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

    # Simple SQL query to extract payment history (no cross-database JOINs)
    query = text("""
        SELECT
            payment_id, member_id, card_id, payment_date, payment_amount,
            minimum_due, payment_status, days_late, late_fee,
            statement_balance, payment_method
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
            # These will be looked up during transformation
            "member_key": None,
            "card_key": None,
            "payment_date_key": None,
            "payment_method_key": None
        }
        payments.append(payment)

    logger.info(f"Extracted {len(payments)} payment history records")
    return payments

def lookup_dimension_keys(dw_db: Session, payment: Dict[str, Any]) -> Dict[str, Any]:
    """
    Lookup dimension keys for a payment record.
    """
    # Lookup member_key
    if payment["member_id"]:
        query = text("""
            SELECT member_key
            FROM dim_member
            WHERE member_id = :member_id AND is_current = TRUE
        """)
        result = dw_db.execute(query, {"member_id": payment["member_id"]})
        member = result.fetchone()
        if member:
            payment["member_key"] = member.member_key

    # Lookup card_key
    if payment["card_id"]:
        query = text("""
            SELECT card_key
            FROM dim_credit_card
            WHERE card_id = :card_id AND is_current = TRUE
        """)
        result = dw_db.execute(query, {"card_id": payment["card_id"]})
        card = result.fetchone()
        if card:
            payment["card_key"] = card.card_key

    # Lookup payment_date_key
    if payment["payment_date"]:
        # Convert string date to proper format if needed
        payment_date = payment["payment_date"]
        if isinstance(payment_date, str):
            try:
                payment_date = datetime.strptime(payment_date, "%Y-%m-%d").date()
            except ValueError:
                logger.warning(f"Invalid date format: {payment_date}")
                payment_date = None

        if payment_date:
            date_key = int(payment_date.strftime("%Y%m%d"))  # Convert to YYYYMMDD format
            query = text("""
                SELECT date_key
                FROM dim_date
                WHERE date_key = :date_key
            """)
            result = dw_db.execute(query, {"date_key": date_key})
            date_record = result.fetchone()
            if date_record:
                payment["payment_date_key"] = date_record.date_key

    # Lookup payment_method_key
    if payment["payment_method"]:
        query = text("""
            SELECT payment_method_key
            FROM dim_payment_method
            WHERE payment_method = :payment_method
        """)
        result = dw_db.execute(query, {"payment_method": payment["payment_method"]})
        payment_method = result.fetchone()
        if payment_method:
            payment["payment_method_key"] = payment_method.payment_method_key

    return payment

def transform_payment_history(dw_db: Session, payments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transform payment history data to fit the DW schema.
    """
    logger.info(f"Transforming {len(payments)} payment history records")

    transformed_payments = []
    skipped_count = 0

    for payment in payments:
        # Lookup dimension keys
        payment = lookup_dimension_keys(dw_db, payment)

        # Skip if any required dimension key is missing
        if not all([payment["member_key"], payment["card_key"], 
                   payment["payment_date_key"], payment["payment_method_key"]]):
            skipped_count += 1
            logger.warning(f"Skipping payment {payment['payment_id']} - missing dimension keys")
            continue


        # Calculate derived measures
        payment_ratio = None
        excess_payment = None

        if payment["minimum_due"] and payment["minimum_due"] > 0 and payment["payment_amount"]:
            calculated_ratio = float(payment["payment_amount"] / payment["minimum_due"])
            # Cap payment_ratio at 9.9999 to fit decimal(5,4) column
            payment_ratio = min(calculated_ratio, 9.9999)

        if payment["payment_amount"] is not None and payment["minimum_due"] is not None:
            excess_payment = float(payment["payment_amount"] - payment["minimum_due"])


        # Calculate flags
        is_on_time = payment["payment_status"] == "on_time"
        is_full_payment = False
        is_minimum_payment = False
        is_over_payment = False

        if payment["payment_amount"] is not None and payment["statement_balance"] is not None:
            is_full_payment = payment["payment_amount"] >= payment["statement_balance"]
            is_over_payment = payment["payment_amount"] > payment["statement_balance"]

        if payment["payment_amount"] is not None and payment["minimum_due"] is not None:
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
    if skipped_count > 0:
        logger.warning(f"Skipped {skipped_count} records due to missing dimension keys")

    return transformed_payments

def load_payment_history(dw_db: Session, transformed_payments: List[Dict[str, Any]]) -> int:
    """
    Load transformed payment history into the DW database.
    """
    if not transformed_payments:
        logger.info("No payment history to load")
        return 0

    logger.info(f"Loading {len(transformed_payments)} payment history records into DW")

    records_loaded = 0
    batch_size = 1000  # Load in batches for better performance

    for i in range(0, len(transformed_payments), batch_size):
        batch = transformed_payments[i:i+batch_size]

        for payment in batch:
            # Insert new record (fact tables typically don't update, just insert)
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

        # Commit batch
        dw_db.commit()
        logger.info(f"Loaded batch {i//batch_size + 1}/{(len(transformed_payments) + batch_size - 1)//batch_size}")

    logger.info(f"Loaded {records_loaded} payment history records into DW")
    return records_loaded

# ------------------------------------
# ETL: Full job with Audit Logging
# ------------------------------------
def run_payment_history_etl(oltp_db: Session, dw_db: Session, last_processed_id: int = 0):
    job_name = "load_fact_payment"
    print("DEBUG: Starting run_payment_history_etl function")
    start_time = datetime.now()
    audit_id = None
    records_read = 0
    records_written = 0

    try:
        print(f"DEBUG: About to INSERT audit record for job: {job_name}")
        result = dw_db.execute(text("""
            INSERT INTO etl_job_audit_log (job_name, source_table, target_table, status, start_time)
            VALUES (:job_name, 'payment_history', 'fact_payment', 'started', :start_time)
        """), {"job_name": job_name, "start_time": start_time})
        dw_db.commit()
        print(f"DEBUG: INSERT successful, affected rows: {result.rowcount}")

        audit_id = dw_db.execute(text("SELECT LAST_INSERT_ID()")).scalar()
        print(f"DEBUG: Retrieved audit_id = {audit_id}")

        payments = extract_payment_history(oltp_db, last_processed_id)
        records_read = len(payments)
        transformed = transform_payment_history(dw_db, payments)
        records_written = load_payment_history(dw_db, transformed)

        end_time = datetime.now()
        print(f"DEBUG: About to UPDATE audit_id {audit_id} with {records_written} records")
        dw_db.execute(text("""
            UPDATE etl_job_audit_log
            SET status = 'success',
                records_read = :records_read,
                records_written = :records_written,
                end_time = :end_time,
                duration_seconds = TIMESTAMPDIFF(SECOND, :start_time, :end_time)
            WHERE audit_id = :audit_id
        """), {
            "records_read": records_read,
            "records_written": records_written,
            "end_time": end_time,
            "start_time": start_time,
            "audit_id": audit_id
        })
        dw_db.commit()
    except Exception as e:
        end_time = datetime.now()
        dw_db.execute(text("""
            UPDATE etl_job_audit_log
            SET status = 'failed',
                error_message = :error,
                end_time = :end_time,
                duration_seconds = TIMESTAMPDIFF(SECOND, :start_time, :end_time)
            WHERE audit_id = :audit_id
        """), {
            "error": str(e),
            "end_time": end_time,
            "start_time": start_time,
            "audit_id": audit_id
        })
        dw_db.commit()
        logger.exception("ETL job failed.")
        raise
