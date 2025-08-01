from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import logging
from typing import Optional
from datetime import date

from database import get_mysql_db
from mongodb import get_mongodb
import schemas
from auth import authenticate_user, create_access_token

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
    # db = get_mysql_db()
    # try:
    #     customers_dblist = db.query("Customer").filter(
    #         "first_name LIKE :name OR last_name LIKE :name",
    #     )
    #     # TODO: Handle case where customer is not found with empty collection
    #     if not customers_dblist:
    #         raise HTTPException(status_code=404, detail="Customer not found")
    #     return schemas.CustomerDetail(
    #         member_id=customer.member_id,
    #         first_name=customer.first_name,
    #         last_name=customer.last_name,
    #         email=customer.email,
    #         phone=customer.phone,
    #         date_of_birth=customer.date_of_birth
    #     )

    try:
        sample_customers = [
            schemas.CustomerDetail(
                member_id=1001,
                first_name="John",
                last_name="Smith",
                email="john.smith@email.com",
                phone="555-0123",
                date_of_birth=date(1985, 3, 15)
            ),
            schemas.CustomerDetail(
                member_id=1002,
                first_name="Sarah",
                last_name="Johnson",
                email="sarah.johnson@email.com",
                phone="555-0456",
                date_of_birth=date(1990, 7, 22)
            ),
            schemas.CustomerDetail(
                member_id=1003,
                first_name="Michael",
                last_name="Brown",
                email="michael.brown@email.com",
                phone="555-0789",
                date_of_birth=date(1978, 12, 8)
            ),
            schemas.CustomerDetail(
                member_id=1004,
                first_name="Emily",
                last_name="Davis",
                email="emily.davis@email.com",
                phone="555-0321",
                date_of_birth=date(1992, 5, 3)
            ),
            schemas.CustomerDetail(
                member_id=1005,
                first_name="David",
                last_name="Wilson",
                email="david.wilson@email.com",
                phone="555-0654",
                date_of_birth=date(1987, 9, 18)
            )
        ]
        return sample_customers

    except Exception as e:
        logger.error(f"Error retrieving customer details: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/recommendations", response_model=schemas.RecommendationsResponse)
def get_recommendations(
    customer_id: str = Query(..., description="Customer ID to get recommendations for")
):
    """
    Retrieve recommendations from MongoDB for a specific customer.
    """
    try:
        mongo_db = get_mongodb()
        recommendations_collection = mongo_db.recommendations
        
        # Find recommendations for the customer
        customer_recs = recommendations_collection.find_one({"customer_id": customer_id})
        
        if not customer_recs:
            raise HTTPException(status_code=404, detail="No recommendations found for customer")
        
        recommendations = []
        for rec in customer_recs.get("recommendations", []):
            recommendations.append(schemas.Recommendation(
                id=rec.get("id"),
                title=rec.get("title"),
                description=rec.get("description")
            ))
        
        return schemas.RecommendationsResponse(recommendations=recommendations)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/auth", response_model=schemas.AuthResponse)
def authenticate(
    username: str = Query(..., description="Username for authentication"),
    password: str = Query(..., description="Password for authentication")
):
    """
    Authenticate user and return JWT token.
    """
    try:
        mongo_db = get_mongodb()
        
        # Authenticate user against MongoDB
        user = authenticate_user(mongo_db, username, password)
        if not user:
            raise HTTPException(status_code=401, detail="Authentication failed")
        
        # Create JWT token
        access_token = create_access_token({"sub": username})
        
        return schemas.AuthResponse(
            access_token=access_token,
            token_type="bearer"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during authentication: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting API Backend server...")
    uvicorn.run(app, host="0.0.0.0", port=5004)
