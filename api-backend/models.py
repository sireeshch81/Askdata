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
    financial_products = relationship("FinancialProduct", back_populates="member")


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

    product_id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.member_id"))
    product_name = Column(String(100))
    product_type = Column(String(50))
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)

    member = relationship("Member", back_populates="financial_products")
