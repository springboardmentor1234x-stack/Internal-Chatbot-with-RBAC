#!/usr/bin/env python3
"""
Test login error messages
"""
import requests

def test_login_errors():
    """Test different login error scenarios"""
    
    test_cases = [
        {
            "name": "Wrong Username",
            "username": "nonexistent_user",
            "password": "password123",
            "expected_status": 401
        },
        {
            "name": "Wrong Password", 
            "username": "admin",
            "password": "wrongpassword",
            "expected_status": 401
        },
        {
            "name": "Empty Username",
            "username": "",
            "password": "password123", 
            "expected_status": 400
        },
        {
            "name": "Empty Password",
            "username": "admin",
            "password": "",
            "expected_status": 400
        },
        {
            "name": "Correct Credentials (Control)",
            "username": "admin",
            "password": "password123",
            "expected_status": 200
        }
    ]
    
    print("🧪 Testing Login Error Messages")
    print("=" * 50)
    
    for test_case in test_cases:
        print(f"\n🔍 {test_case['name']}")
        print("-" * 30)
        
        try:
            response = requests.post(
                'http://127.0.0.1:8000/auth/login',
                data={
                    'username': test_case['username'], 
                    'password': test_case['password']
                },
                timeout=5
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Expected: {test_case['expected_status']}")
            
            if response.status_code == test_case['expected_status']:
                print("✅ Status matches expected")
            else:
                print("❌ Status doesn't match expected")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Login successful - Role: {data.get('user', {}).get('role', 'Unknown')}")
            else:
                try:
                    error_data = response.json()
                    error_detail = error_data.get("detail", "No detail")
                    print(f"Error Detail: {error_detail}")
                except:
                    print(f"Raw Response: {response.text[:100]}")
                    
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_login_errors()