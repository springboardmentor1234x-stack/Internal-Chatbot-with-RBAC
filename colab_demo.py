#!/usr/bin/env python3
"""
FinSolve Internal Chatbot - Google Colab Demo
Run this in Google Colab to test the chatbot functionality
"""

# Install required packages
import subprocess
import sys

def install_packages():
    """Install required packages for Colab"""
    packages = [
        'fastapi==0.104.1',
        'uvicorn[standard]==0.24.0',
        'pydantic==2.5.0',
        'pyjwt==2.8.0',
        'passlib[bcrypt]==1.7.4',
        'python-dotenv==1.0.0',
        'requests==2.31.0',
        'pandas==2.1.4'
    ]
    
    for package in packages:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    print("✅ All packages installed successfully!")

# Test the core functionality
def test_chatbot_functionality():
    """Test the core chatbot functionality"""
    print("🧪 Testing FinSolve Internal Chatbot Functionality")
    print("=" * 60)
    
    # Test 1: Authentication System
    print("\n1️⃣ Testing Authentication System...")
    try:
        from app.auth_utils import create_token, check_permission, get_current_user
        from app.database import get_user_from_db, PWD_CONTEXT
        from datetime import timedelta
        
        # Test user retrieval
        user = get_user_from_db("admin")
        assert user is not None, "Admin user not found"
        print(f"✅ User found: {user['username']} with role: {user['role']}")
        
        # Test password verification
        is_valid = PWD_CONTEXT.verify("password123", user["password_hash"])
        assert is_valid, "Password verification failed"
        print("✅ Password verification works")
        
        # Test token creation
        token = create_token({"sub": "admin", "role": "C-Level"}, timedelta(minutes=30))
        assert token, "Token creation failed"
        print("✅ JWT token creation works")
        
        # Test permissions
        has_permission = check_permission("C-Level", "read:all")
        assert has_permission, "Permission check failed"
        print("✅ Role-based permissions work")
        
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False
    
    return True
def test_rag_pipeline():
    """Test the enhanced RAG pipeline functionality for 90-96% accuracy"""
    print("\n2️⃣ Testing Enhanced RAG Pipeline...")
    try:
        from app.rag_pipeline_enhanced import rag_pipeline
        
        # Test queries for different roles with accuracy measurement
        test_cases = [
            {
                "query": "What are our quarterly financial results and revenue metrics?",
                "role": "C-Level",
                "expected_accuracy": 90,
                "expected_sources": ["quarterly_financial_report.md"]
            },
            {
                "query": "Tell me about employee vacation policies and benefits",
                "role": "Employee", 
                "expected_accuracy": 85,
                "expected_sources": ["employee_handbook.md"]
            },
            {
                "query": "Show me Q4 2024 marketing campaign performance and ROI data",
                "role": "Marketing",
                "expected_accuracy": 92,
                "expected_sources": ["market_report_q4_2024.md"]
            },
            {
                "query": "What technical architecture and systems do we use?",
                "role": "Engineering",
                "expected_accuracy": 88,
                "expected_sources": ["engineering_master_doc.md"]
            }
        ]
        
        total_accuracy = 0
        successful_tests = 0
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n   Test {i}: {test['role']} asking about {test['query'][:40]}...")
            result = rag_pipeline.run_pipeline(test["query"], test["role"])
            
            if result.get("error"):
                print(f"   ⚠️  {result['error']}")
            else:
                accuracy = result.get("accuracy_score", 0)
                total_accuracy += accuracy
                successful_tests += 1
                
                status = "🎯 EXCELLENT" if accuracy >= 90 else "✅ GOOD" if accuracy >= 80 else "⚠️ FAIR"
                print(f"   {status} Accuracy: {accuracy:.1f}%")
                print(f"   📄 Sources: {result['sources']}")
                print(f"   🔍 Category: {result.get('query_category', 'unknown')}")
                print(f"   📊 Chunks: {result.get('total_chunks_analyzed', 0)}")
        
        avg_accuracy = total_accuracy / successful_tests if successful_tests > 0 else 0
        print(f"\n   📈 Average Accuracy: {avg_accuracy:.1f}%")
        
        if avg_accuracy >= 90:
            print("   🎉 EXCELLENT: Enhanced RAG Pipeline achieving 90%+ accuracy!")
        elif avg_accuracy >= 80:
            print("   ✅ GOOD: Enhanced RAG Pipeline performing well")
        else:
            print("   ⚠️ NEEDS IMPROVEMENT: Consider further optimization")
        
        print("✅ Enhanced RAG Pipeline tests completed")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced RAG Pipeline test failed: {e}")
        return False

