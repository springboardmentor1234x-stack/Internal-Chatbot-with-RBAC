import requests
import json

# Test intern_user login
print("Testing intern_user login...")
response = requests.post(
    'http://127.0.0.1:8000/auth/login', 
    data={'username': 'intern_user', 'password': 'password123'}
)

if response.status_code == 200:
    data = response.json()
    print(f"✅ Login successful! Role: {data['user']['role']}")
    
    # Test chat
    headers = {"Authorization": f"Bearer {data['access_token']}"}
    chat_response = requests.post(
        'http://127.0.0.1:8000/api/v1/chat',
        json={"query": "What training materials are available?"},
        headers=headers
    )
    
    if chat_response.status_code == 200:
        chat_data = chat_response.json()
        print(f"✅ Chat successful!")
        print(f"Response: {chat_data['response'][:150]}...")
    else:
        print(f"❌ Chat failed: {chat_response.status_code}")
else:
    print(f"❌ Login failed: {response.status_code} - {response.text}")