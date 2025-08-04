from typing import Dict, List, Any

def transform_recommendation_to_mongodb_format(member_record: Dict[str, Any]) -> Dict[str, Any]:
    """Transform your recommendation JSON format to MongoDB format expected by the team"""
    
    member_info = member_record["member_info"]
    recommendations = member_record["recommendations"]
    metadata = member_record["processing_metadata"]
    
    # Create customer profile with required name field
    customer_profile = {
        "name": f"Member {member_record['member_id']}",
        "annual_income": member_info["annual_income"],
        "credit_score": member_info["credit_score"], 
        "health_score": member_info["health_score"],
        "risk_category": member_info["risk_category"],
        "utilization_ratio": member_info["utilization_ratio"]
    }
    
    # Transform recommendations to match expected schema
    transformed_recommendations = []
    for rec in recommendations:
        transformed_rec = {
            "rank": rec["rank"],
            "product_name": rec["product_name"],
            "product_type": rec["product_type"],
            "score": rec["score"],
            "max_score": 100.0,
            "confidence": rec["probability"] * 100.0,
            "reason": rec["reasons"]
        }
        transformed_recommendations.append(transformed_rec)
    
    # Create the MongoDB document in expected format
    mongo_document = {
        "customer_id": str(member_record["member_id"]),
        "customer_profile": customer_profile,
        "recommendations": transformed_recommendations,
        "created_at": metadata["generated_date"],
        "updated_at": metadata["generated_date"]
    }
    
    return mongo_document

def transform_batch_to_mongodb_format(recommendations_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Transform a batch of recommendations to MongoDB format"""
    return [transform_recommendation_to_mongodb_format(rec) for rec in recommendations_batch]
