import os
import sys
import logging
import time
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from typing import Optional, List, Dict, Any

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

    # ========== NEW DW QUERY METHODS - SCHEMA FIXED ==========

    def get_dw_customer_profile(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get customer profile from DW dim_member table - FIXED FOR YOUR SCHEMA"""
        query = """
        SELECT 
            member_id as customer_id,
            first_name,
            last_name,
            CONCAT(first_name, ' ', last_name) as name,
            annual_income,
            member_since as date_joined,
            member_status,
            member_tenure_years,
            city,
            state,
            region
        FROM dim_member 
        WHERE member_id = %s
        AND is_current = 1
        """

        try:
            df = self.execute_query(query, (customer_id,))
            if not df.empty:
                return df.iloc[0].to_dict()
            return None
        except Exception as e:
            logger.error(f"Error fetching customer profile for {customer_id}: {e}")
            return None


    def get_dw_customer_payment_history(self, customer_id: str, months_back: int = 12) -> pd.DataFrame:
        """Get customer payment history from DW fact_payment table - FIXED COLUMN NAMES"""
        query = """
        SELECT
            fp.payment_key as payment_id,
            dm.member_id as customer_id,
            fp.payment_amount,
            dd.date_value as payment_date,
            dpm.payment_method as payment_method,
            fp.payment_status as transaction_type,
            fh.credit_score,
            dm.annual_income,
            fp.is_on_time,
            fp.is_full_payment,
            fp.payment_ratio
        FROM dim_member dm
        JOIN fact_payment fp ON dm.member_key = fp.member_key
        JOIN dim_date dd ON fp.payment_date_key = dd.date_key
        JOIN dim_payment_method dpm ON fp.payment_method_key = dpm.payment_method_key
        LEFT JOIN fact_financial_health fh ON dm.member_key = fh.member_key
        WHERE dm.member_id = %s
        AND dm.is_current = 1
        AND dd.date_value >= DATE_SUB(CURDATE(), INTERVAL %s MONTH)
        ORDER BY dd.date_value DESC
        """

        try:
            return self.execute_query(query, (customer_id, months_back))
        except Exception as e:
            logger.error(f"Error fetching payment history for {customer_id}: {e}")
            return pd.DataFrame()




    def get_dw_customer_financial_health(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get latest financial health metrics from DW fact_financial_health - FIXED FOR YOUR SCHEMA"""
        query = """
        SELECT 
            dm.member_id as customer_id,
            fh.credit_score,
            fh.health_score,
            fh.debt_to_income_ratio,
            fh.credit_utilization_ratio as utilization_ratio,
            fh.payment_reliability_score as payment_behavior_score,
            fh.credit_utilization_ratio as credit_utilization,
            fh.savings_balance / NULLIF(dm.annual_income, 0) as savings_rate,
            fh.created_datetime as calculated_date
        FROM dim_member dm
        JOIN fact_financial_health fh ON dm.member_key = fh.member_key
        WHERE dm.member_id = %s
        AND dm.is_current = 1
        ORDER BY fh.created_datetime DESC
        LIMIT 1
        """

        try:
            df = self.execute_query(query, (customer_id,))
            if not df.empty:
                return df.iloc[0].to_dict()
            return None
        except Exception as e:
            logger.error(f"Error fetching financial health for {customer_id}: {e}")
            return None

    def get_dw_customer_credit_cards(self, customer_id: str) -> pd.DataFrame:
        """Get customer's credit cards from DW dim_credit_card - FIXED FOR YOUR SCHEMA"""
        query = """
        SELECT 
            dcc.card_id,
            dm.member_id as customer_id,
            dcc.card_type,
            dcc.credit_limit,
            COALESCE(fcb.current_balance, 0) as current_balance,
            dcc.apr_rate as interest_rate,
            dcc.card_status,
            dcc.issue_date,
            dcc.card_age_months
        FROM dim_member dm
        JOIN dim_credit_card dcc ON dm.member_key = dcc.member_key
        LEFT JOIN fact_credit_card_balance fcb ON dcc.card_key = fcb.card_key
        WHERE dm.member_id = %s
        AND dm.is_current = 1
        AND dcc.is_current = 1
        AND dcc.card_status = 'active'
        """

        try:
            return self.execute_query(query, (customer_id,))
        except Exception as e:
            logger.error(f"Error fetching credit cards for {customer_id}: {e}")
            return pd.DataFrame()

    def get_dw_similar_customers(self,
                                credit_score_range: tuple = (50, 50),
                                income_range: tuple = (10000, 10000),
                                customer_id: str = None,
                                limit: int = 100) -> pd.DataFrame:
        """Get similar customers from DW for clustering analysis - FIXED FOR YOUR SCHEMA"""
        query = """
        SELECT 
            dm.member_id as customer_id,
            fh.credit_score,
            dm.annual_income,
            fh.risk_category,
            fh.health_score,
            fh.credit_utilization_ratio as utilization_ratio,
            fh.debt_to_income_ratio,
            fh.payment_reliability_score as payment_behavior_score,
            COUNT(dcc.card_id) as total_cards,
            AVG(dcc.credit_limit) as avg_credit_limit,
            SUM(COALESCE(fcb.current_balance, 0)) as total_balance
        FROM dim_member dm
        LEFT JOIN fact_financial_health fh ON dm.member_key = fh.member_key
        LEFT JOIN dim_credit_card dcc ON dm.member_key = dcc.member_key AND dcc.is_current = 1
        LEFT JOIN fact_credit_card_balance fcb ON dcc.card_key = fcb.card_key
        WHERE fh.credit_score BETWEEN %s AND %s
        AND dm.annual_income BETWEEN %s AND %s
        AND dm.member_status = 'active'
        AND dm.is_current = 1
        """

        if customer_id:
            query += " AND dm.member_id != %s"
            params = (
                credit_score_range[0], credit_score_range[1],
                income_range[0], income_range[1],
                customer_id
            )
        else:
            params = (
                credit_score_range[0], credit_score_range[1],
                income_range[0], income_range[1]
            )

        query += """
        GROUP BY dm.member_id, fh.credit_score, dm.annual_income,
                 fh.risk_category, fh.health_score, fh.credit_utilization_ratio,
                 fh.debt_to_income_ratio, fh.payment_reliability_score
        ORDER BY fh.health_score DESC
        LIMIT %s
        """

        try:
            return self.execute_query(query, params + (limit,))
        except Exception as e:
            logger.error(f"Error fetching similar customers: {e}")
            return pd.DataFrame()

    def get_dw_all_products(self) -> pd.DataFrame:
        """Get all available financial products from DW dim_financial_product - FIXED COLUMN NAMES"""
        query = """
        SELECT
            product_id,
            product_name,
            product_type,
            product_category,
            minimum_credit_score as min_credit_score,
            minimum_income_required as min_income,
            maximum_debt_to_income as max_debt_to_income,
            interest_rate as interest_rate_min,
            interest_rate as interest_rate_max,
            annual_fee,
            rewards_program as product_features,
            eligibility_tier as eligibility_criteria,
            is_active as product_status
        FROM dim_financial_product 
        WHERE is_active = 1
        ORDER BY product_type, product_name
        """

        try:
            return self.execute_query(query)
        except Exception as e:
            logger.error(f"Error fetching financial products: {e}")
            return pd.DataFrame()



    def get_dw_customer_product_history(self, customer_id: str) -> pd.DataFrame:
        """Get customer's product application/approval history - FIXED FOR YOUR SCHEMA"""
        query = """
        SELECT DISTINCT
            dm.member_id as customer_id,
            dfp.product_id,
            dfp.product_name,
            dfp.product_type,
            'existing' as relationship_status
        FROM dim_member dm
        JOIN fact_payment fp ON dm.member_key = fp.member_key
        JOIN dim_financial_product dfp ON fp.product_key = dfp.product_key
        WHERE dm.member_id = %s
        AND dm.is_current = 1
        AND dfp.is_current = 1
        
        UNION
        
        SELECT 
            dm.member_id as customer_id,
            CONCAT('card_', dcc.card_id) as product_id,
            CONCAT(dcc.card_type, ' Card') as product_name,
            'credit_card' as product_type,
            dcc.card_status as relationship_status
        FROM dim_member dm
        JOIN dim_credit_card dcc ON dm.member_key = dcc.member_key
        WHERE dm.member_id = %s
        AND dm.is_current = 1
        AND dcc.is_current = 1
        """

        try:
            return self.execute_query(query, (customer_id, customer_id))
        except Exception as e:
            logger.error(f"Error fetching product history for {customer_id}: {e}")
            return pd.DataFrame()

    def get_dw_batch_customers(self, batch_size: int = 1000, offset: int = 0) -> pd.DataFrame:
        """Get batch of customers for ML processing - FIXED FOR YOUR SCHEMA"""
        query = """
        SELECT 
            dm.member_id as customer_id,
            fh.credit_score,
            dm.annual_income,
            fh.risk_category,
            dm.member_status,
            fh.health_score,
            fh.credit_utilization_ratio as utilization_ratio,
            fh.debt_to_income_ratio,
            fh.payment_reliability_score as payment_behavior_score
        FROM dim_member dm
        LEFT JOIN fact_financial_health fh ON dm.member_key = fh.member_key
        WHERE dm.member_status = 'active'
        AND dm.is_current = 1
        ORDER BY dm.member_id
        LIMIT %s OFFSET %s
        """

        try:
            return self.execute_query(query, (batch_size, offset))
        except Exception as e:
            logger.error(f"Error fetching customer batch: {e}")
            return pd.DataFrame()

    def get_dw_customer_count(self) -> int:
        """Get total count of active customers for batch processing - FIXED FOR YOUR SCHEMA"""
        query = """
        SELECT COUNT(*) as customer_count
        FROM dim_member 
        WHERE member_status = 'active'
        AND is_current = 1
        """

        try:
            df = self.execute_query(query)
            return int(df.iloc[0]['customer_count']) if not df.empty else 0
        except Exception as e:
            logger.error(f"Error getting customer count: {e}")
            return 0

    # ========== EXISTING MONGODB METHODS (PRESERVED) ==========


    def connect_mongodb(self,
                       host: str = None,
                       port: int = None,
                       database: str = None,
                       username: str = None,
                       password: str = None) -> bool:
        """Connect to MongoDB with SSL disabled for local development"""
        try:
            # Read from environment variables if not provided
            host = host or os.environ.get("MONGO_HOST", "localhost")
            port = port or int(os.environ.get("MONGO_PORT", 27017))
            database = database or os.environ.get("MONGO_DATABASE", "askdata_mongo")
            username = username or os.environ.get("MONGO_INITDB_ROOT_USERNAME")
            password = password or os.environ.get("MONGO_INITDB_ROOT_PASSWORD")
        
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
