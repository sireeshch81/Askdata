from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class CustomerDetail(BaseModel):
    customer_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    date_of_birth: date

class Recommendation(BaseModel):
    product_id: str
    product_name: str
    score: float

class RecommendationsResponse(BaseModel):
    customer_id: str
    recommendations: List[Recommendation]

class AuthRequest(BaseModel):
    username: str
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class AuthErrorResponse(BaseModel):
    detail: str

