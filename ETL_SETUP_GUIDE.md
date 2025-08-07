# AskData ETL Pipeline - Complete Setup Guide

## 🎯 Overview
This document provides complete setup instructions for the AskData ETL pipeline that transforms OLTP data into a data warehouse for natural language SQL queries.

## 📊 Data Pipeline Architecture
```
OLTP Database (Source) → ETL Services → Data Warehouse (Analytics)
    ↓                       ↓              ↓
• 2,000 Members         • Transform    • 4,018 Dates
• 3,253 Credit Cards    • Clean        • 5 Payment Methods  
• 17,985 Payments       • Enrich       • 50 Financial Products
• 2,000 Health Metrics  • Load         • 2,000 Members
                                       • 3,253 Credit Cards
                                       • 17,985 Payment Facts
                                       • 2,000 Health Facts
```

## 🚀 Quick Start (For Team Members)

### Prerequisites
- Docker and Docker Compose installed
- MySQL client access
- Git repository cloned

### Step 1: Start Services
```bash
# From project root directory
docker-compose up -d etl-services oltp-db dw-db
```

### Step 2: Create Data Warehouse Schema
```bash
# Create all DW tables with proper schema
docker exec -i dw-db mysql -u askdata_dw_user -paskdata_dw_password askdata_dw < dw-backend/dw-schema.sql
```

### Step 3: Run Complete ETL Pipeline
```bash
# Single command to load ALL tables (27,000+ records)
docker exec -it askdata-etl-services /app/venv/bin/python /app/run_complete_etl_pipeline.py
```

### Step 4: Verify Success
```bash
# Check all tables are populated
docker exec -it dw-db mysql -u askdata_dw_user -paskdata_dw_password -e "
USE askdata_dw;
SELECT 
  'dim_date' as table_name, COUNT(*) as count FROM dim_date
UNION ALL SELECT 
  'dim_payment_method' as table_name, COUNT(*) as count FROM dim_payment_method
UNION ALL SELECT 
  'dim_financial_product' as table_name, COUNT(*) as count FROM dim_financial_product
UNION ALL SELECT 
  'dim_member' as table_name, COUNT(*) as count FROM dim_member
UNION ALL SELECT 
  'dim_credit_card' as table_name, COUNT(*) as count FROM dim_credit_card
UNION ALL SELECT 
  'fact_payment' as table_name, COUNT(*) as count FROM fact_payment
UNION ALL SELECT 
  'fact_financial_health' as table_name, COUNT(*) as count FROM fact_financial_health;
"
```

**Expected Results:**
- dim_date: 4,018 records
- dim_payment_method: 5 records  
- dim_financial_product: 50 records
- dim_member: 2,000 records
- dim_credit_card: 3,253 records
- fact_payment: 17,985 records
- fact_financial_health: 2,000 records

## 🛠 Detailed Setup Instructions

### Database Configuration
The ETL pipeline connects to:
- **OLTP Database**: `oltp-db:3306/askdata_oltp` (source data)
- **DW Database**: `dw-db:3307/askdata_dw` (analytics target)
- **MongoDB**: `mongodb:27017/askdata` (vector storage)

### ETL Jobs Available

#### Individual Jobs (for debugging/testing)
```bash
# Run specific table loads
docker exec -it askdata-etl-services /app/venv/bin/python /app/etl_jobs/run_date_job.py
docker exec -it askdata-etl-services /app/venv/bin/python /app/etl_jobs/run_payment_method_job.py
docker exec -it askdata-etl-services /app/venv/bin/python /app/etl_jobs/run_financial_product_job.py
docker exec -it askdata-etl-services /app/venv/bin/python /app/etl_jobs/run_member_job.py
docker exec -it askdata-etl-services /app/venv/bin/python /app/etl_jobs/run_credit_card_job.py
docker exec -it askdata-etl-services /app/venv/bin/python /app/etl_jobs/run_payment_history_job.py
docker exec -it askdata-etl-services /app/venv/bin/python /app/etl_jobs/run_financial_health_job.py
```

