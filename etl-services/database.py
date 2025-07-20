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

# Create connection/session functions for script-based usage
def get_oltp_connection():
    return oltp_engine.connect()

def get_dw_connection():
    return dw_engine.connect()

def get_oltp_session():
    Session = sessionmaker(bind=oltp_engine)
    return Session()

def get_dw_session():
    Session = sessionmaker(bind=dw_engine)
    return Session()

# Base class for models
Base = declarative_base()