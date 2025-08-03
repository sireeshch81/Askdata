from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date
from dataclasses import dataclass, asdict

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

"""
Data models for recommendation service MongoDB operations.
This module provides Python objects and functions to work with recommendation data.
"""
from dataclasses import dataclass, asdict
from typing import List, Dict, Any


@dataclass
class CustomerProfile:
    """Customer profile data structure"""
    name: str
    annual_income: float
    credit_score: int
    health_score: float
    risk_category: str
    utilization_ratio: float


@dataclass
class Recommendation:
    """Individual recommendation data structure"""
    rank: int
    product_name: str
    product_type: str
    score: float
    max_score: float
    confidence: float
    reason: str


@dataclass
class RecommendationDocument:
    """Complete recommendation document structure for MongoDB"""
    customer_id: str
    customer_profile: CustomerProfile
    recommendations: List[Recommendation]
    created_at: str
    updated_at: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert the document to a dictionary for MongoDB insertion"""
        return {
            "customer_id": self.customer_id,
            "customer_profile": asdict(self.customer_profile),
            "recommendations": [asdict(rec) for rec in self.recommendations],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
