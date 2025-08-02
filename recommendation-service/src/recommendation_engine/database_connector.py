import os
import sys
import logging
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Detect if running in Docker vs local development
if os.path.exists('/app/config/docker_config.py'):
    # Running in Docker container
    sys.path.append('/app')
    from config.docker_config import OLTP_DATABASE_URL, DW_DATABASE_URL
else:
    # Running locally
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from config.config import OLTP_DATABASE_URL, DW_DATABASE_URL

logger = logging.getLogger(__name__)

class DatabaseConnector:
    """Handles database connections using SQLAlchemy (works in Docker and local)"""
    
    def __init__(self):
        self.engine = None
        self.current_source = None
    
    def connect(self, source='oltp'):
        """Connect to specified database using SQLAlchemy"""
        try:
            database_url = OLTP_DATABASE_URL if source == 'oltp' else DW_DATABASE_URL
            self.engine = create_engine(database_url)
            self.current_source = source
            
            # Test connection
            with self.engine.connect() as conn:
                pass
            
            logger.info(f"✅ Connected to {source.upper()} database")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def execute_query(self, query: str, params: tuple = None) -> pd.DataFrame:
        """Execute query and return DataFrame using pandas + SQLAlchemy"""
        try:
            if not self.engine:
                logger.warning("No engine, reconnecting...")
                self.connect(self.current_source)
            
            # Convert tuple params to dict for pandas.read_sql
            if params:
                # For pandas.read_sql, we need to handle parameters differently
                return pd.read_sql(query, self.engine, params=params)
            else:
                return pd.read_sql(query, self.engine)
                
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return pd.DataFrame()
    
    def get_connection(self):
        """Get raw SQLAlchemy connection"""
        if self.engine:
            return self.engine.connect()
        return None
    
    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")
