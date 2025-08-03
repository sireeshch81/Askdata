from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class CustomerDetail(BaseModel):
    customer_id: str = Field(..., description="Unique identifier for the customer")
    first_name: str = Field(..., description="Customer's first name")
    last_name: str = Field(..., description="Customer's last name")
    email: str = Field(..., description="Customer's email address")
    phone: Optional[str] = Field(None, description="Customer's phone number")
    date_of_birth: Optional[date] = Field(None, description="Customer's date of birth")

class Recommendation(BaseModel):
    product_id: str = Field(..., description="ID of the recommended product")
    product_name: str = Field(..., description="Name of the recommended product")
    score: float = Field(..., description="Recommendation confidence score")

class RecommendationsResponse(BaseModel):
    customer_id: str = Field(..., description="ID of the customer for recommendations")
    recommendations: List[Recommendation] = Field(..., description="List of product recommendations")

class AuthRequest(BaseModel):
    username: str = Field(..., description="Username for authentication")
    password: str = Field(..., description="Password for authentication")

class AuthResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Type of the token")

class AuthErrorResponse(BaseModel):
    detail: str = Field(..., description="Error message details")
