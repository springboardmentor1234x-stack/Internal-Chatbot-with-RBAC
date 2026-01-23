#!/usr/bin/env python3
"""
Test login issues for engineering and marketing accounts
"""
import requests
import json

def test_specific_logins():
    """Test login for engineering and marketing users"""
    
    test_users = [
        {"username": "engineering_user", "password": "password123", "expected_role": "Engineering"},
        {"username": "marketing_user", "password": "password123", "expected_role": "Marketing"},
        {"username": "admin", "password": "password123", "expected_role": "C-Level"},  # Control test
    ]
    
    print("🔍 Testing Login Issues")
    print("=" * 50)
    
    for user in test_users:
        print(f"\n🧪 Testing {user['username']}")
        print("-" * 30)
        
        try:
            response = requests.post(
                'http://127.0.0.1:8000/auth/login',
                data={'username': user['username'], 'password': user['password']},
                timeout=10
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                actual_role = data.get("user", {}).get("role", "Unknown")
                print(f"✅ Login successful!")
                print(f"   Username: {data.get('user', {}).get('username', 'Unknown')}")
                print(f"   Role: {actual_role}")
                print(f"   Expected: {user['expected_role']}")
                print(f"   Match: {'✅' if actual_role == user['expected_role'] else '❌'}")
                
            else:
                print(f"❌ Login failed!")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"   Raw response: {response.text}")
                    
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to backend")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_specific_logins()