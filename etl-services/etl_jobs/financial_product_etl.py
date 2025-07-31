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

def extract_financial_products(oltp_db: Session, last_processed_id: int) -> List[Dict[str, Any]]:
    """
    Extract financial products from OLTP database that have an ID greater than the last processed ID.
    """
    logger.info(f"Extracting financial products with ID > {last_processed_id}")

    # SQL query to extract financial products
    query = text("""
        SELECT
            product_id, product_name, product_type, product_category, interest_rate,
            credit_limit_min, credit_limit_max, minimum_income_required, minimum_credit_score,
            maximum_debt_to_income, annual_fee, rewards_program, benefits,
            eligibility_criteria
        FROM financial_products
        WHERE product_id > :last_id
        ORDER BY product_id
    """)

    # Execute query
    result = oltp_db.execute(query, {"last_id": last_processed_id})

    # Convert result to list of dictionaries
    products = []
    for row in result:
        product = {
            "product_id": row.product_id,
            "product_name": row.product_name,
            "product_type": row.product_type,
            "product_category": row.product_category,
            "interest_rate": row.interest_rate,
            "credit_limit_min": row.credit_limit_min,
            "credit_limit_max": row.credit_limit_max,
            "minimum_income_required": row.minimum_income_required,
            "minimum_credit_score": row.minimum_credit_score,
            "maximum_debt_to_income": row.maximum_debt_to_income,
            "annual_fee": row.annual_fee,
            "rewards_program": row.rewards_program,
            "benefits": row.benefits,
            "eligibility_criteria": row.eligibility_criteria
        }
        products.append(product)

    logger.info(f"Extracted {len(products)} financial products")
    return products

def calculate_interest_rate_tier(interest_rate: float) -> str:
    """
    Calculate interest rate tier based on interest rate.
    """
    if not interest_rate and interest_rate != 0:
        return "Unknown"

    if interest_rate < 0.05:
        return "Low"
    elif interest_rate < 0.15:
        return "Medium"
    else:
        return "High"

def calculate_fee_category(annual_fee: float) -> str:
    """
    Calculate fee category based on annual fee.
    """
    if not annual_fee and annual_fee != 0:
        return "Unknown"

    if annual_fee == 0:
        return "No Fee"
    elif annual_fee < 100:
        return "Low Fee"
    else:
        return "High Fee"

def calculate_has_rewards(rewards_program: str) -> bool:
    """
    Calculate has_rewards flag based on rewards_program.
    """
    return bool(rewards_program and rewards_program.strip())

def calculate_eligibility_tier(minimum_credit_score: int, minimum_income_required: float, maximum_debt_to_income: float) -> str:
    """
    Calculate eligibility tier based on minimum credit score, minimum income required, and maximum debt to income ratio.
    """
    # Calculate a score based on the eligibility criteria
    score = 0

    # Credit score component
    if minimum_credit_score:
        if minimum_credit_score < 600:
            score += 1  # Easy
        elif minimum_credit_score < 700:
            score += 2  # Medium
        else:
            score += 3  # Strict

    # Income requirement component
    if minimum_income_required:
        if minimum_income_required < 30000:
            score += 1  # Easy
        elif minimum_income_required < 60000:
            score += 2  # Medium
        else:
            score += 3  # Strict

    # Debt to income component
    if maximum_debt_to_income:
        if maximum_debt_to_income > 0.5:
            score += 1  # Easy
        elif maximum_debt_to_income > 0.35:
            score += 2  # Medium
        else:
            score += 3  # Strict

    # Determine tier based on average score
    components = sum(1 for x in [minimum_credit_score, minimum_income_required, maximum_debt_to_income] if x is not None)
    if components == 0:
        return "Unknown"

    avg_score = score / components

    if avg_score < 1.5:
        return "Easy"
    elif avg_score < 2.5:
        return "Medium"
    else:
        return "Strict"

