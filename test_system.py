#!/usr/bin/env python3
"""
Test script to verify the FinSolve chatbot system is working correctly
Run this in VS Code to test all components
"""
import requests
import time
import sys

BACKEND_URL = "http://127.0.0.1:8000"

def test_backend_health():
    """Test if backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running. Start it first with: python app/main.py")
        return False
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False

def test_authentication():
    """Test authentication system"""
    try:
        # Test login
        login_data = {
            "username": "admin",
            "password": "password123"
        }
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                print("✅ Authentication working")
                return token
            else:
                print("❌ No token received")
                return None
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return None

def test_chat_endpoint(token):
    """Test chat endpoint with authentication"""
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        chat_data = {
            "query": "What is in the employee handbook?"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/v1/chat",
            json=chat_data,
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Chat endpoint working")
            data = response.json()
            print(f"📝 Response preview: {data.get('content', '')[:100]}...")
            return True
        else:
            print(f"❌ Chat failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Chat test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing FinSolve Chatbot System")
    print("=" * 40)
    
    # Test 1: Backend Health
    if not test_backend_health():
        print("\n💡 To start backend: python app/main.py")
        sys.exit(1)
    
    # Test 2: Authentication
    token = test_authentication()
    if not token:
        print("\n💡 Check database setup: python setup.py")
        sys.exit(1)
    
    # Test 3: Chat Endpoint
    if not test_chat_endpoint(token):
        print("\n💡 Check vector store setup")
        sys.exit(1)
    
    print("\n" + "=" * 40)
    print("🎉 All tests passed! System is working correctly.")
    print("\n📋 Next steps:")
    print("1. Start frontend: streamlit run frontend/app.py")
    print("2. Access UI: http://localhost:8501")
    print("3. Login with: admin / password123")

if __name__ == "__main__":
    main()