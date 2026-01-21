#!/usr/bin/env python3
"""
RBAC Testing Script
Tests that users from different departments can only access their own department's data
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def register_user(username, email, password, role):
    """Register a new user"""
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
            "role": role
        }
    )
    return response

def login_user(username, password):
    """Login and get token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": username, "password": password}
    )
    if response.status_code == 200:
        return response.json()
    return None

def send_query(token, query):
    """Send a query to the RAG system"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/query/advanced",
        json={"query": query, "top_k": 5},
        headers=headers
    )
    return response.json() if response.status_code == 200 else None

def print_separator():
    print("=" * 80)

def main():
    print_separator()
    print("RBAC TESTING SCRIPT")
    print("Testing that users can only access their department's data")
    print_separator()
    
    # Test users
    test_users = [
        {"username": "test_hr_user", "email": "test_hr@test.com", "password": "testpass123", "role": "hr_employee"},
        {"username": "test_finance_user", "email": "test_finance@test.com", "password": "testpass123", "role": "finance_employee"},
    ]
    
    # Queries for each department
    hr_query = "What is Krishna Verma's performance rating?"
    finance_query = "What was the total revenue for 2024?"
    marketing_query = "What were the key marketing initiatives in Q4 2024?"
    
    # Register test users
    print("\n1. REGISTERING TEST USERS")
    print("-" * 40)
    for user in test_users:
        resp = register_user(user["username"], user["email"], user["password"], user["role"])
        if resp.status_code in [200, 201]:
            print(f"   [OK] Registered: {user['username']} ({user['role']})")
        elif resp.status_code == 400:
            print(f"   [OK] User already exists: {user['username']} ({user['role']})")
        else:
            print(f"   [ERROR] Failed to register {user['username']}: {resp.text}")
    
    # Login and test HR User
    print("\n" + "=" * 80)
    print("2. TESTING HR EMPLOYEE ACCESS")
    print("-" * 40)
    
    hr_token_data = login_user("test_hr_user", "testpass123")
    if hr_token_data:
        hr_token = hr_token_data["access_token"]
        print(f"   [OK] Logged in as: test_hr_user (role: {hr_token_data['role']})")
        
        # Test HR question (should work)
        print(f"\n   Query 1 (HR - should work): {hr_query}")
        result = send_query(hr_token, hr_query)
        if result:
            sources = result.get('sources', [])
            departments = set(s.get('department', 'Unknown') for s in sources)
            print(f"   Answer preview: {result.get('answer', 'No answer')[:150]}...")
            print(f"   Sources from departments: {departments}")
            if 'HR' in departments or 'General' in departments:
                print("   [PASS] HR user can access HR/General documents")
            else:
                print("   [INFO] No HR/General sources found")
        else:
            print("   [INFO] No results returned")
        
        # Test Finance question (should NOT show finance-specific data)
        print(f"\n   Query 2 (Finance - should be restricted): {finance_query}")
        result = send_query(hr_token, finance_query)
        if result:
            sources = result.get('sources', [])
            departments = set(s.get('department', 'Unknown') for s in sources)
            print(f"   Answer preview: {result.get('answer', 'No answer')[:150]}...")
            print(f"   Sources from departments: {departments}")
            if 'Finance' in departments:
                print("   [FAIL] HR user can access Finance documents - RBAC issue!")
            else:
                print("   [PASS] HR user cannot access Finance-specific documents")
        else:
            print("   [PASS] No finance results returned for HR user")
        
        # Test Marketing question (should NOT show marketing-specific data)
        print(f"\n   Query 3 (Marketing - should be restricted): {marketing_query}")
        result = send_query(hr_token, marketing_query)
        if result:
            sources = result.get('sources', [])
            departments = set(s.get('department', 'Unknown') for s in sources)
            print(f"   Answer preview: {result.get('answer', 'No answer')[:150]}...")
            print(f"   Sources from departments: {departments}")
            if 'Marketing' in departments:
                print("   [FAIL] HR user can access Marketing documents - RBAC issue!")
            else:
                print("   [PASS] HR user cannot access Marketing-specific documents")
        else:
            print("   [PASS] No marketing results returned for HR user")
    else:
        print("   [ERROR] Failed to login as HR user")
    
    # Login and test Finance User
    print("\n" + "=" * 80)
    print("3. TESTING FINANCE EMPLOYEE ACCESS")
    print("-" * 40)
    
    finance_token_data = login_user("test_finance_user", "testpass123")
    if finance_token_data:
        finance_token = finance_token_data["access_token"]
        print(f"   [OK] Logged in as: test_finance_user (role: {finance_token_data['role']})")
        
        # Test Finance question (should work)
        print(f"\n   Query 1 (Finance - should work): {finance_query}")
        result = send_query(finance_token, finance_query)
        if result:
            sources = result.get('sources', [])
            departments = set(s.get('department', 'Unknown') for s in sources)
            print(f"   Answer preview: {result.get('answer', 'No answer')[:150]}...")
            print(f"   Sources from departments: {departments}")
            if 'Finance' in departments or 'General' in departments:
                print("   [PASS] Finance user can access Finance/General documents")
            else:
                print("   [INFO] No Finance/General sources found")
        else:
            print("   [INFO] No results returned")
        
        # Test HR question (should NOT show HR-specific data)
        print(f"\n   Query 2 (HR - should be restricted): {hr_query}")
        result = send_query(finance_token, hr_query)
        if result:
            sources = result.get('sources', [])
            departments = set(s.get('department', 'Unknown') for s in sources)
            print(f"   Answer preview: {result.get('answer', 'No answer')[:150]}...")
            print(f"   Sources from departments: {departments}")
            if 'HR' in departments:
                print("   [FAIL] Finance user can access HR documents - RBAC issue!")
            else:
                print("   [PASS] Finance user cannot access HR-specific documents")
        else:
            print("   [PASS] No HR results returned for Finance user")
        
        # Test Marketing question (should NOT show marketing-specific data)
        print(f"\n   Query 3 (Marketing - should be restricted): {marketing_query}")
        result = send_query(finance_token, marketing_query)
        if result:
            sources = result.get('sources', [])
            departments = set(s.get('department', 'Unknown') for s in sources)
            print(f"   Answer preview: {result.get('answer', 'No answer')[:150]}...")
            print(f"   Sources from departments: {departments}")
            if 'Marketing' in departments:
                print("   [FAIL] Finance user can access Marketing documents - RBAC issue!")
            else:
                print("   [PASS] Finance user cannot access Marketing-specific documents")
        else:
            print("   [PASS] No marketing results returned for Finance user")
    else:
        print("   [ERROR] Failed to login as Finance user")
    
    print("\n" + "=" * 80)
    print("RBAC TESTING COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
