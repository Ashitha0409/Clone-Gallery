#!/usr/bin/env python3
"""
Debug registration with detailed error handling
"""

import requests
import json
import traceback

def debug_registration():
    """Debug user registration with detailed error info."""
    
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
            
            # Try to get more details
            try:
                error_json = response.json()
                print(f"📄 Error JSON: {json.dumps(error_json, indent=2)}")
            except:
                print("📄 Could not parse error as JSON")
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: {e}")
    except requests.exceptions.Timeout as e:
        print(f"❌ Timeout Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        print(f"📄 Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    debug_registration()

