# models.py

from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base

class Member(Base):
    __tablename__ = "members"

    member_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    date_of_birth = Column(Date, nullable=True)

    credit_cards = relationship("CreditCard", back_populates="member")
    payments = relationship("PaymentHistory", back_populates="member")
    financial_metrics = relationship("FinancialHealthMetric", back_populates="member")
    #financial_products = relationship("FinancialProduct", back_populates="member")


class CreditCard(Base):
    __tablename__ = "credit_cards"

    card_id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.member_id"))
    card_number = Column(String(20), unique=True, nullable=False)
    card_type = Column(String(50))
    expiry_date = Column(Date)

    member = relationship("Member", back_populates="credit_cards")


class PaymentHistory(Base):
    __tablename__ = "payment_history"

    payment_id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.member_id"))
    payment_date = Column(DateTime)
    amount = Column(Float)
    description = Column(String(255))

    member = relationship("Member", back_populates="payments")


class FinancialHealthMetric(Base):
    __tablename__ = "financial_health_metrics"

    metric_id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.member_id"))
    metric_name = Column(String(100))
    metric_value = Column(Float)
    recorded_date = Column(DateTime)

    member = relationship("Member", back_populates="financial_metrics")


class FinancialProduct(Base):
    __tablename__ = "financial_products"

    product_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_name = Column(String(100), nullable=False)
    product_type = Column(String(50))  # Enum in DB, use String here or SQLAlchemy Enum if you want
    product_category = Column(String(50))  # Enum in DB, use String here or SQLAlchemy Enum if you want
    interest_rate = Column(Float(precision=4))
    credit_limit_min = Column(Float)
    credit_limit_max = Column(Float)
    minimum_income_required = Column(Float)
    minimum_credit_score = Column(Integer)
    maximum_debt_to_income = Column(Float(precision=4))
    annual_fee = Column(Float)
    rewards_program = Column(String(100))
    benefits = Column(String)  # Use Text if you want: from sqlalchemy import Text
    eligibility_criteria = Column(String)  # Use Text if you want
    is_active = Column(Integer)  # tinyint(1) in MySQL; use Boolean if you want: Column(Boolean)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    #member = relationship("Member", back_populates="financial_products")
