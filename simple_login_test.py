#!/usr/bin/env python3
"""
Simple login test without audit logging to isolate issues
"""
import requests
import json

BACKEND_URL = "http://127.0.0.1:8000"

def test_simple_login():
    """Test basic login functionality"""
    print("🔐 Testing Simple Login...")
    
    # Test with admin user
    username = "admin"
    password = "password123"
    
    try:
        print(f"🧪 Testing login for: {username}")
        
        # Prepare login data
        login_data = {
            "username": username,
            "password": password
        }
        
        print(f"📤 Sending login request to: {BACKEND_URL}/auth/login")
        print(f"📋 Data: {login_data}")
        
        # Make login request
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        print(f"📥 Response status: {response.status_code}")
        print(f"📄 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"📊 Response data: {json.dumps(data, indent=2)}")
            
            # Test the token
            token = data.get("access_token")
            if token:
                print("\n🔑 Testing token with profile endpoint...")
                headers = {"Authorization": f"Bearer {token}"}
                profile_response = requests.get(
                    f"{BACKEND_URL}/api/v1/user/profile",
                    headers=headers,
                    timeout=5
                )
                
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    print("✅ Token works!")
                    print(f"👤 Profile: {json.dumps(profile_data, indent=2)}")
                else:
                    print(f"❌ Token test failed: {profile_response.status_code}")
                    print(f"📄 Error: {profile_response.text}")
            
        else:
            print("❌ Login failed!")
            print(f"📄 Response text: {response.text}")
            
            try:
                error_data = response.json()
                print(f"📊 Error data: {json.dumps(error_data, indent=2)}")
            except:
                print("📄 Could not parse error as JSON")
                
    except Exception as e:
        print(f"❌ Login test error: {e}")

def test_backend_endpoints():
    """Test basic backend endpoints"""
    print("\n🏥 Testing Backend Endpoints...")
    
    endpoints = [
        "/",
        "/health",
        "/docs"
    ]
    
    for endpoint in endpoints:
        try:
            url = f"{BACKEND_URL}{endpoint}"
            print(f"🧪 Testing: {url}")
            
            response = requests.get(url, timeout=5)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ OK")
            else:
                print(f"   ❌ Failed: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def main():
    print("🔧 FinSolve Simple Login Test")
    print("=" * 40)
    
    # Test backend endpoints first
    test_backend_endpoints()
    
    # Test login
    test_simple_login()
    
    print("\n" + "=" * 40)
    print("🏁 Test completed!")

if __name__ == "__main__":
    main()