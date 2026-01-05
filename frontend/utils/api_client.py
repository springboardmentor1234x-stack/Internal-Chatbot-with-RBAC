import requests
from typing import Optional, Dict, Any

class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.token: Optional[str] = None
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login and store token"""
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            return data
        else:
            raise Exception(f"Login failed: {response.text}")
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get current user information"""
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.base_url}/auth/me", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("Failed to get user info")
    
    def send_message(self, query: str) -> Dict[str, Any]:
        """Send chat message"""
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(
            f"{self.base_url}/chat",
            headers=headers,
            json={"query": query}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Chat failed: {response.text}")

