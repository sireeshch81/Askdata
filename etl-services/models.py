from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class ETLJobStatus(Base):
    """
    Model to track ETL job status.
    """
    __tablename__ = 'etl_job_status'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_name = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)  # running, completed, completed_with_errors, failed
    start_time = Column(DateTime, nullable=False, default=func.now())
    end_time = Column(DateTime)
    duration_seconds = Column(Integer)
    records_processed = Column(Integer, default=0)
    tables_processed = Column(JSON)
    errors = Column(JSON)
    last_processed_ids = Column(JSON)
    created_at = Column(DateTime, nullable=False, default=func.now())
    
    def __repr__(self):
        return f"<ETLJobStatus(id={self.id}, job_name='{self.job_name}', status='{self.status}')>"

class ETLJobConfig(Base):
    """
    Model to store ETL job configuration.
    """
    __tablename__ = 'etl_job_config'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    schedule = Column(String(100))  # cron expression
    last_run_id = Column(Integer)  # reference to ETLJobStatus.id
    last_run_time = Column(DateTime)
    config = Column(JSON)  # job-specific configuration
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<ETLJobConfig(id={self.id}, job_name='{self.job_name}', is_active={self.is_active})>"