from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from payment_history_etl import run_payment_history_etl
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Read OLTP DB credentials
MYSQL_OLTP_USER = os.getenv("MYSQL_OLTP_USER")
MYSQL_OLTP_PASSWORD = os.getenv("MYSQL_OLTP_PASSWORD")
MYSQL_OLTP_DATABASE = os.getenv("MYSQL_OLTP_DATABASE")
MYSQL_OLTP_HOST = os.getenv("MYSQL_OLTP_HOST", "oltp-db")
MYSQL_OLTP_PORT = os.getenv("MYSQL_OLTP_PORT", "3306")

# Read DW DB credentials
MYSQL_DW_USER = os.getenv("MYSQL_DW_USER")
MYSQL_DW_PASSWORD = os.getenv("MYSQL_DW_PASSWORD")
MYSQL_DW_DATABASE = os.getenv("MYSQL_DW_DATABASE")
MYSQL_DW_HOST = os.getenv("MYSQL_DW_HOST", "dw-db")
MYSQL_DW_PORT = os.getenv("MYSQL_DW_PORT", "3306")

# Build connection URLs
OLTP_DB_URL = os.getenv("OLTP_DB_URL")
print("Using OLTP DB URL:", OLTP_DB_URL)
DW_DB_URL = os.getenv("DW_DB_URL")
print("Using DW DB URL:", DW_DB_URL)

def main():
    oltp_engine = create_engine(OLTP_DB_URL)
    OltpSession = sessionmaker(bind=oltp_engine)
    oltp_session = OltpSession()

    dw_engine = create_engine(DW_DB_URL)
    DwSession = sessionmaker(bind=dw_engine)
    dw_session = DwSession()

    try:
        last_processed_id = 0
        run_payment_history_etl(oltp_db=oltp_session, dw_db=dw_session, last_processed_id=0)
    finally:
        oltp_session.close()
        dw_session.close()

if __name__ == "__main__":
    main()
