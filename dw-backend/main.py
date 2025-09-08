from fastapi import FastAPI, Depends, HTTPException, Query, status, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import List, Optional
import logging
import math
from datetime import date, datetime
from mongodb import save_offer, get_recommendations
from llm_client import generate_recommendation_letter
from oltpdb import get_member_details
from dotenv import load_dotenv
# import os
from fastapi.testclient import TestClient
from jwtPermissionCheck import *


from database import get_db, engine
import models
import schemas

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Data Warehouse API",
    description="API for Data Warehouse",
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


# Member endpoints
@app.get("/members", response_model=schemas.MemberResponse)
def get_members(
        pagination: schemas.PaginationParams = Depends(),
        filters: schemas.MemberFilterParams = Depends(),
        db: Session = Depends(get_db)
):
    try:
        query = db.query(models.DimMember)

        # Apply filters
        if filters.member_id:
            query = query.filter(models.DimMember.member_id == filters.member_id)
        if filters.first_name:
            query = query.filter(models.DimMember.first_name.ilike(f"%{filters.first_name}%"))
        if filters.last_name:
            query = query.filter(models.DimMember.last_name.ilike(f"%{filters.last_name}%"))
        if filters.email:
            query = query.filter(models.DimMember.email.ilike(f"%{filters.email}%"))
        if filters.city:
            query = query.filter(models.DimMember.city.ilike(f"%{filters.city}%"))
        if filters.state:
            query = query.filter(models.DimMember.state.ilike(f"%{filters.state}%"))
        if filters.income_bracket:
            query = query.filter(models.DimMember.income_bracket == filters.income_bracket)
        if filters.employment_status:
            query = query.filter(models.DimMember.employment_status == filters.employment_status)
        if filters.member_status:
            query = query.filter(models.DimMember.member_status == filters.member_status)
        if filters.is_current is not None:
            query = query.filter(models.DimMember.is_current == filters.is_current)

        # Get total count
        total = query.count()

        # Apply pagination
        query = query.offset(pagination.skip).limit(pagination.limit)

        # Execute query
        members = query.all()

        # Calculate pagination metadata
        page = pagination.skip // pagination.limit + 1 if pagination.limit > 0 else 1
        total_pages = math.ceil(total / pagination.limit) if pagination.limit > 0 else 1

        return {
            "total": total,
            "items": members,
            "page": page,
            "page_size": pagination.limit,
            "total_pages": total_pages
        }
    except Exception as e:
        logger.error(f"Error getting members: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting members: {str(e)}"
        )


@app.get("/members/{member_key}", response_model=schemas.Member)
def get_member(member_key: int, db: Session = Depends(get_db)):
    try:
        member = db.query(models.DimMember).filter(models.DimMember.member_key == member_key).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Member with key {member_key} not found"
            )
        return member
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting member {member_key}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting member: {str(e)}"
        )


# Credit Card endpoints
@app.get("/credit-cards", response_model=schemas.CreditCardResponse)
def get_credit_cards(
        pagination: schemas.PaginationParams = Depends(),
        filters: schemas.CreditCardFilterParams = Depends(),
        db: Session = Depends(get_db)
):
    try:
        query = db.query(models.DimCreditCard)

        # Apply filters
        if filters.card_id:
            query = query.filter(models.DimCreditCard.card_id == filters.card_id)
        if filters.member_key:
            query = query.filter(models.DimCreditCard.member_key == filters.member_key)
        if filters.card_type:
            query = query.filter(models.DimCreditCard.card_type == filters.card_type)
        if filters.credit_limit_tier:
            query = query.filter(models.DimCreditCard.credit_limit_tier == filters.credit_limit_tier)
        if filters.card_status:
            query = query.filter(models.DimCreditCard.card_status == filters.card_status)
        if filters.is_current is not None:
            query = query.filter(models.DimCreditCard.is_current == filters.is_current)

        # Get total count
        total = query.count()

        # Apply pagination
        query = query.offset(pagination.skip).limit(pagination.limit)

        # Execute query
        credit_cards = query.all()

        # Calculate pagination metadata
        page = pagination.skip // pagination.limit + 1 if pagination.limit > 0 else 1
        total_pages = math.ceil(total / pagination.limit) if pagination.limit > 0 else 1

        return {
            "total": total,
            "items": credit_cards,
            "page": page,
            "page_size": pagination.limit,
            "total_pages": total_pages
        }
    except Exception as e:
        logger.error(f"Error getting credit cards: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting credit cards: {str(e)}"
        )


