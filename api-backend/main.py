from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime
import logging
from typing import List

from database import get_db
from mongodb import get_mongodb
import models
import schemas

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

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/customer_detail", response_model=List[schemas.CustomerDetail])
def get_customer_detail(
    customer_name: str = Query(..., description="Customer name to search for"),
    db: Session = Depends(get_db),
):
    customers = (
        db.query(models.Member)
        .filter(
            or_(
                models.Member.first_name.ilike(f"%{customer_name}%"),
                models.Member.last_name.ilike(f"%{customer_name}%"),
            )
        )
        .all()
    )
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


@app.get("/recommendations", response_model=schemas.RecommendationsResponse)
def get_recommendations(
    customer_id: str = Query(..., description="Customer ID to get recommendations for"),
    mongodb=Depends(get_mongodb),
):
    recs_collection = mongodb["recommendations"]
    raw_recs = list(recs_collection.find({"customer_id": customer_id}))

    if not raw_recs:
        raise HTTPException(status_code=404, detail="Recommendations not found")

    recommendations = [
        schemas.Recommendation(
            product_id=rec.get("product_id"),
            product_name=rec.get("product_name"),
            score=rec.get("score"),
        )
        for rec in raw_recs
    ]

    return schemas.RecommendationsResponse(
        customer_id=customer_id, recommendations=recommendations
    )


@app.post("/auth", response_model=schemas.AuthResponse)
def authenticate(
    username: str = Query(..., description="Username for authentication"),
    password: str = Query(..., description="Password for authentication"),
):
    if username and password:
        return schemas.AuthResponse(access_token="stubbed.jwt.token", token_type="bearer")
    else:
        raise HTTPException(status_code=401, detail="Authentication failed")


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting API Backend server...")
    uvicorn.run(app, host="0.0.0.0", port=5004)
