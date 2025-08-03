import os
import logging
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from dotenv import load_dotenv
#!/usr/bin/env python3

import os
from pymongo import MongoClient
from pymongo.collection import Collection
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection settings
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGODB_DB = os.getenv("MONGODB_DB", "askdata")

# MongoDB client instance
_client: Optional[MongoClient] = None


def get_mongodb_client() -> MongoClient:
    """Get MongoDB client instance"""
    global _client
    if _client is None:
        _client = MongoClient(MONGODB_URI)
    return _client


def get_mongodb_database(database_name: Optional[str] = None) -> MongoClient:
    """Get MongoDB database"""
    client = get_mongodb_client()
    return client[database_name or MONGODB_DB]


def get_mongodb_collection(collection_name: str, database_name: Optional[str] = None) -> Collection:
    """Get MongoDB collection"""
    db = get_mongodb_database(database_name)
    return db[collection_name]


def close_mongodb_connection() -> None:
    """Close MongoDB connection"""
    global _client
    if _client is not None:
        _client.close()
        _client = None
# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base class for SQLAlchemy models
Base = declarative_base()


# ============================================================================
# MONGODB CONNECTION
# ============================================================================

class MongoDBConnection:
    """MongoDB connection manager"""

    def __init__(self):
        self.username = os.getenv("MONGO_INITDB_ROOT_USERNAME", "root")
        self.password = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "example")
        self.host = os.getenv("MONGO_HOST", "mongodb")
        self.port = os.getenv("MONGO_PORT", "27017")
        self.database = os.getenv("MONGO_DATABASE", "askdata_recommendation_db")

        self._client = None
        self._database = None

    def get_client(self) -> MongoClient:
        """Get MongoDB client"""
        if self._client is None:
            connection_string = f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/"
            self._client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            logger.info(f"Created MongoDB client for {self.host}:{self.port}")
        return self._client

    def get_database(self) -> Database:
        """Get MongoDB database"""
        if self._database is None:
            client = self.get_client()
            self._database = client[self.database]
            logger.info(f"Connected to MongoDB database: {self.database}")
        return self._database

    def get_collection(self, collection_name: str):
        """Get MongoDB collection"""
        database = self.get_database()
        return database[collection_name]

    def test_connection(self) -> dict:
        """Test MongoDB connection"""
        try:
            client = self.get_client()
            # Ping the server
            client.admin.command('ping')
            database = self.get_database()
            # List collections to verify database access
            collections = database.list_collection_names()
            logger.info(f"MongoDB connection successful. Collections: {collections}")
            return {
                "status": "SUCCESS",
                "collections": collections,
                "database": self.database
            }
        except Exception as e:
            logger.error(f"MongoDB connection failed: {str(e)}")
            return {
                "status": "FAILED",
                "error": str(e)
            }

    def close_connection(self):
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None
            logger.info("MongoDB connection closed")


# ============================================================================
# GLOBAL INSTANCES
# ============================================================================

# Create global instances
mongodb_connection = MongoDBConnection()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_mongodb():
    """Get MongoDB database instance"""
    return mongodb_connection.get_database()


def get_mongodb_collection(collection_name: str):
    """Get MongoDB collection"""
    return mongodb_connection.get_collection(collection_name)


def test_all_connections():
    """Test database connection"""
    logger.info("Testing database connection...")

    # Test MongoDB connection
    mongo_result = mongodb_connection.test_connection()

    return {
        "mongodb": mongo_result
    }


def close_all_connections():
    """Close database connections"""
    mongodb_connection.close_connection()
    logger.info("Mongo database connection closed")