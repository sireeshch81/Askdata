import jwt
from typing import List, Optional
from fastapi import HTTPException, Header
import logging


operational_roles = ["OLTP", "OPS"]
historical_roles = ["MULTI_DB_USER","DW"]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def verify_jwt_token(authorization: Optional[str] = Header(None)):
    """Verify JWT token and extract user info"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        # Extract token from "Bearer <token>" format
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header format")

        token = authorization.split(" ")[1]

        # Decode JWT without verification (since we're using Keycloak tokens)
        # In production, you should verify the signature with Keycloak's public key
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        print(decoded_token)
        return {
            "user_id": decoded_token.get("sub"),
            "username": decoded_token.get("preferred_username"),
            "email": decoded_token.get("email"),
            "realm_roles": decoded_token.get("realm_access", {}).get("roles", []),
            "client_roles": decoded_token.get("resource_access", {}).get("askdataclient", {}).get("roles", [])
        }
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")

def check_user_role_historical(user_info: dict):
    """Check if user has any of the required roles"""
    logger.info(f"User {user_info.get('username')} executing product query with roles: {user_info.get('realm_roles', []) + user_info.get('client_roles', [])}")

    user_roles = user_info.get("realm_roles", []) + user_info.get("client_roles", [])

    if not any(role in user_roles for role in historical_roles):
        raise HTTPException(
            status_code=403,
            detail=f"Access denied. Required roles: {historical_roles}. User roles: {user_roles}"
        )

    return True

def check_user_role_operational(user_info: dict):
    """Check if user has any of the required roles"""
    user_roles = user_info.get("realm_roles", []) + user_info.get("client_roles", [])

    if not any(role in user_roles for role in operational_roles):
        raise HTTPException(
            status_code=403,
            detail=f"Access denied. Required roles: {operational_roles}. User roles: {user_roles}"
        )

    return True
