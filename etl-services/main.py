from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
import os
import logging
from typing import Dict, List, Optional
import json
from datetime import datetime

# Import database connections
from database import get_oltp_db, get_dw_db

# Import ETL jobs
from etl_jobs.etl_manager import run_etl_job

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ETL Services",
    description="ETL Services for AskData",
    version="0.1.0",
)

@app.get("/")
def read_root():
    return {"message": "Welcome to ETL Services"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/etl")
async def trigger_etl(
    background_tasks: BackgroundTasks,
    oltp_db: Session = Depends(get_oltp_db),
    dw_db: Session = Depends(get_dw_db)
):
    """
    Trigger ETL jobs to extract data from OLTP database, transform it, and load it into DW database.
    The ETL process runs in the background.
    """
    try:
        # Add ETL job to background tasks
        background_tasks.add_task(run_etl_job, oltp_db, dw_db)
        return {"status": "ETL job started", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Error triggering ETL job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error triggering ETL job: {str(e)}")

@app.get("/etl/status")
def get_etl_status():
    """
    Get the status of the last ETL job.
    """
    try:
        # Check if status file exists
        status_file_path = os.path.join(os.path.dirname(__file__), "etl_jobs", "status", "last_run_status.json")
        if not os.path.exists(status_file_path):
            return {"status": "No ETL job has been run yet"}
        
        # Read status file
        with open(status_file_path, "r") as f:
            status = json.load(f)
        
        return status
    except Exception as e:
        logger.error(f"Error getting ETL status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting ETL status: {str(e)}")