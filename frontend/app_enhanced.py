import streamlit as st
import requests
import os
import time
import json
from datetime import datetime, timedelta
import sys

# Add the parent directory to the path to import our enhancements
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our security and accuracy enhancements
from security_enhancements import security_manager, secure_input, require_authentication, monitor_security
from accuracy_improvements import advanced_accuracy_enhancer

# The URL where your FastAPI backend is running
BACKEND_URL = "http://127.0.0.1:8000"

# Enhanced session state initialization with security features
def initialize_session_state():
    """Initialize all session state variables with enhanced security."""
    default_states = {
        "authenticated": False,
        "username": "",
        "access_token": "",
        "refresh_token": "",
        "user_role": "Employee",
        "messages": [],
        "chat_session_id": None,
        "login_time": None,
        "last_activity": None,
        "processing": False,
        "error_count": 0,
        "total_queries": 0,
        "session_accuracy": [],
        "theme_preference": "light",
        "security_events": [],
        "failed_login_attempts": 0,
        "last_failed_login": None,
        "session_fingerprint": None,
        "csrf_token": None
    }
    
    for key, default_value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

@monitor_security
def update_activity():
    "