from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# OLTP Database connection
OLTP_USER = os.getenv("MYSQL_OLTP_USER", "askdata")
OLTP_PASSWORD = os.getenv("MYSQL_OLTP_PASSWORD", "askdata")
OLTP_HOST = os.getenv("MYSQL_OLTP_HOST", "oltp-db")
OLTP_PORT = os.getenv("MYSQL_OLTP_PORT", "3306")
OLTP_DATABASE = os.getenv("MYSQL_OLTP_DATABASE", "askdata_oltp")

OLTP_DATABASE_URL = f"mysql+pymysql://{OLTP_USER}:{OLTP_PASSWORD}@{OLTP_HOST}:{OLTP_PORT}/{OLTP_DATABASE}"

# DW Database connection
DW_USER = os.getenv("MYSQL_DW_USER", "askdata")
DW_PASSWORD = os.getenv("MYSQL_DW_PASSWORD", "askdata")
DW_HOST = os.getenv("MYSQL_DW_HOST", "dw-db")
DW_PORT = os.getenv("MYSQL_DW_PORT", "3306")
DW_DATABASE = os.getenv("MYSQL_DW_DATABASE", "askdata_dw")

DW_DATABASE_URL = f"mysql+pymysql://{DW_USER}:{DW_PASSWORD}@{DW_HOST}:{DW_PORT}/{DW_DATABASE}"

# Create engines
try:
    oltp_engine = create_engine(OLTP_DATABASE_URL)
    logger.info("OLTP database engine created successfully")
except Exception as e:
    logger.error(f"Error creating OLTP database engine: {str(e)}")
    raise

try:
    dw_engine = create_engine(DW_DATABASE_URL)
    logger.info("DW database engine created successfully")
except Exception as e:
    logger.error(f"Error creating DW database engine: {str(e)}")
    raise

# Create sessionmakers
OLTPSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=oltp_engine)
DWSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=dw_engine)

# Base classes for models
OLTPBase = declarative_base()
DWBase = declarative_base()

# Dependency to get OLTP database session
def get_oltp_db():
    db = OLTPSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency to get DW database session
def get_dw_db():
    db = DWSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to test database connections
def test_connections():
    try:
        # Test OLTP connection
        with oltp_engine.connect() as conn:
            logger.info("OLTP database connection successful")
        
        # Test DW connection
        with dw_engine.connect() as conn:
            logger.info("DW database connection successful")
        
        return True
    except Exception as e:
        logger.error(f"Error testing database connections: {str(e)}")
        return False