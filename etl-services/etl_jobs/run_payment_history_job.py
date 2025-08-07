#!/usr/bin/env python3
from database import get_oltp_session, get_dw_session
from payment_history_etl import run_payment_history_etl

def main():
    print("Starting payment history ETL job...")
    oltp_session = get_oltp_session()
    dw_session = get_dw_session()
    
    try:
        run_payment_history_etl(oltp_session, dw_session, last_processed_id=0)
        print("Payment history ETL job completed successfully!")
    except Exception as e:
        print(f"Payment history ETL job failed: {e}")
        raise
    finally:
        oltp_session.close()
        dw_session.close()

if __name__ == "__main__":
    main()
