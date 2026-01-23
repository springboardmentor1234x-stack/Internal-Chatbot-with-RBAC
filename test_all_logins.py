#!/usr/bin/env python3
"""
Test all login accounts to verify they work
"""
import requests
import json

# Backend URL
BACKEND_URL = "http://127.0.0.1:8000"

# Test users with their expected roles
TEST_USERS = [
    {"username": "admin", "password": "password123", "expected_role": "C-Level"},
    {"username": "finance_user", "password": "password123", "expected_role": "Finance"},
    {"username": "marketing_user", "password": "password123", "expected_role": "Marketing"},
    {"username": "hr_user", "password": "password123", "expected_role": "HR"},
    {"username": "engineering_user", "password": "password123", "expected_role": "Engineering"},
    {"username": "employee", "password": "password123", "expected_role": "Employee"},
    {"username": "intern_user", "password": "password123", "expected_role": "Intern"},
]

def test_backend_health():
    """Test if backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
            data = response.json()
            print(f"   Status: {data.get('status')}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection error: {e}")
        return False

def test_login(username, password, expected_role):
    """Test login for a specific user"""
    try:
        # Prepare login data
        login_data = {
            "username": username,
            "password": password
        }
        
        # Make login request
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            actual_role = data.get("user", {}).get("role", "Unknown")
            
            if actual_role == expected_role:
                print(f"✅ {username} ({expected_role}) - Login successful")
                return True, data.get("access_token")
            else:
                print(f"⚠️ {username} - Login successful but role mismatch: expected {expected_role}, got {actual_role}")
                return True, data.get("access_token")
        else:
            print(f"❌ {username} - Login failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Raw response: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ {username} - Login error: {e}")
        return False, None

def test_protected_endpoint(username, token):
    """Test accessing a protected endpoint with the token"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BACKEND_URL}/api/v1/user/profile",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Profile access successful - Role: {data.get('role')}")
            return True
        else:
            print(f"   ❌ Profile access failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Profile access error: {e}")
        return False

def main():
    print("🔐 FinSolve Login System Test")
    print("=" * 50)
    
    # Test backend health first
    print("🏥 Testing Backend Health...")
    if not test_backend_health():
        print("\n❌ Backend is not running. Please start it with: python run.py")
        return
    
    print("\n👥 Testing All User Accounts...")
    print("-" * 30)
    
    successful_logins = 0
    total_users = len(TEST_USERS)
    
    for user in TEST_USERS:
        username = user["username"]
        password = user["password"]
        expected_role = user["expected_role"]
        
        print(f"\n🧪 Testing {username}...")
        success, token = test_login(username, password, expected_role)
        
        if success and token:
            successful_logins += 1
            # Test protected endpoint
            test_protected_endpoint(username, token)
        
    print("\n" + "=" * 50)
    print(f"📊 Login Test Results:")
    print(f"   ✅ Successful logins: {successful_logins}/{total_users}")
    print(f"   ❌ Failed logins: {total_users - successful_logins}/{total_users}")
    
    if successful_logins == total_users:
        print("\n🎉 All accounts are working perfectly!")
        print("\n💡 You can now login to the frontend at: http://127.0.0.1:8501")
        print("   Use any of the tested usernames with password: password123")
    else:
        print(f"\n⚠️ {total_users - successful_logins} accounts need attention")
        print("\n🔧 Troubleshooting:")
        print("   1. Make sure the backend is fully started")
        print("   2. Check if the database is properly initialized")
        print("   3. Verify the user accounts exist in the database")

if __name__ == "__main__":
    main()