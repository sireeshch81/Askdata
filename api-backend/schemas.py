# schemas.py - Extended with DW ML classes
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


# EXISTING RULE-BASED SCHEMAS
class CustomerProfile(BaseModel):
    """Customer profile data structure for RULE-BASED recommendations"""
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
    """Complete recommendation document structure for MongoDB (RULE-BASED)"""
    customer_id: str
    customer_profile: CustomerProfile
    recommendations: List[Recommendation]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for MongoDB insertion, excluding None values"""
        return self.dict(exclude_none=True)


# NEW DW ML-BASED SCHEMAS
class DWCustomerProfile(BaseModel):
    """Enhanced customer profile from DW for ML-BASED recommendations"""
    name: str
    annual_income: float
    credit_score: int
    health_score: float
    risk_category: str
    utilization_ratio: float
    
    # Enhanced DW-specific fields
    member_tenure_months: int = Field(..., description="Months since becoming member")
    age_group: str = Field(..., description="Age group category")
    income_bracket: str = Field(..., description="Income bracket category")
    employment_status: str = Field(..., description="Employment status")
    
    # Financial behavior patterns
    payment_trend: str = Field(..., description="Payment behavior trend: improving/stable/declining")
    utilization_trend: str = Field(..., description="Credit utilization trend")
    financial_stability_score: float = Field(..., description="ML-calculated stability score")
    creditworthiness_score: float = Field(..., description="ML-calculated creditworthiness")
    product_readiness_score: float = Field(..., description="Likelihood to accept new products")
    
    # Product interaction history
    total_products_owned: int = Field(default=0, description="Total financial products owned")
    recommendation_acceptance_rate: float = Field(default=0.0, description="Historical acceptance rate")


class MLRecommendation(BaseModel):
    """ML-generated product recommendation with enhanced metadata"""
    rank: int
    product_name: str
    product_type: str
    score: float
    max_score: float
    confidence: float
    reason: str
    
    # ML-specific metadata
    similarity_score: Optional[float] = Field(None, description="Customer similarity score")
    cluster_id: Optional[int] = Field(None, description="Customer cluster assignment")
    feature_importance: Optional[Dict[str, float]] = Field(None, description="Key feature influences")


class DWRecommendationDocument(BaseModel):
    """Complete ML recommendation document from DW data"""
    customer_id: str
    customer_profile: DWCustomerProfile
    recommendations: List[MLRecommendation]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # ML pipeline metadata
    ml_metadata: Dict[str, Any] = Field(default_factory=dict, description="ML model metadata")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for MongoDB insertion, excluding None values"""
        result = self.dict(exclude_none=True)
        
        # Add system metadata
        result['algorithm_type'] = 'ml_similarity'
        result['data_source'] = 'dw'
        
        # Ensure ml_metadata has default values
        if 'ml_metadata' not in result:
            result['ml_metadata'] = {}
        
        result['ml_metadata'].update({
            'model_version': '1.0.0',
            'feature_count': 20,
            'processing_timestamp': datetime.utcnow().isoformat()
        })
        
        return result


class MLModelMetadata(BaseModel):
    """Metadata for tracking ML model performance"""
    model_name: str
    version: str
    algorithm_type: str
    training_date: datetime
    training_data_size: int
    performance_metrics: Dict[str, float]
    feature_importance: Dict[str, float]
    model_parameters: Dict[str, Any]
    status: str  # "active", "deprecated", "training"


# RESPONSE SCHEMAS
class RecommendationsResponse(BaseModel):
    """Response schema for customer recommendations (rule-based)"""
    customer_id: str
    customer_profile: CustomerProfile
    recommendations: List[Recommendation]
    created_at: datetime
    updated_at: datetime


class DWRecommendationsResponse(BaseModel):
    """Response schema for ML customer recommendations (DW-based)"""
    customer_id: str
    customer_profile: DWCustomerProfile
    recommendations: List[MLRecommendation]
    created_at: datetime
    updated_at: datetime
    ml_metadata: Dict[str, Any]


class RecommendationComparison(BaseModel):
    """Schema for comparing rule-based vs ML recommendations"""
    customer_id: str
    rule_based_recommendations: List[Recommendation]
    ml_based_recommendations: List[MLRecommendation]
    comparison_metrics: Dict[str, Any]
    created_at: datetime

class ProductsResponse(BaseModel):
    """Response schema for financial products"""
    product_id: int
    product_name: str
    product_type: Optional[str] = None
    product_category: Optional[str] = None
    interest_rate: Optional[float] = None
    credit_limit_min: Optional[float] = None
    credit_limit_max: Optional[float] = None
    minimum_income_required: Optional[float] = None
    minimum_credit_score: Optional[int] = None
    maximum_debt_to_income: Optional[float] = None
    annual_fee: Optional[float] = None
    rewards_program: Optional[str] = None
    benefits: Optional[str] = None
    eligibility_criteria: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