#### Master Pipeline (recommended)
```bash
# Runs all jobs in correct dependency order
docker exec -it askdata-etl-services /app/venv/bin/python /app/run_complete_etl_pipeline.py
```

### Data Warehouse Schema

#### Dimension Tables
- **dim_date**: Date dimension (2020-2030)
- **dim_member**: Customer demographics and financial profiles
- **dim_credit_card**: Credit card products and limits
- **dim_financial_product**: Available financial products
- **dim_payment_method**: Payment channels and methods

#### Fact Tables  
- **fact_payment**: Payment transactions with business metrics
- **fact_financial_health**: Member financial health assessments

#### Audit Tables
- **etl_job_audit_log**: Complete ETL execution tracking

### ETL Features
- ✅ **Dependency Management**: Loads tables in correct order
- ✅ **Error Handling**: Continues processing on individual failures
- ✅ **Audit Logging**: Tracks all ETL operations with timestamps
- ✅ **Data Quality**: Handles precision issues and missing values
- ✅ **Performance**: Processes 27,000+ records in ~60 seconds

## 🔍 Troubleshooting

### Common Issues

#### 1. Container Not Running
```bash
# Check container status
docker ps -a

# Restart if needed
docker-compose restart etl-services
```

#### 2. Database Connection Issues
```bash
# Check database connectivity
docker exec -it dw-db mysql -u askdata_dw_user -paskdata_dw_password -e "SHOW DATABASES;"
```

#### 3. Empty Tables After ETL
```bash
# Check ETL logs
docker logs askdata-etl-services --tail 50

# Verify source data exists
docker exec -it oltp-db mysql -u askdata_user -paskdata_password -e "USE askdata_oltp; SELECT COUNT(*) FROM members;"
```

#### 4. SSL Certificate Errors
```bash
# Install packages with SSL bypass
docker exec -it askdata-etl-services /app/venv/bin/pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org [package-name]
```

### ETL Monitoring
```bash
# Check audit logs
docker exec -it dw-db mysql -u askdata_dw_user -paskdata_dw_password -e "
USE askdata_dw;
SELECT job_name, target_table, status, records_written, start_time, end_time
FROM etl_job_audit_log 
ORDER BY start_time DESC LIMIT 10;
"
```

## 📁 Project Structure
```
askdata-demo/
├── etl-services/
│   ├── etl_jobs/
│   │   ├── run_complete_etl_pipeline.py  # Master ETL script
│   │   ├── run_*_job.py                  # Individual job scripts
│   │   ├── *_etl.py                      # ETL logic modules
│   │   └── etl_manager.py                # ETL orchestration
│   ├── database.py                       # Database connections
│   └── models/                           # Data models
├── dw-backend/
│   └── dw-schema.sql                     # Complete DW schema
├── oltp-backend/                         # OLTP services
└── docker-compose.yml                   # Service orchestration
```

## 🔄 Development Workflow

### Making Changes
1. **Modify ETL logic** in `etl-services/etl_jobs/`
2. **Test individual jobs** before running complete pipeline
3. **Update schema** in `dw-backend/dw-schema.sql` if needed
4. **Run full pipeline** to verify end-to-end functionality

### Adding New Tables
1. **Create ETL module**: `new_table_etl.py`
2. **Create job script**: `run_new_table_job.py`
3. **Add to master pipeline**: Update `run_complete_etl_pipeline.py`
4. **Update schema**: Add table definition to `dw-schema.sql`

## 🎯 Next Steps
1. **Data Validation**: Verify data quality and completeness
2. **Performance Tuning**: Optimize ETL for larger datasets
3. **Monitoring**: Set up automated ETL scheduling
4. **AskData Integration**: Connect natural language query system

## 📞 Support
- **ETL Issues**: Check individual job logs and audit tables
- **Schema Issues**: Verify table definitions in `dw-schema.sql`
- **Performance Issues**: Monitor ETL execution times and optimize queries

---

**🎉 Your AskData warehouse is ready for natural language SQL queries!**
