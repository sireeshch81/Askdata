#!/usr/bin/env python3
"""
Master ETL Script for AskData - Loads All Tables
Runs all individual ETL jobs in correct dependency order
"""
import subprocess
import sys
from datetime import datetime

def run_etl_job(job_name, job_script):
    """Run an individual ETL job and return success/failure"""
    print(f"\n🚀 Starting {job_name}...")
    print(f"   Running: {job_script}")
    
    try:
        result = subprocess.run([
            "/app/venv/bin/python", 
            f"/app/etl_jobs/{job_script}"
        ], capture_output=True, text=True, check=True)
        
        print(f"✅ {job_name} completed successfully")
        if result.stdout.strip():
            # Print last few lines of output
            output_lines = result.stdout.strip().split('\n')
            for line in output_lines[-3:]:  # Show last 3 lines
                if line.strip():
                    print(f"   {line}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ {job_name} FAILED")
        if e.stdout:
            print(f"   Output: {e.stdout}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        return False

def main():
    """Run complete ETL pipeline for AskData"""
    print("=" * 70)
    print("🎯 AskData Complete ETL Pipeline")
    print("   Loading all dimension and fact tables...")
    print("=" * 70)
    
    start_time = datetime.now()
    
    # ETL jobs in correct dependency order
    etl_jobs = [
        # 1. DIMENSION TABLES (No Dependencies)
        ("Date Dimension", "run_date_job.py"),
        ("Payment Method Dimension", "run_payment_method_job.py"),
        ("Financial Product Dimension", "run_financial_product_job.py"),
        ("Member Dimension", "run_member_job.py"),
        
        # 2. DEPENDENT DIMENSION TABLES
        ("Credit Card Dimension", "run_credit_card_job.py"),
        
        # 3. FACT TABLES (Load Last)
        ("Payment History Facts", "run_payment_history_job.py"),
        ("Financial Health Facts", "run_financial_health_job.py"),
    ]
    
    successful_jobs = []
    failed_jobs = []
    
    # Run each job in order
    for job_name, job_script in etl_jobs:
        success = run_etl_job(job_name, job_script)
        if success:
            successful_jobs.append(job_name)
        else:
            failed_jobs.append(job_name)
            print(f"\n⚠️  Continuing with remaining jobs despite {job_name} failure...")
    
    # Final summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "=" * 70)
    print("📊 ETL Pipeline Summary")
    print("=" * 70)
    print(f"⏱️  Total Duration: {duration:.1f} seconds")
    print(f"✅ Successful Jobs: {len(successful_jobs)}/{len(etl_jobs)}")
    
    if successful_jobs:
        print("\n🎉 Successfully Loaded:")
        for job in successful_jobs:
            print(f"   ✅ {job}")
    
    if failed_jobs:
        print(f"\n❌ Failed Jobs: {len(failed_jobs)}")
        for job in failed_jobs:
            print(f"   ❌ {job}")
        print("\n💡 Check individual job logs for detailed error information")
    
    print("\n🔍 Next Steps:")
    print("   1. Verify data in DW tables")
    print("   2. Check audit logs: SELECT * FROM etl_job_audit_log;")
    print("   3. Test AskData queries against populated tables")
    
    if failed_jobs:
        print(f"\n⚠️  Pipeline completed with {len(failed_jobs)} failures")
        sys.exit(1)
    else:
        print("\n🎉 All ETL jobs completed successfully!")
        print("   Your AskData warehouse is ready for queries!")
        sys.exit(0)

if __name__ == "__main__":
    main()
