"""
Test Module 5 Integration with Backend
Tests the advanced RAG pipeline integration with FastAPI backend
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "username": "alice_finance",
    "password": "SecurePass123!"
}

def print_section(title):
    """Print a section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_result(test_name, passed, details=""):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")
    if details:
        print(f"     {details}")

def test_health_check():
    """Test health check endpoint"""
    print_section("Test 1: Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(json.dumps(health_data, indent=2))
            
            # Check components
            components = health_data.get('components', {})
            all_healthy = all(components.values())
            
            print_result(
                "Health Check",
                all_healthy,
                f"Vector DB: {components.get('vector_db')}, "
                f"Advanced RAG: {components.get('advanced_rag_pipeline')}, "
                f"LLM Provider: {health_data.get('llm_provider', 'N/A')}"
            )
            return all_healthy
        else:
            print_result("Health Check", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_result("Health Check", False, str(e))
        return False

def test_login():
    """Test login and get access token"""
    print_section("Test 2: User Login")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=TEST_USER
        )
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            user_role = token_data.get('role')
            
            print_result(
                "Login",
                True,
                f"User: {token_data.get('username')}, Role: {user_role}"
            )
            return access_token
        else:
            print_result("Login", False, f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print_result("Login", False, str(e))
        return None

def test_basic_query(token):
    """Test basic query endpoint"""
    print_section("Test 3: Basic Query Endpoint")
    
    if not token:
        print_result("Basic Query", False, "No access token")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    query_data = {
        "query": "What are the key engineering initiatives?",
        "top_k": 5
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/query",
            json=query_data,
            headers=headers
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('answer', '')
            sources = result.get('sources', [])
            
            print(f"\nQuery: {query_data['query']}")
            print(f"Response Time: {elapsed:.2f}s")
            print(f"\nAnswer: {answer[:300]}...")
            print(f"\nSources Found: {len(sources)}")
            
            if sources:
                print("\nTop Source:")
                print(f"  - Document: {sources[0].get('document_name')}")
                print(f"  - Department: {sources[0].get('department')}")
                print(f"  - Relevance: {sources[0].get('relevance_score')}")
            
            print_result(
                "Basic Query",
                True,
                f"Found {len(sources)} sources in {elapsed:.2f}s"
            )
            return True
        else:
            print_result("Basic Query", False, f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print_result("Basic Query", False, str(e))
        return False

def test_advanced_query(token):
    """Test advanced query endpoint with LLM integration"""
    print_section("Test 4: Advanced Query Endpoint (Module 5)")
    
    if not token:
        print_result("Advanced Query", False, "No access token")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    query_data = {
        "query": "What are the main engineering priorities and technical initiatives?",
        "top_k": 5
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/query/advanced",
            json=query_data,
            headers=headers
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('answer', '')
            sources = result.get('sources', [])
            confidence = result.get('confidence', {})
            metadata = result.get('metadata', {})
            
            print(f"\nQuery: {query_data['query']}")
            print(f"Response Time: {elapsed:.2f}s")
            print(f"\nAnswer:\n{answer}")
            print(f"\n{'='*80}")
            
            print(f"\nConfidence Metrics:")
            print(f"  Overall: {confidence.get('overall_confidence', 0):.2f}%")
            print(f"  Retrieval Quality: {confidence.get('retrieval_quality', 0):.2f}%")
            print(f"  Citation Coverage: {confidence.get('citation_coverage', 0):.2f}%")
            print(f"  Answer Completeness: {confidence.get('answer_completeness', 0):.2f}%")
            print(f"  Confidence Level: {confidence.get('confidence_level', 'unknown').upper()}")
            
            print(f"\nSources Used: {len(sources)}")
            for i, source in enumerate(sources[:3], 1):
                print(f"\n  Source {i}:")
                print(f"    Document: {source.get('document_name')}")
                print(f"    Department: {source.get('department')}")
                print(f"    Relevance: {source.get('relevance_score', 0):.4f}")
            
            print(f"\nMetadata:")
            print(f"  LLM Provider: {metadata.get('llm_provider', 'unknown')}")
            print(f"  Model: {metadata.get('llm_model', 'unknown')}")
            print(f"  Pipeline: {metadata.get('pipeline', 'unknown')}")
            
            # Success criteria
            success = (
                len(answer) > 0 and
                len(sources) > 0 and
                confidence.get('overall_confidence', 0) > 0
            )
            
            print_result(
                "Advanced Query",
                success,
                f"Confidence: {confidence.get('overall_confidence', 0):.2f}%, "
                f"Sources: {len(sources)}, Time: {elapsed:.2f}s"
            )
            return success
        else:
            print_result(
                "Advanced Query",
                False,
                f"Status: {response.status_code}"
            )
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print_result("Advanced Query", False, str(e))
        import traceback
        print(traceback.format_exc())
        return False

def test_rbac_compliance(token):
    """Test RBAC compliance in advanced query"""
    print_section("Test 5: RBAC Compliance (Finance Role)")
    
    if not token:
        print_result("RBAC Test", False, "No access token")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test queries for different departments
    # alice_finance should have access to Finance and General, but NOT Engineering, HR, Marketing
    test_cases = [
        {
            "query": "What are the engineering team initiatives?",
            "should_have_access": False,  # Finance user should NOT access Engineering
            "department": "Engineering"
        },
        {
            "query": "What is the financial performance?",
            "should_have_access": True,  # Finance user SHOULD access Finance
            "department": "Finance"
        }
    ]
    
    results = []
    for test_case in test_cases:
        query_data = {
            "query": test_case['query'],
            "top_k": 3
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/query/advanced",
                json=query_data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                sources = result.get('sources', [])
                
                # Check if sources match expected department
                has_relevant_sources = any(
                    s.get('department') == test_case['department']
                    for s in sources
                )
                
                # For engineering user, should have engineering sources
                # For finance queries, should not have finance sources
                test_passed = (
                    (test_case['should_have_access'] and has_relevant_sources) or
                    (not test_case['should_have_access'] and not has_relevant_sources)
                )
                
                results.append(test_passed)
                print_result(
                    f"RBAC - {test_case['department']}",
                    test_passed,
                    f"Access: {'Granted' if has_relevant_sources else 'Denied'} "
                    f"(Expected: {'Grant' if test_case['should_have_access'] else 'Deny'})"
                )
            else:
                results.append(False)
                print_result(
                    f"RBAC - {test_case['department']}",
                    False,
                    f"Status: {response.status_code}"
                )
        except Exception as e:
            results.append(False)
            print_result(f"RBAC - {test_case['department']}", False, str(e))
    
    return all(results)

def run_all_tests():
    """Run all integration tests"""
    print("\n" + "█"*80)
    print("  MODULE 5 INTEGRATION TESTS")
    print("  Advanced RAG Pipeline + Backend Integration")
    print("█"*80)
    print(f"\nTest Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    
    # Run tests
    results = {}
    
    # Test 1: Health Check
    results['health'] = test_health_check()
    
    # Test 2: Login
    token = test_login()
    results['login'] = token is not None
    
    if token:
        # Test 3: Basic Query
        results['basic_query'] = test_basic_query(token)
        
        # Test 4: Advanced Query
        results['advanced_query'] = test_advanced_query(token)
        
        # Test 5: RBAC Compliance
        results['rbac'] = test_rbac_compliance(token)
    else:
        print("\n⚠️  Skipping remaining tests - login failed")
        results['basic_query'] = False
        results['advanced_query'] = False
        results['rbac'] = False
    
    # Summary
    print_section("TEST SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\nTest Results:")
    for test_name, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {test_name.replace('_', ' ').title()}")
    
    print("\n" + "="*80)
    
    if all(results.values()):
        print("🎉 ALL TESTS PASSED! Module 5 integration successful!")
    else:
        print("⚠️  Some tests failed. Check logs above for details.")
    
    print("="*80 + "\n")
    
    return all(results.values())

if __name__ == "__main__":
    # Check if server is running
    try:
        requests.get(f"{BASE_URL}/")
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Backend server is not running!")
        print(f"Please start the server first:")
        print(f"  cd module_4_backend")
        print(f"  python main.py")
        print()
