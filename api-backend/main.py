from fastapi import FastAPI, HTTPException, Depends, Query, Body, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_, text
from datetime import datetime
from typing import Optional
import logging
import json
import os
from jwtPermissionCheck import *

from database import get_db
import models
import schemas
from RecommendationDataManager import RecommendationDataManager

from google import genai
from google.genai import types
from pydantic import BaseModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# FastAPI App Initialization
app = FastAPI(
    title="API Backend",
    description="API Backend for UI Layer - connects to OLTP DB and MongoDB",
    version="1.0.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY environment variable not set!")
client = genai.Client(api_key=GEMINI_API_KEY)

# Load schema prompt for OLTP from file once at startup
schema_prompt_path = "prompts/sql_prompt.txt"
try:
    with open(schema_prompt_path, "r") as f:
        SCHEMA_PROMPT_OLTP = f.read()
    logger.info(f"Loaded schema prompt from {schema_prompt_path}")
except Exception as e:
    SCHEMA_PROMPT_OLTP = ""
    logger.error(f"Failed to load schema prompt from {schema_prompt_path}: {e}")

def clean_generated_sql(sql_text: str) -> str:
    sql_text = sql_text.strip()
    if sql_text.startswith("```sql"):
        sql_text = sql_text.replace("```sql", "").replace("```", "").strip()
    elif sql_text.startswith("```"):
        sql_text = sql_text.replace("```", "").strip()
    elif sql_text.lower().startswith("sql"):
        sql_text = sql_text[len("sql"):].strip()
    if sql_text.endswith(";"):
        sql_text = sql_text[:-1].strip()
    return sql_text

def rewrite_sql_with_explicit_columns(sql: str) -> str:
    lower_sql = sql.lower()
    if "select *" in lower_sql:
        new_select = """
        SELECT
            member_id AS customer_id,
            first_name,
            last_name,
            email,
            phone,
            date_of_birth
        """
        select_star_index = lower_sql.find("select *")
        from_index = lower_sql.find("from", select_star_index)
        if from_index == -1:
            return sql
        rewritten_sql = new_select + sql[from_index:]
        return rewritten_sql
    return sql

