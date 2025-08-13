from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from schemas import Customer

load_dotenv()

# Database configuration
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "oltpdb")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


def get_customer_details(customer_id: int):
    session = Session()
    try:
        
        customer = session.query(Customer).filter(Customer.customer_id == customer_id).first()
        if customer:
            return {
                "customer_id": customer.customer_id,
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "email": customer.email,
                "phone": customer.phone,
                "address": customer.address,
                "credit_score": customer.credit_score,
                "income": customer.income
            }
        return None
    finally:
        session.close()
