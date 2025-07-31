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

def extract_payment_methods(oltp_db: Session) -> List[Dict[str, Any]]:
    """
    Extract unique payment methods from payment_history table.
    """
    logger.info("Extracting unique payment methods from payment history")

    # SQL query to extract unique payment methods with usage statistics
    query = text("""
        SELECT
            payment_method,
            COUNT(*) as usage_count,
            AVG(payment_amount) as avg_payment_amount,
            SUM(CASE WHEN payment_status = 'on_time' THEN 1 ELSE 0 END) as on_time_count,
            SUM(CASE WHEN payment_status = 'late' THEN 1 ELSE 0 END) as late_count
        FROM payment_history
        WHERE payment_method IS NOT NULL AND payment_method != ''
        GROUP BY payment_method
        ORDER BY usage_count DESC
    """)

    # Execute query
    result = oltp_db.execute(query)

    # Convert result to list of dictionaries
    payment_methods = []
    for row in result:
        payment_method = {
            "payment_method": row.payment_method,
            "usage_count": row.usage_count,
            "avg_payment_amount": row.avg_payment_amount,
            "on_time_count": row.on_time_count,
            "late_count": row.late_count,
            "on_time_rate": (row.on_time_count / row.usage_count) if row.usage_count > 0 else 0
        }
        payment_methods.append(payment_method)

    logger.info(f"Extracted {len(payment_methods)} unique payment methods")
    return payment_methods

def calculate_payment_channel(payment_method: str) -> str:
    """
    Calculate payment channel based on payment method.
    """
    if not payment_method:
        return "Unknown"

    digital_methods = ["auto_pay", "online", "phone"]
    physical_methods = ["mail", "branch"]

    if payment_method.lower() in digital_methods:
        return "Digital"
    elif payment_method.lower() in physical_methods:
        return "Physical"
    else:
        return "Other"

def calculate_convenience_score(payment_method: str) -> int:
    """
    Calculate convenience score (1-5) based on payment method.
    """
    if not payment_method:
        return 0

    convenience_mapping = {
        "auto_pay": 5,    # Highest convenience - automatic
        "online": 4,      # High convenience - self-service, 24/7
        "phone": 3,       # Medium convenience - assisted, business hours
        "mail": 2,        # Low convenience - slow, manual
        "branch": 1       # Lowest convenience - requires travel
    }

    return convenience_mapping.get(payment_method.lower(), 0)

def transform_payment_methods(payment_methods: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transform payment methods data to fit the DW schema.
    """
    logger.info(f"Transforming {len(payment_methods)} payment methods")

    transformed_methods = []
    for method in payment_methods:
        # Calculate derived fields
        payment_channel = calculate_payment_channel(method["payment_method"])
        convenience_score = calculate_convenience_score(method["payment_method"])

        # Create transformed payment method
        transformed_method = {
            "payment_method": method["payment_method"],
            "payment_channel": payment_channel,
            "convenience_score": convenience_score,
            "avg_payment_amount": method["avg_payment_amount"],
            "usage_count": method["usage_count"],
            "on_time_rate": method["on_time_rate"]
        }

        transformed_methods.append(transformed_method)

    logger.info(f"Transformed {len(transformed_methods)} payment methods")
    return transformed_methods

def load_payment_methods(dw_db: Session, transformed_methods: List[Dict[str, Any]]) -> int:
    """
    Load transformed payment methods into the DW database.
    """
    if not transformed_methods:
        logger.info("No payment methods to load")
        return 0

    logger.info(f"Loading {len(transformed_methods)} payment methods into DW")

    records_loaded = 0
    for method in transformed_methods:
        # Check if payment method already exists
        query = text("""
            SELECT payment_method_key
            FROM dim_payment_method
            WHERE payment_method = :payment_method
        """)

        result = dw_db.execute(query, {"payment_method": method["payment_method"]})
        existing_method = result.fetchone()

        if existing_method:
            # Update existing payment method
            update_query = text("""
                UPDATE dim_payment_method
                SET
                    payment_channel = :payment_channel,
                    convenience_score = :convenience_score
                WHERE payment_method_key = :payment_method_key
            """)

            dw_db.execute(update_query, {
                "payment_channel": method["payment_channel"],
                "convenience_score": method["convenience_score"],
                "payment_method_key": existing_method.payment_method_key
            })
        else:
            # Insert new payment method
            insert_query = text("""
                INSERT INTO dim_payment_method (
                    payment_method, payment_channel, convenience_score
                ) VALUES (
                    :payment_method, :payment_channel, :convenience_score
                )
            """)

            dw_db.execute(insert_query, {
                "payment_method": method["payment_method"],
                "payment_channel": method["payment_channel"],
                "convenience_score": method["convenience_score"]
            })

        records_loaded += 1

    # Commit the transaction
    dw_db.commit()

    logger.info(f"Loaded {records_loaded} payment methods into DW")
    return records_loaded

# ------------------------------------
# ETL: Full job with Audit Logging
# ------------------------------------
def run_payment_method_etl(oltp_db: Session, dw_db: Session):
    job_name = "load_dim_payment_method"
    print("DEBUG: Starting run_payment_method_etl function")
    start_time = datetime.now()
    audit_id = None
    records_read = 0
    records_written = 0

    try:
        print(f"DEBUG: About to INSERT audit record for job: {job_name}")
        result = dw_db.execute(text("""
            INSERT INTO etl_job_audit_log (job_name, source_table, target_table, status, start_time)
            VALUES (:job_name, 'payment_history', 'dim_payment_method', 'started', :start_time)
        """), {"job_name": job_name, "start_time": start_time})
        dw_db.commit()
        print(f"DEBUG: INSERT successful, affected rows: {result.rowcount}")

        audit_id = dw_db.execute(text("SELECT LAST_INSERT_ID()")).scalar()
        print(f"DEBUG: Retrieved audit_id = {audit_id}")

        payment_methods = extract_payment_methods(oltp_db)
        records_read = len(payment_methods)
        transformed = transform_payment_methods(payment_methods)
        records_written = load_payment_methods(dw_db, transformed)

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
