from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import List, Optional
import logging
import math
from datetime import date, datetime

from database import get_db, engine
import models
import schemas
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Data Warehouse API",
    description="API for OLTP Database",
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


# List all members
@app.get("/members")
def get_members(db: Session = Depends(get_db)):
    members = db.query(models.Member).all()
    return JSONResponse(content=jsonable_encoder(members))


# List all credit cards
@app.get("/credit-cards")
def get_credit_cards(db: Session = Depends(get_db)):
    cards = db.query(models.CreditCard).all()
    return JSONResponse(content=jsonable_encoder(cards))


# List all payment history
@app.get("/payment-history")
def get_payment_history(db: Session = Depends(get_db)):
    payments = db.query(models.PaymentHistory).all()
    return JSONResponse(content=jsonable_encoder(payments))


# List all financial health metrics
@app.get("/financial-health-metrics")
def get_financial_health_metrics(db: Session = Depends(get_db)):
    metrics = db.query(models.FinancialHealthMetric).all()
    return JSONResponse(content=jsonable_encoder(metrics))


# List all financial products
@app.get("/financial-products")
def get_financial_products(db: Session = Depends(get_db)):
    products = db.query(models.FinancialProduct).all()
    return JSONResponse(content=jsonable_encoder(products))


if __name__ == "__main__":
    logger.info("Starting Data Warehouse API server...")
