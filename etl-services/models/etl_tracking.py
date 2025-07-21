from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from database import Base

class ETLProcessTracking(Base):
    """Model to track ETL process in the data warehouse database.

    This table stores information about which records have been processed by each ETL job,
    allowing the ETL process to resume from where it left off.
    """
    __tablename__ = 'etl_process_tracking'

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_name = Column(String(100), nullable=False)
    source_table = Column(String(100), nullable=False)
    last_processed_id = Column(Integer, nullable=False, default=0)
    last_run_time = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    records_processed = Column(Integer, default=0)
    status = Column(String(50), default='success')
    error_message = Column(Text)

    def __repr__(self):
        return f"<ETLProcessTracking(job_name='{self.job_name}', source_table='{self.source_table}', last_processed_id={self.last_processed_id})>"
