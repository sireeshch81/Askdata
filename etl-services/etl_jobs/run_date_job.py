from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from date_etl import run_date_etl
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
    # Date ETL only needs DW connection (no OLTP needed)
    dw_engine = create_engine(DW_DB_URL)
    DwSession = sessionmaker(bind=dw_engine)
    dw_session = DwSession()

    try:
        # Generate dates from 2020 to 2030 (11 years = ~4,018 dates)
        run_date_etl(dw_db=dw_session, start_year=2020, end_year=2030)
    finally:
        dw_session.close()

if __name__ == "__main__":
    main()