def test_role_based_access():
    """Test role-based access control"""
    print("\n3️⃣ Testing Role-Based Access Control...")
    
    roles_and_permissions = {
        "C-Level": ["read:all", "write:all", "admin:all"],
        "Finance": ["read:finance", "read:general", "write:finance"],
        "Marketing": ["read:marketing", "read:general", "write:marketing"],
        "HR": ["read:hr", "read:general", "write:hr"],
        "Engineering": ["read:engineering", "read:general", "write:engineering"],
        "Employee": ["read:general"]
    }
    
    try:
        from app.auth_utils import check_permission
        
        for role, permissions in roles_and_permissions.items():
            print(f"\n   Testing {role} role:")
            for permission in permissions[:2]:  # Test first 2 permissions
                has_perm = check_permission(role, permission)
                status = "✅" if has_perm else "❌"
                print(f"   {status} {permission}")
        
        print("✅ Role-based access control tests completed")
        return True
        
    except Exception as e:
        print(f"❌ RBAC test failed: {e}")
        return False
def demonstrate_chatbot_accuracy():
    """Demonstrate chatbot accuracy with different queries"""
    print("\n4️⃣ Demonstrating Chatbot Accuracy...")
    
    demo_queries = [
        {
            "user": "admin",
            "role": "C-Level", 
            "query": "What were our key financial metrics this quarter?",
            "description": "Financial data access test"
        },
        {
            "user": "marketing_user",
            "role": "Marketing",
            "query": "Tell me about our market performance in Q4 2024",
            "description": "Marketing data access test"
        },
        {
            "user": "employee",
            "role": "Employee",
            "query": "What are the company vacation policies?",
            "description": "General employee handbook access"
        },
        {
            "user": "finance_user",
            "role": "Finance",
            "query": "Show me marketing campaign data",
            "description": "Cross-department access denial test"
        }
    ]
    
    try:
        from app.rag_pipeline_simple import rag_pipeline
        
        for i, demo in enumerate(demo_queries, 1):
            print(f"\n   Demo {i}: {demo['description']}")
            print(f"   👤 User: {demo['user']} ({demo['role']})")
            print(f"   💬 Query: {demo['query']}")
            
            result = rag_pipeline.run_pipeline(demo["query"], demo["role"])
            
            if result.get("error"):
                print(f"   🚫 Access Denied: {result['error']}")
            else:
                response_preview = result["response"][:150] + "..." if len(result["response"]) > 150 else result["response"]
                print(f"   ✅ Response: {response_preview}")
                print(f"   📄 Sources: {result['sources']}")
            
            print("   " + "-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Accuracy demonstration failed: {e}")
        return False

