# authentication.py
from typing import Optional

def authenticate_user(mongo_db, username: str, password: str) -> Optional[dict]:
    """
    Stub authentication: always returns a user dict if username and password are provided.
    Replace with real MongoDB lookup as needed.
    """
    if username and password:
        return {"username": username}
    return None

def create_access_token(data: dict) -> str:
    """
    Stub JWT creation: returns a fake token string.
    Replace with real JWT logic as needed.
    """
    return "stubbed.jwt.token"

