"""
API Client for RAG Chatbot
Handles all communication with FastAPI backend
"""

import requests
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

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
            raise APIError("Not authenticated. Please login first.")
        return {"Authorization": f"Bearer {self.access_token}"}
    
    def _map_error_message(self, status_code: int, detail: str = None) -> str:
        """Map HTTP status codes to user-friendly messages"""
        if status_code == 401:
            if detail and "expired" in detail.lower():
                return "🔒 Your session has expired. Please log in again."
            return "🔒 Authentication failed. Please log in again."
        if status_code == 403:
            if detail:
                return f"⛔ {detail}"
            return "⛔ You do not have permission to perform this action."
        if status_code == 404:
            if detail:
                return f"⚠️ {detail}"
            return "⚠️ The requested resource was not found."
        if status_code == 429:
            return "⏳ Too many requests. Please try again shortly."
        if status_code >= 500:
            return "🚧 Server error. Please try again later."
        if detail:
            return f"⚠️ {detail}"
        return "⚠️ Unable to process your request right now."

    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response safely (no backend leaks)"""

        # Extract detail message if available
        detail = None
        try:
            error_data = response.json()
            detail = error_data.get("detail")
        except:
            pass

        # 🔐 Authentication
        if response.status_code == 401:
            if self.refresh_token and not ("refresh" in response.url):
                try:
                    refreshed = self.refresh_access_token()
                    if refreshed:
                        return {"success": False, "retry": True}
                except:
                    pass
            raise APIError(self._map_error_message(401, detail))

        # ⛔ Authorization
        if response.status_code == 403:
            raise APIError(self._map_error_message(403, detail))

        # ❌ Client / Server errors
        if response.status_code >= 400:
            try:
                error_data = response.json()
            except:
                error_data = response.text

            # 🔍 INTERNAL LOG (never shown to user)
            print(
                f"[API ERROR] {response.status_code} | "
                f"URL: {response.url} | "
                f"DETAIL: {error_data}"
            )

            # 🎯 USER-FACING SAFE MESSAGE
            raise APIError(self._map_error_message(response.status_code, detail))

        return response.json()

    
    # ==================== AUTHENTICATION ====================
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login with username and password"""
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
            raise APIError("❌ Cannot connect to server. Please check your network connection.")
        except requests.exceptions.Timeout:
            raise APIError("⏳ Request timed out. Please try again.")
        except APIError as e:
            raise e
        except Exception as e:
            raise APIError(f"⚠️ Login failed: {str(e)}")

    
    def logout(self) -> Dict[str, Any]:
        """Logout and invalidate token"""
        try:
            requests.post(
                f"{self.base_url}/auth/logout",
                headers=self._get_headers(),
                json={
                    "refresh_token": self.refresh_token
                },
                timeout=10
            )
            
            # Clear tokens
            self.access_token = None
            self.refresh_token = None
            self.token_expiry = None
            
            return {"success": True, "message": "Logged out successfully"}
        
        except Exception:
            # Clear tokens anyway
            self.access_token = None
            self.refresh_token = None
            self.token_expiry = None
            return {"success": True, "message": "Logged out locally"}
    
    def refresh_access_token(self) -> bool:
        """Refresh access token using refresh token"""
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
        try:
            response = requests.get(
                f"{self.base_url}/auth/me",
                headers=self._get_headers(),
                timeout=10
            )
            
            return self._handle_response(response)
        except requests.exceptions.Timeout:
            raise APIError("⏳ Request timed out while fetching user information.")
        except APIError:
            raise
        except Exception as e:
            raise APIError(f"⚠️ Failed to fetch user information: {str(e)}")
    
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
        """Send chat query and get AI response with sources"""
        try:
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
        except requests.exceptions.Timeout:
            raise APIError("⏳ The query took too long to process. Please try a simpler question.")
        except APIError:
            raise
        except Exception as e:
            raise APIError(f"⚠️ Failed to process query: {str(e)}")
    
    def retrieval_only(
        self,
        query: str,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """Get document retrieval results without LLM response"""
        try:
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
        except requests.exceptions.Timeout:
            raise APIError("⏳ Document retrieval timed out. Please try again.")
        except APIError:
            raise
        except Exception as e:
            raise APIError(f"⚠️ Failed to retrieve documents: {str(e)}")
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get RAG pipeline statistics for current user"""
        try:
            response = requests.get(
                f"{self.base_url}/chat/stats",
                headers=self._get_headers(),
                timeout=10
            )
            
            return self._handle_response(response)
        except requests.exceptions.Timeout:
            raise APIError("⏳ Request timed out while fetching pipeline statistics.")
        except APIError:
            raise
        except Exception as e:
            raise APIError(f"⚠️ Failed to fetch pipeline statistics: {str(e)}")
    
    # ==================== ADMIN ENDPOINTS ====================
    
    def list_users(self) -> List[Dict[str, Any]]:
        """List all users (admin only)"""
        try:
            response = requests.get(
                f"{self.base_url}/admin/users",
                headers=self._get_headers(),
                timeout=10
            )
            
            data = self._handle_response(response)
            return data.get("users", [])
        except requests.exceptions.Timeout:
            raise APIError("⏳ Request timed out while fetching users.")
        except APIError:
            raise
        except Exception as e:
            raise APIError(f"⚠️ Failed to fetch users: {str(e)}")
    
    def create_user(
        self,
        username: str,
        password: str,
        role: str
    ) -> Dict[str, Any]:
        """Create new user (admin only)"""
        try:
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
        except requests.exceptions.Timeout:
            raise APIError("⏳ Request timed out while creating user.")
        except APIError:
            raise
        except Exception as e:
            raise APIError(f"⚠️ Failed to create user: {str(e)}")
    
    def update_user(
        self,
        username: str,
        is_active: Optional[bool] = None,
        role: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update user (admin only)"""
        try:
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
        except requests.exceptions.Timeout:
            raise APIError("⏳ Request timed out while updating user.")
        except APIError:
            raise
        except Exception as e:
            raise APIError(f"⚠️ Failed to update user: {str(e)}")
    
    # ==================== AUDIT LOGS ====================
    
    def get_auth_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get authentication logs (admin only)"""
        try:
            response = requests.get(
                f"{self.base_url}/logs/auth?limit={limit}",
                headers=self._get_headers(),
                timeout=10
            )
            
            data = self._handle_response(response)
            return data.get("logs", [])
        except requests.exceptions.Timeout:
            raise APIError("⏳ Request timed out while fetching authentication logs.")
        except APIError:
            raise
        except Exception as e:
            raise APIError(f"⚠️ Failed to fetch authentication logs: {str(e)}")
    
    def get_access_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get access control logs (admin only)"""
        try:
            response = requests.get(
                f"{self.base_url}/logs/access?limit={limit}",
                headers=self._get_headers(),
                timeout=10
            )
            
            data = self._handle_response(response)
            return data.get("logs", [])
        except requests.exceptions.Timeout:
            raise APIError("⏳ Request timed out while fetching access logs.")
        except APIError:
            raise
        except Exception as e:
            raise APIError(f"⚠️ Failed to fetch access logs: {str(e)}")
    
    def get_rag_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get RAG pipeline logs (admin only)"""
        try:
            response = requests.get(
                f"{self.base_url}/logs/rag?limit={limit}",
                headers=self._get_headers(),
                timeout=10
            )
            
            data = self._handle_response(response)
            return data.get("logs", [])
        except requests.exceptions.Timeout:
            raise APIError("⏳ Request timed out while fetching RAG logs.")
        except APIError:
            raise
        except Exception as e:
            raise APIError(f"⚠️ Failed to fetch RAG logs: {str(e)}")
    
    def get_user_activity(
        self,
        username: str,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Get activity logs for specific user"""
        try:
            response = requests.get(
                f"{self.base_url}/logs/user/{username}?limit={limit}",
                headers=self._get_headers(),
                timeout=10
            )
            
            return self._handle_response(response)
        except requests.exceptions.Timeout:
            raise APIError("⏳ Request timed out while fetching user activity.")
        except APIError:
            raise
        except Exception as e:
            raise APIError(f"⚠️ Failed to fetch user activity: {str(e)}")
    
    # ==================== HEALTH CHECK ====================
    
    def health_check(self) -> Dict[str, Any]:
        """Check if backend is running"""
        try:
            response = requests.get(
                f"{self.base_url}/",
                timeout=5
            )
            return response.json()
        except requests.exceptions.ConnectionError:
            return {"status": "offline", "message": "Cannot connect to server"}
        except requests.exceptions.Timeout:
            return {"status": "offline", "message": "Server connection timed out"}
        except Exception:
            return {"status": "offline", "message": "Server unavailable"}