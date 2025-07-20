from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import logging
import subprocess

from database import get_db
from data_loader import check_database_has_data, load_initial_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/migrations/run", status_code=202)
async def run_migrations():
    """
    Run database migrations manually.
    This is useful for applying schema changes after the application has started.
    """
    try:
        logger.info("Running database migrations...")
        # Run migrations in a background process
        subprocess.Popen(["./run_migrations.sh"])
        return {"message": "Migrations started successfully. Check logs for details."}
    except Exception as e:
        logger.error(f"Error running migrations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error running migrations: {str(e)}")

@router.post("/data/load", status_code=202)
async def load_data(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Load initial data into the database if it's empty.
    This is useful for initializing the database with test data.
    """
    try:
        if not check_database_has_data(db):
            # Run data loading in a background task to avoid blocking the response
            background_tasks.add_task(load_initial_data, db)
            return {"message": "Data loading started. Check logs for details."}
        else:
            return {"message": "Database already has data. No action taken."}
    except Exception as e:
        logger.error(f"Error checking or loading data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error checking or loading data: {str(e)}")

@router.get("/data/status")
async def check_data_status(db: Session = Depends(get_db)):
    """
    Check if the database has data.
    This is useful for monitoring the data load status.
    """
    try:
        has_data = check_database_has_data(db)
        return {"has_data": has_data}
    except Exception as e:
        logger.error(f"Error checking data status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error checking data status: {str(e)}")
