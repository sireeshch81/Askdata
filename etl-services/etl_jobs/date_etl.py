import logging
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
import calendar

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def generate_date_range(start_date: date, end_date: date) -> List[date]:
    """
    Generate a list of dates between start_date and end_date (inclusive).
    """
    dates = []
    current_date = start_date

    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)

    return dates

def is_us_holiday(date_obj: date) -> bool:
    """
    Check if a date is a major US holiday.
    """
    year = date_obj.year
    month = date_obj.month
    day = date_obj.day

    # Fixed holidays
    fixed_holidays = [
        (1, 1),   # New Year's Day
        (7, 4),   # Independence Day
        (12, 25), # Christmas Day
    ]

    if (month, day) in fixed_holidays:
        return True

    # Memorial Day - Last Monday in May
    if month == 5:
        last_monday = 31
        while date(year, 5, last_monday).weekday() != 0:  # 0 = Monday
            last_monday -= 1
        if day == last_monday:
            return True

    # Labor Day - First Monday in September
    if month == 9 and date_obj.weekday() == 0 and day <= 7:
        return True

    # Thanksgiving - Fourth Thursday in November
    if month == 11 and date_obj.weekday() == 3:  # 3 = Thursday
        # Find the fourth Thursday
        thursdays = [d for d in range(1, 31) if date(year, 11, d).weekday() == 3]
        if len(thursdays) >= 4 and day == thursdays[3]:
            return True

    return False

