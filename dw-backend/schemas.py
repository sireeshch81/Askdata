from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

# Enums
class EmploymentStatus(str, Enum):
    employed = "employed"
    self_employed = "self_employed"
    unemployed = "unemployed"
    retired = "retired"

class MemberStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"

class CardType(str, Enum):
    visa = "visa"
    mastercard = "mastercard"
    amex = "amex"
    discover = "discover"

class CardStatus(str, Enum):
    active = "active"
    blocked = "blocked"
    expired = "expired"
    closed = "closed"

class ProductType(str, Enum):
    credit_card = "credit_card"
    personal_loan = "personal_loan"
    mortgage = "mortgage"
    savings_account = "savings_account"
    cd = "cd"
    investment = "investment"

class ProductCategory(str, Enum):
    premium = "premium"
    standard = "standard"
    basic = "basic"
    secured = "secured"

class PaymentMethod(str, Enum):
    auto_pay = "auto_pay"
    online = "online"
    phone = "phone"
    mail = "mail"
    branch = "branch"

class PaymentStatus(str, Enum):
    on_time = "on_time"
    late = "late"
    missed = "missed"
    partial = "partial"

class RecommendationStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"
    expired = "expired"

# Base schemas
class MemberBase(BaseModel):
    member_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    age_group: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    region: Optional[str] = None
    annual_income: Optional[Decimal] = None
    income_bracket: Optional[str] = None
    employment_status: Optional[EmploymentStatus] = None
    member_since: Optional[date] = None
    member_tenure_years: Optional[int] = None
    member_status: Optional[MemberStatus] = None

class CreditCardBase(BaseModel):
    card_id: int
    member_key: int
    card_type: Optional[CardType] = None
    credit_limit: Optional[Decimal] = None
    credit_limit_tier: Optional[str] = None
    apr_rate: Optional[Decimal] = None
    apr_category: Optional[str] = None
    card_status: Optional[CardStatus] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    card_age_months: Optional[int] = None

class FinancialProductBase(BaseModel):
    product_id: int
    product_name: Optional[str] = None
    product_type: Optional[ProductType] = None
    product_category: Optional[ProductCategory] = None
    interest_rate: Optional[Decimal] = None
    interest_rate_tier: Optional[str] = None
    credit_limit_min: Optional[Decimal] = None
    credit_limit_max: Optional[Decimal] = None
    minimum_income_required: Optional[Decimal] = None
    minimum_credit_score: Optional[int] = None
    maximum_debt_to_income: Optional[Decimal] = None
    annual_fee: Optional[Decimal] = None
    fee_category: Optional[str] = None
    rewards_program: Optional[str] = None
    has_rewards: Optional[bool] = None
    eligibility_tier: Optional[str] = None
    is_active: Optional[bool] = None

class PaymentBase(BaseModel):
    member_key: int
    card_key: int
    payment_date_key: int
    payment_method_key: int
    payment_amount: Decimal
    minimum_due: Decimal
    statement_balance: Optional[Decimal] = None
    late_fee: Optional[Decimal] = Field(default=0.00)
    days_late: Optional[int] = Field(default=0)
    payment_ratio: Optional[Decimal] = None
    excess_payment: Optional[Decimal] = None
    is_on_time: Optional[bool] = None
    is_full_payment: Optional[bool] = None
    is_minimum_payment: Optional[bool] = None
    is_over_payment: Optional[bool] = None
    payment_status: PaymentStatus

class FinancialHealthBase(BaseModel):
    member_key: int
    assessment_date_key: int
    credit_score: Optional[int] = None
    debt_to_income_ratio: Optional[Decimal] = None
    credit_utilization_ratio: Optional[Decimal] = None
    payment_reliability_score: Optional[Decimal] = None
    savings_balance: Optional[Decimal] = None
    checking_balance: Optional[Decimal] = None
    total_debt: Optional[Decimal] = None
    number_of_accounts: Optional[int] = None
    recent_inquiries: Optional[int] = None
    delinquent_accounts: Optional[int] = None
    health_score: Optional[Decimal] = None
    total_liquid_assets: Optional[Decimal] = None
    debt_to_assets_ratio: Optional[Decimal] = None
    net_worth: Optional[Decimal] = None
    risk_category: Optional[str] = None
    credit_score_tier: Optional[str] = None
    utilization_tier: Optional[str] = None

class ProductRecommendationBase(BaseModel):
    member_key: int
    product_key: int
    recommendation_date_key: int
    expires_date_key: Optional[int] = None
    recommendation_score: Optional[Decimal] = None
    member_health_score: Optional[Decimal] = None
    credit_utilization_at_time: Optional[Decimal] = None
    payment_reliability_at_time: Optional[Decimal] = None
    recommendation_tier: Optional[str] = None
    days_to_expiry: Optional[int] = None
    is_expired: Optional[bool] = None
    is_high_confidence: Optional[bool] = None
    recommendation_status: Optional[RecommendationStatus] = None

