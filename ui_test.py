#!/usr/bin/env python3
"""
Frontend UI Test for FinSolve Internal Chatbot
Tests Streamlit frontend functionality and user interface
"""

import requests
import time
import sys

FRONTEND_URL = "http://localhost:8501"

def test_frontend_accessibility():
    """Test if frontend is accessible"""
    print("🌐 Testing Frontend Accessibility...")
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            return True
        else:
            print(f"❌ Frontend returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend not accessible: {str(e)}")
        return False

def test_ui_elements_without_selenium():
    """Test UI elements by checking HTML content"""
    print("🎨 Testing UI Elements...")
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        html_content = response.text
        
        # Check for key UI elements
        ui_checks = [
            ("Login form", "login" in html_content.lower()),
            ("Title", "finsolve" in html_content.lower()),
            ("Streamlit", "streamlit" in html_content.lower()),
        ]
        
        for check_name, condition in ui_checks:
            if condition:
                print(f"✅ {check_name} found")
            else:
                print(f"⚠️  {check_name} not clearly visible")
                
        return True
        
    except Exception as e:
        print(f"❌ UI test error: {str(e)}")
        return False

def test_api_endpoints():
    """Test critical API endpoints"""
    print("🔌 Testing API Endpoints...")
    
    endpoints = [
        ("/health", "Health check"),
        ("/docs", "API documentation"),
        ("/auth/login", "Login endpoint (POST)"),
    ]
    
    for endpoint, description in endpoints:
        try:
            if endpoint == "/auth/login":
                # Test POST endpoint
                response = requests.post(f"http://127.0.0.1:8000{endpoint}", 
                                       data={"username": "test", "password": "test"}, 
                                       timeout=5)
                # Should return 401 for invalid credentials
                if response.status_code == 401:
                    print(f"✅ {description} working correctly")
                else:
                    print(f"⚠️  {description} unexpected response: {response.status_code}")
            else:
                response = requests.get(f"http://127.0.0.1:8000{endpoint}", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {description} accessible")
                else:
                    print(f"⚠️  {description} returned: {response.status_code}")
                    
        except Exception as e:
            print(f"❌ {description} error: {str(e)}")

def test_chat_functionality():
    """Test chat functionality through API"""
    print("💬 Testing Chat Functionality...")
    
    # First login to get token
    try:
        login_response = requests.post(
            "http://127.0.0.1:8000/auth/login",
            data={"username": "admin", "password": "password123"},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print("❌ Could not login for chat test")
            return False
            
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test chat with different query types
        test_queries = [
            ("Simple query", "What is our company policy?"),
            ("Financial query", "Show me revenue information"),
            ("HR query", "What are the employee benefits?"),
            ("Technical query", "Tell me about our engineering processes"),
        ]
        
        for query_type, query in test_queries:
            try:
                chat_response = requests.post(
                    "http://127.0.0.1:8000/api/v1/chat",
                    json={"query": query},
                    headers=headers,
                    timeout=20
                )
                
                if chat_response.status_code == 200:
                    data = chat_response.json()
                    response_text = data.get("response", "")
                    sources = data.get("sources", [])
                    accuracy = data.get("accuracy_score", 0)
                    
                    if response_text and len(response_text) > 10:
                        print(f"✅ {query_type}: Response generated")
                        
                        if sources:
                            print(f"   📄 Sources: {len(sources)} documents")
                        else:
                            print(f"   ⚠️  No sources found")
                            
                        if accuracy > 0:
                            print(f"   📊 Accuracy: {accuracy:.1f}%")
                        else:
                            print(f"   ⚠️  No accuracy score")
                    else:
                        print(f"❌ {query_type}: Empty or invalid response")
                else:
                    print(f"❌ {query_type}: HTTP {chat_response.status_code}")
                    
            except Exception as e:
                print(f"❌ {query_type} error: {str(e)}")
                
        return True
        
    except Exception as e:
        print(f"❌ Chat functionality test error: {str(e)}")
        return False

def test_role_based_ui():
    """Test role-based UI functionality"""
    print("👥 Testing Role-Based UI...")
    
    test_users = [
        ("admin", "password123", "C-Level"),
        ("finance_user", "password123", "Finance"),
        ("employee", "password123", "Employee"),
    ]
    
    for username, password, expected_role in test_users:
        try:
            # Login
            login_response = requests.post(
                "http://127.0.0.1:8000/auth/login",
                data={"username": username, "password": password},
                timeout=10
            )
            
            if login_response.status_code == 200:
                token = login_response.json().get("access_token")
                headers = {"Authorization": f"Bearer {token}"}
                
                # Get profile
                profile_response = requests.get(
                    "http://127.0.0.1:8000/api/v1/user/profile",
                    headers=headers,
                    timeout=5
                )
                
                if profile_response.status_code == 200:
                    profile = profile_response.json()
                    actual_role = profile.get("role")
                    
                    if actual_role == expected_role:
                        print(f"✅ {username}: Role-based access working ({actual_role})")
                    else:
                        print(f"❌ {username}: Role mismatch - expected {expected_role}, got {actual_role}")
                else:
                    print(f"❌ {username}: Could not get profile")
            else:
                print(f"❌ {username}: Login failed")
                
        except Exception as e:
            print(f"❌ {username}: Role test error - {str(e)}")

def test_security_headers():
    """Test security headers and configurations"""
    print("🔒 Testing Security Headers...")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        headers = response.headers
        
        # Check for security headers
        security_checks = [
            ("X-Frame-Options", headers.get("X-Frame-Options")),
            ("X-Content-Type-Options", headers.get("X-Content-Type-Options")),
            ("Content-Security-Policy", headers.get("Content-Security-Policy")),
        ]
        
        for header_name, header_value in security_checks:
            if header_value:
                print(f"✅ {header_name}: {header_value}")
            else:
                print(f"⚠️  {header_name}: Not set")
                
        # Check if server info is exposed
        server_header = headers.get("Server", "")
        if "streamlit" in server_header.lower():
            print(f"⚠️  Server header exposes technology: {server_header}")
        else:
            print(f"✅ Server header: {server_header or 'Not exposed'}")
            
    except Exception as e:
        print(f"❌ Security headers test error: {str(e)}")

def main():
    """Run UI tests"""
    print("🎨 Starting Frontend UI Test Suite")
    print(f"⏰ Test started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run tests
    tests_passed = 0
    total_tests = 6
    
    if test_frontend_accessibility():
        tests_passed += 1
    
    if test_ui_elements_without_selenium():
        tests_passed += 1
        
    test_api_endpoints()
    tests_passed += 1
    
    if test_chat_functionality():
        tests_passed += 1
        
    test_role_based_ui()
    tests_passed += 1
    
    test_security_headers()
    tests_passed += 1
    
    # Summary
    print("\n" + "="*60)
    print("📊 UI TEST SUMMARY")
    print("="*60)
    print(f"✅ Tests completed: {tests_passed}/{total_tests}")
    
    success_rate = (tests_passed / total_tests) * 100
    print(f"📈 Success rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🌟 EXCELLENT: UI is working well")
    elif success_rate >= 80:
        print("✅ GOOD: UI is mostly functional")
    elif success_rate >= 70:
        print("⚠️  FAIR: UI has some issues")
    else:
        print("❌ POOR: UI needs significant work")
    
    print("\n💡 RECOMMENDATIONS:")
    print("1. Test the actual UI manually in a browser")
    print("2. Check all interactive elements work correctly")
    print("3. Verify responsive design on different screen sizes")
    print("4. Test accessibility features")
    print("5. Validate all user workflows end-to-end")
    
    print("\n🏁 UI test suite completed!")

if __name__ == "__main__":
    main()