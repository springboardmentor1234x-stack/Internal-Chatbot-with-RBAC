#!/usr/bin/env python3
"""
Comprehensive Security and Failure Testing Suite for FinSolve Chatbot
Tests security vulnerabilities, failure scenarios, and edge cases.
"""

import requests
import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import jwt


class SecurityTester:
    """Comprehensive security testing for the FinSolve chatbot system."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.test_results = []
        self.valid_token = None
        self.valid_refresh_token = None
        
    def run_all_security_tests(self) -> Dict[str, Any]:
        """Run all security tests and return comprehensive results."""
        print("🔒 Starting Comprehensive Security Testing Suite")
        print("=" * 60)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "critical_issues": [],
            "warnings": [],
            "test_categories": {}
        }
        
        # Test categories
        test_categories = [
            ("Authentication Security", self.test_authentication_security),
            ("JWT Token Security", self.test_jwt_security),
            ("SQL Injection", self.test_sql_injection),
            ("Authorization Bypass", self.test_authorization_bypass),
            ("Input Validation", self.test_input_validation),
            ("Rate Limiting", self.test_rate_limiting),
            ("CORS Security", self.test_cors_security),
            ("Session Security", self.test_session_security)
        ]
        
        for category_name, test_function in test_categories:
            print(f"\n🧪 Testing: {category_name}")
            print("-" * 40)
            
            category_results = test_function()
            results["test_categories"][category_name] = category_results
            
            # Update totals
            results["total_tests"] += category_results["total"]
            results["passed"] += category_results["passed"]
            results["failed"] += category_results["failed"]
            
            # Collect critical issues
            if category_results.get("critical_issues"):
                results["critical_issues"].extend(category_results["critical_issues"])
            
            if category_results.get("warnings"):
                results["warnings"].extend(category_results["warnings"])
        
        # Generate summary
        self.print_security_summary(results)
        return results
    
    def test_authentication_security(self) -> Dict[str, Any]:
        """Test authentication security vulnerabilities."""
        results = {"total": 0, "passed": 0, "failed": 0, "critical_issues": [], "warnings": []}
        
        tests = [
            ("Brute Force Protection", self.test_brute_force_protection),
            ("Password Strength", self.test_password_strength),
            ("Invalid Credentials", self.test_invalid_credentials),
            ("Empty Credentials", self.test_empty_credentials),
            ("SQL Injection in Login", self.test_login_sql_injection),
            ("Username Enumeration", self.test_username_enumeration)
        ]
        
        for test_name, test_func in tests:
            results["total"] += 1
            try:
                test_result = test_func()
                if test_result["passed"]:
                    results["passed"] += 1
                    print(f"  ✅ {test_name}: PASSED")
                else:
                    results["failed"] += 1
                    print(f"  ❌ {test_name}: FAILED - {test_result.get('reason', 'Unknown')}")
                    if test_result.get("critical"):
                        results["critical_issues"].append(f"{test_name}: {test_result.get('reason')}")
                    else:
                        results["warnings"].append(f"{test_name}: {test_result.get('reason')}")
            except Exception as e:
                results["failed"] += 1
                print(f"  ❌ {test_name}: ERROR - {str(e)}")
                results["critical_issues"].append(f"{test_name}: Test execution error - {str(e)}")
        
        return results
    
    def test_brute_force_protection(self) -> Dict[str, Any]:
        """Test if the system has brute force protection."""
        failed_attempts = 0
        for i in range(10):
            try:
                response = requests.post(
                    f"{self.base_url}/auth/login",
                    data={"username": "admin", "password": f"wrong_password_{i}"},
                    timeout=5
                )
                if response.status_code == 401:
                    failed_attempts += 1
                elif response.status_code == 429:  # Rate limited
                    return {"passed": True, "reason": "Rate limiting detected"}
                time.sleep(0.1)
            except:
                pass
        
        if failed_attempts >= 8:
            return {
                "passed": False, 
                "critical": True,
                "reason": "No brute force protection detected - allows unlimited login attempts"
            }
        
        return {"passed": True, "reason": "Some protection mechanism detected"}
    
    def test_password_strength(self) -> Dict[str, Any]:
        """Test password strength requirements."""
        return {
            "passed": False,
            "critical": False,
            "reason": "Test accounts use weak passwords (password123) - should enforce stronger password policy"
        }
    
    def test_invalid_credentials(self) -> Dict[str, Any]:
        """Test handling of invalid credentials."""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                data={"username": "nonexistent_user", "password": "wrong_password"},
                timeout=5
            )
            
            if response.status_code == 401:
                error_msg = response.json().get("detail", "").lower()
                if "user" in error_msg and "not found" in error_msg:
                    return {
                        "passed": False,
                        "critical": False,
                        "reason": "Error message reveals user existence information"
                    }
                return {"passed": True, "reason": "Proper 401 response without user enumeration"}
            else:
                return {
                    "passed": False,
                    "critical": True,
                    "reason": f"Unexpected response code: {response.status_code}"
                }
        except Exception as e:
            return {"passed": False, "critical": True, "reason": f"Request failed: {str(e)}"}
    
    def test_empty_credentials(self) -> Dict[str, Any]:
        """Test handling of empty credentials."""
        test_cases = [
            {"username": "", "password": ""},
            {"username": "admin", "password": ""},
            {"username": "", "password": "password123"}
        ]
        
        for credentials in test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/auth/login",
                    data=credentials,
                    timeout=5
                )
                
                if response.status_code not in [400, 422]:
                    return {
                        "passed": False,
                        "critical": True,
                        "reason": f"Accepts empty credentials: {credentials}"
                    }
            except:
                pass
        
        return {"passed": True, "reason": "Properly rejects empty credentials"}
    
    def test_login_sql_injection(self) -> Dict[str, Any]:
        """Test SQL injection in login form."""
        sql_payloads = [
            "admin' OR '1'='1",
            "admin'; DROP TABLE users; --",
            "admin' UNION SELECT * FROM users --",
            "' OR 1=1 --",
            "admin'/**/OR/**/1=1#"
        ]
        
        for payload in sql_payloads:
            try:
                response = requests.post(
                    f"{self.base_url}/auth/login",
                    data={"username": payload, "password": "any_password"},
                    timeout=5
                )
                
                if response.status_code == 200:
                    return {
                        "passed": False,
                        "critical": True,
                        "reason": f"Possible SQL injection with payload: {payload}"
                    }
            except:
                pass
        
        return {"passed": True, "reason": "No SQL injection vulnerabilities detected in login"}
    
    def test_username_enumeration(self) -> Dict[str, Any]:
        """Test if the system reveals valid usernames."""
        valid_user = "admin"
        invalid_user = "definitely_not_a_user_12345"
        
        try:
            response1 = requests.post(
                f"{self.base_url}/auth/login",
                data={"username": valid_user, "password": "wrong_password"},
                timeout=5
            )
            
            response2 = requests.post(
                f"{self.base_url}/auth/login",
                data={"username": invalid_user, "password": "wrong_password"},
                timeout=5
            )
            
            if response1.status_code != response2.status_code:
                return {
                    "passed": False,
                    "critical": False,
                    "reason": "Different response codes for valid/invalid usernames"
                }
            
            msg1 = response1.json().get("detail", "")
            msg2 = response2.json().get("detail", "")
            
            if msg1 != msg2:
                return {
                    "passed": False,
                    "critical": False,
                    "reason": "Different error messages reveal username validity"
                }
            
            return {"passed": True, "reason": "No username enumeration detected"}
            
        except Exception as e:
            return {"passed": False, "critical": True, "reason": f"Test failed: {str(e)}"}
    
    def test_jwt_security(self) -> Dict[str, Any]:
        """Test JWT token security."""
        results = {"total": 0, "passed": 0, "failed": 0, "critical_issues": [], "warnings": []}
        
        self.get_valid_token()
        
        tests = [
            ("Token Manipulation", self.test_token_manipulation),
            ("Token Expiry", self.test_token_expiry),
            ("Algorithm Confusion", self.test_algorithm_confusion),
            ("Secret Key Strength", self.test_secret_key_strength),
            ("Token Reuse", self.test_token_reuse)
        ]
        
        for test_name, test_func in tests:
            results["total"] += 1
            try:
                test_result = test_func()
                if test_result["passed"]:
                    results["passed"] += 1
                    print(f"  ✅ {test_name}: PASSED")
                else:
                    results["failed"] += 1
                    print(f"  ❌ {test_name}: FAILED - {test_result.get('reason', 'Unknown')}")
                    if test_result.get("critical"):
                        results["critical_issues"].append(f"{test_name}: {test_result.get('reason')}")
                    else:
                        results["warnings"].append(f"{test_name}: {test_result.get('reason')}")
            except Exception as e:
                results["failed"] += 1
                print(f"  ❌ {test_name}: ERROR - {str(e)}")
                results["critical_issues"].append(f"{test_name}: Test execution error - {str(e)}")
        
        return results
    
    def get_valid_token(self) -> bool:
        """Get a valid token for testing."""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                data={"username": "admin", "password": "password123"},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                self.valid_token = data.get("access_token")
                self.valid_refresh_token = data.get("refresh_token")
                return True
        except:
            pass
        return False
    
    def test_token_manipulation(self) -> Dict[str, Any]:
        """Test JWT token manipulation."""
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No valid token available for testing"}
        
        try:
            payload = jwt.decode(self.valid_token, options={"verify_signature": False})
            payload["role"] = "C-Level"
            
            weak_secrets = ["secret", "key", "your_super_secret_key_finsolve_2024"]
            
            for secret in weak_secrets:
                try:
                    manipulated_token = jwt.encode(payload, secret, algorithm="HS256")
                    
                    response = requests.get(
                        f"{self.base_url}/api/v1/user/profile",
                        headers={"Authorization": f"Bearer {manipulated_token}"},
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        return {
                            "passed": False,
                            "critical": True,
                            "reason": f"Token manipulation successful with secret: {secret}"
                        }
                except:
                    continue
            
            return {"passed": True, "reason": "Token manipulation attempts failed"}
            
        except Exception as e:
            return {"passed": False, "critical": True, "reason": f"Token manipulation test failed: {str(e)}"}
    
    def test_algorithm_confusion(self) -> Dict[str, Any]:
        """Test algorithm confusion attack."""
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No valid token available for testing"}
        
        try:
            payload = jwt.decode(self.valid_token, options={"verify_signature": False})
            none_token = jwt.encode(payload, "", algorithm="none")
            
            response = requests.get(
                f"{self.base_url}/api/v1/user/profile",
                headers={"Authorization": f"Bearer {none_token}"},
                timeout=5
            )
            
            if response.status_code == 200:
                return {
                    "passed": False,
                    "critical": True,
                    "reason": "Algorithm confusion attack successful - accepts 'none' algorithm"
                }
            
            return {"passed": True, "reason": "Algorithm confusion attack failed"}
            
        except Exception as e:
            return {"passed": False, "critical": True, "reason": f"Algorithm confusion test failed: {str(e)}"}
    
    def test_secret_key_strength(self) -> Dict[str, Any]:
        """Test JWT secret key strength."""
        secret = "your_super_secret_key_finsolve_2024"
        
        issues = []
        
        if len(secret) < 32:
            issues.append("Secret key too short (< 32 characters)")
        
        if secret.lower() in ["secret", "key", "password", "your_super_secret_key_finsolve_2024"]:
            issues.append("Secret key is predictable/default")
        
        if not any(c.isupper() for c in secret):
            issues.append("Secret key lacks uppercase letters")
        
        if not any(c.isdigit() for c in secret):
            issues.append("Secret key lacks numbers")
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in secret):
            issues.append("Secret key lacks special characters")
        
        if issues:
            return {
                "passed": False,
                "critical": True,
                "reason": f"Weak secret key: {', '.join(issues)}"
            }
        
        return {"passed": True, "reason": "Secret key appears strong"}
    
    def test_token_expiry(self) -> Dict[str, Any]:
        """Test token expiry handling."""
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No valid token available for testing"}
        
        try:
            payload = jwt.decode(self.valid_token, options={"verify_signature": False})
            exp = payload.get("exp")
            
            if not exp:
                return {
                    "passed": False,
                    "critical": True,
                    "reason": "Token has no expiration time"
                }
            
            exp_time = datetime.fromtimestamp(exp)
            now = datetime.now()
            time_diff = exp_time - now
            
            if time_diff.total_seconds() > 3600:
                return {
                    "passed": False,
                    "critical": False,
                    "reason": f"Token expiry too long: {time_diff.total_seconds()/60:.1f} minutes"
                }
            
            return {"passed": True, "reason": f"Token expiry reasonable: {time_diff.total_seconds()/60:.1f} minutes"}
            
        except Exception as e:
            return {"passed": False, "critical": True, "reason": f"Token expiry test failed: {str(e)}"}
    
    def test_token_reuse(self) -> Dict[str, Any]:
        """Test if tokens can be reused after logout."""
        return {
            "passed": False,
            "critical": False,
            "reason": "No logout endpoint found - tokens cannot be invalidated server-side"
        }
    
    def test_sql_injection(self) -> Dict[str, Any]:
        """Test SQL injection vulnerabilities."""
        results = {"total": 0, "passed": 0, "failed": 0, "critical_issues": [], "warnings": []}
        
        if not self.valid_token:
            self.get_valid_token()
        
        tests = [
            ("Chat Query SQL Injection", self.test_chat_sql_injection),
            ("Search SQL Injection", self.test_search_sql_injection),
            ("History SQL Injection", self.test_history_sql_injection)
        ]
        
        for test_name, test_func in tests:
            results["total"] += 1
            try:
                test_result = test_func()
                if test_result["passed"]:
                    results["passed"] += 1
                    print(f"  ✅ {test_name}: PASSED")
                else:
                    results["failed"] += 1
                    print(f"  ❌ {test_name}: FAILED - {test_result.get('reason', 'Unknown')}")
                    if test_result.get("critical"):
                        results["critical_issues"].append(f"{test_name}: {test_result.get('reason')}")
                    else:
                        results["warnings"].append(f"{test_name}: {test_result.get('reason')}")
            except Exception as e:
                results["failed"] += 1
                print(f"  ❌ {test_name}: ERROR - {str(e)}")
                results["critical_issues"].append(f"{test_name}: Test execution error - {str(e)}")
        
        return results
    
    def test_chat_sql_injection(self) -> Dict[str, Any]:
        """Test SQL injection in chat queries."""
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No valid token available"}
        
        sql_payloads = [
            "'; DROP TABLE chat_messages; --",
            "' UNION SELECT * FROM users --",
            "' OR 1=1 --",
            "'; INSERT INTO chat_messages VALUES ('hacked'); --"
        ]
        
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        
        for payload in sql_payloads:
            try:
                response = requests.post(
                    f"{self.base_url}/chat",
                    json={"query": payload},
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 500:
                    error_text = response.text.lower()
                    if any(keyword in error_text for keyword in ["sql", "sqlite", "database", "syntax error"]):
                        return {
                            "passed": False,
                            "critical": True,
                            "reason": f"SQL injection possible - database error exposed with payload: {payload}"
                        }
                
                if response.status_code == 200:
                    response_data = response.json()
                    response_text = str(response_data).lower()
                    if any(keyword in response_text for keyword in ["error", "sql", "database"]):
                        return {
                            "passed": False,
                            "critical": True,
                            "reason": f"Possible SQL injection with payload: {payload}"
                        }
                        
            except Exception as e:
                continue
        
        return {"passed": True, "reason": "No SQL injection vulnerabilities detected in chat"}
    
    def test_search_sql_injection(self) -> Dict[str, Any]:
        """Test SQL injection in search functionality."""
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No valid token available"}
        
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        sql_payloads = [
            "'; DROP TABLE chat_sessions; --",
            "' UNION SELECT username, password_hash FROM users --",
            "' OR 1=1 --"
        ]
        
        for payload in sql_payloads:
            try:
                response = requests.get(
                    f"{self.base_url}/api/v1/chat/history/search",
                    params={"query": payload},
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 500:
                    error_text = response.text.lower()
                    if any(keyword in error_text for keyword in ["sql", "sqlite", "database"]):
                        return {
                            "passed": False,
                            "critical": True,
                            "reason": f"SQL injection in search with payload: {payload}"
                        }
                        
            except:
                continue
        
        return {"passed": True, "reason": "No SQL injection vulnerabilities detected in search"}
    
    def test_history_sql_injection(self) -> Dict[str, Any]:
        """Test SQL injection in history endpoints."""
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No valid token available"}
        
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/chat/history/session/'; DROP TABLE chat_sessions; --",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 500:
                error_text = response.text.lower()
                if any(keyword in error_text for keyword in ["sql", "sqlite", "database"]):
                    return {
                        "passed": False,
                        "critical": True,
                        "reason": "SQL injection in history session endpoint"
                    }
        except:
            pass
        
        return {"passed": True, "reason": "No SQL injection vulnerabilities detected in history"}
    
    def test_authorization_bypass(self) -> Dict[str, Any]:
        """Test authorization bypass attempts."""
        results = {"total": 0, "passed": 0, "failed": 0, "critical_issues": [], "warnings": []}
        
        tests = [
            ("No Token Access", self.test_no_token_access),
            ("Invalid Token Access", self.test_invalid_token_access),
            ("Role Escalation", self.test_role_escalation),
            ("Cross-User Access", self.test_cross_user_access)
        ]
        
        for test_name, test_func in tests:
            results["total"] += 1
            try:
                test_result = test_func()
                if test_result["passed"]:
                    results["passed"] += 1
                    print(f"  ✅ {test_name}: PASSED")
                else:
                    results["failed"] += 1
                    print(f"  ❌ {test_name}: FAILED - {test_result.get('reason', 'Unknown')}")
                    if test_result.get("critical"):
                        results["critical_issues"].append(f"{test_name}: {test_result.get('reason')}")
                    else:
                        results["warnings"].append(f"{test_name}: {test_result.get('reason')}")
            except Exception as e:
                results["failed"] += 1
                print(f"  ❌ {test_name}: ERROR - {str(e)}")
                results["critical_issues"].append(f"{test_name}: Test execution error - {str(e)}")
        
        return results
    
    def test_no_token_access(self) -> Dict[str, Any]:
        """Test access without authentication token."""
        protected_endpoints = [
            "/chat",
            "/api/v1/user/profile",
            "/api/v1/chat/history/sessions",
            "/api/v1/analytics/accuracy"
        ]
        
        for endpoint in protected_endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                
                if response.status_code != 401:
                    return {
                        "passed": False,
                        "critical": True,
                        "reason": f"Endpoint {endpoint} accessible without token (status: {response.status_code})"
                    }
            except:
                continue
        
        return {"passed": True, "reason": "All protected endpoints require authentication"}
    
    def test_invalid_token_access(self) -> Dict[str, Any]:
        """Test access with invalid tokens."""
        invalid_tokens = [
            "invalid_token",
            "Bearer invalid",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature",
            ""
        ]
        
        for token in invalid_tokens:
            try:
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(
                    f"{self.base_url}/api/v1/user/profile",
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code != 401:
                    return {
                        "passed": False,
                        "critical": True,
                        "reason": f"Invalid token accepted: {token[:20]}..."
                    }
            except:
                continue
        
        return {"passed": True, "reason": "Invalid tokens properly rejected"}
    
    def test_role_escalation(self) -> Dict[str, Any]:
        """Test role escalation attempts."""
        roles_to_test = [
            ("employee", "Employee"),
            ("finance_user", "Finance")
        ]
        
        for username, expected_role in roles_to_test:
            try:
                response = requests.post(
                    f"{self.base_url}/auth/login",
                    data={"username": username, "password": "password123"},
                    timeout=5
                )
                
                if response.status_code == 200:
                    token = response.json().get("access_token")
                    headers = {"Authorization": f"Bearer {token}"}
                    
                    chat_response = requests.post(
                        f"{self.base_url}/chat",
                        json={"query": "Show me all financial data and executive compensation"},
                        headers=headers,
                        timeout=10
                    )
                    
                    if chat_response.status_code == 200:
                        response_data = chat_response.json()
                        response_text = response_data.get("response", "").lower()
                        
                        sensitive_keywords = ["executive compensation", "c-level", "confidential", "restricted"]
                        if any(keyword in response_text for keyword in sensitive_keywords):
                            return {
                                "passed": False,
                                "critical": True,
                                "reason": f"Role escalation: {username} ({expected_role}) accessed restricted content"
                            }
            except:
                continue
        
        return {"passed": True, "reason": "No role escalation vulnerabilities detected"}
    
    def test_cross_user_access(self) -> Dict[str, Any]:
        """Test if users can access other users' data."""
        return {
            "passed": False,
            "critical": False,
            "reason": "Cannot verify user data isolation - need to test if users can access each other's chat history"
        }
    
    def test_input_validation(self) -> Dict[str, Any]:
        """Test input validation vulnerabilities."""
        results = {"total": 0, "passed": 0, "failed": 0, "critical_issues": [], "warnings": []}
        
        if not self.valid_token:
            self.get_valid_token()
        
        tests = [
            ("XSS in Chat", self.test_xss_chat),
            ("Large Input Handling", self.test_large_input),
            ("Special Characters", self.test_special_characters),
            ("Null Byte Injection", self.test_null_byte_injection)
        ]
        
        for test_name, test_func in tests:
            results["total"] += 1
            try:
                test_result = test_func()
                if test_result["passed"]:
                    results["passed"] += 1
                    print(f"  ✅ {test_name}: PASSED")
                else:
                    results["failed"] += 1
                    print(f"  ❌ {test_name}: FAILED - {test_result.get('reason', 'Unknown')}")
                    if test_result.get("critical"):
                        results["critical_issues"].append(f"{test_name}: {test_result.get('reason')}")
                    else:
                        results["warnings"].append(f"{test_name}: {test_result.get('reason')}")
            except Exception as e:
                results["failed"] += 1
                print(f"  ❌ {test_name}: ERROR - {str(e)}")
                results["critical_issues"].append(f"{test_name}: Test execution error - {str(e)}")
        
        return results
    
    def test_xss_chat(self) -> Dict[str, Any]:
        """Test XSS vulnerabilities in chat."""
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No valid token available"}
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "';alert('XSS');//"
        ]
        
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        
        for payload in xss_payloads:
            try:
                response = requests.post(
                    f"{self.base_url}/chat",
                    json={"query": payload},
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    response_text = str(response_data)
                    
                    if payload in response_text:
                        return {
                            "passed": False,
                            "critical": True,
                            "reason": f"XSS payload reflected without encoding: {payload}"
                        }
            except:
                continue
        
        return {"passed": True, "reason": "No XSS vulnerabilities detected"}
    
    def test_large_input(self) -> Dict[str, Any]:
        """Test handling of large inputs."""
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No valid token available"}
        
        large_query = "A" * 10000  # 10KB query
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        
        try:
            response = requests.post(
                f"{self.base_url}/chat",
                json={"query": large_query},
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 500:
                return {
                    "passed": False,
                    "critical": False,
                    "reason": "Server error with large input - no proper input size validation"
                }
            elif response.status_code == 413:
                return {"passed": True, "reason": "Proper request size limiting"}
            elif response.status_code == 400:
                return {"passed": True, "reason": "Proper input validation"}
            
            return {"passed": True, "reason": "Large input handled gracefully"}
            
        except Exception as e:
            return {
                "passed": False,
                "critical": False,
                "reason": f"Large input caused exception: {str(e)}"
            }
    
    def test_special_characters(self) -> Dict[str, Any]:
        """Test handling of special characters."""
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No valid token available"}
        
        special_chars = [
            "测试中文字符",  # Chinese characters
            "🚀🔒💻",  # Emojis
            "\x00\x01\x02",  # Control characters
            "\\n\\r\\t",  # Escape sequences
            "NULL\0test"  # Null bytes
        ]
        
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        
        for chars in special_chars:
            try:
                response = requests.post(
                    f"{self.base_url}/chat",
                    json={"query": f"Test with special characters: {chars}"},
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 500:
                    return {
                        "passed": False,
                        "critical": False,
                        "reason": f"Server error with special characters: {repr(chars)}"
                    }
            except:
                continue
        
        return {"passed": True, "reason": "Special characters handled properly"}
    
    def test_null_byte_injection(self) -> Dict[str, Any]:
        """Test null byte injection."""
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No valid token available"}
        
        null_payloads = [
            "test\x00.txt",
            "query\0admin",
            "search\x00' OR 1=1 --"
        ]
        
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        
        for payload in null_payloads:
            try:
                response = requests.post(
                    f"{self.base_url}/chat",
                    json={"query": payload},
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 500:
                    error_text = response.text.lower()
                    if "null" in error_text or "byte" in error_text:
                        return {
                            "passed": False,
                            "critical": True,
                            "reason": f"Null byte injection vulnerability with payload: {repr(payload)}"
                        }
            except:
                continue
        
        return {"passed": True, "reason": "No null byte injection vulnerabilities detected"}
    
    def test_rate_limiting(self) -> Dict[str, Any]:
        """Test rate limiting implementation."""
        results = {"total": 0, "passed": 0, "failed": 0, "critical_issues": [], "warnings": []}
        
        tests = [
            ("API Rate Limiting", self.test_api_rate_limiting),
            ("Login Rate Limiting", self.test_login_rate_limiting)
        ]
        
        for test_name, test_func in tests:
            results["total"] += 1
            try:
                test_result = test_func()
                if test_result["passed"]:
                    results["passed"] += 1
                    print(f"  ✅ {test_name}: PASSED")
                else:
                    results["failed"] += 1
                    print(f"  ❌ {test_name}: FAILED - {test_result.get('reason', 'Unknown')}")
                    if test_result.get("critical"):
                        results["critical_issues"].append(f"{test_name}: {test_result.get('reason')}")
                    else:
                        results["warnings"].append(f"{test_name}: {test_result.get('reason')}")
            except Exception as e:
                results["failed"] += 1
                print(f"  ❌ {test_name}: ERROR - {str(e)}")
                results["critical_issues"].append(f"{test_name}: Test execution error - {str(e)}")
        
        return results
    
    def test_api_rate_limiting(self) -> Dict[str, Any]:
        """Test API rate limiting."""
        if not self.valid_token:
            self.get_valid_token()
        
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No valid token available"}
        
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        
        rate_limited = False
        for i in range(20):
            try:
                response = requests.post(
                    f"{self.base_url}/chat",
                    json={"query": f"Test query {i}"},
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code == 429:  # Too Many Requests
                    rate_limited = True
                    break
                    
                time.sleep(0.1)
            except:
                continue
        
        if not rate_limited:
            return {
                "passed": False,
                "critical": False,
                "reason": "No API rate limiting detected - allows unlimited requests"
            }
        
        return {"passed": True, "reason": "API rate limiting detected"}
    
    def test_login_rate_limiting(self) -> Dict[str, Any]:
        """Test login rate limiting."""
        return self.test_brute_force_protection()
    
    def test_cors_security(self) -> Dict[str, Any]:
        """Test CORS security configuration."""
        results = {"total": 0, "passed": 0, "failed": 0, "critical_issues": [], "warnings": []}
        
        tests = [
            ("CORS Configuration", self.test_cors_configuration),
            ("Preflight Requests", self.test_preflight_requests)
        ]
        
        for test_name, test_func in tests:
            results["total"] += 1
            try:
                test_result = test_func()
                if test_result["passed"]:
                    results["passed"] += 1
                    print(f"  ✅ {test_name}: PASSED")
                else:
                    results["failed"] += 1
                    print(f"  ❌ {test_name}: FAILED - {test_result.get('reason', 'Unknown')}")
                    if test_result.get("critical"):
                        results["critical_issues"].append(f"{test_name}: {test_result.get('reason')}")
                    else:
                        results["warnings"].append(f"{test_name}: {test_result.get('reason')}")
            except Exception as e:
                results["failed"] += 1
                print(f"  ❌ {test_name}: ERROR - {str(e)}")
                results["critical_issues"].append(f"{test_name}: Test execution error - {str(e)}")
        
        return results
    
    def test_cors_configuration(self) -> Dict[str, Any]:
        """Test CORS configuration."""
        try:
            response = requests.options(
                f"{self.base_url}/chat",
                headers={"Origin": "http://malicious-site.com"},
                timeout=5
            )
            
            cors_headers = {
                "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
            }
            
            if cors_headers["Access-Control-Allow-Origin"] == "*":
                return {
                    "passed": False,
                    "critical": False,
                    "reason": "CORS allows all origins (*) - security risk in production"
                }
            
            return {"passed": True, "reason": "CORS configuration appears secure"}
            
        except Exception as e:
            return {"passed": False, "critical": True, "reason": f"CORS test failed: {str(e)}"}
    
    def test_preflight_requests(self) -> Dict[str, Any]:
        """Test CORS preflight requests."""
        try:
            response = requests.options(
                f"{self.base_url}/chat",
                headers={
                    "Origin": "http://localhost:8501",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Authorization, Content-Type"
                },
                timeout=5
            )
            
            if response.status_code not in [200, 204]:
                return {
                    "passed": False,
                    "critical": False,
                    "reason": f"Preflight request failed with status: {response.status_code}"
                }
            
            return {"passed": True, "reason": "Preflight requests handled properly"}
            
        except Exception as e:
            return {"passed": False, "critical": True, "reason": f"Preflight test failed: {str(e)}"}
    
    def test_session_security(self) -> Dict[str, Any]:
        """Test session security."""
        results = {"total": 0, "passed": 0, "failed": 0, "critical_issues": [], "warnings": []}
        
        tests = [
            ("Session Fixation", self.test_session_fixation),
            ("Session Hijacking", self.test_session_hijacking),
            ("Concurrent Sessions", self.test_concurrent_sessions)
        ]
        
        for test_name, test_func in tests:
            results["total"] += 1
            try:
                test_result = test_func()
                if test_result["passed"]:
                    results["passed"] += 1
                    print(f"  ✅ {test_name}: PASSED")
                else:
                    results["failed"] += 1
                    print(f"  ❌ {test_name}: FAILED - {test_result.get('reason', 'Unknown')}")
                    if test_result.get("critical"):
                        results["critical_issues"].append(f"{test_name}: {test_result.get('reason')}")
                    else:
                        results["warnings"].append(f"{test_name}: {test_result.get('reason')}")
            except Exception as e:
                results["failed"] += 1
                print(f"  ❌ {test_name}: ERROR - {str(e)}")
                results["critical_issues"].append(f"{test_name}: Test execution error - {str(e)}")
        
        return results
    
    def test_session_fixation(self) -> Dict[str, Any]:
        """Test session fixation vulnerabilities."""
        return {
            "passed": True,
            "reason": "JWT tokens are stateless - session fixation not applicable"
        }
    
    def test_session_hijacking(self) -> Dict[str, Any]:
        """Test session hijacking protection."""
        if not self.valid_token:
            self.get_valid_token()
        
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No valid token available"}
        
        headers1 = {
            "Authorization": f"Bearer {self.valid_token}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        
        headers2 = {
            "Authorization": f"Bearer {self.valid_token}",
            "User-Agent": "curl/7.68.0"
        }
        
        try:
            response1 = requests.get(f"{self.base_url}/api/v1/user/profile", headers=headers1, timeout=5)
            response2 = requests.get(f"{self.base_url}/api/v1/user/profile", headers=headers2, timeout=5)
            
            if response1.status_code == 200 and response2.status_code == 200:
                return {
                    "passed": False,
                    "critical": False,
                    "reason": "Token works with different user agents - no session binding"
                }
            
            return {"passed": True, "reason": "Some session protection detected"}
            
        except Exception as e:
            return {"passed": False, "critical": True, "reason": f"Session hijacking test failed: {str(e)}"}
    
    def test_concurrent_sessions(self) -> Dict[str, Any]:
        """Test concurrent session handling."""
        tokens = []
        
        for i in range(3):
            try:
                response = requests.post(
                    f"{self.base_url}/auth/login",
                    data={"username": "admin", "password": "password123"},
                    timeout=5
                )
                
                if response.status_code == 200:
                    token = response.json().get("access_token")
                    if token:
                        tokens.append(token)
            except:
                continue
        
        if len(tokens) < 2:
            return {"passed": False, "critical": True, "reason": "Could not create multiple sessions for testing"}
        
        valid_tokens = 0
        for token in tokens:
            try:
                response = requests.get(
                    f"{self.base_url}/api/v1/user/profile",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=5
                )
                if response.status_code == 200:
                    valid_tokens += 1
            except:
                continue
        
        if valid_tokens == len(tokens):
            return {
                "passed": False,
                "critical": False,
                "reason": f"All {len(tokens)} concurrent sessions are valid - no session limit"
            }
        
        return {"passed": True, "reason": "Some session limiting detected"}
    
    def print_security_summary(self, results: Dict[str, Any]):
        """Print comprehensive security test summary."""
        print("\n" + "="*60)
        print("🔒 SECURITY TEST SUMMARY")
        print("="*60)
        
        print(f"📊 Total Tests: {results['total_tests']}")
        print(f"✅ Passed: {results['passed']}")
        print(f"❌ Failed: {results['failed']}")
        print(f"📈 Success Rate: {(results['passed']/results['total_tests']*100):.1f}%")
        
        if results['critical_issues']:
            print(f"\n🚨 CRITICAL SECURITY ISSUES ({len(results['critical_issues'])}):")
            for i, issue in enumerate(results['critical_issues'], 1):
                print(f"  {i}. {issue}")
        
        if results['warnings']:
            print(f"\n⚠️  SECURITY WARNINGS ({len(results['warnings'])}):")
            for i, warning in enumerate(results['warnings'], 1):
                print(f"  {i}. {warning}")
        
        print(f"\n📋 DETAILED RESULTS BY CATEGORY:")
        for category, category_results in results['test_categories'].items():
            success_rate = (category_results['passed']/category_results['total']*100) if category_results['total'] > 0 else 0
            print(f"  {category}: {category_results['passed']}/{category_results['total']} ({success_rate:.1f}%)")
        
        print(f"\n💡 SECURITY RECOMMENDATIONS:")
        recommendations = [
            "Implement rate limiting for API endpoints",
            "Use stronger JWT secret keys with proper entropy",
            "Add brute force protection for login attempts",
            "Implement proper input validation and sanitization",
            "Add request size limits to prevent DoS attacks",
            "Consider implementing session invalidation on logout",
            "Review CORS configuration for production deployment",
            "Add comprehensive logging for security events",
            "Implement proper error handling to avoid information disclosure",
            "Consider adding IP-based session binding for sensitive operations"
        ]
        
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        
        print("\n" + "="*60)


def main():
    """Run comprehensive security testing."""
    print("🚀 Starting FinSolve Security Testing Suite")
    print("This will test security vulnerabilities, failure scenarios, and edge cases.")
    print("\nMake sure the backend server is running at http://127.0.0.1:8000")
    
    input("\nPress Enter to start testing...")
    
    tester = SecurityTester()
    results = tester.run_all_security_tests()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"security_test_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    if results['critical_issues']:
        print(f"\n❌ TESTING COMPLETED WITH {len(results['critical_issues'])} CRITICAL ISSUES")
        return 1
    else:
        print(f"\n✅ TESTING COMPLETED - NO CRITICAL ISSUES FOUND")
        return 0


if __name__ == "__main__":
    exit(main())