@app.get("/credit-cards/{card_key}", response_model=schemas.CreditCard)
def get_credit_card(card_key: int, db: Session = Depends(get_db)):
    try:
        credit_card = db.query(models.DimCreditCard).filter(models.DimCreditCard.card_key == card_key).first()
        if not credit_card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Credit card with key {card_key} not found"
            )
        return credit_card
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting credit card {card_key}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting credit card: {str(e)}"
        )


# Financial Health endpoints
@app.get("/financial-health", response_model=schemas.FinancialHealthResponse)
def get_financial_health(
        pagination: schemas.PaginationParams = Depends(),
        filters: schemas.FinancialHealthFilterParams = Depends(),
        db: Session = Depends(get_db)
):
    try:
        query = db.query(models.FactFinancialHealth)

        # Apply filters
        if filters.member_key:
            query = query.filter(models.FactFinancialHealth.member_key == filters.member_key)
        if filters.assessment_date_key:
            query = query.filter(models.FactFinancialHealth.assessment_date_key == filters.assessment_date_key)
        if filters.risk_category:
            query = query.filter(models.FactFinancialHealth.risk_category == filters.risk_category)
        if filters.credit_score_tier:
            query = query.filter(models.FactFinancialHealth.credit_score_tier == filters.credit_score_tier)
        if filters.utilization_tier:
            query = query.filter(models.FactFinancialHealth.utilization_tier == filters.utilization_tier)

        # Get total count
        total = query.count()

        # Apply pagination
        query = query.offset(pagination.skip).limit(pagination.limit)

        # Execute query
        financial_health = query.all()

        # Calculate pagination metadata
        page = pagination.skip // pagination.limit + 1 if pagination.limit > 0 else 1
        total_pages = math.ceil(total / pagination.limit) if pagination.limit > 0 else 1

        return {
            "total": total,
            "items": financial_health,
            "page": page,
            "page_size": pagination.limit,
            "total_pages": total_pages
        }
    except Exception as e:
        logger.error(f"Error getting financial health: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting financial health: {str(e)}"
        )


# Payment endpoints
@app.get("/payments", response_model=schemas.PaymentResponse)
def get_payments(
        pagination: schemas.PaginationParams = Depends(),
        filters: schemas.PaymentFilterParams = Depends(),
        db: Session = Depends(get_db)
):
    try:
        query = db.query(models.FactPayment)

        # Apply filters
        if filters.member_key:
            query = query.filter(models.FactPayment.member_key == filters.member_key)
        if filters.card_key:
            query = query.filter(models.FactPayment.card_key == filters.card_key)
        if filters.payment_date_key:
            query = query.filter(models.FactPayment.payment_date_key == filters.payment_date_key)
        if filters.payment_status:
            query = query.filter(models.FactPayment.payment_status == filters.payment_status)
        if filters.is_on_time is not None:
            query = query.filter(models.FactPayment.is_on_time == filters.is_on_time)

        # Get total count
        total = query.count()

        # Apply pagination
        query = query.offset(pagination.skip).limit(pagination.limit)

        # Execute query
        payments = query.all()

        # Calculate pagination metadata
        page = pagination.skip // pagination.limit + 1 if pagination.limit > 0 else 1
        total_pages = math.ceil(total / pagination.limit) if pagination.limit > 0 else 1

        return {
            "total": total,
            "items": payments,
            "page": page,
            "page_size": pagination.limit,
            "total_pages": total_pages
        }
    except Exception as e:
        logger.error(f"Error getting payments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting payments: {str(e)}"
        )


# Analytics endpoints
@app.get("/analytics/member-payment-summary", response_model=List[schemas.MemberPaymentSummary])
def get_member_payment_summary(db: Session = Depends(get_db)):
    try:
        # Execute raw SQL query for the view
        result = db.execute(text("SELECT * FROM vw_member_payment_summary"))
        return result.fetchall()
    except Exception as e:
        logger.error(f"Error getting member payment summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting member payment summary: {str(e)}"
        )


@app.get("/analytics/product-recommendation-metrics", response_model=List[schemas.ProductRecommendationMetrics])
def get_product_recommendation_metrics(db: Session = Depends(get_db)):
    try:
        # Execute raw SQL query for the view
        result = db.execute(text("SELECT * FROM vw_product_recommendation_metrics"))
        return result.fetchall()
    except Exception as e:
        logger.error(f"Error getting product recommendation metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting product recommendation metrics: {str(e)}"
        )