# --- Health Check ---
@app.get("/health")
def health_check(authorization: Optional[str] = Header(None)):
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# --- Customer Detail Search ---
@app.get("/customer_detail", response_model=List[schemas.CustomerDetail])
def get_customer_detail(
    customer_name: str = Query(None),
    email: str = Query(None),
    phone: str = Query(None),
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    if not any([customer_name, email, phone]):
        raise HTTPException(status_code=400, detail="At least one search parameter must be provided.")

    query = db.query(models.Member)
    filters = []

    if customer_name:
        pattern = f"%{customer_name}%"
        filters.append(
            or_(
                models.Member.first_name.ilike(pattern),
                models.Member.last_name.ilike(pattern),
                (models.Member.first_name + " " + models.Member.last_name).ilike(pattern),
            )
        )
    if email:
        filters.append(models.Member.email.ilike(f"%{email}%"))
    if phone:
        filters.append(models.Member.phone.ilike(f"%{phone}%"))

    query = query.filter(or_(*filters))
    customers = query.limit(100).all()
    if not customers:
        raise HTTPException(status_code=404, detail="Customers not found")

    return [
        schemas.CustomerDetail(
            customer_id=str(customer.member_id),
            first_name=customer.first_name,
            last_name=customer.last_name,
            email=customer.email,
            phone=customer.phone,
            date_of_birth=customer.date_of_birth,
        )
        for customer in customers
    ]

# --- Recommendations ---
@app.get("/recommendations", response_model=schemas.RecommendationsResponse)
def get_recommendations(customer_id: str = Query(...), authorization: Optional[str] = Header(None)):
    recommendation_manager = RecommendationDataManager()
    collection = recommendation_manager.find_by_customer_id(customer_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Recommendations not found")
    return schemas.RecommendationsResponse(
        customer_id=collection["customer_id"],
        customer_profile=schemas.CustomerProfile(**collection["customer_profile"]),
        recommendations=[schemas.Recommendation(**rec) for rec in collection["recommendations"]],
        created_at=collection["created_at"],
        updated_at=collection["updated_at"]
    )

# --- Products ---
@app.get("/products", response_model=List[schemas.ProductsResponse])
def getProductsByProductName(product_name: str = Query(...), db: Session = Depends(get_db), authorization: Optional[str] = Header(None)):
    query = db.query(models.FinancialProduct)
    pattern = f"%{product_name}%"
    query = query.filter(models.FinancialProduct.product_name.ilike(pattern))
    financialProducts = query.limit(100).all()
    if not financialProducts:
        raise HTTPException(status_code=404, detail="Products not found")
    return [
        schemas.ProductsResponse(
            product_id=p.product_id,
            product_name=p.product_name,
            product_type=p.product_type,
            product_category=p.product_category,
            interest_rate=p.interest_rate,
            credit_limit_min=p.credit_limit_min,
            credit_limit_max=p.credit_limit_max,
            minimum_income_required=p.minimum_income_required,
            minimum_credit_score=p.minimum_credit_score,
            maximum_debt_to_income=p.maximum_debt_to_income,
            annual_fee=p.annual_fee,
            rewards_program=p.rewards_program,
            benefits=p.benefits,
            eligibility_criteria=p.eligibility_criteria,
            is_active=p.is_active,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
        for p in financialProducts
    ]

# --- Recommendation Letter ---
@app.get("/recommendation_letter", response_model=str)
def get_recommendation_letter(customer_id: str = Query(...), db: Session = Depends(get_db), authorization: Optional[str] = Header(None)):
    recommendation_manager = RecommendationDataManager()
    collection = recommendation_manager.find_by_customer_id(customer_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Recommendations not found")
    try:
        member_id_int = int(customer_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid customer ID format.")
    member = db.query(models.Member).filter(models.Member.member_id == member_id_int).first()
    if not member:
        raise HTTPException(status_code=404, detail="Customer not found")
    collection["customer_profile"]["name"] = f"{member.first_name} {member.last_name}"
    json_string = json.dumps(collection, default=str)
    with open("prompts/recommendation-letter-prompt.txt", "r") as f:
        prompt_text = f.read()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt_text + "\n\n JSON data:\n" + json_string,
        config=types.GenerateContentConfig(thinking_config=types.ThinkingConfig(thinking_budget=0)),
    )
    return response.text

# --- Simple Auth ---
@app.post("/auth", response_model=schemas.AuthResponse)
def authenticate(username: str = Query(...), password: str = Query(...), authorization: Optional[str] = Header(None)):
    if username and password:
        return schemas.AuthResponse(access_token="stubbed.jwt.token", token_type="bearer")
    else:
        raise HTTPException(status_code=401, detail="Authentication failed")

# --- NLP Customer SQL ---
@app.post("/generate_sql")
def generate_sql(nl_query: str = Body(..., embed=True), authorization: Optional[str] = Header(None)):
    if not SCHEMA_PROMPT_OLTP:
        raise HTTPException(status_code=500, detail="Schema prompt not loaded")
    prompt = SCHEMA_PROMPT_OLTP.strip() + "\n\nGenerate SQL for request:\n" + nl_query.strip() + "\nSQL:"
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(thinking_config=types.ThinkingConfig(thinking_budget=0)),
        )
        sql_text = clean_generated_sql(response.text)
        return {"sql": sql_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate SQL")

@app.post("/run_custom_query")
def run_custom_query(sql_query: str = Body(..., embed=True), db: Session = Depends(get_db), authorization: Optional[str] = Header(None)):
    lowered = sql_query.lower()
    forbidden_statements = ["delete", "update", "insert", "drop", "alter", "truncate", "create"]
    if any(bad in lowered for bad in forbidden_statements):
        raise HTTPException(status_code=400, detail="Only SELECT queries are allowed")
    try:
        result = db.execute(text(sql_query))
        rows = [dict(row._mapping) for row in result]
        return {"results": rows}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"SQL execution error: {e}")

@app.post("/nlp_customer_search")
def nlp_customer_search(nl_query: str = Body(..., embed=True), db: Session = Depends(get_db), authorization: Optional[str] = Header(None)):
    if not SCHEMA_PROMPT_OLTP:
        raise HTTPException(status_code=500, detail="Schema prompt not loaded")
    prompt = SCHEMA_PROMPT_OLTP.strip() + "\n\nGenerate SQL for customer search:\n" + nl_query.strip() + "\nSQL:"
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(thinking_config=types.ThinkingConfig(thinking_budget=0)),
        )
        sql_text_raw = clean_generated_sql(response.text)
        sql_text = rewrite_sql_with_explicit_columns(sql_text_raw)
        lowered = sql_text.lower()
        forbidden_statements = ["delete", "update", "insert", "drop", "alter", "truncate", "create"]
        if any(bad in lowered for bad in forbidden_statements):
            raise HTTPException(status_code=400, detail="Only SELECT queries are allowed")
        result = db.execute(text(sql_text))
        rows = [dict(row._mapping) for row in result]
        if not rows:
            raise HTTPException(status_code=404, detail="Customers not found")
        customers = []
        for row in rows:
            customers.append(
                schemas.CustomerDetail(
                    customer_id=str(row.get("customer_id") or row.get("member_id")),
                    first_name=row.get("first_name", ""),
                    last_name=row.get("last_name", ""),
                    email=row.get("email", ""),
                    phone=row.get("phone", ""),
                    date_of_birth=row.get("date_of_birth"),
                )
            )
        return customers
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"NLP Customer Search failed: {e}")

# --- NEW: NLP Product SQL ---
class NLProductQuery(BaseModel):
    nl_query: str

class CustomProductSQLQuery(BaseModel):
    sql_query: str
    
def ensure_product_id(sql: str) -> str:
    """Guarantee product_id is included in SELECT clause."""
    lowered = sql.lower()
    if "select" in lowered and "product_id" not in lowered:
        # only patch SELECT at the start of query
        if lowered.strip().startswith("select"):
            sql = sql.replace("SELECT", "SELECT product_id,", 1)
            sql = sql.replace("select", "select product_id,", 1)
    return sql

@app.post("/generate_product_sql")
def generate_product_sql(payload: NLProductQuery, authorization: Optional[str] = Header(None)):
    nl_query = payload.nl_query
    if not nl_query:
        raise HTTPException(status_code=400, detail="Empty query")

    prompt = (
        SCHEMA_PROMPT_OLTP.strip()
        + "\n\nGenerate SQL for product search. "
        + "Always include product_id in the SELECT clause, even if not explicitly asked.\n"
        + nl_query.strip()
        + "\nSQL:"
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            ),
        )
        sql_text = clean_generated_sql(response.text)
        sql_text = ensure_product_id(sql_text)  # <-- enforce product_id
        return {"sql": sql_text}
    except Exception as e:
        logger.exception("Error generating product SQL")
        raise HTTPException(status_code=500, detail="Failed to generate product SQL")


@app.post("/run_custom_product_query")
def run_custom_product_query(
    sql_query: str = Body(..., embed=True), 
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    user_info = verify_jwt_token(authorization)
    check_user_role_operational(user_info)

    lowered = sql_query.lower()
    forbidden_statements = ["delete", "update", "insert", "drop", "alter", "truncate", "create"]
    if any(bad in lowered for bad in forbidden_statements):
        raise HTTPException(status_code=400, detail="Only SELECT queries are allowed")
    try:
        result = db.execute(text(sql_query))
        rows = [dict(row._mapping) for row in result]
        return {"results": rows}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"SQL execution error: {e}")


# --- Main ---
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting API Backend server...")
    uvicorn.run(app, host="0.0.0.0", port=5004)
