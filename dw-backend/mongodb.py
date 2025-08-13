import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# If a full URI is provided, it takes precedence
MONGODB_URI = os.getenv("MONGODB_URI")

# Otherwise, build a Docker-friendly URI from parts
if not MONGODB_URI:
    MONGO_HOST = os.getenv("MONGO_HOST", "mongodb")  # service name on docker network
    MONGO_PORT = os.getenv("MONGO_PORT", "27017")
    MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

    auth_part = f"{MONGO_USER}:{MONGO_PASS}@" if MONGO_USER and MONGO_PASS else ""
    MONGODB_URI = f"mongodb://{auth_part}{MONGO_HOST}:{MONGO_PORT}/"

MONGODB_DB = os.getenv("MONGODB_DB") or os.getenv("MONGO_DATABASE", "askdata")
RECOMMENDATIONS_COLLECTION = os.getenv("RECOMMENDATIONS_COLLECTION", "recommendations")
OFFERS_COLLECTION = os.getenv("OFFERS_COLLECTION", "offers")
CUSTOMER_PROFILES_COLLECTION = os.getenv("CUSTOMER_PROFILES_COLLECTION", "customer_profile")

_client = None

def get_mongodb():
    global _client
    if _client is None:
        # Reasonable timeouts; let pymongo handle retries
        _client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=20000,
            socketTimeoutMS=20000,
        )
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
    recommendations_doc = db[RECOMMENDATIONS_COLLECTION].find_one({"customer_id": customer_id})
    result = {
        "customer_id": customer_id,
        "customer_profile": recommendations_doc.get("customer_profile", []) if recommendations_doc else [],
        "recommendations": recommendations_doc.get("recommendations", []) if recommendations_doc else []
    }
    return result


def save_offer(offer_id: str, offer_data: dict):
    db = get_mongodb()
    db[OFFERS_COLLECTION].replace_one(
        {"offer_id": offer_id}, offer_data, upsert=True
    )

# Example recommendation JSON structure:
# {
#   "customer_id": "1001",
#   "recommendations": [
#       {"product_id": "prod1", "product_name": "Credit Card Gold", "score": 0.95},
#       {"product_id": "prod2", "product_name": "Personal Loan", "score": 0.89}
#   ]
# }