@app.get("/analytics/member-health-trends", response_model=List[schemas.MemberHealthTrend])
def get_member_health_trends(
        member_id: Optional[int] = None,
        year: Optional[int] = None,
        db: Session = Depends(get_db)
):
    try:
        # Start with the base query
        query = "SELECT * FROM vw_member_health_trends"
        params = {}

        # Add filters if provided
        filters = []
        if member_id:
            filters.append("member_id = :member_id")
            params["member_id"] = member_id
        if year:
            filters.append("year = :year")
            params["year"] = year

        if filters:
            query += " WHERE " + " AND ".join(filters)

        # Execute the query
        result = db.execute(text(query), params)
        return result.fetchall()
    except Exception as e:
        logger.error(f"Error getting member health trends: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting member health trends: {str(e)}"
        )


# Financial Product endpoints
@app.get("/financial-products", response_model=schemas.FinancialProductResponse)
def get_financial_products(
        pagination: schemas.PaginationParams = Depends(),
        product_id: Optional[int] = None,
        product_name: Optional[str] = None,
        product_type: Optional[schemas.ProductType] = None,
        product_category: Optional[schemas.ProductCategory] = None,
        is_active: Optional[bool] = None,
        db: Session = Depends(get_db)
):
    try:
        query = db.query(models.DimFinancialProduct)

        # Apply filters
        if product_id:
            query = query.filter(models.DimFinancialProduct.product_id == product_id)
        if product_name:
            query = query.filter(models.DimFinancialProduct.product_name.ilike(f"%{product_name}%"))
        if product_type:
            query = query.filter(models.DimFinancialProduct.product_type == product_type)
        if product_category:
            query = query.filter(models.DimFinancialProduct.product_category == product_category)
        if is_active is not None:
            query = query.filter(models.DimFinancialProduct.is_active == is_active)

        # Get total count
        total = query.count()

        # Apply pagination
        query = query.offset(pagination.skip).limit(pagination.limit)

        # Execute query
        financial_products = query.all()

        # Calculate pagination metadata
        page = pagination.skip // pagination.limit + 1 if pagination.limit > 0 else 1
        total_pages = math.ceil(total / pagination.limit) if pagination.limit > 0 else 1

        return {
            "total": total,
            "items": financial_products,
            "page": page,
            "page_size": pagination.limit,
            "total_pages": total_pages
        }
    except Exception as e:
        logger.error(f"Error getting financial products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting financial products: {str(e)}"
        )


@app.get("/financial-products/{product_key}", response_model=schemas.FinancialProduct)
def get_financial_product(product_key: int, db: Session = Depends(get_db)):
    try:
        financial_product = db.query(models.DimFinancialProduct).filter(
            models.DimFinancialProduct.product_key == product_key).first()
        if not financial_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Financial product with key {product_key} not found"
            )
        return financial_product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting financial product {product_key}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting financial product: {str(e)}"
        )


# Product Recommendation endpoints
@app.get("/product-recommendations", response_model=schemas.ProductRecommendationResponse)
def get_product_recommendations(
        pagination: schemas.PaginationParams = Depends(),
        filters: schemas.ProductRecommendationFilterParams = Depends(),
        db: Session = Depends(get_db)
):
    try:
        query = db.query(models.FactProductRecommendation)

        # Apply filters
        if filters.member_key:
            query = query.filter(models.FactProductRecommendation.member_key == filters.member_key)
        if filters.product_key:
            query = query.filter(models.FactProductRecommendation.product_key == filters.product_key)
        if filters.recommendation_date_key:
            query = query.filter(
                models.FactProductRecommendation.recommendation_date_key == filters.recommendation_date_key)
        if filters.recommendation_status:
            query = query.filter(
                models.FactProductRecommendation.recommendation_status == filters.recommendation_status)
        if filters.is_expired is not None:
            query = query.filter(models.FactProductRecommendation.is_expired == filters.is_expired)
        if filters.is_high_confidence is not None:
            query = query.filter(models.FactProductRecommendation.is_high_confidence == filters.is_high_confidence)

        # Get total count
        total = query.count()

        # Apply pagination
        query = query.offset(pagination.skip).limit(pagination.limit)

        # Execute query
        recommendations = query.all()

        # Calculate pagination metadata
        page = pagination.skip // pagination.limit + 1 if pagination.limit > 0 else 1
        total_pages = math.ceil(total / pagination.limit) if pagination.limit > 0 else 1

        return {
            "total": total,
            "items": recommendations,
            "page": page,
            "page_size": pagination.limit,
            "total_pages": total_pages
        }
    except Exception as e:
        logger.error(f"Error getting product recommendations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting product recommendations: {str(e)}"
        )


