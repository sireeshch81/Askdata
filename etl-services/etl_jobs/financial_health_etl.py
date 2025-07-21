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

def extract_financial_health(oltp_db: Session, last_processed_id: int) -> List[Dict[str, Any]]:
    """
    Extract financial health metrics from OLTP database that have an ID greater than the last processed ID.
    """
    logger.info(f"Extracting financial health metrics with ID > {last_processed_id}")
    
    # SQL query to extract financial health metrics with dimension keys
    query = text("""
        SELECT 
            fh.metric_id, fh.member_id, fh.assessment_date, fh.credit_score, 
            fh.debt_to_income_ratio, fh.credit_utilization_ratio, fh.payment_reliability_score, 
            fh.savings_balance, fh.checking_balance, fh.total_debt, fh.number_of_accounts, 
            fh.recent_inquiries, fh.delinquent_accounts, fh.health_score, fh.risk_category, 
            fh.created_at, m.member_key, d.date_key as assessment_date_key
        FROM financial_health_metrics fh
        JOIN dim_member m ON fh.member_id = m.member_id AND m.is_current = TRUE
        JOIN dim_date d ON fh.assessment_date = d.date_value
        WHERE fh.metric_id > :last_id
        ORDER BY fh.metric_id
    """)
    
    try:
        # Execute query
        result = oltp_db.execute(query, {"last_id": last_processed_id})
        
        # Convert result to list of dictionaries
        health_metrics = []
        for row in result:
            health_metric = {
                "metric_id": row.metric_id,
                "member_id": row.member_id,
                "assessment_date": row.assessment_date,
                "credit_score": row.credit_score,
                "debt_to_income_ratio": row.debt_to_income_ratio,
                "credit_utilization_ratio": row.credit_utilization_ratio,
                "payment_reliability_score": row.payment_reliability_score,
                "savings_balance": row.savings_balance,
                "checking_balance": row.checking_balance,
                "total_debt": row.total_debt,
                "number_of_accounts": row.number_of_accounts,
                "recent_inquiries": row.recent_inquiries,
                "delinquent_accounts": row.delinquent_accounts,
                "health_score": row.health_score,
                "risk_category": row.risk_category,
                "created_at": row.created_at,
                "member_key": row.member_key,
                "assessment_date_key": row.assessment_date_key
            }
            health_metrics.append(health_metric)
        
        logger.info(f"Extracted {len(health_metrics)} financial health metrics")
        return health_metrics
    
    except Exception as e:
        # If the join fails, try without the joins
        logger.warning(f"Error extracting financial health metrics with joins: {str(e)}. Trying without joins.")
        
        # SQL query without joins
        query = text("""
            SELECT 
                metric_id, member_id, assessment_date, credit_score, 
                debt_to_income_ratio, credit_utilization_ratio, payment_reliability_score, 
                savings_balance, checking_balance, total_debt, number_of_accounts, 
                recent_inquiries, delinquent_accounts, health_score, risk_category, 
                created_at
            FROM financial_health_metrics
            WHERE metric_id > :last_id
            ORDER BY metric_id
        """)
        
        # Execute query
        result = oltp_db.execute(query, {"last_id": last_processed_id})
        
        # Convert result to list of dictionaries
        health_metrics = []
        for row in result:
            health_metric = {
                "metric_id": row.metric_id,
                "member_id": row.member_id,
                "assessment_date": row.assessment_date,
                "credit_score": row.credit_score,
                "debt_to_income_ratio": row.debt_to_income_ratio,
                "credit_utilization_ratio": row.credit_utilization_ratio,
                "payment_reliability_score": row.payment_reliability_score,
                "savings_balance": row.savings_balance,
                "checking_balance": row.checking_balance,
                "total_debt": row.total_debt,
                "number_of_accounts": row.number_of_accounts,
                "recent_inquiries": row.recent_inquiries,
                "delinquent_accounts": row.delinquent_accounts,
                "health_score": row.health_score,
                "risk_category": row.risk_category,
                "created_at": row.created_at,
                "member_key": None,  # Will be looked up during transformation
                "assessment_date_key": None  # Will be looked up during transformation
            }
            health_metrics.append(health_metric)
        
        logger.info(f"Extracted {len(health_metrics)} financial health metrics (without joins)")
        return health_metrics

def calculate_total_liquid_assets(savings_balance: float, checking_balance: float) -> float:
    """
    Calculate total liquid assets based on savings and checking balances.
    """
    savings = savings_balance or 0
    checking = checking_balance or 0
    return savings + checking

def calculate_debt_to_assets_ratio(total_debt: float, total_liquid_assets: float) -> float:
    """
    Calculate debt to assets ratio based on total debt and total liquid assets.
    """
    if not total_liquid_assets or total_liquid_assets == 0:
        return None
    
    return total_debt / total_liquid_assets if total_debt else 0

def calculate_net_worth(total_liquid_assets: float, total_debt: float) -> float:
    """
    Calculate net worth based on total liquid assets and total debt.
    """
    assets = total_liquid_assets or 0
    debt = total_debt or 0
    return assets - debt

def calculate_credit_score_tier(credit_score: int) -> str:
    """
    Calculate credit score tier based on credit score.
    """
    if not credit_score:
        return "Unknown"
    
    if credit_score >= 800:
        return "Excellent"
    elif credit_score >= 740:
        return "Very Good"
    elif credit_score >= 670:
        return "Good"
    elif credit_score >= 580:
        return "Fair"
    else:
        return "Poor"

