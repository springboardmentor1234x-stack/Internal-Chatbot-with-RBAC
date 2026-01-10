"""
Session state management for Streamlit
Handles secure session initialization and cleanup
"""

import streamlit as st
from datetime import datetime
from typing import Optional, Dict, Any

class SessionManager:
    """Manage Streamlit session state"""
    
    @staticmethod
    def initialize():
        """Initialize session state with default values"""
        
        # Authentication state
        if "logged_in" not in st.session_state:
            st.session_state.logged_in = False
        
        if "user_info" not in st.session_state:
            st.session_state.user_info = None
        
        if "login_time" not in st.session_state:
            st.session_state.login_time = None
        
        # Chat state
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        if "current_query" not in st.session_state:
            st.session_state.current_query = ""
        
        # UI state
        if "show_sources" not in st.session_state:
            st.session_state.show_sources = True
        
        if "show_confidence" not in st.session_state:
            st.session_state.show_confidence = True
        
        if "sidebar_expanded" not in st.session_state:
            st.session_state.sidebar_expanded = True
        
        # Settings
        if "top_k" not in st.session_state:
            st.session_state.top_k = 3
        
        if "max_tokens" not in st.session_state:
            st.session_state.max_tokens = 256
        
        # Admin state (if admin user)
        if "admin_view" not in st.session_state:
            st.session_state.admin_view = None  # None means chat view
        
        if "selected_user" not in st.session_state:
            st.session_state.selected_user = None
    
    @staticmethod
    def login(user_info: Dict[str, Any]):
        """Set logged in state"""
        st.session_state.logged_in = True
        st.session_state.user_info = user_info
        st.session_state.login_time = datetime.now()
        st.session_state.messages = []  # Clear previous chat
        st.session_state.admin_view = None  # Reset to chat view
    
    @staticmethod
    def logout():
        """Clear session state on logout"""
        # Keep API client instance
        api_client = st.session_state.get("api_client")
        
        # Clear all session state
        for key in list(st.session_state.keys()):
            if key != "api_client":
                del st.session_state[key]
        
        # Reinitialize
        SessionManager.initialize()
        
        # Restore API client
        if api_client:
            st.session_state.api_client = api_client
    
    @staticmethod
    def add_message(role: str, content: str, **kwargs):
        """Add message to chat history"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(),
            **kwargs
        }
        st.session_state.messages.append(message)
    
    @staticmethod
    def clear_chat():
        """Clear chat history"""
        st.session_state.messages = []
    
    @staticmethod
    def get_user_role() -> Optional[str]:
        """Get current user's role"""
        if st.session_state.user_info:
            return st.session_state.user_info.get("role")
        return None
    
    @staticmethod
    def is_admin() -> bool:
        """Check if current user is admin"""
        role = SessionManager.get_user_role()
        if role:
            return role.lower() == "admin"
        return False
    
    @staticmethod
    def get_session_duration() -> Optional[int]:
        """Get session duration in seconds"""
        if st.session_state.login_time:
            delta = datetime.now() - st.session_state.login_time
            return int(delta.total_seconds())
        return None
    
    @staticmethod
    def update_settings(top_k: int = None, max_tokens: int = None):
        """Update search settings"""
        if top_k is not None:
            st.session_state.top_k = top_k
        if max_tokens is not None:
            st.session_state.max_tokens = max_tokens