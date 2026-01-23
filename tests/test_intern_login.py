#!/usr/bin/env python3
"""
Quick test for intern_user login
"""
import requests

def test_intern_login():
    try:
        response = requests.post(
            'http://127.0.0.1:8000/auth/login', 
            data={'username': 'intern_user', 'password': 'password123'},
            timeout=10
        )
        
        print(f'Status Code: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print(f'✅ Login successful!')
            print(f'   Username: {data.get("user", {}).get("username", "Unknown")}')
            print(f'   Role: {data.get("user", {}).get("role", "Unknown")}')
            print(f'   Token: {data.get("access_token", "No token")[:50]}...')
            
            # Test chat query
            headers = {"Authorization": f"Bearer {data.get('access_token')}"}
            chat_response = requests.post(
                'http://127.0.0.1:8000/api/v1/chat',
                json={"query": "What training materials are available?"},
                headers=headers,
                timeout=10
            )
            
            if chat_response.status_code == 200:
                chat_data = chat_response.json()
                print(f'✅ Chat query successful!')
                print(f'   Response: {chat_data.get("response", "No response")[:100]}...')
                print(f'   Sources: {chat_data.get("sources", [])}')
            else:
                print(f'❌ Chat query failed: {chat_response.status_code}')
                print(f'   Error: {chat_response.text}')
                
        else:
            print(f'❌ Login failed!')
            try:
                error_data = response.json()
                print(f'   Error: {error_data.get("detail", "Unknown error")}')
            except:
                print(f'   Raw response: {response.text}')
                
    except Exception as e:
        print(f'❌ Test failed with error: {e}')

if __name__ == "__main__":
    test_intern_login()