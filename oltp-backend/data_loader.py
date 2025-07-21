import os
import logging
import pandas as pd
import sqlalchemy
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Data directory
DATA_DIR = "/app/financial_data"

# Tables to check for data
TABLES_TO_CHECK = [
    "members",
    "financial_health_metrics",
    "credit_cards",
    "payment_history",
    "financial_products"
]

# CSV to table mapping
CSV_TO_TABLE_MAPPING = {
    "members.csv": "members",
    "financial_health_metrics.csv": "financial_health_metrics",
    "credit_cards.csv": "credit_cards",
    "payment_history.csv": "payment_history",
    "financial_products.csv": "financial_products"
}

def check_database_has_data(db: Session) -> bool:
    """
    Check if the OLTP database already has data.
    Returns True if any of the key tables has at least one record.
    """
    try:
        for table in TABLES_TO_CHECK:
            query = text(f"SELECT COUNT(*) as count FROM {table}")
            result = db.execute(query).fetchone()

            if result and result.count > 0:
                logger.info(f"Table '{table}' already has {result.count} records")
                return True

        logger.info("No data found in any of the key tables")
        return False
    except SQLAlchemyError as e:
        logger.error(f"Error checking database for data: {str(e)}")
        # If we can't check, assume there's no data
        return False

def get_csv_files() -> list:
    """
    Get a list of CSV files in the data directory.
    """
    try:
        if not os.path.exists(DATA_DIR):
            logger.error(f"Data directory {DATA_DIR} does not exist")
            return []

        csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
        logger.info(f"Found {len(csv_files)} CSV files in {DATA_DIR}")
        return csv_files
    except Exception as e:
        logger.error(f"Error listing CSV files: {str(e)}")
        return []

def load_csv_to_table(db: Session, csv_file: str, table_name: str) -> int:
    """
    Load data from a CSV file into a database table.
    Returns the number of records loaded.
    """
    try:
        file_path = os.path.join(DATA_DIR, csv_file)

        if not os.path.exists(file_path):
            logger.error(f"CSV file {file_path} does not exist")
            return 0

        # Read CSV file into DataFrame
        df = pd.read_csv(file_path)
        logger.info(f"Read {len(df)} records from {csv_file}")

        # Convert DataFrame to SQL and load into database
        conn = db.connection()
        df.to_sql(table_name, conn, if_exists='append', index=False)

        logger.info(f"Loaded {len(df)} records into {table_name}")
        return len(df)
    except Exception as e:
        logger.error(f"Error loading data from {csv_file} to {table_name}: {str(e)}")
        return 0

def load_initial_data(db: Session):
    """
    Load initial data from CSV files into the database.
    Returns a dictionary with table names and record counts.
    """
    loaded_data = {}

    try:
        if check_database_has_data(db):
            logger.info("Database already has data, skipping initial load")
            return
        else:
            csv_files = get_csv_files()

            if not csv_files:
                logger.warning("No CSV files found to load")
                return loaded_data

            # Load each CSV file into the corresponding table
            for csv_file in csv_files:
                if csv_file in CSV_TO_TABLE_MAPPING:
                    table_name = CSV_TO_TABLE_MAPPING[csv_file]
                    records_loaded = load_csv_to_table(db, csv_file, table_name)
                    loaded_data[table_name] = records_loaded
                else:
                    logger.warning(f"No table mapping for {csv_file}, skipping")

            db.commit()

            return loaded_data
    except Exception as e:
        logger.error(f"Error loading initial data: {str(e)}")
        db.rollback()
        return loaded_data

if __name__ == "__main__":
    logger.info("Starting initial data load...")
    db_gen = database.get_db()
    db = next(db_gen)
    try:
        load_initial_data(db)
        logger.info("Initial data load completed")
    finally:
        db.close()
