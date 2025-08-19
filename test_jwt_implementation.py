#!/usr/bin/env python3
"""
Test script to verify JWT token passing and role verification implementation.
"""

import requests
import jwt
from datetime import datetime, timedelta

# Test JWT token creation (simulating Keycloak token)
def create_test_jwt_token(username="testuser", roles=None):
    """Create a test JWT token with specified roles"""
    if roles is None:
        roles = ["product_analyst"]
    
    payload = {
        "sub": "test-user-id",
        "preferred_username": username,
        "email": f"{username}@example.com",
        "name": f"Test {username.capitalize()}",
        "realm_access": {
            "roles": roles
        },
        "resource_access": {
            "askdataclient": {
                "roles": roles
            }
        },
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
        "iss": "http://keycloak:8080/auth/realms/askdata-realm"
    }
    
    # Create unsigned token (for testing purposes)
    token = jwt.encode(payload, "secret", algorithm="HS256")
    return token

def test_api_with_token(token, sql_query="SELECT * FROM financial_products LIMIT 5"):
    """Test the API endpoint with JWT token"""
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    data = {
        "sql_query": sql_query
    }
    
    try:
        response = requests.post(
            "http://localhost:5004/run_custom_product_query",
            json=data,
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        return response.status_code == 200
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API backend. Make sure it's running on port 5004.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🧪 Testing JWT Token Implementation")
    print("=" * 50)
    
    # Test 1: Valid token with correct role
    print("\n1. Testing with valid token and correct role (product_analyst):")
    valid_token = create_test_jwt_token("analyst", ["product_analyst"])
    success = test_api_with_token(valid_token)
    print("✅ Success!" if success else "❌ Failed!")
    
    # Test 2: Valid token with incorrect role
    print("\n2. Testing with valid token but incorrect role (user):")
    invalid_role_token = create_test_jwt_token("user", ["user"])
    success = test_api_with_token(invalid_role_token)
    print("✅ Correctly rejected!" if not success else "❌ Should have been rejected!")
    
    # Test 3: No token
    print("\n3. Testing without token:")
    try:
        response = requests.post(
            "http://localhost:5004/run_custom_product_query",
            json={"sql_query": "SELECT * FROM financial_products LIMIT 5"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        success = response.status_code == 401
        print("✅ Correctly rejected!" if success else "❌ Should have been rejected!")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API backend.")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

if __name__ == "__main__":
    main()