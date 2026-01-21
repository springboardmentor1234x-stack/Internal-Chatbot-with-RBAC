#!/usr/bin/env python3
"""
RBAC Enforcement Integration Tests
Verifies role-based access control is properly enforced across all endpoints
"""

import requests
import pytest

API_BASE_URL = "http://localhost:8000"

TEST_USERS = {
    "alice_finance": {"password": "SecurePass123!", "role": "finance_employee"},
    "bob_marketing": {"password": "SecurePass123!", "role": "marketing_employee"},
}


class TestRBACEnforcement:
    """Test role-based access control enforcement"""
    
    def test_01_department_access_isolation(self):
        """Test that users can only access their department data"""
        print("\n🔒 Testing Department Access Isolation")
        
        # Login as Finance employee
        finance_login = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"username": "alice_finance", "password": "SecurePass123!"}
        )
        finance_token = finance_login.json()['access_token']
        finance_headers = {"Authorization": f"Bearer {finance_token}"}
        
        # Login as Marketing employee
        marketing_login = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"username": "bob_marketing", "password": "SecurePass123!"}
        )
        marketing_token = marketing_login.json()['access_token']
        marketing_headers = {"Authorization": f"Bearer {marketing_token}"}
        
        # Finance employee queries Finance data
        finance_query = requests.post(
            f"{API_BASE_URL}/query/advanced",
            json={"query": "financial budget allocation", "top_k": 5},
            headers=finance_headers
        )
        assert finance_query.status_code == 200
        finance_data = finance_query.json()
        
        # Check that Finance employee gets Finance department sources
        finance_sources = finance_data.get('sources', [])
        finance_depts = [s.get('department') for s in finance_sources]
        assert 'Finance' in finance_depts or 'General' in finance_depts
        print(f"  ✅ Finance employee can access Finance data")
        print(f"     Departments in response: {set(finance_depts)}")
        
        # Marketing employee queries Marketing data
        marketing_query = requests.post(
            f"{API_BASE_URL}/query/advanced",
            json={"query": "marketing campaign strategy", "top_k": 5},
            headers=marketing_headers
        )
        assert marketing_query.status_code == 200
        marketing_data = marketing_query.json()
        
        # Check that Marketing employee gets Marketing department sources
        marketing_sources = marketing_data.get('sources', [])
        marketing_depts = [s.get('department') for s in marketing_sources]
        assert 'Marketing' in marketing_depts or 'General' in marketing_depts
        print(f"  ✅ Marketing employee can access Marketing data")
        print(f"     Departments in response: {set(marketing_depts)}")
        
        # Marketing employee tries to access Finance data
        marketing_finance_query = requests.post(
            f"{API_BASE_URL}/query/advanced",
            json={"query": "show me the financial statements and budget", "top_k": 5},
            headers=marketing_headers
        )
        assert marketing_finance_query.status_code == 200
        leak_data = marketing_finance_query.json()
        
        # Should NOT get Finance department data
        leak_sources = leak_data.get('sources', [])
        leak_depts = [s.get('department') for s in leak_sources]
        assert 'Finance' not in leak_depts, "SECURITY BREACH: Marketing user accessed Finance data!"
        print(f"  ✅ Marketing employee CANNOT access Finance data")
        print(f"     Departments in response: {set(leak_depts) if leak_depts else 'No sources'}")
        
        print(f"\n  🎉 Department isolation test PASSED")
    
    def test_02_stats_endpoint_permissions(self):
        """Test that users can only see their own stats"""
        print("\n📊 Testing Stats Endpoint Permissions")
        
        # Login as Finance employee
        finance_login = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"username": "alice_finance", "password": "SecurePass123!"}
        )
        finance_token = finance_login.json()['access_token']
        finance_headers = {"Authorization": f"Bearer {finance_token}"}
        
        # Get stats
        stats_response = requests.get(f"{API_BASE_URL}/stats", headers=finance_headers)
        assert stats_response.status_code == 200
        stats = stats_response.json()
        
        # Verify correct user
        assert stats['username'] == 'alice_finance'
        assert stats['role'] == 'finance_employee'
        
        # Verify correct departments
        accessible = stats['accessible_departments']
        assert set(accessible) == {'Finance', 'General'}
        print(f"  ✅ Finance employee sees correct stats")
        print(f"     Accessible departments: {accessible}")
        
        # Login as Marketing employee
        marketing_login = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"username": "bob_marketing", "password": "SecurePass123!"}
        )
        marketing_token = marketing_login.json()['access_token']
        marketing_headers = {"Authorization": f"Bearer {marketing_token}"}
        
        # Get stats
        marketing_stats = requests.get(f"{API_BASE_URL}/stats", headers=marketing_headers)
        assert marketing_stats.status_code == 200
        marketing_data = marketing_stats.json()
        
        # Verify correct user (should be different)
        assert marketing_data['username'] == 'bob_marketing'
        assert marketing_data['role'] == 'marketing_employee'
        assert marketing_data['user_id'] != stats['user_id']
        
        # Verify correct departments
        marketing_accessible = marketing_data['accessible_departments']
        assert set(marketing_accessible) == {'Marketing', 'General'}
        print(f"  ✅ Marketing employee sees correct stats")
        print(f"     Accessible departments: {marketing_accessible}")
        
        print(f"\n  🎉 Stats permissions test PASSED")
    
    def test_03_model_config_isolation(self):
        """Test that model configurations are user-specific"""
        print("\n🤖 Testing Model Configuration Isolation")
        
        # Login users
        alice_login = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"username": "alice_finance", "password": "SecurePass123!"}
        )
        alice_token = alice_login.json()['access_token']
        alice_headers = {"Authorization": f"Bearer {alice_token}"}
        
        bob_login = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"username": "bob_marketing", "password": "SecurePass123!"}
        )
        bob_token = bob_login.json()['access_token']
        bob_headers = {"Authorization": f"Bearer {bob_token}"}
        
        # Alice configures OpenAI
        alice_config = requests.post(
            f"{API_BASE_URL}/config/model",
            json={
                "model_provider": "openai",
                "api_key": "alice_openai_key",
                "model_name": "gpt-4"
            },
            headers=alice_headers
        )
        assert alice_config.status_code == 200
        print(f"  ✅ Alice configured OpenAI/GPT-4")
        
        # Bob configures HuggingFace
        bob_config = requests.post(
            f"{API_BASE_URL}/config/model",
            json={
                "model_provider": "huggingface",
                "api_key": "bob_hf_key",
                "model_name": "meta-llama/Meta-Llama-3.1-8B-Instruct"
            },
            headers=bob_headers
        )
        assert bob_config.status_code == 200
        print(f"  ✅ Bob configured HuggingFace/Llama-3.1")
        
        # Verify Alice's config
        alice_get = requests.get(f"{API_BASE_URL}/config/model", headers=alice_headers)
        alice_data = alice_get.json()
        assert alice_data['model_provider'] == "openai"
        assert alice_data['model_name'] == "gpt-4"
        print(f"  ✅ Alice retrieves her own config (OpenAI/GPT-4)")
        
        # Verify Bob's config
        bob_get = requests.get(f"{API_BASE_URL}/config/model", headers=bob_headers)
        bob_data = bob_get.json()
        assert bob_data['model_provider'] == "huggingface"
        assert "Llama" in bob_data['model_name']
        print(f"  ✅ Bob retrieves his own config (HuggingFace/Llama-3.1)")
        
        # Verify they're different
        assert alice_data['model_provider'] != bob_data['model_provider']
        print(f"  ✅ Model configurations are properly isolated")
        
        print(f"\n  🎉 Model config isolation test PASSED")
    
    def test_04_unauthorized_access_attempts(self):
        """Test that unauthorized access is properly blocked"""
        print("\n🚫 Testing Unauthorized Access Prevention")
        
        # Try to access stats without token
        no_auth_stats = requests.get(f"{API_BASE_URL}/stats")
        assert no_auth_stats.status_code == 403 or no_auth_stats.status_code == 401
        print(f"  ✅ Stats endpoint blocked without authentication")
        
        # Try to query without token
        no_auth_query = requests.post(
            f"{API_BASE_URL}/query/advanced",
            json={"query": "test", "top_k": 5}
        )
        assert no_auth_query.status_code == 403 or no_auth_query.status_code == 401
        print(f"  ✅ Query endpoint blocked without authentication")
        
        # Try with invalid token
        bad_headers = {"Authorization": "Bearer invalid_token_12345"}
        bad_token_query = requests.get(f"{API_BASE_URL}/stats", headers=bad_headers)
        assert bad_token_query.status_code == 401
        print(f"  ✅ Invalid token rejected")
        
        print(f"\n  🎉 Unauthorized access prevention test PASSED")


def run_rbac_tests():
    """Run all RBAC enforcement tests"""
    print("="*70)
    print("🔒 RUNNING RBAC ENFORCEMENT TESTS")
    print("="*70)
    
    test_suite = TestRBACEnforcement()
    
    tests = [
        ("Department Access Isolation", test_suite.test_01_department_access_isolation),
        ("Stats Endpoint Permissions", test_suite.test_02_stats_endpoint_permissions),
        ("Model Config Isolation", test_suite.test_03_model_config_isolation),
        ("Unauthorized Access Prevention", test_suite.test_04_unauthorized_access_attempts),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            failed += 1
            print(f"\n  ❌ FAILED: {test_name}")
            print(f"     Error: {str(e)}")
        except Exception as e:
            failed += 1
            print(f"\n  ❌ ERROR: {test_name}")
            print(f"     Exception: {str(e)}")
    
    # Summary
    print(f"\n{'='*70}")
    print(f"📊 RBAC TEST SUMMARY")
    print(f"{'='*70}")
    print(f"Total Tests: {len(tests)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed/len(tests)*100):.1f}%")
    print(f"{'='*70}")
    
    return passed == len(tests)


if __name__ == "__main__":
    try:
        success = run_rbac_tests()
        exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend")
        exit(1)
