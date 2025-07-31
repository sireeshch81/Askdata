import logging
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, date
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def extract_members(oltp_db: Session, last_processed_id: int) -> List[Dict[str, Any]]:
    """
    Extract members from OLTP database that have an ID greater than the last processed ID.
    """
    logger.info(f"Extracting members with ID > {last_processed_id}")
    
    # SQL query to extract members
    query = text("""
        SELECT 
            member_id, first_name, last_name, email, phone, date_of_birth, 
            address, city, state, zip_code, annual_income, employment_status, 
            member_since, member_status, created_at, updated_at
        FROM members
        WHERE member_id > :last_id
        ORDER BY member_id
    """)
    
    # Execute query
    result = oltp_db.execute(query, {"last_id": last_processed_id})
    
    # Convert result to list of dictionaries
    members = []
    for row in result:
        member = {
            "member_id": row.member_id,
            "first_name": row.first_name,
            "last_name": row.last_name,
            "email": row.email,
            "phone": row.phone,
            "date_of_birth": row.date_of_birth,
            "address": row.address,
            "city": row.city,
            "state": row.state,
            "zip_code": row.zip_code,
            "annual_income": row.annual_income,
            "employment_status": row.employment_status,
            "member_since": row.member_since,
            "member_status": row.member_status,
            "created_at": row.created_at,
            "updated_at": row.updated_at
        }
        members.append(member)
    
    logger.info(f"Extracted {len(members)} members")
    return members

def calculate_age_group(birth_date: date) -> str:
    """
    Calculate age group based on birth date.
    """
    if not birth_date:
        return "Unknown"
    
    today = datetime.now().date()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    
    if age < 18:
        return "Under 18"
    elif age <= 25:
        return "18-25"
    elif age <= 35:
        return "26-35"
    elif age <= 45:
        return "36-45"
    elif age <= 55:
        return "46-55"
    elif age <= 65:
        return "56-65"
    else:
        return "65+"

def calculate_region(state: str) -> str:
    """
    Calculate region based on state.
    """
    if not state:
        return "Unknown"
    
    northeast = ["ME", "NH", "VT", "MA", "RI", "CT", "NY", "NJ", "PA"]
    midwest = ["OH", "MI", "IN", "IL", "WI", "MN", "IA", "MO", "ND", "SD", "NE", "KS"]
    south = ["DE", "MD", "DC", "VA", "WV", "NC", "SC", "GA", "FL", "KY", "TN", "AL", "MS", "AR", "LA", "OK", "TX"]
    west = ["MT", "ID", "WY", "CO", "NM", "AZ", "UT", "NV", "WA", "OR", "CA", "AK", "HI"]
    
    state_upper = state.upper()
    
    if state_upper in northeast:
        return "Northeast"
    elif state_upper in midwest:
        return "Midwest"
    elif state_upper in south:
        return "South"
    elif state_upper in west:
        return "West"
    else:
        return "Other"

def calculate_income_bracket(annual_income: float) -> str:
    """
    Calculate income bracket based on annual income.
    """
    if not annual_income:
        return "Unknown"
    
    if annual_income < 25000:
        return "Low"
    elif annual_income < 50000:
        return "Medium"
    elif annual_income < 100000:
        return "High"
    else:
        return "Premium"

def calculate_member_tenure_years(member_since: date) -> int:
    """
    Calculate member tenure in years.
    """
    if not member_since:
        return 0
    
    today = datetime.now().date()
    tenure = today.year - member_since.year - ((today.month, today.day) < (member_since.month, member_since.day))
    
    return max(0, tenure)

def transform_members(members: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transform members data to fit the DW schema.
    """
    logger.info(f"Transforming {len(members)} members")
    
    transformed_members = []
    for member in members:
        # Calculate derived fields
        age_group = calculate_age_group(member["date_of_birth"])
        region = calculate_region(member["state"])
        income_bracket = calculate_income_bracket(member["annual_income"])
        member_tenure_years = calculate_member_tenure_years(member["member_since"])
        
        # Create transformed member
        transformed_member = {
            "member_id": member["member_id"],
            "first_name": member["first_name"],
            "last_name": member["last_name"],
            "email": member["email"],
            "phone": member["phone"],
            "date_of_birth": member["date_of_birth"],
            "age_group": age_group,
            "address": member["address"],
            "city": member["city"],
            "state": member["state"],
            "zip_code": member["zip_code"],
            "region": region,
            "annual_income": member["annual_income"],
            "income_bracket": income_bracket,
            "employment_status": member["employment_status"],
            "member_since": member["member_since"],
            "member_tenure_years": member_tenure_years,
            "member_status": member["member_status"],
            "effective_date": datetime.now().date(),
            "expiry_date": None,
            "is_current": True
        }
        
        transformed_members.append(transformed_member)
    
    logger.info(f"Transformed {len(transformed_members)} members")
    return transformed_members

def load_members(dw_db: Session, transformed_members: List[Dict[str, Any]]) -> int:
    """
    Load transformed members into the DW database.
    """
    if not transformed_members:
        logger.info("No members to load")
        return 0
    
    logger.info(f"Loading {len(transformed_members)} members into DW")
    
    # For each member, check if it already exists in the DW
    records_loaded = 0
    for member in transformed_members:
        # Check if member already exists
        query = text("""
            SELECT member_key, member_id
            FROM dim_member
            WHERE member_id = :member_id AND is_current = TRUE
        """)
        
        result = dw_db.execute(query, {"member_id": member["member_id"]})
        existing_member = result.fetchone()
        
        if existing_member:
            # Update existing member (SCD Type 2)
            # First, expire the current record
            update_query = text("""
                UPDATE dim_member
                SET is_current = FALSE, expiry_date = :effective_date
                WHERE member_key = :member_key
            """)
            
            dw_db.execute(update_query, {
                "effective_date": member["effective_date"],
                "member_key": existing_member.member_key
            })
        
        # Insert new record
        insert_query = text("""
            INSERT INTO dim_member (
                member_id, first_name, last_name, email, phone, date_of_birth, age_group,
                address, city, state, zip_code, region, annual_income, income_bracket,
                employment_status, member_since, member_tenure_years, member_status,
                effective_date, expiry_date, is_current
            ) VALUES (
                :member_id, :first_name, :last_name, :email, :phone, :date_of_birth, :age_group,
                :address, :city, :state, :zip_code, :region, :annual_income, :income_bracket,
                :employment_status, :member_since, :member_tenure_years, :member_status,
                :effective_date, :expiry_date, :is_current
            )
        """)
        
        dw_db.execute(insert_query, member)
        records_loaded += 1
    
    # Commit the transaction
    dw_db.commit()
    
    logger.info(f"Loaded {records_loaded} members into DW")
    return records_loaded