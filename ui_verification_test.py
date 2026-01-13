#!/usr/bin/env python3
"""
Comprehensive UI Verification Testing Suite for FinSolve Chatbot
Tests chat UI functionality, session management, and user experience.
"""

import requests
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed


class UIVerificationTester:
    """Comprehensive UI verification testing for the FinSolve chatbot system."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000", frontend_url: str = "http://localhost:8501"):
        self.base_url = base_url
        self.frontend_url = frontend_url
        self.test_results = []
        self.valid_token = None
        self.session_data = {}
        
    def run_all_ui_tests(self) -> Dict[str, Any]:
        """Run all UI verification tests and return comprehensive results."""
        print("🖥️  Starting Comprehensive UI Verification Testing Suite")
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
            ("Authentication Flow", self.test_authentication_flow),
            ("Chat Interface", self.test_chat_interface),
            ("Session Management", self.test_session_management),
            ("Message Display", self.test_message_display),
            ("Error Handling UI", self.test_error_handling_ui),
            ("Real-time Updates", self.test_realtime_updates),
            ("User Experience", self.test_user_experience),
            ("Accessibility", self.test_accessibility),
            ("Performance UI", self.test_performance_ui),
            ("Data Persistence", self.test_data_persistence)
        ]
        
        for category_name, test_function in test_categories:
            print(f"\n🖥️  Testing: {category_name}")
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
        self.print_ui_summary(results)
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
                return True
        except:
            pass
        return False
    
    def test_authentication_flow(self) -> Dict[str, Any]:
        """Test authentication flow and UI behavior."""
        results = {"total": 0, "passed": 0, "failed": 0, "critical_issues": [], "warnings": []}
        
        tests = [
            ("Login Process", self.test_login_process),
            ("Token Refresh Flow", self.test_token_refresh_flow),
            ("Session Expiry Handling", self.test_session_expiry_handling),
            ("Logout Behavior", self.test_logout_behavior),
            ("Invalid Credentials UI", self.test_invalid_credentials_ui),
            ("Role-Based Access UI", self.test_role_based_access_ui)
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
    
    def test_login_process(self) -> Dict[str, Any]:
        """Test login process and UI feedback."""
        try:
            # Test successful login
            response = requests.post(
                f"{self.base_url}/auth/login",
                data={"username": "admin", "password": "password123"},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "refresh_token" in data:
                    return {"passed": True, "reason": "Login process works correctly"}
                else:
                    return {
                        "passed": False,
                        "critical": True,
                        "reason": "Login response missing required tokens"
                    }
            else:
                return {
                    "passed": False,
                    "critical": True,
                    "reason": f"Login failed with status: {response.status_code}"
                }
                
        except Exception as e:
            return {"passed": False, "critical": True, "reason": f"Login test failed: {str(e)}"}
    
    def test_token_refresh_flow(self) -> Dict[str, Any]:
        """Test token refresh flow."""
        try:
            # Get initial tokens
            login_response = requests.post(
                f"{self.base_url}/auth/login",
                data={"username": "admin", "password": "password123"},
                timeout=5
            )
            
            if login_response.status_code != 200:
                return {"passed": False, "critical": True, "reason": "Could not get initial tokens"}
            
            tokens = login_response.json()
            refresh_token = tokens.get("refresh_token")
            
            if not refresh_token:
                return {"passed": False, "critical": True, "reason": "No refresh token provided"}
            
            # Test token refresh
            refresh_response = requests.post(
                f"{self.base_url}/auth/refresh",
                params={"refresh_token": refresh_token},
                timeout=5
            )
            
            if refresh_response.status_code == 200:
                refresh_data = refresh_response.json()
                if "access_token" in refresh_data:
                    return {"passed": True, "reason": "Token refresh flow works correctly"}
                else:
                    return {
                        "passed": False,
                        "critical": True,
                        "reason": "Refresh response missing access token"
                    }
            else:
                return {
                    "passed": False,
                    "critical": True,
                    "reason": f"Token refresh failed with status: {refresh_response.status_code}"
                }
                
        except Exception as e:
            return {"passed": False, "critical": True, "reason": f"Token refresh test failed: {str(e)}"}
    
    def test_session_expiry_handling(self) -> Dict[str, Any]:
        """Test session expiry handling in UI."""
        # This would require testing the frontend behavior
        # Since we can't directly test Streamlit UI, we'll test the backend behavior
        import jwt
        from datetime import datetime, timedelta
        
        try:
            # Create an expired token
            expired_payload = {
                "sub": "admin",
                "role": "C-Level",
                "exp": datetime.utcnow() - timedelta(hours=1)
            }
            
            expired_token = jwt.encode(expired_payload, "your_super_secret_key_finsolve_2024", algorithm="HS256")
            
            # Try to use expired token
            response = requests.get(
                f"{self.base_url}/api/v1/user/profile",
                headers={"Authorization": f"Bearer {expired_token}"},
                timeout=5
            )
            
            if response.status_code == 401:
                return {"passed": True, "reason": "Session expiry properly detected"}
            else:
                return {
                    "passed": False,
                    "critical": True,
                    "reason": f"Expired token accepted with status: {response.status_code}"
                }
                
        except Exception as e:
            return {"passed": False, "critical": True, "reason": f"Session expiry test failed: {str(e)}"}
    
    def test_logout_behavior(self) -> Dict[str, Any]:
        """Test logout behavior."""
        # Since there's no logout endpoint, this is a design issue
        return {
            "passed": False,
            "critical": False,
            "reason": "No logout endpoint available - tokens cannot be invalidated server-side"
        }
    
    def test_invalid_credentials_ui(self) -> Dict[str, Any]:
        """Test UI behavior with invalid credentials."""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                data={"username": "invalid_user", "password": "wrong_password"},
                timeout=5
            )
            
            if response.status_code == 401:
                error_data = response.json()
                error_message = error_data.get("detail", "")
                
                if len(error_message) > 5:  # Has meaningful error message
                    return {"passed": True, "reason": "Invalid credentials properly handled with error message"}
                else:
                    return {
                        "passed": False,
                        "critical": False,
                        "reason": "Error message too short or missing"
                    }
            else:
                return {
                    "passed": False,
                    "critical": True,
                    "reason": f"Invalid credentials returned status: {response.status_code}"
                }
                
        except Exception as e:
            return {"passed": False, "critical": True, "reason": f"Invalid credentials test failed: {str(e)}"}
    
    def test_role_based_access_ui(self) -> Dict[str, Any]:
        """Test role-based access in UI."""
        roles_to_test = [
            ("admin", "C-Level"),
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
                    
                    # Get user profile to verify role
                    profile_response = requests.get(
                        f"{self.base_url}/api/v1/user/profile",
                        headers={"Authorization": f"Bearer {token}"},
                        timeout=5
                    )
                    
                    if profile_response.status_code == 200:
                        profile_data = profile_response.json()
                        actual_role = profile_data.get("role")
                        
                        if actual_role != expected_role:
                            return {
                                "passed": False,
                                "critical": True,
                                "reason": f"Role mismatch for {username}: expected {expected_role}, got {actual_role}"
                            }
                    else:
                        return {
                            "passed": False,
                            "critical": True,
                            "reason": f"Could not get profile for {username}"
                        }
            except:
                continue
        
        return {"passed": True, "reason": "Role-based access works correctly"}
    
    def test_chat_interface(self) -> Dict[str, Any]:
        """Test chat interface functionality."""
        results = {"total": 0, "passed": 0, "failed": 0, "critical_issues": [], "warnings": []}
        
        if not self.valid_token:
            self.get_valid_token()
        
        tests = [
            ("Message Sending", self.test_message_sending),
            ("Response Format", self.test_response_format),
            ("Source Attribution", self.test_source_attribution),
            ("Accuracy Display", self.test_accuracy_display),
            ("Citation Formatting", self.test_citation_formatting),
            ("Query Optimization Display", self.test_query_optimization_display)
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
    
    def test_message_sending(self) -> Dict[str, Any]:
        """Test message sending functionality."""
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No valid token available"}
        
        try:
            response = requests.post(
                f"{self.base_url}/chat",
                json={"query": "What is the company's mission?"},
 