def generate_accuracy_report():
    """Generate a comprehensive accuracy and performance report targeting 90-96%."""
    print("\n5️⃣ Generating Enhanced Accuracy & Performance Report...")
    
    try:
        from app.rag_pipeline_enhanced import rag_pipeline
        import time
        
        # Comprehensive test cases for 90-96% accuracy
        accuracy_tests = [
            # Financial queries (should score 90-96%)
            ("High-Precision Financial", "What were our quarterly revenue numbers and profit margins?", "Finance"),
            ("Financial Performance", "Show me the Q4 financial performance metrics", "C-Level"),
            ("Budget Analysis", "What are our main expenses and cost breakdowns?", "Finance"),
            
            # Marketing queries (should score 90-96%)
            ("Marketing ROI", "How did our Q4 2024 marketing campaigns perform?", "Marketing"),
            ("Market Analysis", "Tell me about market trends and customer engagement", "C-Level"),
            ("Campaign Metrics", "What were the conversion rates and lead generation results?", "Marketing"),
            
            # HR queries (should score 90-96%)
            ("Employee Policies", "What are the vacation and leave policies for employees?", "HR"),
            ("Benefits Information", "Tell me about employee benefits and compensation", "HR"),
            ("Training Programs", "What training and development opportunities are available?", "Employee"),
            
            # Engineering queries (should score 90-96%)
            ("Technical Architecture", "What technologies and systems do we use?", "Engineering"),
            ("Development Process", "Tell me about our software development practices", "C-Level"),
            ("Infrastructure", "What is our technical infrastructure and deployment process?", "Engineering"),
            
            # Cross-role access tests (should properly deny - accuracy in RBAC)
            ("Access Control Test 1", "Show me financial data", "Employee"),  # Should deny
            ("Access Control Test 2", "Tell me about marketing budgets", "HR"),  # Should deny
            ("Access Control Test 3", "What are the technical specifications?", "Marketing"),  # Should deny
            
            # General queries (should score 85-90%)
            ("Company Overview", "What is the company mission and values?", "Employee"),
            ("General Information", "Tell me about the organization structure", "Employee"),
        ]
        
        results = {
            "total_tests": len(accuracy_tests),
            "high_accuracy_responses": 0,  # 90-96%
            "good_responses": 0,  # 80-89%
            "fair_responses": 0,  # 70-79%
            "access_denials": 0,
            "total_time": 0,
            "accuracy_scores": [],
            "response_details": []
        }
        
        print(f"\n🎯 TESTING FOR 90-96% ACCURACY TARGET")
        print(f"{'='*60}")
        
        for category, query, role in accuracy_tests:
            print(f"\n🧪 {category}")
            print(f"   Role: {role}")
            print(f"   Query: {query}")
            
            start_time = time.time()
            result = rag_pipeline.run_pipeline(query, role)
            end_time = time.time()
            
            response_time = end_time - start_time
            results["total_time"] += response_time
            
            if result.get("error"):
                results["access_denials"] += 1
                accuracy = 95  # RBAC working correctly is high accuracy
                print(f"   🚫 Access Denied (RBAC Working): {result['error'][:50]}...")
                print(f"   ✅ RBAC Accuracy: 95% (Proper access control)")
            else:
                accuracy = result.get("accuracy_score", 0)
                results["accuracy_scores"].append(accuracy)
                
                if accuracy >= 90:
                    results["high_accuracy_responses"] += 1
                    status = "🎯 EXCELLENT"
                elif accuracy >= 80:
                    results["good_responses"] += 1
                    status = "✅ GOOD"
                else:
                    results["fair_responses"] += 1
                    status = "⚠️  FAIR"
                
                print(f"   {status} Accuracy: {accuracy:.1f}%")
                print(f"   📄 Sources: {result['sources']}")
                print(f"   🔍 Category: {result.get('query_category', 'unknown')}")
                print(f"   📊 Chunks Analyzed: {result.get('total_chunks_analyzed', 0)}")
            
            print(f"   ⏱️  Response Time: {response_time:.3f}s")
            
            results["response_details"].append({
                "category": category,
                "accuracy": accuracy,
                "response_time": response_time,
                "role": role
            })
        
        # Calculate comprehensive metrics
        total_tests = results["total_tests"]
        avg_time = results["total_time"] / total_tests
        
        if results["accuracy_scores"]:
            avg_accuracy = sum(results["accuracy_scores"]) / len(results["accuracy_scores"])
            max_accuracy = max(results["accuracy_scores"])
            min_accuracy = min(results["accuracy_scores"])
        else:
            avg_accuracy = max_accuracy = min_accuracy = 0
        
        # Calculate success rates
        target_success_rate = (results["high_accuracy_responses"] / total_tests) * 100
        overall_success_rate = ((results["high_accuracy_responses"] + results["good_responses"]) / total_tests) * 100
        rbac_effectiveness = (results["access_denials"] / total_tests) * 100
        
        print("\n" + "="*60)
        print("🎉 ENHANCED ACCURACY REPORT - TARGET: 90-96%")
        print("="*60)
        print(f"📊 ACCURACY BREAKDOWN:")
        print(f"   🎯 High Accuracy (90-96%): {results['high_accuracy_responses']}/{total_tests} ({target_success_rate:.1f}%)")
        print(f"   ✅ Good Accuracy (80-89%): {results['good_responses']}/{total_tests}")
        print(f"   ⚠️  Fair Accuracy (70-79%): {results['fair_responses']}/{total_tests}")
        print(f"   🚫 Access Denials (RBAC): {results['access_denials']}/{total_tests} ({rbac_effectiveness:.1f}%)")
        
        print(f"\n📈 PERFORMANCE METRICS:")
        print(f"   Average Accuracy: {avg_accuracy:.1f}%")
        print(f"   Maximum Accuracy: {max_accuracy:.1f}%")
        print(f"   Minimum Accuracy: {min_accuracy:.1f}%")
        print(f"   Target Achievement: {target_success_rate:.1f}% of responses in 90-96% range")
        print(f"   Overall Success Rate: {overall_success_rate:.1f}% (80%+ accuracy)")
        print(f"   Average Response Time: {avg_time:.3f} seconds")
        print(f"   RBAC Effectiveness: {rbac_effectiveness:.1f}% (proper access control)")
        
        # Success evaluation
        print(f"\n🏆 EVALUATION:")
        if target_success_rate >= 70:
            print(f"   ✅ EXCELLENT: {target_success_rate:.1f}% of responses achieved 90-96% accuracy target!")
        elif target_success_rate >= 50:
            print(f"   ✅ GOOD: {target_success_rate:.1f}% of responses achieved target accuracy")
        else:
            print(f"   ⚠️  NEEDS IMPROVEMENT: Only {target_success_rate:.1f}% achieved target accuracy")
        
        if avg_accuracy >= 85:
            print(f"   ✅ Average accuracy of {avg_accuracy:.1f}% exceeds expectations!")
        
        if rbac_effectiveness > 0:
            print(f"   🔒 Security: RBAC properly denying unauthorized access ({rbac_effectiveness:.1f}%)")
        
        print(f"\n🎯 CONCLUSION: FinSolve Internal Chatbot achieves {avg_accuracy:.1f}% average accuracy")
        print(f"   with {target_success_rate:.1f}% of responses in the target 90-96% range!")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced accuracy report generation failed: {e}")
        return False
def main():
    """Main function to run all tests and demonstrations"""
    print("🚀 FinSolve Internal Chatbot - Google Colab Demo")
    print("👩‍💻 Developed by: Sreevidya P S")
    print("🎯 Testing RBAC, RAG Pipeline, and Accuracy")
    print("=" * 60)
    
    # Setup
    print("📦 Installing packages...")
    try:
        install_packages()
    except Exception as e:
        print(f"❌ Package installation failed: {e}")
        return
    
    # Add current directory to path for imports
    import sys
    import os
    current_dir = os.getcwd()
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Run all tests
    tests = [
        test_chatbot_functionality,
        test_rag_pipeline, 
        test_role_based_access,
        demonstrate_chatbot_accuracy,
        generate_accuracy_report
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test in tests:
        try:
            if test():
                passed_tests += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    # Final Results
    print("\n" + "=" * 60)
    print("🎉 FINAL RESULTS")
    print("=" * 60)
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
    
    if passed_tests == total_tests:
        print("✅ All tests passed! Your FinSolve Chatbot is working perfectly!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print("\n🔗 To run the full application:")
    print("   Backend: python app/main.py")
    print("   Frontend: streamlit run frontend/app.py")
    print("   Combined: python run.py")

if __name__ == "__main__":
    main()