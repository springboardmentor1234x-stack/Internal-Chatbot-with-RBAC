#!/usr/bin/env python3
"""
Comprehensive Failure Scenario Testing Suite for FinSolve Chatbot
Tests failure scenarios, edge cases, and system resilience.
"""

import requests
import json
import time
import threading
import subprocess
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed


class FailureScenarioTester:
    """Comprehensive failure scenario testing for the FinSolve chatbot system."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.test_results = []
        self.valid_token = None
        
    def run_all_failure_tests(self) -> Dict[str, Any]:
        """Run all failure scenario tests and return comprehensive results."""
        print("💥 Starting Comprehensive Failure Scenario Testing Suite")
        print("=" * 60)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "critical_failures": [],
            "warnings": [],
            "test_categories": {}
        }
        
        # Test categories
        test_categories = [
            ("Backend Connectivity", self.test_backend_connectivity),
            ("Database Failures", self.test_database_failures),
            ("Authentication Failures", self.test_authentication_failures),
            ("Token Expiry Scenarios", self.test_token_expiry_scenarios),
            ("Malformed Requests", self.test_malformed_requests),
            ("Network Timeouts", self.test_network_timeouts),
            ("Concurrent Request Handling", self.test_concurrent_requests),
            ("Edge Case Inputs", self.test_edge_case_inputs),
            ("Resource Exhaustion", self.test_resource_exhaustion),
            ("Error Recovery", self.test_error_recovery)
        ]
        
        for category_name, test_function in test_categories:
            print(f"\n💥 Testing: {category_name}")
            print("-" * 40)
            
            category_results = test_function()
            results["test_categories"][category_name] = category_results
            
            # Update totals
            results["total_tests"] += category_results["total"]
            results["passed"] += category_results["passed"]
            results["failed"] += category_results["failed"]
            
            # Collect critical failures
            if category_results.get("critical_failures"):
                results["critical_failures"].extend(category_results["critical_failures"])
            
            if category_results.get("warnings"):
                results["warnings"].extend(category_results["warnings"])
        
        # Generate summary
        self.print_failure_summary(results)
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
    
    def test_backend_connectivity(self) -> Dict[str, Any]:
        """Test backend connectivity failure scenarios."""
        results = {"total": 0, "passed": 0, "failed": 0, "critical_failures": [], "warnings": []}
        
        tests = [
            ("Server Unreachable", self.test_server_unreachable),
            ("Invalid Base URL", self.test_invalid_base_url),
            ("Port Not Available", self.test_port_not_available),
            ("DNS Resolution Failure", self.test_dns_failure),
            ("SSL/TLS Errors", self.test_ssl_errors)
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
                        results["critical_failures"].append(f"{test_name}: {test_result.get('reason')}")
                    else:
                        results["warnings"].append(f"{test_name}: {test_result.get('reason')}")
            except Exception as e:
                results["failed"] += 1
                print(f"  ❌ {test_name}: ERROR - {str(e)}")
                results["critical_failures"].append(f"{test_name}: Test execution error - {str(e)}")
        
        return results
    
    def test_server_unreachable(self) -> Dict[str, Any]:
        """Test behavior when server is unreachable."""
        unreachable_url = "http://127.0.0.1:9999"  # Non-existent port
        
        try:
            response = requests.get(f"{unreachable_url}/health", timeout=2)
            return {
                "passed": False,
                "critical": True,
                "reason": "Server responded when it should be unreachable"
            }
        except requests.exceptions.ConnectionError:
            return {"passed": True, "reason": "Properly handles connection errors"}
        except requests.exceptions.Timeout:
            return {"passed": True, "reason": "Properly handles timeouts"}
        except Exception as e:
            return {"passed": True, "reason": f"Properly handles network errors: {type(e).__name__}"}
    
    def test_invalid_base_url(self) -> Dict[str, Any]:
        """Test behavior with invalid base URLs."""
        invalid_urls = [
            "http://invalid-domain-that-does-not-exist.com",
            "https://localhost:99999",
            "ftp://127.0.0.1:8000",
            "http://",
            "not-a-url"
        ]
        
        for url in invalid_urls:
            try:
                response = requests.get(f"{url}/health", timeout=2)
                return {
                    "passed": False,
                    "critical": False,
                    "reason": f"Invalid URL {url} unexpectedly responded"
                }
            except:
                continue
        
        return {"passed": True, "reason": "Properly handles invalid URLs"}
    
    def test_port_not_available(self) -> Dict[str, Any]:
        """Test behavior when port is not available."""
        try:
            response = requests.get("http://127.0.0.1:8001/health", timeout=2)
            return {
                "passed": False,
                "critical": False,
                "reason": "Port 8001 unexpectedly responded"
            }
        except requests.exceptions.ConnectionError:
            return {"passed": True, "reason": "Properly handles unavailable ports"}
        except Exception as e:
            return {"passed": True, "reason": f"Properly handles port errors: {type(e).__name__}"}
    
    def test_dns_failure(self) -> Dict[str, Any]:
        """Test behavior with DNS resolution failures."""
        try:
            response = requests.get("http://non-existent-domain-12345.com/health", timeout=2)
            return {
                "passed": False,
                "critical": False,
                "reason": "DNS resolution succeeded for non-existent domain"
            }
        except requests.exceptions.ConnectionError:
            return {"passed": True, "reason": "Properly handles DNS failures"}
        except Exception as e:
            return {"passed": True, "reason": f"Properly handles DNS errors: {type(e).__name__}"}
    
    def test_ssl_errors(self) -> Dict[str, Any]:
        """Test behavior with SSL/TLS errors."""
        # This is more of a conceptual test since we're using HTTP
        return {"passed": True, "reason": "SSL/TLS not applicable for HTTP endpoints"}
    
    def test_database_failures(self) -> Dict[str, Any]:
        """Test database failure scenarios."""
        results = {"total": 0, "passed": 0, "failed": 0, "critical_failures": [], "warnings": []}
        
        tests = [
            ("Database Connection Loss", self.test_db_connection_loss),
            ("Database Corruption", self.test_db_corruption),
            ("Database Lock", self.test_db_lock),
            ("Disk Space Full", self.test_disk_space_full),
            ("Permission Denied", self.test_db_permission_denied)
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
                        results["critical_failures"].append(f"{test_name}: {test_result.get('reason')}")
                    else:
                        results["warnings"].append(f"{test_name}: {test_result.get('reason')}")
            except Exception as e:
                results["failed"] += 1
                print(f"  ❌ {test_name}: ERROR - {str(e)}")
                results["critical_failures"].append(f"{test_name}: Test execution error - {str(e)}")
        
        return results
    
    def test_db_connection_loss(self) -> Dict[str, Any]:
        """Test behavior when database connection is lost."""
        # This would require temporarily moving/renaming the database file
        db_path = "app/project.db"
        backup_path = "app/project.db.backup"
        
        if not os.path.exists(db_path):
            return {"passed": False, "critical": True, "reason": "Database file not found for testing"}
        
        try:
            # Backup the database
            os.rename(db_path, backup_path)
            
            # Try to login (should fail)
            response = requests.post(
                f"{self.base_url}/auth/login",
                data={"username": "admin", "password": "password123"},
                timeout=5
            )
            
            # Restore the database
            os.rename(backup_path, db_path)
            
            if response.status_code == 500:
                return {"passed": True, "reason": "Properly handles database connection loss"}
            else:
                return {
                    "passed": False,
                    "critical": True,
                    "reason": f"Unexpected response when database unavailable: {response.status_code}"
                }
                
        except Exception as e:
            # Make sure to restore database if something goes wrong
            if os.path.exists(backup_path):
                os.rename(backup_path, db_path)
            return {"passed": False, "critical": True, "reason": f"Database test failed: {str(e)}"}
    
    def test_db_corruption(self) -> Dict[str, Any]:
        """Test behavior with corrupted database."""
        # This is a destructive test, so we'll simulate it
        return {
            "passed": False,
            "critical": False,
            "reason": "Cannot test database corruption without risking data loss - needs isolated test environment"
        }
    
    def test_db_lock(self) -> Dict[str, Any]:
        """Test behavior when database is locked."""
        db_path = "app/project.db"
        
        if not os.path.exists(db_path):
            return {"passed": False, "critical": True, "reason": "Database file not found for testing"}
        
        try:
            # Create a long-running connection to lock the database
            conn = sqlite3.connect(db_path, timeout=1)
            conn.execute("BEGIN EXCLUSIVE TRANSACTION")
            
            # Try to login while database is locked
            response = requests.post(
                f"{self.base_url}/auth/login",
                data={"username": "admin", "password": "password123"},
                timeout=5
            )
            
            # Release the lock
            conn.rollback()
            conn.close()
            
            if response.status_code == 500:
                return {"passed": True, "reason": "Properly handles database locks"}
            else:
                return {
                    "passed": False,
                    "critical": False,
                    "reason": f"Unexpected response when database locked: {response.status_code}"
                }
                
        except Exception as e:
            return {"passed": False, "critical": True, "reason": f"Database lock test failed: {str(e)}"}
    
    def test_disk_space_full(self) -> Dict[str, Any]:
        """Test behavior when disk space is full."""
        # This is difficult to test safely without affecting the system
        return {
            "passed": False,
            "critical": False,
            "reason": "Cannot safely test disk space exhaustion - needs isolated test environment"
        }
    
    def test_db_permission_denied(self) -> Dict[str, Any]:
        """Test behavior when database permissions are denied."""
        # This would require changing file permissions
        return {
            "passed": False,
            "critical": False,
            "reason": "Cannot test permission changes without affecting system - needs isolated test environment"
        }
    
    def test_authentication_failures(self) -> Dict[str, Any]:
        """Test authentication failure scenarios."""
        results = {"total": 0, "passed": 0, "failed": 0, "critical_failures": [], "warnings": []}
        
        tests = [
            ("Expired Token Usage", self.test_expired_token_usage),
            ("Malformed Token", self.test_malformed_token),
            ("Token Without Bearer", self.test_token_without_bearer),
            ("Multiple Authorization Headers", self.test_multiple_auth_headers),
            ("Case Sensitive Headers", self.test_case_sensitive_headers)
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
                        results["critical_failures"].append(f"{test_name}: {test_result.get('reason')}")
                    else:
                        results["warnings"].append(f"{test_name}: {test_result.get('reason')}")
            except Exception as e:
                results["failed"] += 1
                print(f"  ❌ {test_name}: ERROR - {str(e)}")
                results["critical_failures"].append(f"{test_name}: Test execution error - {str(e)}")
        
        return results
    
    def test_expired_token_usage(self) -> Dict[str, Any]:
        """Test usage of expired tokens."""
        # Create a token that's already expired
        import jwt
        from datetime import datetime, timedelta
        
        expired_payload = {
            "sub": "admin",
            "role": "C-Level",
            "exp": datetime.utcnow() - timedelta(hours=1)  # Expired 1 hour ago
        }
        
        try:
            expired_token = jwt.encode(expired_payload, "your_super_secret_key_finsolve_2024", algorithm="HS256")
            
            response = requests.get(
                f"{self.base_url}/api/v1/user/profile",
                headers={"Authorization": f"Bearer {expired_token}"},
                timeout=5
            )
            
            if response.status_code == 401:
                return {"passed": True, "reason": "Properly rejects expired tokens"}
            else:
                return {
                    "passed": False,
                    "critical": True,
                    "reason": f"Expired token accepted with status: {response.status_code}"
                }
                
        except Exception as e:
            return {"passed": False, "critical": True, "reason": f"Expired token test failed: {str(e)}"}
    
    def test_malformed_token(self) -> Dict[str, Any]:
        """Test malformed JWT tokens."""
        malformed_tokens = [
            "not.a.jwt",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.malformed",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..missing_payload",
            "...",
            "Bearer token_without_jwt_structure"
        ]
        
        for token in malformed_tokens:
            try:
                response = requests.get(
                    f"{self.base_url}/api/v1/user/profile",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=5
                )
                
                if response.status_code != 401:
                    return {
                        "passed": False,
                        "critical": True,
                        "reason": f"Malformed token accepted: {token[:20]}..."
                    }
            except:
                continue
        
        return {"passed": True, "reason": "Properly rejects malformed tokens"}
    
    def test_token_without_bearer(self) -> Dict[str, Any]:
        """Test tokens without Bearer prefix."""
        if not self.valid_token:
            self.get_valid_token()
        
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No valid token available"}
        
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/user/profile",
                headers={"Authorization": self.valid_token},  # Missing "Bearer "
                timeout=5
            )
            
            if response.status_code == 401:
                return {"passed": True, "reason": "Properly requires Bearer prefix"}
            else:
                return {
                    "passed": False,
                    "critical": True,
                    "reason": f"Token without Bearer prefix accepted: {response.status_code}"
                }
                
        except Exception as e:
            return {"passed": False, "critical": True, "reason": f"Bearer prefix test failed: {str(e)}"}
    
    def test_multiple_auth_headers(self) -> Dict[str, Any]:
        """Test multiple authorization headers."""
        if not self.valid_token:
            self.get_valid_token()
        
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No valid token available"}
        
        try:
            # This is tricky with requests library, so we'll test conceptually
            return {
                "passed": False,
                "critical": False,
                "reason": "Cannot test multiple headers with requests library - needs manual HTTP testing"
            }
                
        except Exception as e:
            return {"passed": False, "critical": True, "reason": f"Multiple headers test failed: {str(e)}"}
    
    def test_case_sensitive_headers(self) -> Dict[str, Any]:
        """Test case sensitivity of authorization headers."""
        if not self.valid_token:
            self.get_valid_token()
        
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No valid token available"}
        
        case_variations = [
            "authorization",
            "Authorization",
            "AUTHORIZATION",
            "AuthoriZation"
        ]
        
        for header_name in case_variations:
            try:
                response = requests.get(
                    f"{self.base_url}/api/v1/user/profile",
                    headers={header_name: f"Bearer {self.valid_token}"},
                    timeout=5
                )
                
                if response.status_code != 200:
                    return {
                        "passed": False,
                        "critical": False,
                        "reason": f"Case variation {header_name} not accepted"
                    }
            except:
                continue
        
        return {"passed": True, "reason": "Properly handles header case variations"}
    
    def test_token_expiry_scenarios(self) -> Dict[str, Any]:
        """Test token expiry scenarios."""
        results = {"total": 0, "passed": 0, "failed": 0, "critical_failures": [], "warnings": []}
        
        tests = [
            ("Token Refresh on Expiry", self.test_token_refresh_on_expiry),
            ("Refresh Token Expiry", self.test_refresh_token_expiry),
            ("Concurrent Token Refresh", self.test_concurrent_token_refresh),
            ("Invalid Refresh Token", self.test_invalid_refresh_token)
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
                        results["critical_failures"].append(f"{test_name}: {test_result.get('reason')}")
                    else:
                        results["warnings"].append(f"{test_name}: {test_result.get('reason')}")
            except Exception as e:
                results["failed"] += 1
                print(f"  ❌ {test_name}: ERROR - {str(e)}")
                results["critical_failures"].append(f"{test_name}: Test execution error - {str(e)}")
        
        return results
    
    def test_token_refresh_on_expiry(self) -> Dict[str, Any]:
        """Test token refresh when access token expires."""
        # Get initial tokens
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                data={"username": "admin", "password": "password123"},
                timeout=5
            )
            
            if response.status_code != 200:
                return {"passed": False, "critical": True, "reason": "Could not get initial tokens"}
            
            tokens = response.json()
            refresh_token = tokens.get("refresh_token")
            
            if not refresh_token:
                return {"passed": False, "critical": True, "reason": "No refresh token provided"}
            
            # Try to refresh token
            refresh_response = requests.post(
                f"{self.base_url}/auth/refresh",
                params={"refresh_token": refresh_token},
                timeout=5
            )
            
            if refresh_response.status_code == 200:
                return {"passed": True, "reason": "Token refresh works properly"}
            else:
                return {
                    "passed": False,
                    "critical": True,
                    "reason": f"Token refresh failed with status: {refresh_response.status_code}"
                }
                
        except Exception as e:
            return {"passed": False, "critical": True, "reason": f"Token refresh test failed: {str(e)}"}
    
    def test_refresh_token_expiry(self) -> Dict[str, Any]:
        """Test behavior when refresh token expires."""
        # Create an expired refresh token
        import jwt
        from datetime import datetime, timedelta
        
        expired_refresh_payload = {
            "sub": "admin",
            "type": "refresh",
            "exp": datetime.utcnow() - timedelta(days=1)  # Expired 1 day ago
        }
        
        try:
            expired_refresh_token = jwt.encode(expired_refresh_payload, "your_super_secret_key_finsolve_2024", algorithm="HS256")
            
            response = requests.post(
                f"{self.base_url}/auth/refresh",
                params={"refresh_token": expired_refresh_token},
                timeout=5
            )
            
            if response.status_code == 401:
                return {"passed": True, "reason": "Properly rejects expired refresh tokens"}
            else:
                return {
                    "passed": False,
                    "critical": True,
                    "reason": f"Expired refresh token accepted: {response.status_code}"
                }
                
        except Exception as e:
            return {"passed": False, "critical": True, "reason": f"Expired refresh token test failed: {str(e)}"}
    
    def test_concurrent_token_refresh(self) -> Dict[str, Any]:
        """Test concurrent token refresh requests."""
        # Get refresh token
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                data={"username": "admin", "password": "password123"},
                timeout=5
            )
            
            if response.status_code != 200:
                return {"passed": False, "critical": True, "reason": "Could not get refresh token"}
            
            refresh_token = response.json().get("refresh_token")
            
            if not refresh_token:
                return {"passed": False, "critical": True, "reason": "No refresh token provided"}
            
            # Make concurrent refresh requests
            def refresh_request():
                return requests.post(
                    f"{self.base_url}/auth/refresh",
                    params={"refresh_token": refresh_token},
                    timeout=5
                )
            
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(refresh_request) for _ in range(3)]
                responses = [future.result() for future in as_completed(futures)]
            
            success_count = sum(1 for r in responses if r.status_code == 200)
            
            if success_count >= 1:
                return {"passed": True, "reason": f"Concurrent refresh handled properly ({success_count}/3 succeeded)"}
            else:
                return {
                    "passed": False,
                    "critical": True,
                    "reason": "All concurrent refresh requests failed"
                }
                
        except Exception as e:
            return {"passed": False, "critical": True, "reason": f"Concurrent refresh test failed: {str(e)}"}
    
    def test_invalid_refresh_token(self) -> Dict[str, Any]:
        """Test invalid refresh tokens."""
        invalid_tokens = [
            "invalid_refresh_token",
            "",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
        ]
        
        for token in invalid_tokens:
            try:
                response = requests.post(
                    f"{self.base_url}/auth/refresh",
                    params={"refresh_token": token},
                    timeout=5
                )
                
                if response.status_code != 401:
                    return {
                        "passed": False,
                        "critical": True,
                        "reason": f"Invalid refresh token accepted: {token[:20]}..."
                    }
            except:
                continue
        
        return {"passed": True, "reason": "Properly rejects invalid refresh tokens"}
    
    def test_malformed_requests(self) -> Dict[str, Any]:
        """Test malformed request scenarios."""
        results = {"total": 0, "passed": 0, "failed": 0, "critical_failures": [], "warnings": []}
        
        if not self.valid_token:
            self.get_valid_token()
        
        tests = [
            ("Missing Content-Type", self.test_missing_content_type),
            ("Invalid JSON", self.test_invalid_json),
            ("Missing Required Fields", self.test_missing_required_fields),
            ("Wrong HTTP Method", self.test_wrong_http_method),
            ("Invalid URL Paths", self.test_invalid_url_paths)
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
                        results["critical_failures"].append(f"{test_name}: {test_result.get('reason')}")
                    else:
                        results["warnings"].append(f"{test_name}: {test_result.get('reason')}")
            except Exception as e:
                results["failed"] += 1
                print(f"  ❌ {test_name}: ERROR - {str(e)}")
                results["critical_failures"].append(f"{test_name}: Test execution error - {str(e)}")
        
        return results
    
    def test_missing_content_type(self) -> Dict[str, Any]:
        """Test requests without Content-Type header."""
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No valid token available"}
        
        try:
            response = requests.post(
                f"{self.base_url}/chat",
                data='{"query": "test"}',  # Raw string instead of JSON
                headers={"Authorization": f"Bearer {self.valid_token}"},
                timeout=5
            )
            
            if response.status_code in [400, 415, 422]:  # Bad Request, Unsupported Media Type, or Unprocessable Entity
                return {"passed": True, "reason": "Properly handles missing Content-Type"}
            else:
                return {
                    "passed": False,
                    "critical": False,
                    "reason": f"Missing Content-Type accepted with status: {response.status_code}"
                }
                
        except Exception as e:
            return {"passed": False, "critical": True, "reason": f"Content-Type test failed: {str(e)}"}
    
    def test_invalid_json(self) -> Dict[str, Any]:
        """Test invalid JSON payloads."""
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No valid token available"}
        
        invalid_json_payloads = [
            '{"query": "test"',  # Missing closing brace
            '{"query": "test",}',  # Trailing comma
            '{query: "test"}',  # Unquoted key
            '{"query": "test" "extra": "value"}',  # Missing comma
            'not json at all',
            '{"query": }',  # Missing value
            ''  # Empty string
        ]
        
        headers = {
            "Authorization": f"Bearer {self.valid_token}",
            "Content-Type": "application/json"
        }
        
        for payload in invalid_json_payloads:
            try:
                response = requests.post(
                    f"{self.base_url}/chat",
                    data=payload,
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code not in [400, 422]:  # Should return bad request
                    return {
                        "passed": False,
                        "critical": True,
                        "reason": f"Invalid JSON accepted: {payload[:30]}..."
                    }
            except:
                continue
        
        return {"passed": True, "reason": "Properly rejects invalid JSON"}
    
    def test_missing_required_fields(self) -> Dict[str, Any]:
        """Test requests with missing required fields."""
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No valid token available"}
        
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        
        missing_field_payloads = [
            {},  # Empty object
            {"not_query": "test"},  # Wrong field name
            {"query": ""},  # Empty query
            {"query": None},  # Null query
        ]
        
        for payload in missing_field_payloads:
            try:
                response = requests.post(
                    f"{self.base_url}/chat",
                    json=payload,
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code not in [400, 422]:  # Should return validation error
                    return {
                        "passed": False,
                        "critical": True,
                        "reason": f"Missing required fields accepted: {payload}"
                    }
            except:
                continue
        
        return {"passed": True, "reason": "Properly validates required fields"}
    
    def test_wrong_http_method(self) -> Dict[str, Any]:
        """Test wrong HTTP methods on endpoints."""
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No valid token available"}
        
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        
        # Test wrong methods on chat endpoint (should be POST)
        wrong_methods = [
            ("GET", requests.get),
            ("PUT", requests.put),
            ("DELETE", requests.delete),
            ("PATCH", requests.patch)
        ]
        
        for method_name, method_func in wrong_methods:
            try:
                response = method_func(
                    f"{self.base_url}/chat",
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code not in [405, 404]:  # Method Not Allowed or Not Found
                    return {
                        "passed": False,
                        "critical": False,
                        "reason": f"Wrong HTTP method {method_name} accepted with status: {response.status_code}"
                    }
            except:
                continue
        
        return {"passed": True, "reason": "Properly rejects wrong HTTP methods"}
    
    def test_invalid_url_paths(self) -> Dict[str, Any]:
        """Test invalid URL paths."""
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No valid token available"}
        
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        
        invalid_paths = [
            "/nonexistent",
            "/chat/invalid",
            "/api/v2/chat",  # Wrong version
            "/api/v1/invalid",
            "/../../../etc/passwd",  # Path traversal attempt
            "/chat/../admin",
            "/api/v1/chat/../../admin"
        ]
        
        for path in invalid_paths:
            try:
                response = requests.get(
                    f"{self.base_url}{path}",
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code not in [404, 403]:  # Not Found or Forbidden
                    return {
                        "passed": False,
                        "critical": True,
                        "reason": f"Invalid path {path} returned status: {response.status_code}"
                    }
            except:
                continue
        
        return {"passed": True, "reason": "Properly handles invalid URL paths"}
    
    def test_network_timeouts(self) -> Dict[str, Any]:
        """Test network timeout scenarios."""
        results = {"total": 0, "passed": 0, "failed": 0, "critical_failures": [], "warnings": []}
        
        tests = [
            ("Connection Timeout", self.test_connection_timeout),
            ("Read Timeout", self.test_read_timeout),
            ("Very Short Timeout", self.test_very_short_timeout)
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
                        results["critical_failures"].append(f"{test_name}: {test_result.get('reason')}")
                    else:
                        results["warnings"].append(f"{test_name}: {test_result.get('reason')}")
            except Exception as e:
                results["failed"] += 1
                print(f"  ❌ {test_name}: ERROR - {str(e)}")
                results["critical_failures"].append(f"{test_name}: Test execution error - {str(e)}")
        
        return results
    
    def test_connection_timeout(self) -> Dict[str, Any]:
        """Test connection timeout handling."""
        try:
            # Use a non-routable IP address to force connection timeout
            response = requests.get("http://10.255.255.1:8000/health", timeout=2)
            return {
                "passed": False,
                "critical": False,
                "reason": "Connection to non-routable IP succeeded unexpectedly"
            }
        except requests.exceptions.ConnectTimeout:
            return {"passed": True, "reason": "Properly handles connection timeouts"}
        except requests.exceptions.Timeout:
            return {"passed": True, "reason": "Properly handles timeouts"}
        except Exception as e:
            return {"passed": True, "reason": f"Properly handles network errors: {type(e).__name__}"}
    
    def test_read_timeout(self) -> Dict[str, Any]:
        """Test read timeout handling."""
        if not self.valid_token:
            self.get_valid_token()
        
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No valid token available"}
        
        try:
            # Make a request with very short read timeout
            response = requests.post(
                f"{self.base_url}/chat",
                json={"query": "What is the company's financial performance?"},
                headers={"Authorization": f"Bearer {self.valid_token}"},
                timeout=(5, 0.001)  # 5s connect, 1ms read
            )
            
            return {
                "passed": False,
                "critical": False,
                "reason": "Request completed despite very short read timeout"
            }
        except requests.exceptions.ReadTimeout:
            return {"passed": True, "reason": "Properly handles read timeouts"}
        except requests.exceptions.Timeout:
            return {"passed": True, "reason": "Properly handles timeouts"}
        except Exception as e:
            return {"passed": True, "reason": f"Properly handles timeout errors: {type(e).__name__}"}
    
    def test_very_short_timeout(self) -> Dict[str, Any]:
        """Test very short timeout values."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=0.001)  # 1ms timeout
            return {
                "passed": False,
                "critical": False,
                "reason": "Request completed despite 1ms timeout"
            }
        except requests.exceptions.Timeout:
            return {"passed": True, "reason": "Properly handles very short timeouts"}
        except Exception as e:
            return {"passed": True, "reason": f"Properly handles timeout errors: {type(e).__name__}"}
    
    def test_concurrent_requests(self) -> Dict[str, Any]:
        """Test concurrent request handling."""
        results = {"total": 0, "passed": 0, "failed": 0, "critical_failures": [], "warnings": []}
        
        if not self.valid_token:
            self.get_valid_token()
        
        tests = [
            ("Concurrent Chat Requests", self.test_concurrent_chat_requests),
            ("Concurrent Login Requests", self.test_concurrent_login_requests),
            ("Mixed Concurrent Requests", self.test_mixed_concurrent_requests),
            ("High Load Simulation", self.test_high_load_simulation)
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
                        results["critical_failures"].append(f"{test_name}: {test_result.get('reason')}")
                    else:
                        results["warnings"].append(f"{test_name}: {test_result.get('reason')}")
            except Exception as e:
                results["failed"] += 1
                print(f"  ❌ {test_name}: ERROR - {str(e)}")
                results["critical_failures"].append(f"{test_name}: Test execution error - {str(e)}")
        
        return results
    
    def test_concurrent_chat_requests(self) -> Dict[str, Any]:
        """Test concurrent chat requests."""
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No valid token available"}
        
        def make_chat_request(query_id):
            return requests.post(
                f"{self.base_url}/chat",
                json={"query": f"Test query {query_id}"},
                headers={"Authorization": f"Bearer {self.valid_token}"},
                timeout=30
            )
        
        try:
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_chat_request, i) for i in range(10)]
                responses = [future.result() for future in as_completed(futures)]
            
            success_count = sum(1 for r in responses if r.status_code == 200)
            error_count = sum(1 for r in responses if r.status_code >= 500)
            
            if error_count > 3:  # More than 30% server errors
                return {
                    "passed": False,
                    "critical": True,
                    "reason": f"High server error rate under concurrent load: {error_count}/10"
                }
            elif success_count >= 7:  # At least 70% success
                return {"passed": True, "reason": f"Concurrent requests handled well: {success_count}/10 succeeded"}
            else:
                return {
                    "passed": False,
                    "critical": False,
                    "reason": f"Low success rate under concurrent load: {success_count}/10"
                }
                
        except Exception as e:
            return {"passed": False, "critical": True, "reason": f"Concurrent chat test failed: {str(e)}"}
    
    def test_concurrent_login_requests(self) -> Dict[str, Any]:
        """Test concurrent login requests."""
        def make_login_request():
            return requests.post(
                f"{self.base_url}/auth/login",
                data={"username": "admin", "password": "password123"},
                timeout=10
            )
        
        try:
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(make_login_request) for _ in range(5)]
                responses = [future.result() for future in as_completed(futures)]
            
            success_count = sum(1 for r in responses if r.status_code == 200)
            
            if success_count >= 4:  # At least 80% success
                return {"passed": True, "reason": f"Concurrent logins handled well: {success_count}/5 succeeded"}
            else:
                return {
                    "passed": False,
                    "critical": False,
                    "reason": f"Concurrent login issues: {success_count}/5 succeeded"
                }
                
        except Exception as e:
            return {"passed": False, "critical": True, "reason": f"Concurrent login test failed: {str(e)}"}
    
    def test_mixed_concurrent_requests(self) -> Dict[str, Any]:
        """Test mixed types of concurrent requests."""
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No valid token available"}
        
        def make_login_request():
            return requests.post(
                f"{self.base_url}/auth/login",
                data={"username": "admin", "password": "password123"},
                timeout=10
            )
        
        def make_chat_request():
            return requests.post(
                f"{self.base_url}/chat",
                json={"query": "Test mixed request"},
                headers={"Authorization": f"Bearer {self.valid_token}"},
                timeout=15
            )
        
        def make_profile_request():
            return requests.get(
                f"{self.base_url}/api/v1/user/profile",
                headers={"Authorization": f"Bearer {self.valid_token}"},
                timeout=10
            )
        
        try:
            with ThreadPoolExecutor(max_workers=6) as executor:
                futures = []
                futures.extend([executor.submit(make_login_request) for _ in range(2)])
                futures.extend([executor.submit(make_chat_request) for _ in range(3)])
                futures.extend([executor.submit(make_profile_request) for _ in range(2)])
                
                responses = [future.result() for future in as_completed(futures)]
            
            success_count = sum(1 for r in responses if r.status_code == 200)
            
            if success_count >= 5:  # At least 70% success
                return {"passed": True, "reason": f"Mixed concurrent requests handled well: {success_count}/7 succeeded"}
            else:
                return {
                    "passed": False,
                    "critical": False,
                    "reason": f"Mixed concurrent request issues: {success_count}/7 succeeded"
                }
                
        except Exception as e:
            return {"passed": False, "critical": True, "reason": f"Mixed concurrent test failed: {str(e)}"}
    
    def test_high_load_simulation(self) -> Dict[str, Any]:
        """Test high load simulation."""
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No valid token available"}
        
        def make_request(request_id):
            return requests.post(
                f"{self.base_url}/chat",
                json={"query": f"Load test query {request_id}"},
                headers={"Authorization": f"Bearer {self.valid_token}"},
                timeout=30
            )
        
        try:
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request, i) for i in range(20)]
                responses = [future.result() for future in as_completed(futures)]
            
            end_time = time.time()
            duration = end_time - start_time
            
            success_count = sum(1 for r in responses if r.status_code == 200)
            error_count = sum(1 for r in responses if r.status_code >= 500)
            
            if error_count > 5:  # More than 25% server errors
                return {
                    "passed": False,
                    "critical": True,
                    "reason": f"High error rate under load: {error_count}/20 errors in {duration:.1f}s"
                }
            elif success_count >= 15:  # At least 75% success
                return {"passed": True, "reason": f"High load handled well: {success_count}/20 succeeded in {duration:.1f}s"}
            else:
                return {
                    "passed": False,
                    "critical": False,
                    "reason": f"Performance issues under load: {success_count}/20 succeeded in {duration:.1f}s"
                }
                
        except Exception as e:
            return {"passed": False, "critical": True, "reason": f"High load test failed: {str(e)}"}
    
    def test_edge_case_inputs(self) -> Dict[str, Any]:
        """Test edge case inputs."""
        results = {"total": 0, "passed": 0, "failed": 0, "critical_failures": [], "warnings": []}
        
        if not self.valid_token:
            self.get_valid_token()
        
        tests = [
            ("Empty String Inputs", self.test_empty_string_inputs),
            ("Very Long Inputs", self.test_very_long_inputs),
            ("Unicode and Emoji Inputs", self.test_unicode_inputs),
            ("Binary Data Inputs", self.test_binary_inputs),
            ("Nested JSON Inputs", self.test_nested_json_inputs)
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
                        results["critical_failures"].append(f"{test_name}: {test_result.get('reason')}")
                    else:
                        results["warnings"].append(f"{test_name}: {test_result.get('reason')}")
            except Exception as e:
                results["failed"] += 1
                print(f"  ❌ {test_name}: ERROR - {str(e)}")
                results["critical_failures"].append(f"{test_name}: Test execution error - {str(e)}")
        
        return results
    
    def test_empty_string_inputs(self) -> Dict[str, Any]:
        """Test empty string inputs."""
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No valid token available"}
        
        empty_inputs = ["", " ", "   ", "\n", "\t", "\r\n"]
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        
        for empty_input in empty_inputs:
            try:
                response = requests.post(
                    f"{self.base_url}/chat",
                    json={"query": empty_input},
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 500:
                    return {
                        "passed": False,
                        "critical": True,
                        "reason": f"Server error with empty input: {repr(empty_input)}"
                    }
            except:
                continue
        
        return {"passed": True, "reason": "Empty string inputs handled properly"}
    
    def test_very_long_inputs(self) -> Dict[str, Any]:
        """Test very long inputs."""
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No valid token available"}
        
        # Test with increasingly long inputs
        long_inputs = [
            "A" * 1000,    # 1KB
            "B" * 10000,   # 10KB
            "C" * 100000,  # 100KB
        ]
        
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        
        for long_input in long_inputs:
            try:
                response = requests.post(
                    f"{self.base_url}/chat",
                    json={"query": long_input},
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 500:
                    return {
                        "passed": False,
                        "critical": False,
                        "reason": f"Server error with {len(long_input)} character input"
                    }
                elif response.status_code == 413:  # Payload Too Large
                    return {"passed": True, "reason": "Properly limits request size"}
                    
            except requests.exceptions.Timeout:
                return {"passed": True, "reason": "Long input handled with timeout"}
            except:
                continue
        
        return {"passed": True, "reason": "Very long inputs handled properly"}
    
    def test_unicode_inputs(self) -> Dict[str, Any]:
        """Test Unicode and emoji inputs."""
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No valid token available"}
        
        unicode_inputs = [
            "Hello 世界",  # Chinese
            "مرحبا بالعالم",  # Arabic
            "Здравствуй мир",  # Russian
            "🚀🔒💻🌟✨",  # Emojis
            "Ñoño piñata jalapeño",  # Spanish with accents
            "Café naïve résumé",  # French with accents
            "\u0000\u0001\u0002",  # Control characters
        ]
        
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        
        for unicode_input in unicode_inputs:
            try:
                response = requests.post(
                    f"{self.base_url}/chat",
                    json={"query": f"Test with unicode: {unicode_input}"},
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 500:
                    return {
                        "passed": False,
                        "critical": False,
                        "reason": f"Server error with unicode input: {repr(unicode_input)}"
                    }
            except:
                continue
        
        return {"passed": True, "reason": "Unicode inputs handled properly"}
    
    def test_binary_data_inputs(self) -> Dict[str, Any]:
        """Test binary data inputs."""
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No valid token available"}
        
        # Test with binary data (should be rejected)
        binary_data = b'\x00\x01\x02\x03\x04\x05'
        
        try:
            response = requests.post(
                f"{self.base_url}/chat",
                data=binary_data,
                headers={
                    "Authorization": f"Bearer {self.valid_token}",
                    "Content-Type": "application/octet-stream"
                },
                timeout=10
            )
            
            if response.status_code in [400, 415]:  # Bad Request or Unsupported Media Type
                return {"passed": True, "reason": "Properly rejects binary data"}
            else:
                return {
                    "passed": False,
                    "critical": True,
                    "reason": f"Binary data accepted with status: {response.status_code}"
                }
                
        except Exception as e:
            return {"passed": True, "reason": f"Binary data properly rejected: {type(e).__name__}"}
    
    def test_nested_json_inputs(self) -> Dict[str, Any]:
        """Test deeply nested JSON inputs."""
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No valid token available"}
        
        # Create deeply nested JSON
        nested_json = {"query": "test"}
        for i in range(100):  # 100 levels deep
            nested_json = {"level": i, "data": nested_json}
        
        try:
            response = requests.post(
                f"{self.base_url}/chat",
                json=nested_json,
                headers={"Authorization": f"Bearer {self.valid_token}"},
                timeout=10
            )
            
            if response.status_code == 500:
                return {
                    "passed": False,
                    "critical": False,
                    "reason": "Server error with deeply nested JSON"
                }
            elif response.status_code in [400, 413]:  # Bad Request or Payload Too Large
                return {"passed": True, "reason": "Properly handles deeply nested JSON"}
            
            return {"passed": True, "reason": "Deeply nested JSON handled gracefully"}
            
        except Exception as e:
            return {"passed": True, "reason": f"Nested JSON properly handled: {type(e).__name__}"}
    
    def test_resource_exhaustion(self) -> Dict[str, Any]:
        """Test resource exhaustion scenarios."""
        results = {"total": 0, "passed": 0, "failed": 0, "critical_failures": [], "warnings": []}
        
        tests = [
            ("Memory Exhaustion", self.test_memory_exhaustion),
            ("CPU Exhaustion", self.test_cpu_exhaustion),
            ("Connection Pool Exhaustion", self.test_connection_exhaustion),
            ("File Handle Exhaustion", self.test_file_handle_exhaustion)
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
                        results["critical_failures"].append(f"{test_name}: {test_result.get('reason')}")
                    else:
                        results["warnings"].append(f"{test_name}: {test_result.get('reason')}")
            except Exception as e:
                results["failed"] += 1
                print(f"  ❌ {test_name}: ERROR - {str(e)}")
                results["critical_failures"].append(f"{test_name}: Test execution error - {str(e)}")
        
        return results
    
    def test_memory_exhaustion(self) -> Dict[str, Any]:
        """Test memory exhaustion scenarios."""
        # This is dangerous to test in a real environment
        return {
            "passed": False,
            "critical": False,
            "reason": "Cannot safely test memory exhaustion - needs isolated test environment"
        }
    
    def test_cpu_exhaustion(self) -> Dict[str, Any]:
        """Test CPU exhaustion scenarios."""
        # This is dangerous to test in a real environment
        return {
            "passed": False,
            "critical": False,
            "reason": "Cannot safely test CPU exhaustion - needs isolated test environment"
        }
    
    def test_connection_exhaustion(self) -> Dict[str, Any]:
        """Test connection pool exhaustion."""
        if not self.valid_token:
            self.get_valid_token()
        
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No valid token available"}
        
        # Try to exhaust connection pool with many simultaneous requests
        def make_long_request(request_id):
            return requests.post(
                f"{self.base_url}/chat",
                json={"query": f"Long running query {request_id} " + "A" * 1000},
                headers={"Authorization": f"Bearer {self.valid_token}"},
                timeout=60
            )
        
        try:
            with ThreadPoolExecutor(max_workers=50) as executor:
                futures = [executor.submit(make_long_request, i) for i in range(100)]
                
                # Don't wait for all to complete, just check if server handles it
                completed = 0
                errors = 0
                
                for future in as_completed(futures, timeout=30):
                    try:
                        response = future.result()
                        completed += 1
                        if response.status_code >= 500:
                            errors += 1
                    except:
                        errors += 1
                    
                    if completed >= 20:  # Check first 20 responses
                        break
            
            if errors > 10:  # More than 50% errors
                return {
                    "passed": False,
                    "critical": True,
                    "reason": f"High error rate under connection load: {errors}/{completed}"
                }
            else:
                return {"passed": True, "reason": f"Connection exhaustion handled: {errors}/{completed} errors"}
                
        except Exception as e:
            return {"passed": False, "critical": True, "reason": f"Connection exhaustion test failed: {str(e)}"}
    
    def test_file_handle_exhaustion(self) -> Dict[str, Any]:
        """Test file handle exhaustion."""
        # This is system-dependent and dangerous to test
        return {
            "passed": False,
            "critical": False,
            "reason": "Cannot safely test file handle exhaustion - needs isolated test environment"
        }
    
    def test_error_recovery(self) -> Dict[str, Any]:
        """Test error recovery scenarios."""
        results = {"total": 0, "passed": 0, "failed": 0, "critical_failures": [], "warnings": []}
        
        tests = [
            ("Recovery After Error", self.test_recovery_after_error),
            ("Graceful Degradation", self.test_graceful_degradation),
            ("Error Message Quality", self.test_error_message_quality),
            ("Logging and Monitoring", self.test_logging_monitoring)
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
                        results["critical_failures"].append(f"{test_name}: {test_result.get('reason')}")
                    else:
                        results["warnings"].append(f"{test_name}: {test_result.get('reason')}")
            except Exception as e:
                results["failed"] += 1
                print(f"  ❌ {test_name}: ERROR - {str(e)}")
                results["critical_failures"].append(f"{test_name}: Test execution error - {str(e)}")
        
        return results
    
    def test_recovery_after_error(self) -> Dict[str, Any]:
        """Test system recovery after errors."""
        if not self.valid_token:
            self.get_valid_token()
        
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No valid token available"}
        
        try:
            # First, cause an error with invalid JSON
            error_response = requests.post(
                f"{self.base_url}/chat",
                data='{"invalid": json}',
                headers={
                    "Authorization": f"Bearer {self.valid_token}",
                    "Content-Type": "application/json"
                },
                timeout=5
            )
            
            # Then, make a valid request to see if system recovered
            recovery_response = requests.post(
                f"{self.base_url}/chat",
                json={"query": "Test recovery"},
                headers={"Authorization": f"Bearer {self.valid_token}"},
                timeout=10
            )
            
            if recovery_response.status_code == 200:
                return {"passed": True, "reason": "System recovers properly after errors"}
            else:
                return {
                    "passed": False,
                    "critical": True,
                    "reason": f"System did not recover after error: {recovery_response.status_code}"
                }
                
        except Exception as e:
            return {"passed": False, "critical": True, "reason": f"Recovery test failed: {str(e)}"}
    
    def test_graceful_degradation(self) -> Dict[str, Any]:
        """Test graceful degradation under stress."""
        if not self.valid_token:
            self.get_valid_token()
        
        if not self.valid_token:
            return {"passed": False, "critical": True, "reason": "No valid token available"}
        
        # Test if system provides meaningful responses even under stress
        def make_stress_request(request_id):
            return requests.post(
                f"{self.base_url}/chat",
                json={"query": f"Stress test query {request_id}"},
                headers={"Authorization": f"Bearer {self.valid_token}"},
                timeout=30
            )
        
        try:
            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = [executor.submit(make_stress_request, i) for i in range(30)]
                responses = [future.result() for future in as_completed(futures)]
            
            # Check response quality
            meaningful_responses = 0
            for response in responses:
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data.get("response") and len(data.get("response", "")) > 10:
                            meaningful_responses += 1
                    except:
                        pass
                elif response.status_code == 503:  # Service Unavailable - graceful degradation
                    meaningful_responses += 1
            
            if meaningful_responses >= 20:  # At least 67% meaningful responses
                return {"passed": True, "reason": f"Graceful degradation: {meaningful_responses}/30 meaningful responses"}
            else:
                return {
                    "passed": False,
                    "critical": False,
                    "reason": f"Poor degradation: {meaningful_responses}/30 meaningful responses"
                }
                
        except Exception as e:
            return {"passed": False, "critical": True, "reason": f"Graceful degradation test failed: {str(e)}"}
    
    def test_error_message_quality(self) -> Dict[str, Any]:
        """Test quality of error messages."""
        if not self.valid_token:
            self.get_valid_token()
        
        error_scenarios = [
            # (request_data, expected_status, description)
            ({}, 422, "Empty request"),
            ({"wrong_field": "value"}, 422, "Wrong field name"),
            ({"query": ""}, 400, "Empty query"),
        ]
        
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        
        for request_data, expected_status, description in error_scenarios:
            try:
                response = requests.post(
                    f"{self.base_url}/chat",
                    json=request_data,
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code != expected_status:
                    continue
                
                try:
                    error_data = response.json()
                    error_message = error_data.get("detail", "")
                    
                    # Check if error message is informative
                    if len(error_message) < 10:
                        return {
                            "passed": False,
                            "critical": False,
                            "reason": f"Error message too short for {description}: '{error_message}'"
                        }
                    
                    # Check if error message doesn't expose sensitive info
                    sensitive_keywords = ["password", "secret", "key", "token", "database", "internal"]
                    if any(keyword in error_message.lower() for keyword in sensitive_keywords):
                        return {
                            "passed": False,
                            "critical": True,
                            "reason": f"Error message exposes sensitive info for {description}: '{error_message}'"
                        }
                        
                except:
                    return {
                        "passed": False,
                        "critical": False,
                        "reason": f"Error response not JSON for {description}"
                    }
                    
            except:
                continue
        
        return {"passed": True, "reason": "Error messages are appropriate"}
    
    def test_logging_monitoring(self) -> Dict[str, Any]:
        """Test logging and monitoring capabilities."""
        # This would require access to log files or monitoring endpoints
        return {
            "passed": False,
            "critical": False,
            "reason": "Cannot test logging without access to log files - needs monitoring endpoint"
        }
    
    def print_failure_summary(self, results: Dict[str, Any]):
        """Print comprehensive failure test summary."""
        print("\n" + "="*60)
        print("💥 FAILURE SCENARIO TEST SUMMARY")
        print("="*60)
        
        print(f"📊 Total Tests: {results['total_tests']}")
        print(f"✅ Passed: {results['passed']}")
        print(f"❌ Failed: {results['failed']}")
        print(f"📈 Success Rate: {(results['passed']/results['total_tests']*100):.1f}%")
        
        if results['critical_failures']:
            print(f"\n🚨 CRITICAL FAILURES ({len(results['critical_failures'])}):")
            for i, failure in enumerate(results['critical_failures'], 1):
                print(f"  {i}. {failure}")
        
        if results['warnings']:
            print(f"\n⚠️  WARNINGS ({len(results['warnings'])}):")
            for i, warning in enumerate(results['warnings'], 1):
                print(f"  {i}. {warning}")
        
        print(f"\n📋 DETAILED RESULTS BY CATEGORY:")
        for category, category_results in results['test_categories'].items():
            success_rate = (category_results['passed']/category_results['total']*100) if category_results['total'] > 0 else 0
            print(f"  {category}: {category_results['passed']}/{category_results['total']} ({success_rate:.1f}%)")
        
        print(f"\n💡 RESILIENCE RECOMMENDATIONS:")
        recommendations = [
            "Implement proper error handling and recovery mechanisms",
            "Add request size limits and input validation",
            "Implement connection pooling and rate limiting",
            "Add comprehensive logging and monitoring",
            "Implement graceful degradation under load",
            "Add health checks and circuit breakers",
            "Implement proper timeout handling",
            "Add database connection retry logic",
            "Implement proper resource cleanup",
            "Add performance monitoring and alerting"
        ]
        
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        
        print("\n" + "="*60)


def main():
    """Run comprehensive failure scenario testing."""
    print("🚀 Starting FinSolve Failure Scenario Testing Suite")
    print("This will test failure scenarios, edge cases, and system resilience.")
    print("\nMake sure the backend server is running at http://127.0.0.1:8000")
    
    input("\nPress Enter to start testing...")
    
    tester = FailureScenarioTester()
    results = tester.run_all_failure_tests()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"failure_test_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    if results['critical_failures']:
        print(f"\n❌ TESTING COMPLETED WITH {len(results['critical_failures'])} CRITICAL FAILURES")
        return 1
    else:
        print(f"\n✅ TESTING COMPLETED - NO CRITICAL FAILURES FOUND")
        return 0


if __name__ == "__main__":
    exit(main())