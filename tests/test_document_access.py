#!/usr/bin/env python3
"""
Test document access functionality
"""
import requests
import json

def test_document_access():
    """Test if users can access documents through chat queries"""
    
    # Test users with different roles
    test_cases = [
        {"username": "hr_user", "role": "HR", "query": "What are the employee policies?"},
        {"username": "finance_user", "role": "Finance", "query": "What is our financial performance?"},
        {"username": "marketing_user", "role": "Marketing", "query": "What are our marketing results?"},
        {"username": "engineering_user", "role": "Engineering", "query": "What are the technical guidelines?"},
        {"username": "intern_user", "role": "Intern", "query": "What company policies should I know?"},
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 Testing {test_case['username']} ({test_case['role']})")
        print("-" * 50)
        
        # Login
        login_response = requests.post(
            'http://127.0.0.1:8000/auth/login',
            data={'username': test_case['username'], 'password': 'password123'},
            timeout=10
        )
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            print(f"✅ Login successful")
            
            # Test chat query
            headers = {"Authorization": f"Bearer {login_data['access_token']}"}
            chat_response = requests.post(
                'http://127.0.0.1:8000/api/v1/chat',
                json={"query": test_case['query']},
                headers=headers,
                timeout=15
            )
            
            if chat_response.status_code == 200:
                chat_data = chat_response.json()
                print(f"✅ Chat query successful")
                print(f"   Query: {test_case['query']}")
                print(f"   Response length: {len(chat_data.get('response', ''))} characters")
                print(f"   Sources: {chat_data.get('sources', [])}")
                print(f"   Accuracy: {chat_data.get('accuracy_score', 0)}")
                print(f"   Document-based: {chat_data.get('quality_metrics', {}).get('document_based', False)}")
                
                # Show first 150 characters of response
                response_preview = chat_data.get('response', '')[:150] + "..."
                print(f"   Preview: {response_preview}")
                
            else:
                print(f"❌ Chat query failed: {chat_response.status_code}")
                print(f"   Error: {chat_response.text}")
        else:
            print(f"❌ Login failed: {login_response.status_code}")

if __name__ == "__main__":
    print("🚀 Testing Document Access Functionality")
    print("=" * 60)
    test_document_access()
    print("\n" + "=" * 60)
    print("✅ Document access test completed!")