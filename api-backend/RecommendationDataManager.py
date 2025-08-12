# RecommendationDataManager.py - Extended for ML recommendations
#!/usr/bin/env python3

from datetime import datetime
from typing import List, Optional, Dict, Any
from pymongo.collection import Collection
from mongo_connection import get_mongodb_collection
from schemas import (
    CustomerProfile, Recommendation, RecommendationDocument,
    DWCustomerProfile, MLRecommendation, DWRecommendationDocument,
    MLModelMetadata
)
import uuid
import json
import logging

logger = logging.getLogger(__name__)

class RecommendationDataManager:
    """Enhanced manager class for both rule-based and ML recommendation data operations"""

    def __init__(self, rule_collection_name: str = "recommendations", ml_collection_name: str = "ml_recommendations"):
        # Collection names
        self.rule_collection_name = rule_collection_name
        self.ml_collection_name = ml_collection_name
        
        # Collections (lazy initialization)
        self.rule_collection: Optional[Collection] = None
        self.ml_collection: Optional[Collection] = None
        self.metadata_collection: Optional[Collection] = None

    # RULE-BASED METHODS (Your existing methods)
    def get_rule_collection(self) -> Collection:
        """Get rule-based recommendations MongoDB collection"""
        if self.rule_collection is None:
            self.rule_collection = get_mongodb_collection(self.rule_collection_name)
        return self.rule_collection

    def create_recommendation_from_json(self, json_data: Dict[str, Any]) -> RecommendationDocument:
        """Create a RecommendationDocument from JSON data (EXISTING METHOD)"""
        # Create customer profile
        customer_profile_data = json_data["customer_profile"]
        customer_profile = CustomerProfile(
            name=customer_profile_data["name"],
            annual_income=customer_profile_data["annual_income"],
            credit_score=customer_profile_data["credit_score"],
            health_score=customer_profile_data["health_score"],
            risk_category=customer_profile_data["risk_category"],
            utilization_ratio=customer_profile_data["utilization_ratio"]
        )

        # Create recommendations list
        recommendations = []
        for rec_data in json_data["recommendations"]:
            recommendation = Recommendation(
                rank=rec_data["rank"],
                product_name=rec_data["product_name"],
                product_type=rec_data["product_type"],
                score=rec_data["score"],
                max_score=rec_data["max_score"],
                confidence=rec_data["confidence"],
                reason=rec_data["reason"]
            )
            recommendations.append(recommendation)

        # Create the complete document
        document = RecommendationDocument(
            customer_id=json_data["customer_id"],
            customer_profile=customer_profile,
            recommendations=recommendations,
            created_at=json_data["created_at"],
            updated_at=json_data["updated_at"]
        )

        return document

    def insert_recommendation(self, document: RecommendationDocument) -> str:
        """Insert a rule-based recommendation document into MongoDB (EXISTING METHOD)"""
        collection = self.get_rule_collection()
        doc_dict = document.to_dict()
        # Add metadata to distinguish from ML recommendations
        doc_dict['algorithm_type'] = 'rule_based'
        doc_dict['data_source'] = 'oltp'
        
        result = collection.insert_one(doc_dict)
        return str(result.inserted_id)

    def insert_recommendation_from_json(self, json_data: Dict[str, Any]) -> str:
        """Insert a rule-based recommendation document from JSON data (EXISTING METHOD)"""
        document = self.create_recommendation_from_json(json_data)
        return self.insert_recommendation(document)

    def find_by_customer_id(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Find a rule-based recommendation document by customer ID (EXISTING METHOD)"""
        collection = self.get_rule_collection()
        return collection.find_one({"customer_id": customer_id})

    def find_all_recommendations(self) -> List[Dict[str, Any]]:
        """Find all rule-based recommendation documents (EXISTING METHOD)"""
        collection = self.get_rule_collection()
        return list(collection.find())

    def update_recommendation(self, customer_id: str, updated_data: Dict[str, Any]) -> bool:
        """Update a rule-based recommendation document (EXISTING METHOD)"""
        collection = self.get_rule_collection()
        result = collection.update_one(
            {"customer_id": customer_id},
            {"$set": updated_data}
        )
        return result.modified_count > 0

    def delete_recommendation(self, customer_id: str) -> bool:
        """Delete a rule-based recommendation document (EXISTING METHOD)"""
        collection = self.get_rule_collection()
        result = collection.delete_one({"customer_id": customer_id})
        return result.deleted_count > 0

    # NEW ML-BASED METHODS
    def get_ml_collection(self) -> Collection:
        """Get ML recommendations MongoDB collection"""
        if self.ml_collection is None:
            self.ml_collection = get_mongodb_collection(self.ml_collection_name)
        return self.ml_collection
    
    def get_metadata_collection(self) -> Collection:
        """Get ML model metadata collection"""
        if self.metadata_collection is None:
            self.metadata_collection = get_mongodb_collection("ml_model_metadata")
        return self.metadata_collection

    def create_dw_recommendation_from_json(self, json_data: Dict[str, Any]) -> DWRecommendationDocument:
        """Create a DWRecommendationDocument from JSON data"""
        # Create enhanced customer profile
        customer_profile_data = json_data["customer_profile"]
        customer_profile = DWCustomerProfile(
            name=customer_profile_data["name"],
            annual_income=customer_profile_data["annual_income"],
            credit_score=customer_profile_data["credit_score"],
            health_score=customer_profile_data["health_score"],
            risk_category=customer_profile_data["risk_category"],
            utilization_ratio=customer_profile_data["utilization_ratio"],
            
            # Enhanced DW fields
            member_tenure_months=customer_profile_data.get("member_tenure_months", 12),
            age_group=customer_profile_data.get("age_group", "26-35"),
            income_bracket=customer_profile_data.get("income_bracket", "Medium"),
            employment_status=customer_profile_data.get("employment_status", "employed"),
            payment_trend=customer_profile_data.get("payment_trend", "stable"),
            utilization_trend=customer_profile_data.get("utilization_trend", "stable"),
            financial_stability_score=customer_profile_data.get("financial_stability_score", 75.0),
            creditworthiness_score=customer_profile_data.get("creditworthiness_score", 75.0),
            product_readiness_score=customer_profile_data.get("product_readiness_score", 75.0),
            total_products_owned=customer_profile_data.get("total_products_owned", 1),
            recommendation_acceptance_rate=customer_profile_data.get("recommendation_acceptance_rate", 0.0)
        )

        # Create ML recommendations list
        recommendations = []
        for rec_data in json_data["recommendations"]:
            recommendation = MLRecommendation(
                rank=rec_data["rank"],
                product_name=rec_data["product_name"],
                product_type=rec_data["product_type"],
                score=rec_data["score"],
                max_score=rec_data["max_score"],
                confidence=rec_data["confidence"],
                reason=rec_data["reason"],
                similarity_score=rec_data.get("similarity_score"),
                cluster_id=rec_data.get("cluster_id"),
                feature_importance=rec_data.get("feature_importance")
            )
            recommendations.append(recommendation)

        # Create the complete ML document
        document = DWRecommendationDocument(
            customer_id=json_data["customer_id"],
            customer_profile=customer_profile,
            recommendations=recommendations,
            created_at=json_data.get("created_at"),
            updated_at=json_data.get("updated_at"),
            ml_metadata=json_data.get("ml_metadata", {})
        )

        return document

    def insert_ml_recommendation(self, document: DWRecommendationDocument) -> str:
        """Insert an ML recommendation document into MongoDB"""
        collection = self.get_ml_collection()
        doc_dict = document.to_dict()
        
        # Use upsert to replace existing ML recommendation for the customer
        result = collection.replace_one(
            {"customer_id": doc_dict["customer_id"]},
            doc_dict,
            upsert=True
        )
        
        if result.upserted_id:
            logger.info(f"Inserted new ML recommendation for customer {doc_dict['customer_id']}")
            return str(result.upserted_id)
        else:
            logger.info(f"Updated existing ML recommendation for customer {doc_dict['customer_id']}")
            return doc_dict["customer_id"]

    def insert_ml_recommendation_from_json(self, json_data: Dict[str, Any]) -> str:
        """Insert an ML recommendation document from JSON data"""
        document = self.create_dw_recommendation_from_json(json_data)
        return self.insert_ml_recommendation(document)

    def find_ml_by_customer_id(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Find an ML recommendation document by customer ID"""
        collection = self.get_ml_collection()
        return collection.find_one({"customer_id": customer_id})

    def find_all_ml_recommendations(self) -> List[Dict[str, Any]]:
        """Find all ML recommendation documents"""
        collection = self.get_ml_collection()
        return list(collection.find())

    def update_ml_recommendation(self, customer_id: str, updated_data: Dict[str, Any]) -> bool:
        """Update an ML recommendation document"""
        collection = self.get_ml_collection()
        updated_data['updated_at'] = datetime.utcnow()
        result = collection.update_one(
            {"customer_id": customer_id},
            {"$set": updated_data}
        )
        return result.modified_count > 0

    def delete_ml_recommendation(self, customer_id: str) -> bool:
        """Delete an ML recommendation document"""
        collection = self.get_ml_collection()
        result = collection.delete_one({"customer_id": customer_id})
        return result.deleted_count > 0

    # COMPARISON AND ANALYTICS METHODS
    def get_recommendations_comparison(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get both rule-based and ML recommendations for comparison"""
        rule_rec = self.find_by_customer_id(customer_id)
        ml_rec = self.find_ml_by_customer_id(customer_id)
        
        if not rule_rec and not ml_rec:
            return None
        
        return {
            "customer_id": customer_id,
            "rule_based": rule_rec,
            "ml_based": ml_rec,
            "comparison_timestamp": datetime.utcnow()
        }

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about both recommendation collections"""
        rule_collection = self.get_rule_collection()
        ml_collection = self.get_ml_collection()
        
        rule_count = rule_collection.count_documents({})
        ml_count = ml_collection.count_documents({})
        
        # Get latest timestamps
        rule_latest = rule_collection.find_one(
            {}, sort=[("created_at", -1)]
        )
        ml_latest = ml_collection.find_one(
            {}, sort=[("created_at", -1)]
        )
        
        return {
            "rule_based_count": rule_count,
            "ml_based_count": ml_count,
            "rule_latest_created": rule_latest.get("created_at") if rule_latest else None,
            "ml_latest_created": ml_latest.get("created_at") if ml_latest else None,
            "total_unique_customers": len(set(
                [doc["customer_id"] for doc in rule_collection.find({}, {"customer_id": 1})] +
                [doc["customer_id"] for doc in ml_collection.find({}, {"customer_id": 1})]
            ))
        }

    # ML MODEL METADATA METHODS
    def save_model_metadata(self, metadata: MLModelMetadata) -> str:
        """Save ML model metadata"""
        collection = self.get_metadata_collection()
        doc_dict = metadata.dict()
        doc_dict['created_at'] = datetime.utcnow()
        
        # Use upsert based on model name and version
        result = collection.replace_one(
            {"model_name": metadata.model_name, "version": metadata.version},
            doc_dict,
            upsert=True
        )
        
        return str(result.upserted_id) if result.upserted_id else "updated"

    def get_latest_model_metadata(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get latest metadata for a model"""
        collection = self.get_metadata_collection()
        return collection.find_one(
            {"model_name": model_name},
            sort=[("created_at", -1)]
        )

    def cleanup_old_recommendations(self, days_old: int = 30, collection_type: str = "both") -> Dict[str, int]:
        """Clean up old recommendations"""
        cutoff_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_old)
        
        cleanup_results = {}
        
        if collection_type in ["rule", "both"]:
            rule_result = self.get_rule_collection().delete_many({
                "created_at": {"$lt": cutoff_date}
            })
            cleanup_results["rule_based_deleted"] = rule_result.deleted_count
        
        if collection_type in ["ml", "both"]:
            ml_result = self.get_ml_collection().delete_many({
                "created_at": {"$lt": cutoff_date}
            })
            cleanup_results["ml_based_deleted"] = ml_result.deleted_count
        
        return cleanup_results


# HELPER FUNCTIONS FOR SAMPLE DATA
def create_sample_ml_recommendation() -> DWRecommendationDocument:
    """Create a sample ML recommendation document"""
    
    # Create enhanced customer profile
    customer_profile = DWCustomerProfile(
        name="John Smith",
        annual_income=75000.0,
        credit_score=720,
        health_score=78.5,
        risk_category="low",
        utilization_ratio=0.25,
        member_tenure_months=24,
        age_group="26-35",
        income_bracket="High",
        employment_status="employed",
        payment_trend="improving",
        utilization_trend="stable",
        financial_stability_score=82.5,
        creditworthiness_score=85.0,
        product_readiness_score=88.0,
        total_products_owned=2,
        recommendation_acceptance_rate=0.75
    )

    # Create ML recommendations
    recommendations = [
        MLRecommendation(
            rank=1,
            product_name="Premium Rewards Card",
            product_type="credit_card",
            score=88.5,
            max_score=100.0,
            confidence=92.0,
            reason="High creditworthiness; Similar customers accepted this product",
            similarity_score=0.89,
            cluster_id=3,
            feature_importance={
                "credit_score": 0.35,
                "income": 0.25,
                "payment_history": 0.20,
                "utilization": 0.20
            }
        )
    ]

    # Create timestamp
    timestamp = datetime.utcnow()

    # Create document
    document = DWRecommendationDocument(
        customer_id=str(uuid.uuid4()),
        customer_profile=customer_profile,
        recommendations=recommendations,
        created_at=timestamp,
        updated_at=timestamp,
        ml_metadata={
            "model_version": "1.0.0",
            "algorithm_type": "similarity_clustering",
            "feature_count": 20,
            "cluster_count": 5,
            "training_data_size": 1000
        }
    )

    return document


def main():
    """Example usage of the enhanced recommendation data models"""
    
    print("Enhanced Recommendation Data Manager Example")
    print("=" * 60)

    # Create data manager
    manager = RecommendationDataManager()

    try:
        # Method 1: Create and insert ML recommendation
        print("\n1. Creating ML recommendation document...")
        ml_document = create_sample_ml_recommendation()
        ml_doc_id = manager.insert_ml_recommendation(ml_document)
        print(f"Inserted ML document with ID: {ml_doc_id}")

        # Method 2: Get collection statistics
        print("\n2. Getting collection statistics...")
        stats = manager.get_collection_stats()
        print(f"Collection Stats: {stats}")

        # Method 3: Compare recommendations
        print("\n3. Comparing recommendations...")
        comparison = manager.get_recommendations_comparison(ml_document.customer_id)
        if comparison:
            print(f"Found comparison data for customer: {ml_document.customer_id}")

        print("\n✅ All ML operations completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure MongoDB is running and accessible.")


if __name__ == "__main__":
    main()
