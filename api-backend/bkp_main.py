from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import logging
from typing import Optional
from datetime import date

from database import get_db
from mongodb import get_mongodb
import schemas
from authentication import authenticate_user, create_access_token

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API Backend",
    description="API Backend for UI Layer - connects to OLTP DB and MongoDB",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/customer_detail", response_model=schemas.CustomerDetail)
def get_customer_detail(
    customer_name: str = Query(..., description="Customer name to search for")
):
    """
    Return a stubbed customer detail matching the name, or a default if not found.
    """
    sample_customers = [
        schemas.CustomerDetail(
            customer_id="1001",
            first_name="John",
            last_name="Smith",
            email="john.smith@email.com",
            phone="555-0123",
            date_of_birth=date(1985, 3, 15)
        ),
        schemas.CustomerDetail(
            customer_id="1002",
            first_name="Sarah",
            last_name="Johnson",
            email="sarah.johnson@email.com",
            phone="555-0456",
            date_of_birth=date(1990, 7, 22)
        ),
    ]
    for customer in sample_customers:
        if customer_name.lower() in customer.first_name.lower() or customer_name.lower() in customer.last_name.lower():
            return customer
    return sample_customers[0]  # Default stub


@app.get("/recommendations", response_model=schemas.RecommendationsResponse)
def get_recommendations(
    customer_id: str = Query(..., description="Customer ID to get recommendations for")
):
    """
    Return stubbed recommendations for a customer.
    """
    sample_recommendations = [
        schemas.Recommendation(product_id="prod1", product_name="Credit Card Gold", score=0.95),
        schemas.Recommendation(product_id="prod2", product_name="Personal Loan", score=0.89),
    ]
    return schemas.RecommendationsResponse(customer_id=customer_id, recommendations=sample_recommendations)


@app.post("/auth", response_model=schemas.AuthResponse)
def authenticate(
    username: str = Query(..., description="Username for authentication"),
    password: str = Query(..., description="Password for authentication")
):
    """
    Stub authentication endpoint. Always returns a fake JWT.
    """
    if username and password:
        return schemas.AuthResponse(access_token="stubbed.jwt.token", token_type="bearer")
    else:
        raise HTTPException(status_code=401, detail="Authentication failed")


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting API Backend server...")
    uvicorn.run(app, host="0.0.0.0", port=5004)