# Credit Card Balance endpoints
@app.get("/credit-card-balances", response_model=schemas.CreditCardBalanceResponse)
def get_credit_card_balances(
        pagination: schemas.PaginationParams = Depends(),
        member_key: Optional[int] = None,
        card_key: Optional[int] = None,
        snapshot_date_key: Optional[int] = None,
        db: Session = Depends(get_db)
):
    try:
        query = db.query(models.FactCreditCardBalance)

        # Apply filters
        if member_key:
            query = query.filter(models.FactCreditCardBalance.member_key == member_key)
        if card_key:
            query = query.filter(models.FactCreditCardBalance.card_key == card_key)
        if snapshot_date_key:
            query = query.filter(models.FactCreditCardBalance.snapshot_date_key == snapshot_date_key)

        # Get total count
        total = query.count()

        # Apply pagination
        query = query.offset(pagination.skip).limit(pagination.limit)

        # Execute query
        balances = query.all()

        # Calculate pagination metadata
        page = pagination.skip // pagination.limit + 1 if pagination.limit > 0 else 1
        total_pages = math.ceil(total / pagination.limit) if pagination.limit > 0 else 1

        return {
            "total": total,
            "items": balances,
            "page": page,
            "page_size": pagination.limit,
            "total_pages": total_pages
        }
    except Exception as e:
        logger.error(f"Error getting credit card balances: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting credit card balances: {str(e)}"
        )


@app.get("/credit-card-balances/{balance_key}", response_model=schemas.CreditCardBalance)
def get_credit_card_balance(balance_key: int, db: Session = Depends(get_db)):
    try:
        balance = db.query(models.FactCreditCardBalance).filter(
            models.FactCreditCardBalance.balance_key == balance_key
        ).first()

        if not balance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Credit card balance with key {balance_key} not found"
            )

        return balance
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting credit card balance {balance_key}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting credit card balance: {str(e)}"
        )


@app.post("/offer-customer", response_model=schemas.OfferCustomerResponse)
def offer_customer(request: schemas.OfferCustomerRequest, authorization: Optional[str] = Header(None)):
    """
    Create an offer for a customer based on their profile and recommendations
    """
    try:
        customer_id = request.customer_id
        # Generate offer ID (simple implementation)
        import uuid
        offer_id = str(uuid.uuid4())[:8].upper()

        # Get customer details from OLTP database
        try:
            customer_details = get_member_details(customer_id)
            if not customer_details:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Customer with ID {customer_id} not found"
                )
        except Exception as err:
            logger.error(f"Database error: {err}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(err)}"
            )

        # Get customer's recommendations and financial health
        customer_profile_recommendations = get_recommendations(customer_id)
        logger.info(f" Customer data for {customer_id} :--> {customer_profile_recommendations}")

        # Generate a recommendation letter using customer details and recommendations
        recommendation_letter = generate_recommendation_letter(customer_details, customer_profile_recommendations, offer_id)
        logger.info(f"Generated recommendation letter for customer {customer_id} with offer ID {offer_id}")

        # Save recommendation letter to file
        with open(f"recommendation_letters/{offer_id}.txt", "w") as f:
            f.write(recommendation_letter)
        # Save offer to MongoDB
        save_offer(offer_id, {
            "customer_id": customer_id,
            "offer_id": offer_id,
            "status": "created",
            "message": f"Offer created successfully for customer id : {customer_id}",
            "created_at": datetime.now()
        })

        # Create offer response
        offer_response = schemas.OfferCustomerResponse(
            customer_id=customer_id,
            offer_id=offer_id,
            status="created",
            message=f"Offer created successfully for customer id : {customer_id}",
            created_at=datetime.now()
        )
        logger.info(f"Offer created for customer {customer_id} with offer ID {offer_id}")
        return offer_response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating offer for customer {request.customer_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating offer: {str(e)}"
        )
def get_and_check_user_info(authorization):
    print(authorization)
    user_info = verify_jwt_token(authorization)
    print(user_info)
    check_user_role_historical(user_info)
    return user_info


if __name__ == "__main__":
    print("Starting Data Warehouse API server...")
    # client = TestClient(app)
    # # Test offer_customer endpoint
    # test_request = schemas.OfferCustomerRequest(
    #     customer_id="1"
    # )
    # response = client.post("/offer-customer", json=test_request.model_dump())
    # print("Test response:", response.json())