class CreditCardBalanceBase(BaseModel):
    member_key: int
    card_key: int
    snapshot_date_key: int
    credit_limit: Optional[Decimal] = None
    current_balance: Optional[Decimal] = None
    available_credit: Optional[Decimal] = None
    minimum_payment: Optional[Decimal] = None
    utilization_ratio: Optional[Decimal] = None
    utilization_tier: Optional[str] = None
    balance_trend: Optional[str] = None
    is_over_limit: Optional[bool] = None
    is_high_utilization: Optional[bool] = None
    is_maxed_out: Optional[bool] = None

# Response schemas
class Member(MemberBase):
    member_key: int
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    is_current: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }

class CreditCard(CreditCardBase):
    card_key: int
    effective_date: Optional[date] = None
    expiry_date_scd: Optional[date] = None
    is_current: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class FinancialProduct(FinancialProductBase):
    product_key: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class Payment(PaymentBase):
    payment_key: int
    created_datetime: Optional[datetime] = None

    class Config:
        orm_mode = True

class FinancialHealth(FinancialHealthBase):
    health_key: int
    created_datetime: Optional[datetime] = None

    class Config:
        orm_mode = True

class ProductRecommendation(ProductRecommendationBase):
    recommendation_key: int
    created_datetime: Optional[datetime] = None
    updated_datetime: Optional[datetime] = None

    class Config:
        orm_mode = True

class CreditCardBalance(CreditCardBalanceBase):
    balance_key: int
    created_datetime: Optional[datetime] = None

    class Config:
        orm_mode = True

# Query parameter schemas
class PaginationParams(BaseModel):
    skip: int = 0
    limit: int = 100

class MemberFilterParams(BaseModel):
    member_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    income_bracket: Optional[str] = None
    employment_status: Optional[EmploymentStatus] = None
    member_status: Optional[MemberStatus] = None
    is_current: Optional[bool] = True

class CreditCardFilterParams(BaseModel):
    card_id: Optional[int] = None
    member_key: Optional[int] = None
    card_type: Optional[CardType] = None
    credit_limit_tier: Optional[str] = None
    card_status: Optional[CardStatus] = None
    is_current: Optional[bool] = True

class FinancialHealthFilterParams(BaseModel):
    member_key: Optional[int] = None
    assessment_date_key: Optional[int] = None
    risk_category: Optional[str] = None
    credit_score_tier: Optional[str] = None
    utilization_tier: Optional[str] = None

class PaymentFilterParams(BaseModel):
    member_key: Optional[int] = None
    card_key: Optional[int] = None
    payment_date_key: Optional[int] = None
    payment_status: Optional[PaymentStatus] = None
    is_on_time: Optional[bool] = None

class ProductRecommendationFilterParams(BaseModel):
    member_key: Optional[int] = None
    product_key: Optional[int] = None
    recommendation_date_key: Optional[int] = None
    recommendation_status: Optional[RecommendationStatus] = None
    is_expired: Optional[bool] = None
    is_high_confidence: Optional[bool] = None

# Response wrappers
class PaginatedResponse(BaseModel):
    total: int
    items: List[Any]
    page: int
    page_size: int
    total_pages: int

class MemberResponse(PaginatedResponse):
    items: List[Member]

class CreditCardResponse(PaginatedResponse):
    items: List[CreditCard]

class FinancialProductResponse(PaginatedResponse):
    items: List[FinancialProduct]

class PaymentResponse(PaginatedResponse):
    items: List[Payment]

class FinancialHealthResponse(PaginatedResponse):
    items: List[FinancialHealth]

class ProductRecommendationResponse(PaginatedResponse):
    items: List[ProductRecommendation]

class CreditCardBalanceResponse(PaginatedResponse):
    items: List[CreditCardBalance]

# Analytics response schemas
class MemberPaymentSummary(BaseModel):
    member_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    income_bracket: Optional[str] = None
    employment_status: Optional[str] = None
    total_payments: int
    avg_payment_amount: Decimal
    on_time_rate: Decimal
    total_late_fees: Decimal
    avg_days_late: Decimal

    class Config:
        orm_mode = True

class ProductRecommendationMetrics(BaseModel):
    product_name: str
    product_type: str
    product_category: str
    total_recommendations: int
    accepted_count: int
    acceptance_rate: Decimal
    avg_recommendation_score: Decimal

    class Config:
        orm_mode = True

class MemberHealthTrend(BaseModel):
    member_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    year: int
    month_name: str
    avg_health_score: Decimal
    avg_credit_score: int
    avg_debt_to_income: Decimal
    avg_credit_utilization: Decimal

    class Config:
        orm_mode = True