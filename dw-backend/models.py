from sqlalchemy import (
    Column, Integer, String, Date, DECIMAL, Enum, ForeignKey, Boolean, 
    TIMESTAMP, func, Text, CheckConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Dimension Tables
class DimMember(Base):
    __tablename__ = 'dim_member'
    
    member_key = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100))
    phone = Column(String(15))
    date_of_birth = Column(Date)
    age_group = Column(String(20))  # Derived: '18-25', '26-35', '36-45', '46-55', '56-65', '65+'
    address = Column(String(255))
    city = Column(String(50))
    state = Column(String(50))
    zip_code = Column(String(10))
    region = Column(String(50))  # Derived from state
    annual_income = Column(DECIMAL(12, 2))
    income_bracket = Column(String(20))  # Derived: 'Low', 'Medium', 'High', 'Premium'
    employment_status = Column(Enum('employed', 'self_employed', 'unemployed', 'retired', name='employment_status'))
    member_since = Column(Date)
    member_tenure_years = Column(Integer)  # Derived
    member_status = Column(Enum('active', 'inactive', 'suspended', name='member_status'))
    
    # SCD Type 2 fields
    effective_date = Column(Date)
    expiry_date = Column(Date)
    is_current = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

class DimCreditCard(Base):
    __tablename__ = 'dim_credit_card'
    
    card_key = Column(Integer, primary_key=True, autoincrement=True)
    card_id = Column(Integer, nullable=False)
    member_key = Column(Integer, ForeignKey('dim_member.member_key'), nullable=False)
    card_type = Column(Enum('visa', 'mastercard', 'amex', 'discover', name='card_type'))
    credit_limit = Column(DECIMAL(10, 2))
    credit_limit_tier = Column(String(20))  # Derived: 'Low', 'Medium', 'High', 'Premium'
    apr_rate = Column(DECIMAL(5, 4))
    apr_category = Column(String(20))  # Derived: 'Low', 'Medium', 'High'
    card_status = Column(Enum('active', 'blocked', 'expired', 'closed', name='card_status'))
    issue_date = Column(Date)
    expiry_date = Column(Date)
    card_age_months = Column(Integer)  # Derived
    
    # SCD Type 2 fields
    effective_date = Column(Date)
    expiry_date_scd = Column(Date)
    is_current = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

class DimFinancialProduct(Base):
    __tablename__ = 'dim_financial_product'
    
    product_key = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, nullable=False)
    product_name = Column(String(100))
    product_type = Column(Enum('credit_card', 'personal_loan', 'mortgage', 'savings_account', 'cd', 'investment', name='product_type'))
    product_category = Column(Enum('premium', 'standard', 'basic', 'secured', name='product_category'))
    interest_rate = Column(DECIMAL(5, 4))
    interest_rate_tier = Column(String(20))  # Derived: 'Low', 'Medium', 'High'
    credit_limit_min = Column(DECIMAL(10, 2))
    credit_limit_max = Column(DECIMAL(10, 2))
    minimum_income_required = Column(DECIMAL(10, 2))
    minimum_credit_score = Column(Integer)
    maximum_debt_to_income = Column(DECIMAL(5, 4))
    annual_fee = Column(DECIMAL(6, 2))
    fee_category = Column(String(20))  # Derived: 'No Fee', 'Low Fee', 'High Fee'
    rewards_program = Column(String(100))
    has_rewards = Column(Boolean)  # Derived
    eligibility_tier = Column(String(20))  # Derived: 'Easy', 'Medium', 'Strict'
    is_active = Column(Boolean)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

class DimDate(Base):
    __tablename__ = 'dim_date'
    
    date_key = Column(Integer, primary_key=True)
    date_value = Column(Date, nullable=False)
    day_of_week = Column(Integer)
    day_name = Column(String(10))
    day_of_month = Column(Integer)
    day_of_year = Column(Integer)
    week_of_year = Column(Integer)
    month_number = Column(Integer)
    month_name = Column(String(10))
    quarter = Column(Integer)
    year = Column(Integer)
    is_weekend = Column(Boolean)
    is_holiday = Column(Boolean)
    fiscal_year = Column(Integer)
    fiscal_quarter = Column(Integer)
    fiscal_month = Column(Integer)

class DimPaymentMethod(Base):
    __tablename__ = 'dim_payment_method'
    
    payment_method_key = Column(Integer, primary_key=True, autoincrement=True)
    payment_method = Column(Enum('auto_pay', 'online', 'phone', 'mail', 'branch', name='payment_method'))
    payment_channel = Column(String(20))  # Derived: 'Digital', 'Traditional'
    convenience_score = Column(Integer)  # Derived: 1-5 scale

# Fact Tables
class FactPayment(Base):
    __tablename__ = 'fact_payment'
    
    payment_key = Column(Integer, primary_key=True, autoincrement=True)
    member_key = Column(Integer, ForeignKey('dim_member.member_key'), nullable=False)
    card_key = Column(Integer, ForeignKey('dim_credit_card.card_key'), nullable=False)
    payment_date_key = Column(Integer, ForeignKey('dim_date.date_key'), nullable=False)
    payment_method_key = Column(Integer, ForeignKey('dim_payment_method.payment_method_key'), nullable=False)
    
    # Measures
    payment_amount = Column(DECIMAL(10, 2), nullable=False)
    minimum_due = Column(DECIMAL(10, 2), nullable=False)
    statement_balance = Column(DECIMAL(10, 2))
    late_fee = Column(DECIMAL(6, 2), default=0.00)
    days_late = Column(Integer, default=0)
    
    # Derived measures
    payment_ratio = Column(DECIMAL(5, 4))  # payment_amount / minimum_due
    excess_payment = Column(DECIMAL(10, 2))  # payment_amount - minimum_due
    
    # Flags
    is_on_time = Column(Boolean)
    is_full_payment = Column(Boolean)  # payment >= statement_balance
    is_minimum_payment = Column(Boolean)  # payment >= minimum_due
    is_over_payment = Column(Boolean)  # payment > statement_balance
    
    payment_status = Column(String(10), nullable=False)  # 'on_time', 'late', 'missed', 'partial'
    created_datetime = Column(TIMESTAMP, server_default=func.current_timestamp())

