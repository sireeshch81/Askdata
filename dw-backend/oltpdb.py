import os

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from models import Member
# from models import DimMember

load_dotenv()

# Database connection settings
MYSQL_OLTP_USER = os.getenv("MYSQL_OLTP_USER", "root")
MYSQL_OLTP_PASSWORD = os.getenv("MYSQL_OLTP_PASSWORD", "password")
MYSQL_OLTP_HOST = os.getenv("MYSQL_OLTP_HOST", "oltp-db")
MYSQL_OLTP_PORT = os.getenv("MYSQL_OLTP_PORT", "3306")
MYSQL_OLTP_DATABASE = os.getenv("MYSQL_OLTP_DATABASE", "askdata_oltp")

# Create SQLAlchemy database URL 
DATABASE_URL = f"mysql+pymysql://{MYSQL_OLTP_USER}:{MYSQL_OLTP_PASSWORD}@{MYSQL_OLTP_HOST}:{MYSQL_OLTP_PORT}/{MYSQL_OLTP_DATABASE}"

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Enables reconnection on stale connections
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=False  # Set to True to see SQL queries
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_member_details(member_id: str):
    try:
        db = SessionLocal()
        member = db.query(Member).filter(Member.member_id == member_id).first()
        if member:
            return {
                "member_id": member.member_id,
                "first_name": member.first_name,
                "last_name": member.last_name,
                "email": member.email,
                "phone": member.phone,
                "address": member.address,
                "city": member.city,
                "state": member.state,
                "zip_code": member.zip_code,
            }
        return None
    finally:
        if db:
            db.close()
