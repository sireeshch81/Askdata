from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime
import logging
from typing import List
import json
from database import get_db
import models
import schemas
from RecommendationDataManager import RecommendationDataManager
from google import genai
from google.genai import types

# from auth import authenticate_user, create_access_token

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

    # The client gets the API key from the environment variable `GEMINI_API_KEY`.
    client = genai.Client()

    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt_text + "\n\n The JSON data file is: \n" +  json_string,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disables thinking
        ),

    )

    print(response.text)
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


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting API Backend server...")
    uvicorn.run(app, host="0.0.0.0", port=5004)
