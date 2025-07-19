import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection settings
MYSQL_OLTP_USER = os.getenv("MYSQL_OLTP_USER", "root")
MYSQL_OLTP_PASSWORD = os.getenv("MYSQL_OLTP_PASSWORD", "password")
MYSQL_OLTP_HOST = os.getenv("MYSQL_OLTP_HOST", "oltp-db")
MYSQL_OLTP_PORT = os.getenv("MYSQL_OLTP_PORT", "3306")
MYSQL_OLTP_DATABASE = os.getenv("MYSQL_OLTP_DATABASE", "oltp")

# Create SQLAlchemy database URL
DATABASE_URL = f"mysql+pymysql://{MYSQL_OLTP_USER}:{MYSQL_OLTP_PASSWORD}@{MYSQL_OLTP_HOST}:{MYSQL_OLTP_PORT}/{MYSQL_OLTP_DATABASE}"

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Enables reconnection on stale connections
    pool_recycle=3600,   # Recycle connections after 1 hour
    echo=False           # Set to True to see SQL queries
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