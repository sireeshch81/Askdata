import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

MYSQL_OLTP_USER = os.getenv("MYSQL_OLTP_USER", "askdata_user")
MYSQL_OLTP_PASSWORD = os.getenv("MYSQL_OLTP_PASSWORD", "askdata_password")
MYSQL_OLTP_HOST = os.getenv("MYSQL_OLTP_HOST", "oltp-db")
MYSQL_OLTP_PORT = os.getenv("MYSQL_OLTP_PORT", "3306")
MYSQL_OLTP_DATABASE = os.getenv("MYSQL_OLTP_DATABASE", "askdata_oltp")

DATABASE_URL = (
    f"mysql+pymysql://{MYSQL_OLTP_USER}:{MYSQL_OLTP_PASSWORD}@{MYSQL_OLTP_HOST}:{MYSQL_OLTP_PORT}/{MYSQL_OLTP_DATABASE}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
