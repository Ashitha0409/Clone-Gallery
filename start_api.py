#!/usr/bin/env python3
"""
Start the API server
"""

import subprocess
import time
import requests
import sys

def start_api():
    """Start the API server and test it."""
    
    print("🚀 Starting CloneGallery API...")
    
    try:
        # Start the API server
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "main_enhanced:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("⏳ Waiting for API to start...")
        time.sleep(10)  # Wait for API to start
        
        # Test health endpoint
        print("🧪 Testing health endpoint...")
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ API is running successfully!")
                print(f"📄 Health response: {response.json()}")
                
                # Test registration endpoint
                print("🧪 Testing registration endpoint...")
                test_data = {
                    "name": "Test User",
                    "username": "testuser",
                    "email": "test@example.com",
                    "password": "testpassword123",
                    "role": "Visitor"
                }
                
                reg_response = requests.post(
                    "http://localhost:8000/auth/register",
                    json=test_data,
                    timeout=10
                )
                
                print(f"📊 Registration Status: {reg_response.status_code}")
                if reg_response.status_code == 200:
                    print("✅ Registration working!")
                    print(f"📄 Response: {reg_response.json()}")
                else:
                    print("❌ Registration failed!")
                    print(f"📄 Error: {reg_response.text}")
                    
            else:
                print(f"❌ Health check failed: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to API. It may still be starting...")
        except Exception as e:
            print(f"❌ Error testing API: {e}")
            
        print("\n🔄 API is running in the background. You can now test the login page!")
        print("🌐 Open index.html in your browser to test account creation.")
        
        # Keep the process running
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping API...")
            process.terminate()
            
    except Exception as e:
        print(f"❌ Failed to start API: {e}")

if __name__ == "__main__":
    start_api()
