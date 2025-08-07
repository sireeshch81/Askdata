#!/usr/bin/env python3
"""
Master ETL script to run all individual ETL jobs in correct dependency order
"""
import subprocess
import sys
from datetime import datetime

def run_etl_job(job_script):
    """Run an individual ETL job and return success/failure"""
    print(f"🚀 Starting {job_script} at {datetime.now()}")
    try:
        result = subprocess.run([
            "/app/venv/bin/python", 
            f"/app/etl_jobs/{job_script}"
        ], capture_output=True, text=True, check=True)
        
        print(f"✅ {job_script} completed successfully")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {job_script} failed with exit code {e.returncode}")
        if e.stdout:
            print(f"   Output: {e.stdout}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        return False

def main():
    """Run all ETL jobs in correct dependency order"""
    print("=" * 60)
    print("🎯 AskData ETL Pipeline - Running All Jobs")
    print("=" * 60)
    
    # ETL jobs in correct dependency order
    etl_jobs = [
        # 1. Dimension tables with no dependencies
        "run_date_job.py",              # dim_date
        "run_payment_method_job.py",    # dim_payment_method  
        "run_financial_product_job.py", # dim_financial_product
        "run_member_job.py",            # dim_member
        
        # 2. Dimension tables with dependencies
        "run_credit_card_job.py",       # dim_credit_card (needs dim_member)
        
        # 3. Fact tables (load last)
        "run_payment_history_job.py",   # fact_payment (needs all dimensions)
        # Note: financial_health might have issues, run separately if needed
    ]
    
    successful_jobs = 0
    failed_jobs = []
    
    for job in etl_jobs:
        success = run_etl_job(job)
        if success:
            successful_jobs += 1
        else:
            failed_jobs.append(job)
    
    # Summary
    print("=" * 60)
    print(f"📊 ETL Pipeline Summary:")
    print(f"   ✅ Successful jobs: {successful_jobs}/{len(etl_jobs)}")
    if failed_jobs:
        print(f"   ❌ Failed jobs: {', '.join(failed_jobs)}")
    print("=" * 60)
    
    # Exit with appropriate code
    sys.exit(0 if len(failed_jobs) == 0 else 1)

if __name__ == "__main__":
    main()
