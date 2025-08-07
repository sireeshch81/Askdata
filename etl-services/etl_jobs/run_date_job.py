#!/usr/bin/env python3
"""
Fixed date ETL job using working database connections
"""
from database import get_dw_session
from date_etl import run_date_etl

def main():
    print("Starting date ETL job...")
    dw_session = get_dw_session()
    
    try:
        run_date_etl(dw_session, start_year=2020, end_year=2030)
        print("Date ETL job completed successfully!")
    except Exception as e:
        print(f"Date ETL job failed: {e}")
        raise
    finally:
        dw_session.close()

if __name__ == "__main__":
    main()
