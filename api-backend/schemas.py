from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date, datetime


class CustomerDetail(BaseModel):
    """Customer details schema"""
    customer_id: str = Field(..., description="Unique identifier for the customer")
    first_name: str = Field(..., description="Customer's first name")
    last_name: str = Field(..., description="Customer's last name")
    email: str = Field(..., description="Customer's email address")
    phone: Optional[str] = Field(None, description="Customer's phone number")
    date_of_birth: Optional[date] = Field(None, description="Customer's date of birth")


class AuthRequest(BaseModel):
    """Request model for authentication"""
    username: str = Field(..., description="Username for authentication")
    password: str = Field(..., description="Password for authentication")


class AuthResponse(BaseModel):
    """Response model for successful authentication"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Type of the token")


class AuthErrorResponse(BaseModel):
    """Response model for authentication errors"""
    detail: str = Field(..., description="Error message details")


class CustomerProfile(BaseModel):
    """Customer profile data structure for recommendations"""
    name: str
    annual_income: float
    credit_score: int
    health_score: float
    risk_category: str
    utilization_ratio: float


class Recommendation(BaseModel):
    """Individual product recommendation data structure"""
    rank: int
    product_name: str
    product_type: str
    score: float
    max_score: float
    confidence: float
    reason: str


class RecommendationDocument(BaseModel):
    """Complete recommendation document structure for MongoDB"""
    customer_id: str
    customer_profile: CustomerProfile
    recommendations: List[Recommendation]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for MongoDB insertion, excluding None values"""
        return self.dict(exclude_none=True)


class RecommendationsResponse(BaseModel):
    """Response schema for customer recommendations"""
    customer_id: str
    customer_profile: CustomerProfile
    recommendations: List[Recommendation]
    created_at: datetime
    updated_at: datetime
