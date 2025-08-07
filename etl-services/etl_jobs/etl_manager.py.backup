import logging
import os
import json
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
import traceback
from typing import List, Optional

# Import ETL tracking model
from models.etl_tracking import ETLProcessTracking

# Import ETL job modules
from etl_jobs.member_etl import extract_members, transform_members, load_members
from etl_jobs.credit_card_etl import extract_credit_cards, transform_credit_cards, load_credit_cards
from etl_jobs.payment_history_etl import extract_payment_history, transform_payment_history, load_payment_history
from etl_jobs.financial_health_etl import extract_financial_health, transform_financial_health, load_financial_health
from etl_jobs.financial_product_etl import extract_financial_products, transform_financial_products, load_financial_products

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Status file for backward compatibility
STATUS_FILE = os.path.join(os.path.dirname(__file__), "status", "last_run_status.json")

def get_last_processed_ids(dw_db: Session):
    """
    Get the IDs of the last processed records from the ETL tracking table.
    If no records exist, return default values (0 for all tables).
    """
    default_ids = {
        "members": 0,
        "credit_cards": 0,
        "payment_history": 0,
        "financial_health_metrics": 0,
        "financial_products": 0
    }
    
    try:
        # Query the ETL tracking table for the last processed IDs
        tracking_records = dw_db.query(ETLProcessTracking).all()
        
        # If no records exist, return default values
        if not tracking_records:
            return default_ids
        
        # Build a dictionary of last processed IDs
        last_processed_ids = {}
        for record in tracking_records:
            last_processed_ids[record.source_table] = record.last_processed_id
        
        # Fill in any missing tables with default values
        for table in default_ids:
            if table not in last_processed_ids:
                last_processed_ids[table] = default_ids[table]
        
        return last_processed_ids
    
    except Exception as e:
        logger.error(f"Error retrieving last processed IDs: {str(e)}")
        return default_ids

def save_last_processed_ids(dw_db: Session, last_processed_ids):
    """
    Save the IDs of the last processed records to the ETL tracking table.
    """
    try:
        # For each table, update or create a tracking record
        for table, last_id in last_processed_ids.items():
            # Check if a record already exists for this table
            tracking_record = dw_db.query(ETLProcessTracking).filter_by(
                job_name='etl_job',
                source_table=table
            ).first()
            
            if tracking_record:
                # Update existing record
                tracking_record.last_processed_id = last_id
                tracking_record.last_run_time = datetime.now()
            else:
                # Create new record
                tracking_record = ETLProcessTracking(
                    job_name='etl_job',
                    source_table=table,
                    last_processed_id=last_id,
                    last_run_time=datetime.now(),
                    records_processed=0,
                    status='success'
                )
                dw_db.add(tracking_record)
            
        # Commit the changes
        dw_db.commit()
    
    except Exception as e:
        logger.error(f"Error saving last processed IDs: {str(e)}")
        dw_db.rollback()

def save_status(status):
    """
    Save the status of the ETL job to the status file.
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
    
    with open(STATUS_FILE, "w") as f:
        json.dump(status, f, indent=2)

def run_etl_job(oltp_db: Session, dw_db: Session, job_names: Optional[List[str]] = None):
    """
    Run the ETL job to extract data from OLTP database, transform it, and load it into DW database.
    """
    start_time = datetime.now()
    status = {
        "status": "running",
        "start_time": start_time.isoformat(),
        "end_time": None,
        "duration_seconds": None,
        "tables_processed": [],
        "records_processed": 0,
        "errors": []
    }
    
    try:
        # Get last processed record IDs
        last_processed_ids = get_last_processed_ids(dw_db)
        
        # Process each table
        tables_to_process = [
            {
                "name": "members",
                "extract": extract_members,
                "transform": transform_members,
                "load": load_members,
                "id_field": "member_id"
            },
            {
                "name": "credit_cards",
                "extract": extract_credit_cards,
                "transform": transform_credit_cards,
                "load": load_credit_cards,
                "id_field": "card_id"
            },
            {
                "name": "payment_history",
                "extract": extract_payment_history,
                "transform": transform_payment_history,
                "load": load_payment_history,
                "id_field": "payment_id"
            },
            {
                "name": "financial_health_metrics",
                "extract": extract_financial_health,
                "transform": transform_financial_health,
                "load": load_financial_health,
                "id_field": "metric_id"
            },
            {
                "name": "financial_products",
                "extract": extract_financial_products,
                "transform": transform_financial_products,
                "load": load_financial_products,
                "id_field": "product_id"
            }
        ]
        
        total_records_processed = 0
        
        for table in tables_to_process:
            table_name = table["name"]
            last_id = last_processed_ids.get(table_name, 0)
            
            try:
                logger.info(f"Processing table {table_name}, starting from ID {last_id}")
                
                # Extract data
                extracted_data = table["extract"](oltp_db, last_id)
                
                if not extracted_data:
                    logger.info(f"No new data to process for table {table_name}")
                    status["tables_processed"].append({
                        "name": table_name,
                        "records_processed": 0,
                        "status": "success",
                        "message": "No new data to process"
                    })
                    continue
                
                # Transform data
                transformed_data = table["transform"](extracted_data)
                
                # Load data
                records_loaded = table["load"](dw_db, transformed_data)
                
                # Update last processed ID
                if records_loaded > 0:
                    max_id = max(item[table["id_field"]] for item in extracted_data)
                    last_processed_ids[table_name] = max_id
                    
                    # Save last processed IDs after each table is processed
                    save_last_processed_ids(dw_db, last_processed_ids)
                
                total_records_processed += records_loaded
                
                status["tables_processed"].append({
                    "name": table_name,
                    "records_processed": records_loaded,
                    "status": "success",
                    "message": f"Processed {records_loaded} records"
                })
                
                logger.info(f"Successfully processed {records_loaded} records for table {table_name}")
            
            except Exception as e:
                error_message = f"Error processing table {table_name}: {str(e)}"
                logger.error(error_message)
                logger.error(traceback.format_exc())
                
                status["tables_processed"].append({
                    "name": table_name,
                    "records_processed": 0,
                    "status": "error",
                    "message": error_message
                })
                
                status["errors"].append({
                    "table": table_name,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                })
        
        # Update status
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        status["status"] = "completed" if not status["errors"] else "completed_with_errors"
        status["end_time"] = end_time.isoformat()
        status["duration_seconds"] = duration
        status["records_processed"] = total_records_processed
        
        logger.info(f"ETL job completed in {duration} seconds, processed {total_records_processed} records")
    
    except Exception as e:
        error_message = f"Error running ETL job: {str(e)}"
        logger.error(error_message)
        logger.error(traceback.format_exc())
        
        # Update status
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        status["status"] = "failed"
        status["end_time"] = end_time.isoformat()
        status["duration_seconds"] = duration
        status["errors"].append({
            "table": "global",
            "error": str(e),
            "traceback": traceback.format_exc()
        })
    
    finally:
        # Save status
        save_status(status)
        
        return status