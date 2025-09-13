#!/usr/bin/env python3
"""
Test the registration endpoint
"""

import requests
import json

def test_registration():
    """Test user registration."""
    
    url = "http://localhost:8000/auth/register"
    
    # Test data
    user_data = {
        "name": "Test User",
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "role": "Visitor"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("🧪 Testing registration endpoint...")
        print(f"📤 Sending data: {json.dumps(user_data, indent=2)}")
        
        response = requests.post(url, json=user_data, headers=headers, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Registration successful!")
            print(f"📄 Response: {json.dumps(response.json(), indent=2)}")
        else:
            print("❌ Registration failed!")
            print(f"📄 Error Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API server. Is it running on port 8000?")
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_registration()