def calculate_utilization_tier(credit_utilization_ratio: float) -> str:
    """
    Calculate utilization tier based on credit utilization ratio.
    """
    if not credit_utilization_ratio and credit_utilization_ratio != 0:
        return "Unknown"
    
    if credit_utilization_ratio < 0.10:
        return "Low"
    elif credit_utilization_ratio < 0.30:
        return "Medium"
    elif credit_utilization_ratio < 0.80:
        return "High"
    else:
        return "Maxed"

def transform_financial_health(health_metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transform financial health metrics data to fit the DW schema.
    """
    logger.info(f"Transforming {len(health_metrics)} financial health metrics")
    
    transformed_metrics = []
    for metric in health_metrics:
        # Calculate derived measures
        total_liquid_assets = calculate_total_liquid_assets(metric["savings_balance"], metric["checking_balance"])
        debt_to_assets_ratio = calculate_debt_to_assets_ratio(metric["total_debt"], total_liquid_assets)
        net_worth = calculate_net_worth(total_liquid_assets, metric["total_debt"])
        credit_score_tier = calculate_credit_score_tier(metric["credit_score"])
        utilization_tier = calculate_utilization_tier(metric["credit_utilization_ratio"])
        
        # Create transformed financial health metric
        transformed_metric = {
            "member_key": metric["member_key"],
            "assessment_date_key": metric["assessment_date_key"],
            "credit_score": metric["credit_score"],
            "debt_to_income_ratio": metric["debt_to_income_ratio"],
            "credit_utilization_ratio": metric["credit_utilization_ratio"],
            "payment_reliability_score": metric["payment_reliability_score"],
            "savings_balance": metric["savings_balance"],
            "checking_balance": metric["checking_balance"],
            "total_debt": metric["total_debt"],
            "number_of_accounts": metric["number_of_accounts"],
            "recent_inquiries": metric["recent_inquiries"],
            "delinquent_accounts": metric["delinquent_accounts"],
            "health_score": metric["health_score"],
            "total_liquid_assets": total_liquid_assets,
            "debt_to_assets_ratio": debt_to_assets_ratio,
            "net_worth": net_worth,
            "risk_category": metric["risk_category"],
            "credit_score_tier": credit_score_tier,
            "utilization_tier": utilization_tier,
            "created_datetime": datetime.now()
        }
        
        transformed_metrics.append(transformed_metric)
    
    logger.info(f"Transformed {len(transformed_metrics)} financial health metrics")
    return transformed_metrics

def load_financial_health(dw_db: Session, transformed_metrics: List[Dict[str, Any]]) -> int:
    """
    Load transformed financial health metrics into the DW database.
    """
    if not transformed_metrics:
        logger.info("No financial health metrics to load")
        return 0
    
    logger.info(f"Loading {len(transformed_metrics)} financial health metrics into DW")
    
    # For each financial health metric, look up any missing dimension keys
    records_loaded = 0
    for metric in transformed_metrics:
        # Skip if any required dimension key is missing
        missing_keys = []
        
        if metric["member_key"] is None:
            missing_keys.append("member_key")
            # Try to look up the member_key
            query = text("""
                SELECT member_key
                FROM dim_member
                WHERE member_id = :member_id AND is_current = TRUE
            """)
            
            result = dw_db.execute(query, {"member_id": metric["member_id"]})
            member = result.fetchone()
            
            if member:
                metric["member_key"] = member.member_key
            else:
                logger.warning(f"No member_key found for member_id {metric['member_id']}")
        
        if metric["assessment_date_key"] is None:
            missing_keys.append("assessment_date_key")
            # Try to look up the assessment_date_key
            query = text("""
                SELECT date_key
                FROM dim_date
                WHERE date_value = :date_value
            """)
            
            result = dw_db.execute(query, {"date_value": metric["assessment_date"]})
            date_record = result.fetchone()
            
            if date_record:
                metric["assessment_date_key"] = date_record.date_key
            else:
                logger.warning(f"No date_key found for date {metric['assessment_date']}")
        
        # Skip if any required dimension key is still missing
        if metric["member_key"] is None or metric["assessment_date_key"] is None:
            logger.warning(f"Skipping financial health metric - missing dimension keys: {missing_keys}")
            continue
        
        # Insert new record
        insert_query = text("""
            INSERT INTO fact_financial_health (
                member_key, assessment_date_key, credit_score, debt_to_income_ratio,
                credit_utilization_ratio, payment_reliability_score, savings_balance,
                checking_balance, total_debt, number_of_accounts, recent_inquiries,
                delinquent_accounts, health_score, total_liquid_assets, debt_to_assets_ratio,
                net_worth, risk_category, credit_score_tier, utilization_tier, created_datetime
            ) VALUES (
                :member_key, :assessment_date_key, :credit_score, :debt_to_income_ratio,
                :credit_utilization_ratio, :payment_reliability_score, :savings_balance,
                :checking_balance, :total_debt, :number_of_accounts, :recent_inquiries,
                :delinquent_accounts, :health_score, :total_liquid_assets, :debt_to_assets_ratio,
                :net_worth, :risk_category, :credit_score_tier, :utilization_tier, :created_datetime
            )
        """)
        
        dw_db.execute(insert_query, metric)
        records_loaded += 1
    
    # Commit the transaction
    dw_db.commit()
    
    logger.info(f"Loaded {records_loaded} financial health metrics into DW")
    return records_loaded