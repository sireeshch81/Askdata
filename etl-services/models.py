from sqlalchemy import (
    Column, Integer, String, Date, DECIMAL, Enum, ForeignKey, Boolean, TIMESTAMP, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# OLTP MODELS
class OltpMember(Base):
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
    employment_status = Column(Enum('employed', 'self_employed', 'unemployed', 'retired', name='employment_status'))
    member_since = Column(Date)
    member_status = Column(Enum('active', 'inactive', 'suspended', name='member_status'), default='active')
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    credit_cards = relationship('OltpCreditCard', back_populates='member')
    payments = relationship('OltpPaymentHistory', back_populates='member')

class OltpCreditCard(Base):
    __tablename__ = 'credit_cards'
    card_id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey('members.member_id'), nullable=False)
    card_number = Column(String(16), nullable=False)
    card_type = Column(Enum('visa', 'mastercard', 'amex', 'discover', name='card_type'))
    credit_limit = Column(DECIMAL(10,2), nullable=False)
    current_balance = Column(DECIMAL(10,2), default=0.00)
    apr_rate = Column(DECIMAL(5,4))
    minimum_payment = Column(DECIMAL(8,2))
    payment_due_date = Column(Date)
    card_status = Column(Enum('active', 'blocked', 'expired', 'closed', name='card_status'), default='active')
    issue_date = Column(Date)
    expiry_date = Column(Date)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    member = relationship('OltpMember', back_populates='credit_cards')
    payments = relationship('OltpPaymentHistory', back_populates='credit_card')

class OltpPaymentHistory(Base):
    __tablename__ = 'payment_history'
    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey('members.member_id'), nullable=False)
    card_id = Column(Integer, ForeignKey('credit_cards.card_id'), nullable=False)
    payment_date = Column(Date, nullable=False)
    payment_amount = Column(DECIMAL(10,2), nullable=False)
    minimum_due = Column(DECIMAL(10,2), nullable=False)
    payment_status = Column(Enum('on_time', 'late', 'missed', 'partial', name='payment_status'), nullable=False)
    days_late = Column(Integer, default=0)
    member = relationship('OltpMember', back_populates='payments')
    credit_card = relationship('OltpCreditCard', back_populates='payments')

# DW MODELS
class DwMember(Base):
    __tablename__ = 'dim_member'
    member_key = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100))
    phone = Column(String(15))
    date_of_birth = Column(Date)
    age_group = Column(String(20))
    address = Column(String(255))
    city = Column(String(50))
    state = Column(String(50))
    zip_code = Column(String(10))
    region = Column(String(50))
    annual_income = Column(DECIMAL(12,2))
    income_bracket = Column(String(20))
    employment_status = Column(Enum('employed', 'self_employed', 'unemployed', 'retired', name='dw_employment_status'))
    member_since = Column(Date)
    member_tenure_years = Column(Integer)
    member_status = Column(Enum('active', 'inactive', 'suspended', name='dw_member_status'))
    effective_date = Column(Date)
    expiry_date = Column(Date)
    is_current = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

class DwCreditCard(Base):
    __tablename__ = 'dim_credit_card'
    card_key = Column(Integer, primary_key=True, autoincrement=True)
    card_id = Column(Integer, nullable=False)
    member_key = Column(Integer, nullable=False)
    card_type = Column(Enum('visa', 'mastercard', 'amex', 'discover', name='dw_card_type'))
    credit_limit = Column(DECIMAL(10,2))
    credit_limit_tier = Column(String(20))
    apr_rate = Column(DECIMAL(5,4))
    apr_category = Column(String(20))
    card_status = Column(Enum('active', 'blocked', 'expired', 'closed', name='dw_card_status'))
    issue_date = Column(Date)
    expiry_date = Column(Date)
    card_age_months = Column(Integer)
    effective_date = Column(Date)
    expiry_date_scd = Column(Date)
    is_current = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