class FactFinancialHealth(Base):
    __tablename__ = 'fact_financial_health'
    
    health_key = Column(Integer, primary_key=True, autoincrement=True)
    member_key = Column(Integer, ForeignKey('dim_member.member_key'), nullable=False)
    assessment_date_key = Column(Integer, ForeignKey('dim_date.date_key'), nullable=False)
    
    # Measures
    credit_score = Column(Integer)
    debt_to_income_ratio = Column(DECIMAL(5, 4))
    credit_utilization_ratio = Column(DECIMAL(5, 4))
    payment_reliability_score = Column(DECIMAL(5, 2))
    savings_balance = Column(DECIMAL(12, 2))
    checking_balance = Column(DECIMAL(12, 2))
    total_debt = Column(DECIMAL(12, 2))
    number_of_accounts = Column(Integer)
    recent_inquiries = Column(Integer)
    delinquent_accounts = Column(Integer)
    health_score = Column(DECIMAL(5, 2))
    
    # Derived measures
    total_liquid_assets = Column(DECIMAL(12, 2))  # savings + checking
    debt_to_assets_ratio = Column(DECIMAL(5, 4))  # total_debt / total_liquid_assets
    net_worth = Column(DECIMAL(12, 2))  # total_liquid_assets - total_debt
    
    # Categorical measures
    risk_category = Column(String(10))  # 'low', 'medium', 'high'
    credit_score_tier = Column(String(12))  # Derived: 'Excellent', 'Good', 'Fair', 'Poor'
    utilization_tier = Column(String(12))  # Derived: 'Low', 'Medium', 'High', 'Maxed'
    
    created_datetime = Column(TIMESTAMP, server_default=func.current_timestamp())

class FactProductRecommendation(Base):
    __tablename__ = 'fact_product_recommendation'
    
    recommendation_key = Column(Integer, primary_key=True, autoincrement=True)
    member_key = Column(Integer, ForeignKey('dim_member.member_key'), nullable=False)
    product_key = Column(Integer, ForeignKey('dim_financial_product.product_key'), nullable=False)
    recommendation_date_key = Column(Integer, ForeignKey('dim_date.date_key'), nullable=False)
    expires_date_key = Column(Integer, ForeignKey('dim_date.date_key'))
    
    # Measures
    recommendation_score = Column(DECIMAL(5, 2))
    member_health_score = Column(DECIMAL(5, 2))
    credit_utilization_at_time = Column(DECIMAL(5, 4))
    payment_reliability_at_time = Column(DECIMAL(5, 2))
    
    # Derived measures
    recommendation_tier = Column(String(20))  # Derived from score: 'High', 'Medium', 'Low'
    days_to_expiry = Column(Integer)  # Calculated from expires_at
    
    # Flags
    is_expired = Column(Boolean)
    is_high_confidence = Column(Boolean)  # recommendation_score > 80
    
    recommendation_status = Column(String(10))  # 'pending', 'accepted', 'declined', 'expired'
    
    created_datetime = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_datetime = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

class FactCreditCardBalance(Base):
    __tablename__ = 'fact_credit_card_balance'
    
    balance_key = Column(Integer, primary_key=True, autoincrement=True)
    member_key = Column(Integer, ForeignKey('dim_member.member_key'), nullable=False)
    card_key = Column(Integer, ForeignKey('dim_credit_card.card_key'), nullable=False)
    snapshot_date_key = Column(Integer, ForeignKey('dim_date.date_key'), nullable=False)
    
    # Measures
    credit_limit = Column(DECIMAL(10, 2))
    current_balance = Column(DECIMAL(10, 2))
    available_credit = Column(DECIMAL(10, 2))
    minimum_payment = Column(DECIMAL(8, 2))
    
    # Derived measures
    utilization_ratio = Column(DECIMAL(5, 4))  # current_balance / credit_limit
    utilization_tier = Column(String(12))  # Derived: 'Low', 'Medium', 'High', 'Maxed'
    balance_trend = Column(String(20))  # Derived: 'Increasing', 'Decreasing', 'Stable'
    
    # Flags
    is_over_limit = Column(Boolean)
    is_high_utilization = Column(Boolean)  # > 80%
    is_maxed_out = Column(Boolean)  # > 95%
    
    created_datetime = Column(TIMESTAMP, server_default=func.current_timestamp())

class Member(Base):
    __tablename__ = "members"

    member_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    address = Column(String(255), nullable=False)
    city = Column(String(50), nullable=False)
    state = Column(String(50), nullable=False)
    zip_code = Column(String(10), nullable=False)

    # credit_cards = relationship("CreditCard", back_populates="member")
    # payments = relationship("PaymentHistory", back_populates="member")
    # financial_metrics = relationship("FinancialHealthMetric", back_populates="member")
    #financial_products = relationship("FinancialProduct", back_populates="member")
