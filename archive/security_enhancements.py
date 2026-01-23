"""
Enhanced Security Module for Streamlit App
Provides comprehensive security features including rate limiting, input validation,
session management, and security headers.
"""

import streamlit as st
import hashlib
import time
import re
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from functools import wraps
import logging

# Configure security logging
logging.basicConfig(level=logging.INFO)
security_logger = logging.getLogger("security")

class SecurityManager:
    """Comprehensive security manager for Streamlit app."""
    
    def __init__(self):
        self.rate_limits = {}
        self.failed_attempts = {}
        self.blocked_ips = {}
        self.session_tokens = {}
        self.csrf_tokens = {}
        
    def get_client_ip(self) -> str:
        """Get client IP address from Streamlit context."""
        try:
            # Try to get real IP from headers
            if hasattr(st, 'context') and hasattr(st.context, 'headers'):
                headers = st.context.headers
                # Check common proxy headers
                for header in ['X-Forwarded-For', 'X-Real-IP', 'CF-Connecting-IP']:
                    if header in headers:
                        return headers[header].split(',')[0].strip()
            
            # Fallback to session-based identification
            if 'client_id' not in st.session_state:
                st.session_state.client_id = secrets.token_hex(16)
            return st.session_state.client_id
        except:
            return "unknown"
    
    def rate_limit(self, action: str, max_attempts: int = 5, window_minutes: int = 15):
        """Rate limiting decorator for actions."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                client_ip = self.get_client_ip()
                key = f"{client_ip}:{action}"
                current_time = datetime.now()
                
                # Clean old entries
                if key in self.rate_limits:
                    self.rate_limits[key] = [
                        timestamp for timestamp in self.rate_limits[key]
                        if current_time - timestamp < timedelta(minutes=window_minutes)
                    ]
                else:
                    self.rate_limits[key] = []
                
                # Check rate limit
                if len(self.rate_limits[key]) >= max_attempts:
                    security_logger.warning(f"Rate limit exceeded for {client_ip} on {action}")
                    st.error(f"⚠️ Too many attempts. Please wait {window_minutes} minutes before trying again.")
                    return None
                
                # Record attempt
                self.rate_limits[key].append(current_time)
                
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def validate_input(self, input_text: str, input_type: str = "general") -> Dict[str, Any]:
        """Comprehensive input validation."""
        validation_result = {
            "is_valid": True,
            "sanitized_input": input_text,
            "warnings": [],
            "blocked_patterns": []
        }
        
        if not input_text or not isinstance(input_text, str):
            validation_result["is_valid"] = False
            validation_result["warnings"].append("Invalid input type")
            return validation_result
        
        # Length validation
        max_lengths = {
            "query": 2000,
            "username": 50,
            "general": 1000
        }
        max_length = max_lengths.get(input_type, 1000)
        
        if len(input_text) > max_length:
            validation_result["is_valid"] = False
            validation_result["warnings"].append(f"Input too long (max {max_length} characters)")
            return validation_result
        
        # XSS prevention
        xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>',
            r'<link[^>]*>',
            r'<meta[^>]*>',
            r'vbscript:',
            r'data:text/html'
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, input_text, re.IGNORECASE):
                validation_result["blocked_patterns"].append("XSS attempt")
                validation_result["sanitized_input"] = re.sub(pattern, '', input_text, flags=re.IGNORECASE)
                validation_result["warnings"].append("Potentially malicious content removed")
        
        # SQL injection prevention
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",
            r"(--|#|/\*|\*/)",
            r"(\bUNION\s+SELECT\b)",
            r"(\b(EXEC|EXECUTE)\s+\w+)",
            r"(\bDROP\s+TABLE\b)"
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, input_text, re.IGNORECASE):
                validation_result["blocked_patterns"].append("SQL injection attempt")
                validation_result["warnings"].append("Potentially malicious SQL content detected")
                # Don't sanitize SQL - reject entirely for security
                validation_result["is_valid"] = False
                break
        
        # Command injection prevention
        command_patterns = [
            r'[;&|`$(){}[\]\\]',
            r'\b(cat|ls|pwd|whoami|id|uname|ps|netstat|ifconfig|ping|wget|curl)\b'
        ]
        
        for pattern in command_patterns:
            if re.search(pattern, input_text):
                validation_result["blocked_patterns"].append("Command injection attempt")
                validation_result["sanitized_input"] = re.sub(pattern, '', input_text)
                validation_result["warnings"].append("Potentially dangerous characters removed")
        
        # Path traversal prevention
        if '../' in input_text or '..\\' in input_text:
            validation_result["blocked_patterns"].append("Path traversal attempt")
            validation_result["sanitized_input"] = input_text.replace('../', '').replace('..\\', '')
            validation_result["warnings"].append("Path traversal attempt blocked")
        
        # Log security events
        if validation_result["blocked_patterns"]:
            client_ip = self.get_client_ip()
            security_logger.warning(f"Security violation from {client_ip}: {validation_result['blocked_patterns']}")
        
        return validation_result
    
    def generate_csrf_token(self) -> str:
        """Generate CSRF token for forms."""
        token = secrets.token_urlsafe(32)
        self.csrf_tokens[token] = datetime.now()
        return token
    
    def validate_csrf_token(self, token: str) -> bool:
        """Validate CSRF token."""
        if not token or token not in self.csrf_tokens:
            return False
        
        # Check if token is expired (30 minutes)
        if datetime.now() - self.csrf_tokens[token] > timedelta(minutes=30):
            del self.csrf_tokens[token]
            return False
        
        return True
    
    def secure_session_management(self):
        """Enhanced session security."""
        # Generate session fingerprint
        if 'session_fingerprint' not in st.session_state:
            user_agent = st.context.headers.get('User-Agent', 'unknown') if hasattr(st, 'context') else 'unknown'
            client_ip = self.get_client_ip()
            fingerprint_data = f"{user_agent}:{client_ip}:{datetime.now().date()}"
            st.session_state.session_fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()
        
        # Session timeout with warning
        if st.session_state.get("last_activity"):
            time_since_activity = datetime.now() - st.session_state.last_activity
            
            # Warning at 25 minutes
            if time_since_activity > timedelta(minutes=25) and time_since_activity < timedelta(minutes=30):
                st.warning("⏰ Your session will expire in 5 minutes due to inactivity.")
            
            # Force logout at 30 minutes
            if time_since_activity > timedelta(minutes=30):
                self.force_logout("Session expired due to inactivity")
                return False
        
        return True
    
    def force_logout(self, reason: str = "Security logout"):
        """Force user logout and clear session."""
        security_logger.info(f"Force logout: {reason} for client {self.get_client_ip()}")
        
        # Clear all session data except preferences
        keys_to_keep = ["theme_preference"]
        for key in list(st.session_state.keys()):
            if key not in keys_to_keep:
                del st.session_state[key]
        
        st.error(f"🔐 {reason}")
        st.rerun()
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security events for monitoring."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "client_ip": self.get_client_ip(),
            "event_type": event_type,
            "details": details,
            "user": st.session_state.get("username", "anonymous")
        }
        
        security_logger.info(f"Security Event: {event_type} - {details}")
        
        # Store in session for admin review (in production, use proper logging system)
        if 'security_events' not in st.session_state:
            st.session_state.security_events = []
        
        st.session_state.security_events.append(log_entry)
        
        # Keep only last 100 events
        if len(st.session_state.security_events) > 100:
            st.session_state.security_events = st.session_state.security_events[-100:]
    
    def add_security_headers(self):
        """Add security headers to the response."""
        # Note: Streamlit doesn't allow direct header manipulation
        # These would be implemented at the reverse proxy level
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
        
        # Log recommendation for proxy configuration
        security_logger.info("Recommended security headers for reverse proxy configuration:")
        for header, value in security_headers.items():
            security_logger.info(f"{header}: {value}")
    
    def monitor_suspicious_activity(self):
        """Monitor for suspicious activity patterns."""
        client_ip = self.get_client_ip()
        current_time = datetime.now()
        
        # Track rapid requests
        if 'request_times' not in st.session_state:
            st.session_state.request_times = []
        
        st.session_state.request_times.append(current_time)
        
        # Keep only last 10 minutes of requests
        st.session_state.request_times = [
            req_time for req_time in st.session_state.request_times
            if current_time - req_time < timedelta(minutes=10)
        ]
        
        # Check for suspicious patterns
        if len(st.session_state.request_times) > 50:  # More than 50 requests in 10 minutes
            self.log_security_event("suspicious_activity", {
                "pattern": "high_request_rate",
                "request_count": len(st.session_state.request_times),
                "time_window": "10_minutes"
            })
            
            st.warning("⚠️ High activity detected. Please slow down your requests.")
            time.sleep(2)  # Force a small delay


# Global security manager instance
security_manager = SecurityManager()

def secure_input(input_text: str, input_type: str = "general") -> str:
    """Secure input validation and sanitization."""
    validation = security_manager.validate_input(input_text, input_type)
    
    if not validation["is_valid"]:
        st.error("❌ Invalid input detected. Please check your input and try again.")
        for warning in validation["warnings"]:
            st.warning(f"⚠️ {warning}")
        return ""
    
    if validation["warnings"]:
        for warning in validation["warnings"]:
            st.info(f"ℹ️ {warning}")
    
    return validation["sanitized_input"]

def require_authentication(func):
    """Decorator to require authentication for functions."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not st.session_state.get("authenticated", False):
            st.error("🔐 Authentication required")
            return None
        
        # Check session security
        if not security_manager.secure_session_management():
            return None
        
        return func(*args, **kwargs)
    return wrapper

def monitor_security(func):
    """Decorator to monitor function calls for security."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        security_manager.monitor_suspicious_activity()
        return func(*args, **kwargs)
    return wrapper