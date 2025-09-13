#!/usr/bin/env python3
"""
Test the health endpoint
"""

import requests

def test_health():
    """Test health endpoint."""
    
    url = "http://localhost:8000/health"
    
    try:
        print("🧪 Testing health endpoint...")
        
        response = requests.get(url, timeout=5)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Health check successful!")
            print(f"📄 Response: {response.json()}")
        else:
            print("❌ Health check failed!")
            print(f"📄 Error Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API server. Is it running on port 8000?")
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_health()

