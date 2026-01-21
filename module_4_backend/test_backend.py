#!/usr/bin/env python3
"""
Test script for Module 4 Backend
Tests all API endpoints with RBAC validation
"""

import requests
import json
from typing import Dict, Optional

# Configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 10

# Test users with different roles
TEST_USERS = [
    {"username": "admin_user", "email": "admin@company.com", "password": "admin123", "role": "Admin"},
    {"username": "hr_user", "email": "hr@company.com", "password": "hr123", "role": "HR"},
    {"username": "finance_user", "email": "finance@company.com", "password": "finance123", "role": "Finance"},
    {"username": "eng_user", "email": "eng@company.com", "password": "eng123", "role": "Engineering"},
    {"username": "marketing_user", "email": "marketing@company.com", "password": "marketing123", "role": "Marketing"},
    {"username": "general_user", "email": "general@company.com", "password": "general123", "role": "General"},
]

# Test queries for different departments
TEST_QUERIES = {
    "HR": "What is the employee handbook policy?",
    "Finance": "What are the quarterly financial results?",
    "Engineering": "What are the engineering best practices?",
    "Marketing": "What is the marketing strategy for Q4 2024?",
    "General": "What are the company values?",
}


class BackendTester:
    def __init__(self):
        self.results = {
            "passed": 0,
            "failed": 0,
            "tests": []
        }
        self.tokens: Dict[str, str] = {}
    
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   └─ {message}")
        
        self.results["tests"].append({
            "test": test_name,
            "passed": passed,
            "message": message
        })
        
        if passed:
            self.results["passed"] += 1
        else:
            self.results["failed"] += 1
    
    def test_health(self):
        """Test health endpoint"""
        print("\n📊 Testing Health Endpoint...")
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") in ["healthy", "degraded"]:
                    self.log_test("Health Check", True, f"Status: {data.get('status')}, Vector DB docs: {data.get('vector_db_documents', 0)}")
                else:
                    self.log_test("Health Check", False, f"Unexpected status: {data.get('status')}")
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}")
        
        except Exception as e:
            self.log_test("Health Check", False, f"Error: {str(e)}")
    
    def test_registration(self):
        """Test user registration"""
        print("\n👤 Testing User Registration...")
        
        for user in TEST_USERS:
            try:
                response = requests.post(
                    f"{BASE_URL}/auth/register",
                    json=user,
                    timeout=TIMEOUT
                )
                
                if response.status_code in [201, 400]:  # 400 if user already exists
                    if response.status_code == 201:
                        self.log_test(f"Register {user['username']}", True, f"Role: {user['role']}")
                    else:
                        # User already exists - still a pass
                        self.log_test(f"Register {user['username']}", True, "User already exists (OK)")
                else:
                    self.log_test(f"Register {user['username']}", False, f"Status: {response.status_code}")
            
            except Exception as e:
                self.log_test(f"Register {user['username']}", False, f"Error: {str(e)}")
    
    def test_login(self):
        """Test user login"""
        print("\n🔐 Testing User Login...")
        
        for user in TEST_USERS:
            try:
                response = requests.post(
                    f"{BASE_URL}/auth/login",
                    json={
                        "username": user["username"],
                        "password": user["password"]
                    },
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "access_token" in data and "refresh_token" in data:
                        # Store token for future tests
                        self.tokens[user["username"]] = data["access_token"]
                        self.log_test(f"Login {user['username']}", True, f"Role: {data.get('role')}")
                    else:
                        self.log_test(f"Login {user['username']}", False, "Missing tokens in response")
                else:
                    self.log_test(f"Login {user['username']}", False, f"Status: {response.status_code}")
            
            except Exception as e:
                self.log_test(f"Login {user['username']}", False, f"Error: {str(e)}")
    
    def test_rag_queries(self):
        """Test RAG queries with RBAC"""
        print("\n🔍 Testing RAG Queries with RBAC...")
        
        # Test queries for each role
        test_cases = [
            ("hr_user", "HR", "What is the vacation policy?"),
            ("finance_user", "Finance", "What are the revenue numbers?"),
            ("eng_user", "Engineering", "What are the coding standards?"),
            ("marketing_user", "Marketing", "What is the marketing budget?"),
            ("general_user", "General", "What is the company mission?"),
        ]
        
        for username, role, query in test_cases:
            if username not in self.tokens:
                self.log_test(f"RAG Query - {role}", False, "No token available")
                continue
            
            try:
                response = requests.post(
                    f"{BASE_URL}/query",
                    json={"query": query, "top_k": 5},
                    headers={"Authorization": f"Bearer {self.tokens[username]}"},
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    sources = data.get("sources", [])
                    answer = data.get("answer", "")
                    
                    # Verify RBAC: sources should only be from allowed departments
                    valid_rbac = all(
                        source.get("department") in self.get_allowed_departments(role)
                        for source in sources
                    )
                    
                    if valid_rbac:
                        self.log_test(
                            f"RAG Query - {role}",
                            True,
                            f"Found {len(sources)} sources, answer length: {len(answer)}"
                        )
                    else:
                        self.log_test(
                            f"RAG Query - {role}",
                            False,
                            "RBAC violation: unauthorized department in sources"
                        )
                else:
                    self.log_test(f"RAG Query - {role}", False, f"Status: {response.status_code}")
            
            except Exception as e:
                self.log_test(f"RAG Query - {role}", False, f"Error: {str(e)}")
    
    def test_stats(self):
        """Test user stats endpoint"""
        print("\n📈 Testing User Stats...")
        
        for username in ["admin_user", "hr_user", "finance_user"]:
            if username not in self.tokens:
                continue
            
            try:
                response = requests.get(
                    f"{BASE_URL}/stats",
                    headers={"Authorization": f"Bearer {self.tokens[username]}"},
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(
                        f"Stats - {username}",
                        True,
                        f"Queries: {data.get('total_queries', 0)}, Permissions: {len(data.get('permissions', []))}"
                    )
                else:
                    self.log_test(f"Stats - {username}", False, f"Status: {response.status_code}")
            
            except Exception as e:
                self.log_test(f"Stats - {username}", False, f"Error: {str(e)}")
    
    def test_admin_endpoint(self):
        """Test admin-only endpoint"""
        print("\n🔒 Testing Admin Authorization...")
        
        # Test with admin user
        if "admin_user" in self.tokens:
            try:
                response = requests.get(
                    f"{BASE_URL}/admin/users",
                    headers={"Authorization": f"Bearer {self.tokens['admin_user']}"},
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test("Admin - List Users (Admin)", True, f"Total users: {data.get('total_users', 0)}")
                else:
                    self.log_test("Admin - List Users (Admin)", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Admin - List Users (Admin)", False, f"Error: {str(e)}")
        
        # Test with non-admin user (should fail)
        if "general_user" in self.tokens:
            try:
                response = requests.get(
                    f"{BASE_URL}/admin/users",
                    headers={"Authorization": f"Bearer {self.tokens['general_user']}"},
                    timeout=TIMEOUT
                )
                
                if response.status_code == 403:
                    self.log_test("Admin - List Users (Non-Admin)", True, "Correctly denied access")
                else:
                    self.log_test("Admin - List Users (Non-Admin)", False, f"Should be 403, got: {response.status_code}")
            except Exception as e:
                self.log_test("Admin - List Users (Non-Admin)", False, f"Error: {str(e)}")
    
    def get_allowed_departments(self, role: str) -> list:
        """Get allowed departments for a role (based on RBAC rules)"""
        rbac_mapping = {
            "Admin": ["HR", "Finance", "Engineering", "Marketing", "General"],
            "HR": ["HR", "General"],
            "Finance": ["Finance", "General"],
            "Engineering": ["Engineering", "General"],
            "Marketing": ["Marketing", "General"],
            "General": ["General"],
        }
        return rbac_mapping.get(role, ["General"])
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("📋 TEST SUMMARY")
        print("="*60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📊 Total:  {self.results['passed'] + self.results['failed']}")
        
        if self.results['failed'] == 0:
            print("\n🎉 ALL TESTS PASSED!")
        else:
            print(f"\n⚠️  {self.results['failed']} test(s) failed")
            print("\nFailed tests:")
            for test in self.results['tests']:
                if not test['passed']:
                    print(f"  - {test['test']}: {test['message']}")
        
        print("="*60)
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Module 4 Backend Tests...")
        print(f"🌐 Backend URL: {BASE_URL}")
        print("="*60)
        
        self.test_health()
        self.test_registration()
        self.test_login()
        self.test_rag_queries()
        self.test_stats()
        self.test_admin_endpoint()
        
        self.print_summary()
        
        # Save results to file
        with open("test_results_module4.json", "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Results saved to: test_results_module4.json")
        
        return self.results['failed'] == 0


if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    
    exit(0 if success else 1)
