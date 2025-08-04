#!/usr/bin/env python3
"""
Test script to verify MongoDB integration works with team's implementation
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from recommendation_engine.database_connector import DatabaseConnector
from utils.mongo_transformer import transform_recommendation_to_mongodb_format

def test_mongodb_connection():
    """Test MongoDB connection and data transformation"""
    print("🧪 Testing MongoDB Integration")
    print("=" * 50)
    
    db = DatabaseConnector()
    
    # Test MongoDB connection
    connected = db.connect_mongodb(
        host="localhost",
        port=27017,
        database="askdata_mongo",
        username="mongo_root",
        password="mongo_password"
    )
    
    if connected:
        print("✅ MongoDB connection successful!")
        
        # Test collection access
        collection = db.get_mongo_collection("recommendations")
        print("✅ Collection 'recommendations' accessible")
        
        # Test data transformation
        sample_data = {
            "member_id": 999,
            "member_info": {
                "annual_income": 75000.0,
                "credit_score": 720,
                "health_score": 85.0,
                "risk_category": "low",
                "utilization_ratio": 0.25
            },
            "recommendations": [{
                "rank": 1,
                "product_id": 3,
                "product_name": "Test Product",
                "product_type": "credit_card",
                "score": 95.0,
                "probability": 0.95,
                "eligible": True,
                "reasons": "Test reason"
            }],
            "processing_metadata": {
                "recommendation_method": "Test",
                "generated_date": "2025-08-04T10:00:00",
                "algorithm_version": "v1.0",
                "batch_number": 1
            }
        }
        
        # Transform and insert test document
        mongo_doc = transform_recommendation_to_mongodb_format(sample_data)
        print("✅ Data transformation successful")
        print(f"   Transformed customer_id: {mongo_doc['customer_id']}")
        print(f"   Customer name: {mongo_doc['customer_profile']['name']}")
        print(f"   Recommendations count: {len(mongo_doc['recommendations'])}")
        
        # Insert test document
        result = collection.replace_one(
            {"customer_id": mongo_doc["customer_id"]},
            mongo_doc,
            upsert=True
        )
        print(f"✅ Test document saved (upserted: {result.upserted_id is not None})")
        
        # Verify document exists
        found = collection.find_one({"customer_id": mongo_doc["customer_id"]})
        if found:
            print("✅ Test document retrieved successfully")
            print(f"   Customer profile name: {found['customer_profile']['name']}")
            print(f"   Recommendations: {len(found['recommendations'])}")
        
        # Clean up test document
        collection.delete_one({"customer_id": mongo_doc["customer_id"]})
        print("✅ Test document cleaned up")
        
        print("\n🎉 All MongoDB integration tests passed!")
        return True
        
    else:
        print("❌ MongoDB connection failed")
        return False
    
    db.close_mongodb()

if __name__ == "__main__":
    success = test_mongodb_connection()
    if success:
        print("\n✅ Ready to run actual recommendations with MongoDB support!")
    else:
        print("\n❌ Fix MongoDB connection issues before proceeding")
