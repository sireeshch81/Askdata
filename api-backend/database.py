import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection settings
MYSQL_DW_USER = os.getenv("MYSQL_DW_USER", "root")
MYSQL_DW_PASSWORD = os.getenv("MYSQL_DW_PASSWORD", "password")
MYSQL_DW_HOST = os.getenv("MYSQL_DW_HOST", "dw-db")
MYSQL_DW_PORT = os.getenv("MYSQL_DW_PORT", "3306")
MYSQL_DW_DATABASE = os.getenv("MYSQL_DW_DATABASE", "dw")

# Create SQLAlchemy database URL
DATABASE_URL = f"mysql+pymysql://{MYSQL_DW_USER}:{MYSQL_DW_PASSWORD}@{MYSQL_DW_HOST}:{MYSQL_DW_PORT}/{MYSQL_DW_DATABASE}"

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