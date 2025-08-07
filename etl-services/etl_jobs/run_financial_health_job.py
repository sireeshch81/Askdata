#!/usr/bin/env python3
from database import get_oltp_session, get_dw_session
from financial_health_etl import extract_financial_health, transform_financial_health, load_financial_health
from decimal import Decimal

def main():
    print("Starting financial health ETL job...")
    oltp_session = get_oltp_session()
    dw_session = get_dw_session()
    
    try:
        # Extract
        extracted_data = extract_financial_health(oltp_session, last_processed_id=0)
        print(f"Extracted {len(extracted_data)} financial health records")
        
        # Transform
        transformed_data = transform_financial_health(extracted_data)
        print(f"Transformed {len(transformed_data)} financial health records")
        
        # Fix: Add missing fields and adjust precision for MySQL columns
        for i, metric in enumerate(transformed_data):
            if i < len(extracted_data):
                metric["member_id"] = extracted_data[i]["member_id"]
                metric["assessment_date"] = extracted_data[i]["assessment_date"]
            
            # Fix decimal precision issues for MySQL columns
            if "debt_to_assets_ratio" in metric and metric["debt_to_assets_ratio"] is not None:
                # Limit to 4 decimal places and ensure it fits DECIMAL(5,4)
                ratio = float(metric["debt_to_assets_ratio"])
                if ratio > 9.9999:
                    metric["debt_to_assets_ratio"] = Decimal('9.9999')  # Cap at max value
                else:
                    metric["debt_to_assets_ratio"] = Decimal(str(round(ratio, 4)))
        
        print("Fixed data precision issues for MySQL")
        
        # Load
        loaded_count = load_financial_health(dw_session, transformed_data)
        print(f"Loaded {loaded_count} financial health records")
        
        print("Financial health ETL job completed successfully!")
    except Exception as e:
        print(f"Financial health ETL job failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        oltp_session.close()
        dw_session.close()

if __name__ == "__main__":
    main()
