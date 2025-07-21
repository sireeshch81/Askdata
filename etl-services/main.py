import logging
import argparse
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

# Import database connections
from database import get_oltp_session, get_dw_session

# Import ETL job manager
from etl_jobs.etl_manager import run_etl_job

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="ETL Services API")

class ETLJobRequest(BaseModel):
    jobs: Optional[List[str]] = ["all"]

@app.post("/etl")
def trigger_etl(request: ETLJobRequest):
    job_names = request.jobs if "all" not in request.jobs else None
    try:
        oltp_session = get_oltp_session()
        dw_session = get_dw_session()
        result = run_etl_job(oltp_session, dw_session, job_names)
        oltp_session.close()
        dw_session.close()
        if result['status'] == 'failed' or result['status'] == 'completed_with_errors':
            raise HTTPException(status_code=500, detail=result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def main():
    parser = argparse.ArgumentParser(description="Run ETL jobs for AskData")
    parser.add_argument(
        "--jobs", 
        nargs="*", 
        choices=["members", "credit_cards", "payment_history", "financial_health", "financial_products", "all"],
        default=["all"],
        help="Specify jobs to run (default: all)"
    )

    args = parser.parse_args()
    job_names = args.jobs if "all" not in args.jobs else None  # None means run all jobs

    logger.info(f"Starting ETL job execution at {datetime.now().isoformat()}")

    try:
        # Get database sessions
        oltp_session = get_oltp_session()
        dw_session = get_dw_session()

        # Run ETL jobs
        result = run_etl_job(oltp_session, dw_session, job_names)

        # Close sessions
        oltp_session.close()
        dw_session.close()

        logger.info(f"ETL job execution completed at {datetime.now().isoformat()}")
        logger.info(f"Status: {result['status']}")
        logger.info(f"Records processed: {result['records_processed']}")

        if result['status'] == 'failed' or result['status'] == 'completed_with_errors':
            return 1  # Return error code for scheduling systems
        return 0  # Return success code

    except Exception as e:
        logger.error(f"Unexpected error during ETL execution: {str(e)}")
        return 1

if __name__ == "__main__":
    print("Starting ETL service...")
