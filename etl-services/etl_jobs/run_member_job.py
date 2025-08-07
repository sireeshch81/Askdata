#!/usr/bin/env python3
"""
Fixed member ETL job using working database connections
"""
from database import get_oltp_session, get_dw_session
from member_etl import run_member_etl

def main():
    print("Starting member ETL job...")
    oltp_session = get_oltp_session()
    dw_session = get_dw_session()
    
    try:
        run_member_etl(oltp_session, dw_session, last_processed_id=0)
        print("Member ETL job completed successfully!")
    except Exception as e:
        print(f"Member ETL job failed: {e}")
        raise
    finally:
        oltp_session.close()
        dw_session.close()

if __name__ == "__main__":
    main()
