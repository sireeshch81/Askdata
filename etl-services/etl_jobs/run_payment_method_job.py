#!/usr/bin/env python3
"""
Fixed payment method ETL job using working database connections
"""
from database import get_oltp_session, get_dw_session
from payment_method_etl import run_payment_method_etl

def main():
    print("Starting payment method ETL job...")
    oltp_session = get_oltp_session()
    dw_session = get_dw_session()
    
    try:
        run_payment_method_etl(oltp_session, dw_session)
        print("Payment method ETL job completed successfully!")
    except Exception as e:
        print(f"Payment method ETL job failed: {e}")
        raise
    finally:
        oltp_session.close()
        dw_session.close()

if __name__ == "__main__":
    main()
