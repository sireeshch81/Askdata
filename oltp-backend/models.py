from sqlalchemy import (
    Column, Integer, String, Date, DECIMAL, Enum, ForeignKey, Boolean, 
    TIMESTAMP, func, Text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Member(Base):
    __tablename__ = 'members'
    member_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(15))
    date_of_birth = Column(Date)
    address = Column(String(255))
    city = Column(String(50))
    state = Column(String(50))
    zip_code = Column(String(10))
    annual_income = Column(DECIMAL(12,2))
    employment_status = Column(Enum('employed', 'self_employed', 'unemployed', 'retired'))
    member_since = Column(Date)
    member_status = Column(Enum('active', 'inactive', 'suspended'), default='active')
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    credit_cards = relationship('CreditCard', back_populates='member', cascade="all, delete-orphan")
    payment_history = relationship('PaymentHistory', back_populates='member', cascade="all, delete-orphan")
    health_metrics = relationship('FinancialHealthMetric', back_populates='member', cascade="all, delete-orphan")

class CreditCard(Base):
    __tablename__ = 'credit_cards'
    card_id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey('members.member_id', ondelete='CASCADE'), nullable=False)
    card_number = Column(String(16), nullable=False)
    card_type = Column(Enum('visa', 'mastercard', 'amex', 'discover'))
    credit_limit = Column(DECIMAL(10,2), nullable=False)
    current_balance = Column(DECIMAL(10,2), default=0.00)
    apr_rate = Column(DECIMAL(5,4))
    minimum_payment = Column(DECIMAL(8,2))
    payment_due_date = Column(Date)
    card_status = Column(Enum('active', 'blocked', 'expired', 'closed'), default='active')
    issue_date = Column(Date)
    expiry_date = Column(Date)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    member = relationship('Member', back_populates='credit_cards')
    payment_history = relationship('PaymentHistory', back_populates='credit_card', cascade="all, delete-orphan")

class PaymentHistory(Base):
    __tablename__ = 'payment_history'
    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey('members.member_id', ondelete='CASCADE'), nullable=False)
    card_id = Column(Integer, ForeignKey('credit_cards.card_id', ondelete='CASCADE'), nullable=False)
    payment_date = Column(Date, nullable=False)
    payment_amount = Column(DECIMAL(10,2), nullable=False)
    minimum_due = Column(DECIMAL(10,2), nullable=False)
    payment_status = Column(Enum('on_time', 'late', 'missed', 'partial'), nullable=False)
    days_late = Column(Integer, default=0)
    late_fee = Column(DECIMAL(6,2), default=0.00)
    statement_balance = Column(DECIMAL(10,2))
    payment_method = Column(Enum('auto_pay', 'online', 'phone', 'mail', 'branch'))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    member = relationship('Member', back_populates='payment_history')
    credit_card = relationship('CreditCard', back_populates='payment_history')

class FinancialHealthMetric(Base):
    __tablename__ = 'financial_health_metrics'
    metric_id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey('members.member_id', ondelete='CASCADE'), nullable=False)
    assessment_date = Column(Date, nullable=False)
    credit_score = Column(Integer)
    debt_to_income_ratio = Column(DECIMAL(5,4))
    credit_utilization_ratio = Column(DECIMAL(5,4))
    payment_reliability_score = Column(DECIMAL(5,2))
    savings_balance = Column(DECIMAL(12,2))
    checking_balance = Column(DECIMAL(12,2))
    total_debt = Column(DECIMAL(12,2))
    number_of_accounts = Column(Integer)
    recent_inquiries = Column(Integer)
    delinquent_accounts = Column(Integer)
    health_score = Column(DECIMAL(5,2))
    risk_category = Column(Enum('low', 'medium', 'high'))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    member = relationship('Member', back_populates='health_metrics')

class FinancialProduct(Base):
    __tablename__ = 'financial_products'
    product_id = Column(Integer, primary_key=True, autoincrement=True)
    product_name = Column(String(100), nullable=False)
    product_type = Column(Enum('credit_card', 'personal_loan', 'mortgage', 'savings_account', 'cd', 'investment'))
    product_category = Column(Enum('premium', 'standard', 'basic', 'secured'))
    interest_rate = Column(DECIMAL(5,4))
    credit_limit_min = Column(DECIMAL(10,2))
    credit_limit_max = Column(DECIMAL(10,2))
    minimum_income_required = Column(DECIMAL(10,2))
    minimum_credit_score = Column(Integer)
    maximum_debt_to_income = Column(DECIMAL(5,4))
    annual_fee = Column(DECIMAL(6,2), default=0.00)
    rewards_program = Column(String(100))
    benefits = Column(Text)
    eligibility_criteria = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
