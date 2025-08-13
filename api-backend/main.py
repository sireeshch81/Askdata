from fastapi import FastAPI, HTTPException, Depends, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_, text
from datetime import datetime
import logging
from typing import List
import json
import os
import traceback

from database import get_db
import models
import schemas
from RecommendationDataManager import RecommendationDataManager

from google import genai
from google.genai import types

# Logging setup
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

# Initialize Gemini client with API key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY environment variable not set!")
client = genai.Client(api_key=GEMINI_API_KEY)

# Load schema prompt for OLTP from file once at startup
schema_prompt_path = "prompts/schema_oltp.txt"
try:
    with open(schema_prompt_path, "r") as f:
        SCHEMA_PROMPT_OLTP = f.read()
    logger.info(f"Loaded schema prompt from {schema_prompt_path}")
except Exception as e:
    SCHEMA_PROMPT_OLTP = ""
    logger.error(f"Failed to load schema prompt from {schema_prompt_path}: {e}")

# Helper function to clean generated SQL
def clean_generated_sql(sql_text: str) -> str:
    sql_text = sql_text.strip()
    # Remove markdown/code block markers if present
    if sql_text.startswith("```sql"):
        sql_text = sql_text.replace("```sql", "").replace("```", "").strip()
    elif sql_text.startswith("```"):
        sql_text = sql_text.replace("```", "").strip()
    elif sql_text.lower().startswith("sql"):
        sql_text = sql_text[len("sql"):].strip()
    # Remove trailing semicolon
    if sql_text.endswith(";"):
        sql_text = sql_text[:-1].strip()
    return sql_text

def rewrite_sql_with_explicit_columns(sql: str) -> str:
    """
    Rewrites the SQL to select explicit columns with proper aliases.
    This function assumes the original query starts with SELECT * FROM ...
    """
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
            return sql  # can't rewrite properly, return as-is

        rewritten_sql = new_select + sql[from_index:]
        return rewritten_sql
    else:
        # If query is already explicit, return as is
        return sql

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Enhanced customer detail search endpoint
@app.get("/customer_detail", response_model=List[schemas.CustomerDetail])
def get_customer_detail(
    customer_name: str = Query(None, description="Customer name to search for (optional)"),
    email: str = Query(None, description="Email to search for (optional)"),
    phone: str = Query(None, description="Phone to search for (optional)"),
    db: Session = Depends(get_db),
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

    customers = query.limit(100).all()  # limit to 100 results

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

# Recommendations endpoint
@app.get("/recommendations", response_model=schemas.RecommendationsResponse)
def get_recommendations(
    customer_id: str = Query(..., description="Customer ID to get recommendations for")
):
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

# Find all the products
@app.get("/products", response_model=List[schemas.ProductsResponse])
def getProductsByProductName(
    product_name: str = Query(..., description="Product name to search for"),
    db: Session = Depends(get_db),
):
    """
    Return stubbed products based on product name.
    """

    print(product_name)


    query = db.query(models.FinancialProduct)

    filters = []

    pattern = f"%{product_name}%"
    filters.append(
        or_(
            models.FinancialProduct.product_name.ilike(pattern),
            
        )
    )
    query  = query.filter(or_(*filters))

    financialProducts = query.limit(100).all()  # limit to 100 results

    if not financialProducts:
        raise HTTPException(status_code=404, detail="Products not found")

    return [
            schemas.ProductsResponse(
                product_id=financialProduct.product_id,
                product_name=financialProduct.product_name,
                product_type=financialProduct.product_type,
                product_category=financialProduct.product_category,
                interest_rate=financialProduct.interest_rate,
                credit_limit_min=financialProduct.credit_limit_min,
                credit_limit_max=financialProduct.credit_limit_max,
                minimum_income_required=financialProduct.minimum_income_required,
                minimum_credit_score=financialProduct.minimum_credit_score,
                maximum_debt_to_income=financialProduct.maximum_debt_to_income,
                annual_fee=financialProduct.annual_fee,
                rewards_program=financialProduct.rewards_program,
                benefits=financialProduct.benefits,
                eligibility_criteria=financialProduct.eligibility_criteria,
                is_active=financialProduct.is_active,
                created_at=financialProduct.created_at,
                updated_at=financialProduct.updated_at,
            )
            for financialProduct in financialProducts
    ]


# Recommendation Letter Endpoint
@app.get("/recommendation_letter", response_model=str)
def get_recommendation_letter(
    customer_id: str = Query(..., description="Customer ID to get recommendations for"),
    db: Session = Depends(get_db),
):
    recommendation_manager = RecommendationDataManager()
    collection = recommendation_manager.find_by_customer_id(customer_id)

    if not collection:
        raise HTTPException(status_code=404, detail="Recommendations not found for this customer.")

    try:
        member_id_int = int(customer_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid customer ID format.")

    member = db.query(models.Member).filter(models.Member.member_id == member_id_int).first()

    if not member:
        raise HTTPException(status_code=404, detail="Customer not found in database.")

    # Add full name to the customer profile
    collection["customer_profile"]["name"] = f"{member.first_name} {member.last_name}"

    # Convert MongoDB document to JSON string
    json_string = json.dumps(collection, default=str)

    with open("prompts/recommendation-letter-prompt.txt", "r") as f:
        prompt_text = f.read()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt_text + "\n\n The JSON data file is: \n" +  json_string,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disables thinking
        ),
    )

    logger.info("Generated recommendation letter via Gemini")
    return response.text

