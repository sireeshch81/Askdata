#!/usr/bin/env python3

from RecommendationDataManager import RecommendationDataManager
from datetime import datetime
import json


def main():
    """Example using your provided JSON structure"""

    # Your provided JSON data
    json_data = {
        "customer_id": "12345",
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

    print(" Converting JSON to Python Objects and Inserting into MongoDB")

    # Create the data manager
    manager = RecommendationDataManager()

    try:
        # Method 1: Direct insertion from JSON
        print("\n Method 1: Insert directly from JSON")
        print("-" * 40)

        # Update timestamps to current time
        current_time = datetime.utcnow().isoformat() + "Z"
        json_data["created_at"] = current_time
        json_data["updated_at"] = current_time

        # Insert the document
        doc_id = manager.insert_recommendation_from_json(json_data)
        print(f"  Successfully inserted document with ID: {doc_id}")

        # Method 2: Create Python objects first, then insert
        print("\n Method 2: Create Python objects, then insert")

        # Create the document object
        document = manager.create_recommendation_from_json(json_data)
        print(f"✅ Created Python object for customer: {document.customer_id}")
        print(f"   Customer: {document.customer_profile.name}")
        print(f"   Income: ${document.customer_profile.annual_income:,.2f}")
        print(f"   Credit Score: {document.customer_profile.credit_score}")
        print(f"   Recommendations: {len(document.recommendations)}")

        # Convert to dictionary for MongoDB
        doc_dict = document.to_dict()
        print(f" Converted to dictionary format")
        print(f"   Dictionary keys: {list(doc_dict.keys())}")

        # Insert the document
        doc_id = manager.insert_recommendation(document)
        print(f"  Successfully inserted document with ID: {doc_id}")

        # Retrieve and verify
        print("\n Retrieving and verifying data")

        # Find by customer ID
        retrieved_doc = manager.find_by_customer_id(json_data["customer_id"])
        if retrieved_doc:
            print(f"   Found document in MongoDB:")
            print(f"   Customer ID: {retrieved_doc['customer_id']}")
            print(f"   Member Name: {retrieved_doc['customer_profile']['name']}")
            print(f"   Annual Income: ${retrieved_doc['customer_profile']['annual_income']:,.2f}")
            print(f"   Credit Score: {retrieved_doc['customer_profile']['credit_score']}")
            print(f"   Risk Category: {retrieved_doc['customer_profile']['risk_category']}")
            print(f"   Recommendations Count: {len(retrieved_doc['recommendations'])}")

            # Show first recommendation
            if retrieved_doc['recommendations']:
                first_rec = retrieved_doc['recommendations'][0]
                print(f"   Top Recommendation: {first_rec['product_name']} (Score: {first_rec['score']})")

        # Show all documents count
        all_docs = manager.find_all_recommendations()
        print(f"\n Total documents in collection: {len(all_docs)}")

        print("\n All operations completed successfully!")

    except Exception as e:
        print(f" Error occurred: {e}")
        print("Make sure MongoDB is running and the connection is properly configured.")


if __name__ == "__main__":
    main()
