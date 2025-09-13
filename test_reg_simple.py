#!/usr/bin/env python3
"""
Test registration with detailed error info
"""

import requests
import json

def test_registration():
    """Test user registration with detailed error info."""
    
    url = "http://localhost:8000/auth/register"
    
    # Test data
    user_data = {
        "name": "Test User",
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "testpassword123",
        "role": "Visitor"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("🧪 Testing registration endpoint...")
        print(f"📤 Sending data: {json.dumps(user_data, indent=2)}")
        
        response = requests.post(url, json=user_data, headers=headers, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Registration successful!")
            print(f"📄 Response: {response.json()}")
        else:
            print("❌ Registration failed!")
            print(f"📄 Error Response: {response.text}")
            
            # Try to parse as JSON for more details
            try:
                error_data = response.json()
                print(f"📄 Error Details: {json.dumps(error_data, indent=2)}")
            except:
                print("📄 Raw Error Response:")
                print(response.text)
                
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API server. Is it running on port 8000?")
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_registration()