def calculate_fiscal_attributes(date_obj: date, fiscal_year_start_month: int = 1) -> tuple:
    """
    Calculate fiscal year, quarter, and month based on fiscal year start month.
    Default fiscal year starts in January (calendar year).
    """
    year = date_obj.year
    month = date_obj.month

    if month >= fiscal_year_start_month:
        fiscal_year = year
        fiscal_month = month - fiscal_year_start_month + 1
    else:
        fiscal_year = year - 1
        fiscal_month = month + (12 - fiscal_year_start_month + 1)

    fiscal_quarter = ((fiscal_month - 1) // 3) + 1

    return fiscal_year, fiscal_quarter, fiscal_month

def extract_date_attributes(date_obj: date) -> Dict[str, Any]:
    """
    Extract all date attributes for a given date.
    """
    # Basic attributes
    date_key = int(date_obj.strftime("%Y%m%d"))  # YYYYMMDD format
    day_of_week = date_obj.weekday() + 1  # 1=Monday, 7=Sunday
    day_name = date_obj.strftime("%A")
    day_of_month = date_obj.day
    day_of_year = date_obj.timetuple().tm_yday
    week_of_year = date_obj.isocalendar()[1]
    month_number = date_obj.month
    month_name = date_obj.strftime("%B")
    quarter = ((date_obj.month - 1) // 3) + 1
    year = date_obj.year

    # Business attributes
    is_weekend = date_obj.weekday() >= 5  # Saturday=5, Sunday=6
    is_holiday = is_us_holiday(date_obj)

    # Fiscal attributes (assuming fiscal year starts in January)
    fiscal_year, fiscal_quarter, fiscal_month = calculate_fiscal_attributes(date_obj)

    return {
        "date_key": date_key,
        "date_value": date_obj,
        "day_of_week": day_of_week,
        "day_name": day_name,
        "day_of_month": day_of_month,
        "day_of_year": day_of_year,
        "week_of_year": week_of_year,
        "month_number": month_number,
        "month_name": month_name,
        "quarter": quarter,
        "year": year,
        "is_weekend": is_weekend,
        "is_holiday": is_holiday,
        "fiscal_year": fiscal_year,
        "fiscal_quarter": fiscal_quarter,
        "fiscal_month": fiscal_month
    }

def generate_date_dimension(start_year: int = 2020, end_year: int = 2030) -> List[Dict[str, Any]]:
    """
    Generate complete date dimension data for the specified year range.
    """
    logger.info(f"Generating date dimension from {start_year} to {end_year}")

    start_date = date(start_year, 1, 1)
    end_date = date(end_year, 12, 31)

    date_list = generate_date_range(start_date, end_date)

    date_dimension = []
    for date_obj in date_list:
        date_attributes = extract_date_attributes(date_obj)
        date_dimension.append(date_attributes)

    logger.info(f"Generated {len(date_dimension)} date records")
    return date_dimension

def load_date_dimension(dw_db: Session, date_records: List[Dict[str, Any]]) -> int:
    """
    Load date dimension into the DW database.
    """
    if not date_records:
        logger.info("No date records to load")
        return 0

    logger.info(f"Loading {len(date_records)} date records into DW")

    records_loaded = 0
    batch_size = 1000  # Load in batches for better performance

    for i in range(0, len(date_records), batch_size):
        batch = date_records[i:i+batch_size]

        for date_record in batch:
            # Check if date already exists
            query = text("""
                SELECT date_key
                FROM dim_date
                WHERE date_key = :date_key
            """)

            result = dw_db.execute(query, {"date_key": date_record["date_key"]})
            existing_date = result.fetchone()

            if existing_date:
                # Update existing date (in case business rules changed)
                update_query = text("""
                    UPDATE dim_date
                    SET
                        date_value = :date_value,
                        day_of_week = :day_of_week,
                        day_name = :day_name,
                        day_of_month = :day_of_month,
                        day_of_year = :day_of_year,
                        week_of_year = :week_of_year,
                        month_number = :month_number,
                        month_name = :month_name,
                        quarter = :quarter,
                        year = :year,
                        is_weekend = :is_weekend,
                        is_holiday = :is_holiday,
                        fiscal_year = :fiscal_year,
                        fiscal_quarter = :fiscal_quarter,
                        fiscal_month = :fiscal_month
                    WHERE date_key = :date_key
                """)

                dw_db.execute(update_query, date_record)
            else:
                # Insert new date
                insert_query = text("""
                    INSERT INTO dim_date (
                        date_key, date_value, day_of_week, day_name, day_of_month,
                        day_of_year, week_of_year, month_number, month_name, quarter,
                        year, is_weekend, is_holiday, fiscal_year, fiscal_quarter, fiscal_month
                    ) VALUES (
                        :date_key, :date_value, :day_of_week, :day_name, :day_of_month,
                        :day_of_year, :week_of_year, :month_number, :month_name, :quarter,
                        :year, :is_weekend, :is_holiday, :fiscal_year, :fiscal_quarter, :fiscal_month
                    )
                """)

                dw_db.execute(insert_query, date_record)

            records_loaded += 1

        # Commit batch
        dw_db.commit()
        logger.info(f"Loaded batch {i//batch_size + 1}/{(len(date_records) + batch_size - 1)//batch_size}")

    logger.info(f"Loaded {records_loaded} date records into DW")
    return records_loaded

# ------------------------------------
# ETL: Full job with Audit Logging
# ------------------------------------
def run_date_etl(dw_db: Session, start_year: int = 2020, end_year: int = 2030):
    job_name = "load_dim_date"
    print("DEBUG: Starting run_date_etl function")
    start_time = datetime.now()
    audit_id = None
    records_read = 0
    records_written = 0

    try:
        print(f"DEBUG: About to INSERT audit record for job: {job_name}")
        result = dw_db.execute(text("""
            INSERT INTO etl_job_audit_log (job_name, source_table, target_table, status, start_time)
            VALUES (:job_name, 'generated', 'dim_date', 'started', :start_time)
        """), {"job_name": job_name, "start_time": start_time})
        dw_db.commit()
        print(f"DEBUG: INSERT successful, affected rows: {result.rowcount}")

        audit_id = dw_db.execute(text("SELECT LAST_INSERT_ID()")).scalar()
        print(f"DEBUG: Retrieved audit_id = {audit_id}")

        date_records = generate_date_dimension(start_year, end_year)
        records_read = len(date_records)
        records_written = load_date_dimension(dw_db, date_records)

        end_time = datetime.now()
        print(f"DEBUG: About to UPDATE audit_id {audit_id} with {records_written} records")
        dw_db.execute(text("""
            UPDATE etl_job_audit_log
            SET status = 'success',
                records_read = :records_read,
                records_written = :records_written,
                end_time = :end_time,
                duration_seconds = TIMESTAMPDIFF(SECOND, :start_time, :end_time)
            WHERE audit_id = :audit_id
        """), {
            "records_read": records_read,
            "records_written": records_written,
            "end_time": end_time,
            "start_time": start_time,
            "audit_id": audit_id
        })
        dw_db.commit()
    except Exception as e:
        end_time = datetime.now()
        dw_db.execute(text("""
            UPDATE etl_job_audit_log
            SET status = 'failed',
                error_message = :error,
                end_time = :end_time,
                duration_seconds = TIMESTAMPDIFF(SECOND, :start_time, :end_time)
            WHERE audit_id = :audit_id
        """), {
            "error": str(e),
            "end_time": end_time,
            "start_time": start_time,
            "audit_id": audit_id
        })
        dw_db.commit()
        logger.exception("ETL job failed.")
        raise
