import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGODB_DB = os.getenv("MONGODB_DB", "askdata")
RECOMMENDATIONS_COLLECTION = os.getenv("RECOMMENDATIONS_COLLECTION", "recommendations")

_client = None

def get_mongodb():
    global _client
    if _client is None:
        _client = MongoClient(MONGODB_URI)
    return _client[MONGODB_DB]

def save_recommendations(customer_id: str, recommendations: list):
    db = get_mongodb()
    rec_doc = {
        "customer_id": customer_id,
        "recommendations": recommendations
    }
    db[RECOMMENDATIONS_COLLECTION].replace_one(
        {"customer_id": customer_id}, rec_doc, upsert=True
    )

def get_recommendations(customer_id: str):
    db = get_mongodb()
    doc = db[RECOMMENDATIONS_COLLECTION].find_one({"customer_id": customer_id})
    if doc:
        return doc.get("recommendations", [])
    return []

# Example recommendation JSON structure:
# {
#   "customer_id": "1001",
#   "recommendations": [
#       {"product_id": "prod1", "product_name": "Credit Card Gold", "score": 0.95},
#       {"product_id": "prod2", "product_name": "Personal Loan", "score": 0.89}
#   ]
# }