# Simple auth endpoint (stub)
@app.post("/auth", response_model=schemas.AuthResponse)
def authenticate(
    username: str = Query(..., description="Username for authentication"),
    password: str = Query(..., description="Password for authentication"),
):
    if username and password:
        # Replace with real auth logic
        return schemas.AuthResponse(access_token="stubbed.jwt.token", token_type="bearer")
    else:
        raise HTTPException(status_code=401, detail="Authentication failed")

# New Endpoint: Generate SQL from natural language query using schema prompt injection
@app.post("/generate_sql")
def generate_sql(nl_query: str = Body(..., embed=True)):
    """
    Accepts natural language query string,
    returns SQL query generated by Gemini API,
    injecting the OLTP schema prompt to guide generation.
    """
    if not SCHEMA_PROMPT_OLTP:
        logger.error("Schema prompt not loaded; cannot generate SQL.")
        raise HTTPException(status_code=500, detail="Schema prompt not loaded")

    prompt = (
        SCHEMA_PROMPT_OLTP.strip()
        + "\n\n"
        + "Generate a SQL query for the following request:\n"
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
        logger.info(f"Generated SQL: {sql_text}")
        return {"sql": sql_text}
    except Exception as e:
        logger.error(f"Gemini API call failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate SQL")

# New Endpoint: Run user-edited SQL query and return results
@app.post("/run_custom_query")
def run_custom_query(sql_query: str = Body(..., embed=True), db: Session = Depends(get_db)):
    """
    Accepts a raw SQL query string,
    executes it safely on the DB,
    returns query results as list of dicts.
    """
    try:
        # Basic safety check to allow only SELECT queries
        lowered = sql_query.lower()
        forbidden_statements = ["delete", "update", "insert", "drop", "alter", "truncate", "create"]
        if any(bad in lowered for bad in forbidden_statements):
            logger.warning(f"Rejected unsafe SQL query: {sql_query}")
            raise HTTPException(status_code=400, detail="Only SELECT queries are allowed")

        result = db.execute(text(sql_query))
        rows = [dict(row._mapping) for row in result]  # Fix to avoid TypeError
        logger.info(f"Executed custom SQL query, returned {len(rows)} rows")
        return {"results": rows}
    except Exception as e:
        tb_str = traceback.format_exc()
        logger.error(f"Failed to execute SQL: {e}\nTraceback:\n{tb_str}")
        raise HTTPException(status_code=400, detail=f"SQL execution error: {e}")

# New Endpoint: NLP-powered customer search using Gemini LLM to generate SQL
@app.post("/nlp_customer_search")
def nlp_customer_search(nl_query: str = Body(..., embed=True), db: Session = Depends(get_db)):
    """
    Accepts a natural language query string,
    uses Gemini to generate SQL,
    runs SQL on DB,
    returns customer search results.
    """
    if not SCHEMA_PROMPT_OLTP:
        logger.error("Schema prompt not loaded; cannot perform NLP search.")
        raise HTTPException(status_code=500, detail="Schema prompt not loaded")

    prompt = (
        SCHEMA_PROMPT_OLTP.strip()
        + "\n\n"
        + "Generate a SQL query for the following customer search request:\n"
        + nl_query.strip()
        + "\nSQL:"
    )

    try:
        # Generate SQL query from natural language
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            ),
        )
        sql_text_raw = clean_generated_sql(response.text)
        sql_text = rewrite_sql_with_explicit_columns(sql_text_raw)
        logger.info(f"NLP-generated SQL (rewritten): {sql_text}")

        # Safety check
        lowered = sql_text.lower()
        forbidden_statements = ["delete", "update", "insert", "drop", "alter", "truncate", "create"]
        if any(bad in lowered for bad in forbidden_statements):
            logger.warning(f"Rejected unsafe SQL from NLP: {sql_text}")
            raise HTTPException(status_code=400, detail="Only SELECT queries are allowed")

        # Run the SQL query
        result = db.execute(text(sql_text))
        rows = [dict(row._mapping) for row in result]

        if not rows:
            raise HTTPException(status_code=404, detail="Customers not found")

        # Convert raw DB rows to CustomerDetail schema list
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
        logger.error(f"NLP Customer Search failed: {e}")
        raise HTTPException(status_code=400, detail=f"NLP Customer Search failed: {e}")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting API Backend server...")
    uvicorn.run(app, host="0.0.0.0", port=5004)
