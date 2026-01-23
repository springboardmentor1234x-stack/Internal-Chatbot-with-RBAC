
# Quick accuracy test
import requests
import json

def quick_test():
    # Test login
    login_response = requests.post(
        "http://127.0.0.1:8000/auth/login",
        data={"username": "admin", "password": "password123"}
    )
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        print("Login successful")
        
        # Test chat with accuracy metrics
        headers = {"Authorization": f"Bearer {token}"}
        chat_response = requests.post(
            "http://127.0.0.1:8000/api/v1/chat",
            json={"query": "What is FinSolve's mission?"},
            headers=headers
        )
        
        if chat_response.status_code == 200:
            data = chat_response.json()
            accuracy = data.get("accuracy_score", 0)
            print(f"Chat successful - Accuracy: {accuracy:.1f}%")
            
            # Check for enhanced features
            if "quality_metrics" in data:
                print("Quality metrics available")
            if "query_optimization" in data:
                print("Query optimization available")
            if "improvement_suggestions" in data:
                print("Improvement suggestions available")
        else:
            print(f"Chat failed: {chat_response.status_code}")
    else:
        print(f"Login failed: {login_response.status_code}")

if __name__ == "__main__":
    quick_test()
