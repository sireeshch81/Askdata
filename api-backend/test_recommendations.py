#!/usr/bin/env python3

import requests
import json

# Test the /recommendations endpoint
def test_recommendations():
    url = "http://localhost:5004/recommendations"
    customer_id = "12345"  # Use a customer ID that exists in your MongoDB
    
    params = {"customer_id": customer_id}
    
    try:
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Raw response: {response.text}")

if __name__ == "__main__":
    test_recommendations()