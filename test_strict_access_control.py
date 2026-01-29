#!/usr/bin/env python3
"""
Test script to verify strict role-based document access control
Each user should only access their specific documents
"""
import requests
import json

BACKEND_URL = "http://127.0.0.1:8000"

# Test scenarios for strict access control
TEST_SCENARIOS = [
    {
        "username": "admin",
        "role": "C-Level",
        "should_access": ["quarterly_financial_report.md", "market_report_q4_2024.md", "employee_handbook.md", "engineering_master_doc.md"],
        "queries": ["What are our financial results?", "Show me marketing data", "What's in the employee handbook?", "Show engineering docs"]
    },
    {
        "username": "finance_user", 
        "role": "Finance",
        "should_access": ["quarterly_financial_report.md"],
        "should_deny": ["market_report_q4_2024.md", "employee_handbook.md", "engineering_master_doc.md"],
        "queries": ["What are our financial results?", "Show me marketing data", "What's in the employee handbook?"]
    },
    {
        "username": "marketing_user",
        "role": "Marketing", 
        "should_access": ["market_report_q4_2024.md"],
        "should_deny": ["quarterly_financial_report.md", "employee_handbook.md", "engineering_master_doc.md"],
        "queries": ["Show me marketing data", "What are our financial results?", "What's in the employee handbook?"]
    },
    {
        "username": "hr_user",
        "role": "HR",
        "should_access": ["employee_handbook.md"],
        "should_deny": ["quarterly_financial_report.md", "market_report_q4_2024.md", "engineering_master_doc.md"],
        "queries": ["What's in the employee handbook?", "What are our financial results?", "Show me marketing data"]
    },
    {
        "username": "engineering_user",
        "role": "Engineering",
        "should_access": ["engineering_master_doc.md"],
        "should_deny": ["quarterly_financial_report.md", "market_report_q4_2024.md", "employee_handbook.md"],
        "queries": ["Show engineering docs", "What are our financial results?", "What's in the employee handbook?"]
    },
    {
        "username": "employee",
        "role": "Employee",
        "should_access": [],
        "should_deny": ["quarterly_financial_report.md", "market_report_q4_2024.md", "employee_handbook.md", "engineering_master_doc.md"],
        "queries": ["What are our financial results?", "Show me marketing data", "What's in the employee handbook?"]
    },
    {
        "username": "intern_user",
        "role": "Intern", 
        "should_access": [],
        "should_deny": ["quarterly_financial_report.md", "market_report_q4_2024.md", "employee_handbook.md", "engineering_master_doc.md"],
        "queries": ["What are our financial results?", "Show me marketing data", "What's in the employee handbook?"]
    }
]

def login_user(username, password="password123"):
    """Login and get access token"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print(f"❌ Login failed for {username}: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Login error for {username}: {e}")
        return None

def test_chat_query(token, query, expected_access=True):
    """Test a chat query and check if access is granted or denied"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{BACKEND_URL}/api/v1/chat",
            json={"query": query},
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get("response", "")
            sources = data.get("sources", [])
            
            # Check if access was denied
            access_denied = "Access Denied" in response_text or "access denied" in response_text.lower()
            
            if expected_access and not access_denied:
                return True, f"✅ Access granted - Sources: {sources}"
            elif not expected_access and access_denied:
                return True, f"✅ Access correctly denied"
            elif expected_access and access_denied:
                return False, f"❌ Access unexpectedly denied"
            else:
                return False, f"❌ Access unexpectedly granted - Sources: {sources}"
        else:
            return False, f"❌ Query failed: {response.status_code}"
            
    except Exception as e:
        return False, f"❌ Query error: {e}"

def test_user_access(scenario):
    """Test access control for a specific user"""
    username = scenario["username"]
    role = scenario["role"]
    
    print(f"\n🧪 Testing {username} ({role})")
    print("-" * 40)
    
    # Login
    token = login_user(username)
    if not token:
        print(f"❌ Could not login {username}")
        return False
    
    print(f"✅ Logged in successfully")
    
    # Test queries that should be allowed
    allowed_count = 0
    total_allowed = len(scenario.get("should_access", []))
    
    if total_allowed > 0:
        print(f"\n📄 Testing access to {total_allowed} allowed documents:")
        for i, query in enumerate(scenario["queries"][:total_allowed]):
            success, message = test_chat_query(token, query, expected_access=True)
            print(f"   {i+1}. {query}")
            print(f"      {message}")
            if success:
                allowed_count += 1
    
    # Test queries that should be denied
    denied_count = 0
    denied_queries = scenario["queries"][total_allowed:] if total_allowed > 0 else scenario["queries"]
    
    if denied_queries:
        print(f"\n🔒 Testing access denial for {len(denied_queries)} restricted queries:")
        for i, query in enumerate(denied_queries):
            success, message = test_chat_query(token, query, expected_access=False)
            print(f"   {i+1}. {query}")
            print(f"      {message}")
            if success:
                denied_count += 1
    
    # Calculate success rate
    total_tests = total_allowed + len(denied_queries)
    successful_tests = allowed_count + denied_count
    success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n📊 Results: {successful_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
    
    return success_rate == 100.0

def main():
    print("🔐 Strict Role-Based Access Control Test")
    print("=" * 50)
    print("Testing that each user can ONLY access their specific documents")
    print("Employee handbook should NOT be accessible to all users anymore")
    print()
    
    # Test backend health
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend is not running. Please start it with: python run.py")
            return
        print("✅ Backend is running")
    except:
        print("❌ Backend is not accessible. Please start it with: python run.py")
        return
    
    # Test each user scenario
    successful_users = 0
    total_users = len(TEST_SCENARIOS)
    
    for scenario in TEST_SCENARIOS:
        success = test_user_access(scenario)
        if success:
            successful_users += 1
    
    print("\n" + "=" * 50)
    print("📊 STRICT ACCESS CONTROL TEST RESULTS")
    print("=" * 50)
    print(f"✅ Users with correct access control: {successful_users}/{total_users}")
    print(f"❌ Users with access issues: {total_users - successful_users}/{total_users}")
    
    if successful_users == total_users:
        print("\n🎉 PERFECT! Strict access control is working correctly!")
        print("✅ Each user can only access their specific documents")
        print("✅ Employee handbook is no longer accessible to all users")
        print("✅ Role-based permissions are properly enforced")
    else:
        print(f"\n⚠️ {total_users - successful_users} users have access control issues")
        print("🔧 Please check the role-based document permissions")
    
    print("\n🔐 Access Summary:")
    print("• C-Level: All documents")
    print("• Finance: Financial reports only") 
    print("• Marketing: Marketing reports only")
    print("• HR: Employee handbook only")
    print("• Engineering: Technical docs only")
    print("• Employee: No specific documents")
    print("• Intern: No specific documents")

if __name__ == "__main__":
    main()