def transform_financial_products(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transform financial products data to fit the DW schema.
    """
    logger.info(f"Transforming {len(products)} financial products")

    transformed_products = []
    for product in products:
        # Calculate derived fields
        interest_rate_tier = calculate_interest_rate_tier(product["interest_rate"])
        fee_category = calculate_fee_category(product["annual_fee"])
        has_rewards = calculate_has_rewards(product["rewards_program"])
        eligibility_tier = calculate_eligibility_tier(
            product["minimum_credit_score"],
            product["minimum_income_required"],
            product["maximum_debt_to_income"]
        )

        # Create transformed product
        transformed_product = {
            "product_id": product["product_id"],
            "product_name": product["product_name"],
            "product_type": product["product_type"],
            "product_category": product["product_category"],
            "interest_rate": product["interest_rate"],
            "interest_rate_tier": interest_rate_tier,
            "credit_limit_min": product["credit_limit_min"],
            "credit_limit_max": product["credit_limit_max"],
            "minimum_income_required": product["minimum_income_required"],
            "minimum_credit_score": product["minimum_credit_score"],
            "maximum_debt_to_income": product["maximum_debt_to_income"],
            "annual_fee": product["annual_fee"],
            "fee_category": fee_category,
            "rewards_program": product["rewards_program"],
            "has_rewards": has_rewards,
            "eligibility_tier": eligibility_tier,
            "is_active": True,  # default to active
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        transformed_products.append(transformed_product)

    logger.info(f"Transformed {len(transformed_products)} financial products")
    return transformed_products

def load_financial_products(dw_db: Session, transformed_products: List[Dict[str, Any]]) -> int:
    """
    Load transformed financial products into the DW database.
    """
    if not transformed_products:
        logger.info("No financial products to load")
        return 0

    logger.info(f"Loading {len(transformed_products)} financial products into DW")

    # For each financial product, check if it already exists in the DW
    records_loaded = 0
    for product in transformed_products:
        # Check if product already exists
        query = text("""
            SELECT product_key, product_id
            FROM dim_financial_product
            WHERE product_id = :product_id
        """)

        result = dw_db.execute(query, {"product_id": product["product_id"]})
        existing_product = result.fetchone()

        if existing_product:
            # Update existing product
            update_query = text("""
                UPDATE dim_financial_product
                SET 
                    product_name = :product_name,
                    product_type = :product_type,
                    product_category = :product_category,
                    interest_rate = :interest_rate,
                    interest_rate_tier = :interest_rate_tier,
                    credit_limit_min = :credit_limit_min,
                    credit_limit_max = :credit_limit_max,
                    minimum_income_required = :minimum_income_required,
                    minimum_credit_score = :minimum_credit_score,
                    maximum_debt_to_income = :maximum_debt_to_income,
                    annual_fee = :annual_fee,
                    fee_category = :fee_category,
                    rewards_program = :rewards_program,
                    has_rewards = :has_rewards,
                    eligibility_tier = :eligibility_tier,
                    is_active = :is_active,
                    updated_at = :updated_at
                WHERE product_key = :product_key
            """)

            dw_db.execute(update_query, {
                **product,
                "product_key": existing_product.product_key
            })
        else:
            # Insert new product
            insert_query = text("""
                INSERT INTO dim_financial_product (
                    product_id, product_name, product_type, product_category,
                    interest_rate, interest_rate_tier, credit_limit_min, credit_limit_max,
                    minimum_income_required, minimum_credit_score, maximum_debt_to_income,
                    annual_fee, fee_category, rewards_program, has_rewards,
                    eligibility_tier, is_active, created_at, updated_at
                ) VALUES (
                    :product_id, :product_name, :product_type, :product_category,
                    :interest_rate, :interest_rate_tier, :credit_limit_min, :credit_limit_max,
                    :minimum_income_required, :minimum_credit_score, :maximum_debt_to_income,
                    :annual_fee, :fee_category, :rewards_program, :has_rewards,
                    :eligibility_tier, :is_active, :created_at, :updated_at
                )
            """)

            dw_db.execute(insert_query, product)

        records_loaded += 1

    # Commit the transaction
    dw_db.commit()

    logger.info(f"Loaded {records_loaded} financial products into DW")
    return records_loaded

# ------------------------------------
# ETL: Full job with Audit Logging
# ------------------------------------
def run_financial_product_etl(oltp_db: Session, dw_db: Session, last_processed_id: int = 0):
    job_name = "load_dim_financial_product"
    print("DEBUG: Starting run_financial_product_etl function")
    start_time = datetime.now()
    audit_id = None
    records_read = 0
    records_written = 0

    try:
        print(f"DEBUG: About to INSERT audit record for job: {job_name}")
        result = dw_db.execute(text("""
            INSERT INTO etl_job_audit_log (job_name, source_table, target_table, status, start_time)
            VALUES (:job_name, 'financial_products', 'dim_financial_product', 'started', :start_time)
        """), {"job_name": job_name, "start_time": start_time})
        dw_db.commit()
        print(f"DEBUG: INSERT successful, affected rows: {result.rowcount}")

        audit_id = dw_db.execute(text("SELECT LAST_INSERT_ID()")).scalar()
        print(f"DEBUG: Retrieved audit_id = {audit_id}")

        products = extract_financial_products(oltp_db, last_processed_id)
        records_read = len(products)
        transformed = transform_financial_products(products)
        records_written = load_financial_products(dw_db, transformed)

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





































