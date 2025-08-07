#!/usr/bin/env python3
from database import get_oltp_session, get_dw_session
from financial_product_etl import run_financial_product_etl

def main():
    print("Starting financial product ETL job...")
    oltp_session = get_oltp_session()
    dw_session = get_dw_session()
    
    try:
        run_financial_product_etl(oltp_session, dw_session, last_processed_id=0)
        print("Financial product ETL job completed successfully!")
    except Exception as e:
        print(f"Financial product ETL job failed: {e}")
        raise
    finally:
        oltp_session.close()
        dw_session.close()

if __name__ == "__main__":
    main()
