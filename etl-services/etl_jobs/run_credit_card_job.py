#!/usr/bin/env python3
from database import get_oltp_session, get_dw_session
from credit_card_etl import run_credit_card_etl

def main():
    print("Starting credit card ETL job...")
    oltp_session = get_oltp_session()
    dw_session = get_dw_session()
    
    try:
        run_credit_card_etl(oltp_session, dw_session, last_processed_id=0)
        print("Credit card ETL job completed successfully!")
    except Exception as e:
        print(f"Credit card ETL job failed: {e}")
        raise
    finally:
        oltp_session.close()
        dw_session.close()

if __name__ == "__main__":
    main()
