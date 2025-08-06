import os
import sys
import logging
import time
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

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
        # MongoDB connection attributes
        self.mongo_client = None
        self.mongo_db = None

    def connect(self, source='oltp'):
        """Connect to specified database using SQLAlchemy with retry logic"""
        database_url = OLTP_DATABASE_URL if source == 'oltp' else DW_DATABASE_URL
        max_retries = 5
        retry_delay = 5  # seconds

        for attempt in range(1, max_retries + 1):
            try:
                self.engine = create_engine(database_url)
                self.current_source = source
                
                # Test connection
                with self.engine.connect() as conn:
                    pass
                
                logger.info(f"✅ Connected to {source.upper()} database on attempt {attempt}")
                return True
            except Exception as e:
                logger.error(f"❌ Database connection failed on attempt {attempt}: {e}")
                if attempt < max_retries:
                    time.sleep(retry_delay)
                else:
                    logger.error("❌ Exhausted all retries to connect to database.")
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

    def connect_mongodb(self, 
                       host: str = "localhost", 
                       port: int = 27017, 
                       database: str = "askdata_mongo",
                       username: str = None,
                       password: str = None) -> bool:
        """Connect to MongoDB with SSL disabled for local development"""
        try:
            # Build connection string with SSL disabled
            if username and password:
                connection_string = f"mongodb://{username}:{password}@{host}:{port}/{database}?authSource=admin&ssl=false&tlsAllowInvalidCertificates=true"
            else:
                connection_string = f"mongodb://{host}:{port}/{database}?ssl=false"
            
            self.mongo_client = MongoClient(
                connection_string, 
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            
            # Test connection
            self.mongo_client.admin.command('ping')
            self.mongo_db = self.mongo_client[database]
            
            logger.info(f"✅ Connected to MongoDB: {host}:{port}/{database}")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected MongoDB connection error: {e}")
            return False

    def get_mongo_collection(self, collection_name: str):
        """Get MongoDB collection"""
        if not hasattr(self, 'mongo_db') or self.mongo_db is None:
            raise Exception("MongoDB not connected")
        return self.mongo_db[collection_name]

    def close_mongodb(self):
        """Close MongoDB connection"""
        if hasattr(self, 'mongo_client') and self.mongo_client:
            self.mongo_client.close()
            logger.info("MongoDB connection closed")

    def close(self):
        """Close all database connections"""
        if self.engine:
            self.engine.dispose()
            logger.info("MySQL database connection closed")
        
        # Close MongoDB connection too
        self.close_mongodb()
