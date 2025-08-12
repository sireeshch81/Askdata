#!/usr/bin/env python3

from datetime import datetime
from typing import List, Optional, Dict, Any
from pymongo.collection import Collection
from mongo_connection import get_mongodb_collection
from schemas import CustomerProfile, Recommendation, RecommendationDocument
import uuid
import json


class RecommendationDataManager:
    """Manager class for recommendation data operations"""

    def __init__(self, collection_name: str = "recommendations"):
        self.collection_name = collection_name
        self.collection: Optional[Collection] = None

    def get_collection(self) -> Collection:
        """Get MongoDB collection"""
        if self.collection is None:
            self.collection = get_mongodb_collection(self.collection_name)
        return self.collection

    def create_recommendation_from_json(self, json_data: Dict[str, Any]) -> RecommendationDocument:
        """Create a RecommendationDocument from JSON data"""

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
        """Insert a recommendation document into MongoDB"""
        collection = self.get_collection()
        doc_dict = document.to_dict()
        result = collection.insert_one(doc_dict)
        return str(result.inserted_id)

    def insert_recommendation_from_json(self, json_data: Dict[str, Any]) -> str:
        """Insert a recommendation document from JSON data"""
        document = self.create_recommendation_from_json(json_data)
        return self.insert_recommendation(document)

    def find_by_customer_id(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Find a recommendation document by customer ID"""
        collection = self.get_collection()
        return collection.find_one({"customer_id": customer_id})

    def find_all_recommendations(self) -> List[Dict[str, Any]]:
        """Find all recommendation documents"""
        collection = self.get_collection()
        return list(collection.find())

    def update_recommendation(self, customer_id: str, updated_data: Dict[str, Any]) -> bool:
        """Update a recommendation document"""
        collection = self.get_collection()
        result = collection.update_one(
            {"customer_id": customer_id},
            {"$set": updated_data}
        )
        return result.modified_count > 0

    def delete_recommendation(self, customer_id: str) -> bool:
        """Delete a recommendation document"""
        collection = self.get_collection()
        result = collection.delete_one({"customer_id": customer_id})
        return result.deleted_count > 0


def create_sample_recommendation() -> RecommendationDocument:
    """Create a sample recommendation document"""

    # Create customer profile
    customer_profile = CustomerProfile(
        name="John Smith",
        annual_income=75000.0,
        credit_score=720,
        health_score=78.5,
        risk_category="low",
        utilization_ratio=0.25
    )

    # Create recommendations
    recommendations = [
        Recommendation(
            rank=1,
            product_name="Secured Starter Card",
            product_type="credit_card",
            score=130.0,
            max_score=100.0,
            confidence=100.0,
            reason="Excellent credit score; High income; Low utilization ratio"
        ),
        Recommendation(
            rank=2,
            product_name="Premium Rewards Card",
            product_type="credit_card",
            score=95.0,
            max_score=100.0,
            confidence=85.0,
            reason="Good credit score; Eligible for premium products"
        )
    ]

    # Create timestamp
    timestamp = datetime.utcnow().isoformat() + "Z"

    # Create document
    document = RecommendationDocument(
        customer_id=str(uuid.uuid4()),
        customer_profile=customer_profile,
        recommendations=recommendations,
        created_at=timestamp,
        updated_at=timestamp
    )

    return document


def main():
    """Example usage of the recommendation data models"""

    # Sample JSON data (your provided structure)
    sample_json = {
        "customer_id": "unique-uuid",
        "customer_profile": {
            "name": "John Smith",
            "annual_income": 75000.0,
            "credit_score": 720,
            "health_score": 78.5,
            "risk_category": "low",
            "utilization_ratio": 0.25
        },
        "recommendations": [
            {
                "rank": 1,
                "product_name": "Secured Starter Card",
                "product_type": "credit_card",
                "score": 130.0,
                "max_score": 100.0,
                "confidence": 100.0,
                "reason": "Excellent credit score; High income..."
            }
        ],
        "created_at": "2025-08-02T10:30:00.000Z",
        "updated_at": "2025-08-02T10:30:00.000Z"
    }

    print("Recommendation Data Model Example")
    print("=" * 50)

    # Create data manager
    manager = RecommendationDataManager()

    try:
        # Method 1: Create from JSON and insert
        print("\n1. Creating document from JSON...")
        document = manager.create_recommendation_from_json(sample_json)
        print(f"Created document for customer: {document.customer_id}")

        # Method 2: Insert directly from JSON
        print("\n2. Inserting document from JSON...")
        doc_id = manager.insert_recommendation_from_json(sample_json)
        print(f"Inserted document with ID: {doc_id}")

        # Method 3: Create programmatically and insert
        print("\n3. Creating sample document programmatically...")
        sample_doc = create_sample_recommendation()
        doc_id = manager.insert_recommendation(sample_doc)
        print(f"Inserted sample document with ID: {doc_id}")

        # Retrieve and display
        print("\n4. Retrieving documents...")
        all_docs = manager.find_all_recommendations()
        print(f"Total documents in collection: {len(all_docs)}")

        for i, doc in enumerate(all_docs[:2], 1):  # Show first 2 documents
            print(f"\n📄 Document {i}:")
            print(f"   Customer ID: {doc['customer_id']}")
            print(f"   Customer Name: {doc['customer_profile']['name']}")
            print(f"   Recommendations Count: {len(doc['recommendations'])}")

        print("\n All operations completed successfully!")

    except Exception as e:
        print(f"Error: {e}")
        print("Make sure MongoDB is running and accessible.")


if __name__ == "__main__":
    main() 