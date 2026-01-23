#!/usr/bin/env python3
"""
Direct login test for engineering and marketing users
"""
import requests
import time

def test_direct_login():
    """Test login API directly"""
    
    users_to_test = [
        "engineering_user",
        "marketing_user", 
        "admin",  # Control test
        "hr_user"  # Control test
    ]
    
    print("🔍 Direct Login API Test")
    print("=" * 40)
    
    for username in users_to_test:
        print(f"\n🧪 Testing: {username}")
        
        try:
            # Test login
            response = requests.post(
                'http://127.0.0.1:8000/auth/login',
                data={'username': username, 'password': 'password123'},
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=5
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS")
                print(f"   Role: {data.get('user', {}).get('role', 'Unknown')}")
                print(f"   Token: {'Yes' if data.get('access_token') else 'No'}")
            else:
                print(f"   ❌ FAILED")
                try:
                    error = response.json()
                    print(f"   Error: {error.get('detail', 'Unknown')}")
                except:
                    print(f"   Raw: {response.text[:100]}")
                    
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection failed - backend not running?")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        time.sleep(0.5)  # Small delay between tests

if __name__ == "__main__":
    test_direct_login()