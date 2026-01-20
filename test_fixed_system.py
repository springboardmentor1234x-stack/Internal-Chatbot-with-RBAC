#!/usr/bin/env python3
"""
Test script to verify all fixes are working properly
"""
import requests
import time
import json
import sys
import os

# Test configuration
BACKEND_URL = "http://127.0.0.1:8000"
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
    """Test if backend is running and healthy"""
    print("🔍 Testing backend health...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is healthy: {data.get('message', 'OK')}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running on port 8000")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_user_login(username, password, expected_role):
    """Test user login and role assignment"""
    print(f"🔐 Testing login for {username}...")
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            data={"username": username, "password": password},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            actual_role = data.get("user", {}).get("role", "Unknown")
            
            if actual_role == expected_role:
                print(f"✅ Login successful for {username} (Role: {actual_role})")
                return data.get("access_token")
            else:
                print(f"⚠️ Login successful but role mismatch: expected {expected_role}, got {actual_role}")
                return data.get("access_token")
        else:
            print(f"❌ Login failed for {username}: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                pass
            return None
    except Exception as e:
        print(f"❌ Login error for {username}: {e}")
        return None

def test_chat_query(access_token, username, role):
    """Test chat query functionality"""
    print(f"💬 Testing chat query for {username}...")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.post(
            f"{BACKEND_URL}/api/v1/chat",
            json={"query": "What is our company's financial performance?"},
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get("response", "")
            accuracy_score = data.get("accuracy_score", 0)
            sources = data.get("sources", [])
            
            print(f"✅ Chat query successful for {username}")
            print(f"   Response length: {len(response_text)} characters")
            print(f"   Accuracy score: {accuracy_score}")
            print(f"   Sources: {len(sources)} documents")
            print(f"   Role in response: {data.get('user', {}).get('role', 'Unknown')}")
            return True
        else:
            print(f"❌ Chat query failed for {username}: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                pass
            return False
    except Exception as e:
        print(f"❌ Chat query error for {username}: {e}")
        return False

def test_user_profile(access_token, username):
    """Test user profile endpoint"""
    print(f"👤 Testing user profile for {username}...")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(
            f"{BACKEND_URL}/api/v1/user/profile",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Profile fetch successful for {username}")
            print(f"   Username: {data.get('username', 'Unknown')}")
            print(f"   Role: {data.get('role', 'Unknown')}")
            print(f"   Permissions: {len(data.get('permissions', []))}")
            return True
        else:
            print(f"❌ Profile fetch failed for {username}: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Profile fetch error for {username}: {e}")
        return False

def test_chat_history_endpoints(access_token, username):
    """Test chat history endpoints"""
    print(f"📚 Testing chat history endpoints for {username}...")
    
    endpoints = [
        ("save", "POST", "/api/v1/chat/history/save"),
        ("search", "GET", "/api/v1/chat/history/search?q=test"),
        ("analytics", "GET", "/api/v1/chat/history/analytics"),
        ("export", "GET", "/api/v1/chat/history/export")
    ]
    
    headers = {"Authorization": f"Bearer {access_token}"}
    success_count = 0
    
    for name, method, endpoint in endpoints:
        try:
            if method == "POST":
                response = requests.post(
                    f"{BACKEND_URL}{endpoint}",
                    json={"test": "data"},
                    headers=headers,
                    timeout=10
                )
            else:
                response = requests.get(
                    f"{BACKEND_URL}{endpoint}",
                    headers=headers,
                    timeout=10
                )
            
            if response.status_code == 200:
                print(f"   ✅ {name} endpoint working")
                success_count += 1
            else:
                print(f"   ❌ {name} endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {name} endpoint error: {e}")
    
    print(f"📊 Chat history endpoints: {success_count}/{len(endpoints)} working")
    return success_count == len(endpoints)

def main():
    """Run all tests"""
    print("🚀 Starting FinSolve System Test")
    print("=" * 50)
    
    # Test backend health
    if not test_backend_health():
        print("\n❌ Backend is not running. Please start it first:")
        print("   cd app && python main.py")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    
    # Test all users
    successful_logins = 0
    successful_chats = 0
    successful_profiles = 0
    
    for user in TEST_USERS:
        print(f"\n🧪 Testing user: {user['username']}")
        print("-" * 30)
        
        # Test login
        access_token = test_user_login(
            user["username"], 
            user["password"], 
            user["expected_role"]
        )
        
        if access_token:
            successful_logins += 1
            
            # Test chat query
            if test_chat_query(access_token, user["username"], user["expected_role"]):
                successful_chats += 1
            
            # Test user profile
            if test_user_profile(access_token, user["username"]):
                successful_profiles += 1
            
            # Test chat history endpoints (only for first user to avoid spam)
            if user["username"] == "admin":
                test_chat_history_endpoints(access_token, user["username"])
        
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"✅ Successful logins: {successful_logins}/{len(TEST_USERS)}")
    print(f"✅ Successful chat queries: {successful_chats}/{len(TEST_USERS)}")
    print(f"✅ Successful profile fetches: {successful_profiles}/{len(TEST_USERS)}")
    
    if successful_logins == len(TEST_USERS) and successful_chats == len(TEST_USERS):
        print("\n🎉 ALL TESTS PASSED! The system is working correctly.")
        print("\n🚀 You can now start the frontend:")
        print("   cd frontend && streamlit run app.py")
    else:
        print(f"\n⚠️ Some tests failed. Please check the issues above.")
        
        if successful_logins < len(TEST_USERS):
            print("   - Login issues: Check database and authentication")
        if successful_chats < successful_logins:
            print("   - Chat issues: Check RAG pipeline and routes")
        if successful_profiles < successful_logins:
            print("   - Profile issues: Check user profile endpoint")

if __name__ == "__main__":
    main()