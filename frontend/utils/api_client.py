"""
API Client for RAG Chatbot
Handles all communication with FastAPI backend
"""

import requests
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import streamlit as st

class APIError(Exception):
    """Safe, user-facing API error"""
    pass


class APIClient:
    """Client for interacting with RAG Chatbot API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token"""
        if not self.access_token:
            raise Exception("Not authenticated. Please login first.")
        return {"Authorization": f"Bearer {self.access_token}"}
    
    def _map_error_message(self, status_code: int) -> str:
        if status_code == 401:
            return "🔒 Your session has expired. Please log in again."
        if status_code == 403:
            return "⛔ You do not have permission to perform this action."
        if status_code == 404:
            return "⚠️ The AI service is temporarily unavailable."
        if status_code == 429:
            return "⏳ Too many requests. Please try again shortly."
        if status_code >= 500:
            return "🚧 Server error. Please try again later."
        return "⚠️ Unable to process your request right now."

    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response safely (no backend leaks)"""

        # 🔐 Authentication
        if response.status_code == 401:
            if self.refresh_token:
                try:
                    refreshed = self.refresh_access_token()
                    if refreshed:
                        return {"success": False, "retry": True}
                except Exception:
                    pass
            raise APIError("🔒 Your session has expired. Please log in again.")

        # ⛔ Authorization
        if response.status_code == 403:
            raise APIError("⛔ Access denied. Insufficient permissions.")

        # ❌ Client / Server errors
        if response.status_code >= 400:
            try:
                error_data = response.json()
            except Exception:
                error_data = response.text

            # 🔍 INTERNAL LOG (never shown to user)
            print(
                f"[API ERROR] {response.status_code} | "
                f"URL: {response.url} | "
                f"DETAIL: {error_data}"
            )

            # 🎯 USER-FACING SAFE MESSAGE
            raise APIError(self._map_error_message(response.status_code))

        return response.json()

    
    # ==================== AUTHENTICATION ====================
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={"username": username, "password": password},
                timeout=10
            )

            data = self._handle_response(response)

            self.access_token = data["access_token"]
            self.refresh_token = data["refresh_token"]

            expires_in = data.get("expires_in", 900)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)

            return {
                "success": True,
                "user_info": data["user_info"],
                "expires_in": expires_in
            }

        except requests.exceptions.ConnectionError:
            raise APIError("❌ Cannot connect to server.")
        except requests.exceptions.Timeout:
            raise APIError("⏳ Request timed out.")
        except APIError as e:
            raise e
        except Exception:
            raise APIError("⚠️ Login failed. Please try again.")

    
    def logout(self) -> Dict[str, Any]:
        """
        Logout and invalidate token
        """
        try:
            response = requests.post(
                f"{self.base_url}/auth/logout",
                headers=self._get_headers(),
                timeout=10
            )
            
            # Clear tokens
            self.access_token = None
            self.refresh_token = None
            self.token_expiry = None
            
            return {"success": True, "message": "Logged out successfully"}
        
        except Exception as e:
            # Clear tokens anyway
            self.access_token = None
            self.refresh_token = None
            self.token_expiry = None
            return {"success": True, "message": "Logged out locally"}
    
    def refresh_access_token(self) -> bool:
        """
        Refresh access token using refresh token
        
        Returns:
            True if successful, False otherwise
        """
        if not self.refresh_token:
            return False
        
        try:
            response = requests.post(
                f"{self.base_url}/auth/refresh",
                json={"refresh_token": self.refresh_token},
                timeout=10
            )
            
            data = self._handle_response(response)
            
            self.access_token = data["access_token"]
            expires_in = data.get("expires_in", 900)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            
            return True
        
        except:
            return False
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get current user information including accessible departments"""
        response = requests.get(
            f"{self.base_url}/auth/me",
            headers=self._get_headers(),
            timeout=10
        )
        
        return self._handle_response(response)
    
    def is_token_expiring_soon(self) -> bool:
        """Check if token will expire in next 2 minutes"""
        if not self.token_expiry:
            return False
        return datetime.now() >= (self.token_expiry - timedelta(minutes=2))
    
    # ==================== CHAT ENDPOINTS ====================
    
    def chat_query(
        self,
        query: str,
        top_k: int = 5,
        max_tokens: int = 500
    ) -> Dict[str, Any]:
        """
        Send chat query and get AI response with sources
        
        Args:
            query: User's question
            top_k: Number of documents to retrieve
            max_tokens: Maximum tokens for LLM response
            
        Returns:
            Response with answer, sources, and confidence
        """
        response = requests.post(
            f"{self.base_url}/chat/query",
            headers=self._get_headers(),
            json={
                "query": query,
                "top_k": top_k,
                "max_tokens": max_tokens
            },
            timeout=80  # Longer timeout for LLM
        )
        
        return self._handle_response(response)
    
    def retrieval_only(
        self,
        query: str,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Get document retrieval results without LLM response
        
        Args:
            query: Search query
            top_k: Number of documents to retrieve
            
        Returns:
            Retrieved documents with metadata
        """
        response = requests.post(
            f"{self.base_url}/chat/retrieval-only",
            headers=self._get_headers(),
            json={
                "query": query,
                "top_k": top_k
            },
            timeout=30
        )
        
        return self._handle_response(response)
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get RAG pipeline statistics for current user"""
        response = requests.get(
            f"{self.base_url}/chat/stats",
            headers=self._get_headers(),
            timeout=10
        )
        
        return self._handle_response(response)
    
    # ==================== ADMIN ENDPOINTS ====================
    
    def list_users(self) -> List[Dict[str, Any]]:
        """List all users (admin only)"""
        response = requests.get(
            f"{self.base_url}/admin/users",
            headers=self._get_headers(),
            timeout=10
        )
        
        data = self._handle_response(response)
        return data.get("users", [])
    
    def create_user(
        self,
        username: str,
        password: str,
        role: str
    ) -> Dict[str, Any]:
        """Create new user (admin only)"""
        response = requests.post(
            f"{self.base_url}/admin/users",
            headers=self._get_headers(),
            json={
                "username": username,
                "password": password,
                "role": role
            },
            timeout=10
        )
        
        return self._handle_response(response)
    
    def update_user(
        self,
        username: str,
        is_active: Optional[bool] = None,
        role: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update user (admin only)"""
        update_data = {}
        if is_active is not None:
            update_data["is_active"] = is_active
        if role is not None:
            update_data["role"] = role
        
        response = requests.patch(
            f"{self.base_url}/admin/users/{username}",
            headers=self._get_headers(),
            json=update_data,
            timeout=10
        )
        
        return self._handle_response(response)
    
    # ==================== AUDIT LOGS ====================
    
    def get_auth_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get authentication logs (admin only)"""
        response = requests.get(
            f"{self.base_url}/logs/auth?limit={limit}",
            headers=self._get_headers(),
            timeout=10
        )
        
        data = self._handle_response(response)
        return data.get("logs", [])
    
    def get_access_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get access control logs (admin only)"""
        response = requests.get(
            f"{self.base_url}/logs/access?limit={limit}",
            headers=self._get_headers(),
            timeout=10
        )
        
        data = self._handle_response(response)
        return data.get("logs", [])
    
    def get_rag_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get RAG pipeline logs (admin only)"""
        response = requests.get(
            f"{self.base_url}/logs/rag?limit={limit}",
            headers=self._get_headers(),
            timeout=10
        )
        
        data = self._handle_response(response)
        return data.get("logs", [])
    
    def get_user_activity(
        self,
        username: str,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Get activity logs for specific user"""
        response = requests.get(
            f"{self.base_url}/logs/user/{username}?limit={limit}",
            headers=self._get_headers(),
            timeout=10
        )
        
        return self._handle_response(response)
    
    # ==================== HEALTH CHECK ====================
    
    def health_check(self) -> Dict[str, Any]:
        """Check if backend is running"""
        try:
            response = requests.get(
                f"{self.base_url}/",
                timeout=5
            )
            return response.json()
        except:
            return {"status": "offline"}