import os

# Database Configuration - UPDATED WITH CORRECT CREDENTIALS
OLTP_CONFIG = {
    'host': os.getenv('OLTP_HOST', 'localhost'),
    'port': int(os.getenv('OLTP_PORT', '3306')),
    'database': os.getenv('OLTP_DATABASE', 'askdata_oltp'),
    'user': os.getenv('OLTP_USER', 'askdata_user'),          # Fixed username
    'password': os.getenv('OLTP_PASSWORD', 'askdata_password') # Fixed password
}

DW_CONFIG = {
    'host': os.getenv('DW_HOST', 'localhost'),
    'port': int(os.getenv('DW_PORT', '3306')),
    'database': os.getenv('DW_DATABASE', 'askdata_dw'),
    'user': os.getenv('DW_USER', 'askdata_dw_user'),        # Fixed username
    'password': os.getenv('DW_PASSWORD', 'askdata_dw_password') # Fixed password
}

# SQLAlchemy URLs
OLTP_DATABASE_URL = f"postgresql+psycopg2://{OLTP_CONFIG['user']}:{OLTP_CONFIG['password']}@{OLTP_CONFIG['host']}:{OLTP_CONFIG['port']}/{OLTP_CONFIG['database']}"
DW_DATABASE_URL = f"postgresql+psycopg2://{DW_CONFIG['user']}:{DW_CONFIG['password']}@{DW_CONFIG['host']}:{DW_CONFIG['port']}/{DW_CONFIG['database']}"

# Processing Configuration
DEFAULT_BATCH_SIZE = 100
MAX_RECOMMENDATIONS_PER_MEMBER = 5
OUTPUT_DIRECTORY = "output"

# Feature weights for recommendation scoring
FEATURE_WEIGHTS = {
    'credit_score': 0.25,
    'income_ratio': 0.20,
    'utilization_ratio': 0.15,
    'payment_history': 0.20,
    'risk_category': 0.10,
    'health_score': 0.10
}

# Risk category mappings
RISK_CATEGORIES = {
    'low': 1.0,
    'medium': 0.8,
    'high': 0.5
}
