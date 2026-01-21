#!/usr/bin/env python3
"""
End-to-End Workflow Integration Tests
Tests complete user workflows for all roles
"""

import requests
import pytest
import time
from typing import Dict, List

API_BASE_URL = "http://localhost:8000"

# Test user credentials
TEST_USERS = {
    "alice_finance": {
        "password": "SecurePass123!",
        "role": "finance_employee",
        "accessible_depts": ["Finance", "General"],
        "inaccessible_depts": ["Marketing", "HR", "Engineering"]
    },
    "bob_marketing": {
        "password": "SecurePass123!",
        "role": "marketing_employee",
        "accessible_depts": ["Marketing", "General"],
        "inaccessible_depts": ["Finance", "HR", "Engineering"]
    },
    "admin_user": {
        "password": "AdminPass456!",
        "role": "admin",
        "accessible_depts": ["Finance", "Marketing", "HR", "Engineering", "General"],
        "inaccessible_depts": []
    }
}


class TestEndToEndWorkflow:
    """Comprehensive end-to-end workflow tests"""
    
    def test_01_backend_health(self):
        """Test that backend is running and healthy"""
        response = requests.get(f"{API_BASE_URL}/health")
        assert response.status_code == 200, "Backend health check failed"
        
        data = response.json()
        assert data['status'] == 'healthy', "Backend status is not healthy"
        assert data['components']['vector_db'] is True, "Vector DB not available"
        assert data['components']['embedding_generator'] is True, "Embedding generator not available"
        
        print("✅ Backend health check passed")
    
    def test_02_user_registration_flow(self):
        """Test new user registration workflow"""
        # Try to register a new user
        new_user = {
            "username": f"test_user_{int(time.time())}",
            "email": f"test_{int(time.time())}@example.com",
            "password": "TestPassword123!",
            "role": "employee"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/auth/register",
            json=new_user
        )
        
        # Registration should succeed
        assert response.status_code == 201, f"Registration failed: {response.text}"
        data = response.json()
        assert data['username'] == new_user['username']
        assert data['role'] == new_user['role']
        
        print(f"✅ User registration successful: {new_user['username']}")
    
    def test_03_complete_finance_employee_workflow(self):
        """Test complete workflow for finance employee"""
        username = "alice_finance"
        user_data = TEST_USERS[username]
        
        # Step 1: Login
        login_response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"username": username, "password": user_data['password']}
        )
        assert login_response.status_code == 200, "Login failed"
        
        token_data = login_response.json()
        token = token_data['access_token']
        assert token_data['role'] == user_data['role']
        
        headers = {"Authorization": f"Bearer {token}"}
        print(f"✅ Step 1: {username} logged in successfully")
        
        # Step 2: Get user stats
        stats_response = requests.get(f"{API_BASE_URL}/stats", headers=headers)
        assert stats_response.status_code == 200, "Stats request failed"
        
        stats = stats_response.json()
        assert set(stats['accessible_departments']) == set(user_data['accessible_depts'])
        print(f"✅ Step 2: Stats retrieved - {stats['accessible_departments']}")
        
        # Step 3: Query accessible data (Finance)
        query_response = requests.post(
            f"{API_BASE_URL}/query/advanced",
            json={"query": "What is the financial performance?", "top_k": 5},
            headers=headers
        )
        assert query_response.status_code == 200, "Finance query failed"
        
        query_data = query_response.json()
        assert 'answer' in query_data
        assert len(query_data.get('sources', [])) > 0
        print(f"✅ Step 3: Finance query successful - {len(query_data['sources'])} sources")
        
        # Step 4: Configure model settings
        config_response = requests.post(
            f"{API_BASE_URL}/config/model",
            json={
                "model_provider": "huggingface",
                "api_key": "hf_test_key",
                "model_name": "meta-llama/Meta-Llama-3.1-8B-Instruct"
            },
            headers=headers
        )
        assert config_response.status_code == 200, "Model config failed"
        print(f"✅ Step 4: Model configuration saved")
        
        # Step 5: Retrieve model config
        get_config_response = requests.get(
            f"{API_BASE_URL}/config/model",
            headers=headers
        )
        assert get_config_response.status_code == 200, "Get model config failed"
        
        config_data = get_config_response.json()
        assert config_data['configured'] is True
        assert config_data['model_provider'] == "huggingface"
        print(f"✅ Step 5: Model configuration retrieved successfully")
        
        print(f"\n🎉 Complete workflow test passed for {username}")
    
    def test_04_complete_marketing_employee_workflow(self):
        """Test complete workflow for marketing employee"""
        username = "bob_marketing"
        user_data = TEST_USERS[username]
        
        # Step 1: Login
        login_response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"username": username, "password": user_data['password']}
        )
        assert login_response.status_code == 200
        
        token = login_response.json()['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        print(f"✅ Step 1: {username} logged in")
        
        # Step 2: Query Marketing data
        query_response = requests.post(
            f"{API_BASE_URL}/query/advanced",
            json={"query": "What are the marketing strategies?", "top_k": 5},
            headers=headers
        )
        assert query_response.status_code == 200
        
        query_data = query_response.json()
        # Verify sources are from accessible departments
        for source in query_data.get('sources', []):
            dept = source.get('department', '')
            assert dept in user_data['accessible_depts'], f"Unauthorized dept: {dept}"
        
        print(f"✅ Step 2: Marketing query successful with {len(query_data['sources'])} sources")
        
        # Step 3: Try to access Finance data (should return limited or no results)
        finance_query = requests.post(
            f"{API_BASE_URL}/query/advanced",
            json={"query": "Show me financial statements", "top_k": 5},
            headers=headers
        )
        assert finance_query.status_code == 200
        
        # Should not get Finance department sources
        finance_data = finance_query.json()
        for source in finance_data.get('sources', []):
            assert source.get('department') != 'Finance', "Unauthorized access to Finance data"
        
        print(f"✅ Step 3: RBAC enforcement verified - no Finance data leaked")
        
        print(f"\n🎉 Complete workflow test passed for {username}")
    
    def test_05_session_lifecycle(self):
        """Test complete session lifecycle"""
        username = "alice_finance"
        user_data = TEST_USERS[username]
        
        # Login
        login_response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"username": username, "password": user_data['password']}
        )
        assert login_response.status_code == 200
        
        token_data = login_response.json()
        access_token = token_data['access_token']
        refresh_token = token_data['refresh_token']
        
        headers = {"Authorization": f"Bearer {access_token}"}
        print(f"✅ Session started for {username}")
        
        # Make authenticated request
        stats = requests.get(f"{API_BASE_URL}/stats", headers=headers)
        assert stats.status_code == 200
        print(f"✅ Authenticated request successful")
        
        # Wait a moment to ensure different timestamp in new token
        time.sleep(1)
        
        # Refresh token
        refresh_response = requests.post(
            f"{API_BASE_URL}/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert refresh_response.status_code == 200
        
        new_access_token = refresh_response.json()['access_token']
        assert new_access_token != access_token
        print(f"✅ Token refresh successful")

        
        # Use new token
        new_headers = {"Authorization": f"Bearer {new_access_token}"}
        stats2 = requests.get(f"{API_BASE_URL}/stats", headers=new_headers)
        assert stats2.status_code == 200
        print(f"✅ New token works correctly")
        
        print(f"\n🎉 Session lifecycle test passed")
    
    def test_06_multi_query_workflow(self):
        """Test multiple queries in a session"""
        username = "alice_finance"
        user_data = TEST_USERS[username]
        
        # Login
        login_response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"username": username, "password": user_data['password']}
        )
        token = login_response.json()['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        
        queries = [
            "What is the revenue?",
            "Show me quarterly reports",
            "What are the financial goals?",
            "Explain budget allocation"
        ]
        
        for i, query_text in enumerate(queries, 1):
            response = requests.post(
                f"{API_BASE_URL}/query/advanced",
                json={"query": query_text, "top_k": 3},
                headers=headers
            )
            assert response.status_code == 200
            data = response.json()
            assert 'answer' in data
            print(f"✅ Query {i}/4: '{query_text[:30]}...' successful")
        
        # Verify query count increased
        stats = requests.get(f"{API_BASE_URL}/stats", headers=headers).json()
        assert stats['total_queries'] >= len(queries)
        print(f"✅ Query logging verified - total queries: {stats['total_queries']}")
        
        print(f"\n🎉 Multi-query workflow test passed")


def run_integration_tests():
    """Run all integration tests"""
    print("="*70)
    print("🧪 RUNNING END-TO-END INTEGRATION TESTS")
    print("="*70)
    print()
    
    test_suite = TestEndToEndWorkflow()
    
    tests = [
        ("Backend Health Check", test_suite.test_01_backend_health),
        ("User Registration Flow", test_suite.test_02_user_registration_flow),
        ("Finance Employee Workflow", test_suite.test_03_complete_finance_employee_workflow),
        ("Marketing Employee Workflow", test_suite.test_04_complete_marketing_employee_workflow),
        ("Session Lifecycle", test_suite.test_05_session_lifecycle),
        ("Multi-Query Workflow", test_suite.test_06_multi_query_workflow),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{'='*70}")
        print(f"🧪 Running: {test_name}")
        print(f"{'='*70}")
        
        try:
            test_func()
            passed += 1
            print(f"\n✅ PASSED: {test_name}")
        except AssertionError as e:
            failed += 1
            print(f"\n❌ FAILED: {test_name}")
            print(f"   Error: {str(e)}")
        except Exception as e:
            failed += 1
            print(f"\n❌ ERROR: {test_name}")
            print(f"   Exception: {str(e)}")
    
    # Summary
    print(f"\n{'='*70}")
    print(f"📊 TEST SUMMARY")
    print(f"{'='*70}")
    print(f"Total Tests: {len(tests)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed/len(tests)*100):.1f}%")
    print(f"{'='*70}")
    
    return passed == len(tests)


if __name__ == "__main__":
    try:
        success = run_integration_tests()
        exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Please ensure it's running on port 8000")
        print("   Start backend with: cd module_4_backend && python main.py")
        exit(1)
    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
