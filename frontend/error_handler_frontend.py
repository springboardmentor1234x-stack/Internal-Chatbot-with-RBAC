"""
Frontend Error Handler for Streamlit Application

This module provides comprehensive error handling for the Streamlit frontend,
including user-friendly error messages, retry mechanisms, and error reporting.
"""

import streamlit as st
import requests
import traceback
import json
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from enum import Enum
import time


class ErrorType(Enum):
    """Frontend error types"""
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    SERVER = "server"
    SYSTEM = "system"
    USER_INPUT = "user_input"


class FrontendErrorHandler:
    """Comprehensive error handler for Streamlit frontend"""
    
    def __init__(self):
        self.error_count = 0
        self.last_errors = []
        self.max_stored_errors = 10
    
    def handle_request_error(
        self,
        error: Exception,
        operation: str = "request",
        show_user_message: bool = True,
        retry_callback: Callable = None
    ) -> Dict[str, Any]:
        """
        Handle request-related errors with user-friendly messages
        
        Args:
            error: The exception that occurred
            operation: Description of the operation that failed
            show_user_message: Whether to show error message to user
            retry_callback: Function to call for retry
            
        Returns:
            Error information dictionary
        """
        
        error_info = self._analyze_error(error, operation)
        
        # Store error for debugging
        self._store_error(error_info)
        
        if show_user_message:
            self._display_error_message(error_info, retry_callback)
        
        return error_info
    
    def _analyze_error(self, error: Exception, operation: str) -> Dict[str, Any]:
        """Analyze error and categorize it"""
        
        error_str = str(error).lower()
        error_type = type(error).__name__
        
        # Determine error category
        if isinstance(error, requests.exceptions.ConnectionError):
            category = ErrorType.NETWORK
            user_message = "🔌 Cannot connect to the server. Please check your internet connection."
            suggestions = [
                "Check if the backend server is running",
                "Verify your internet connection",
                "Try refreshing the page"
            ]
            severity = "high"
            
        elif isinstance(error, requests.exceptions.Timeout):
            category = ErrorType.NETWORK
            user_message = "⏰ Request timed out. The server might be busy."
            suggestions = [
                "Try again in a few moments",
                "Check your internet connection",
                "Contact support if the problem persists"
            ]
            severity = "medium"
            
        elif isinstance(error, requests.exceptions.HTTPError):
            status_code = getattr(error.response, 'status_code', 0) if hasattr(error, 'response') else 0
            
            if status_code == 401:
                category = ErrorType.AUTHENTICATION
                user_message = "🔐 Your session has expired. Please log in again."
                suggestions = [
                    "Click the login button",
                    "Check your credentials",
                    "Clear browser cache if problems persist"
                ]
                severity = "high"
                
            elif status_code == 403:
                category = ErrorType.AUTHORIZATION
                user_message = "🚫 You don't have permission to access this resource."
                suggestions = [
                    "Contact your administrator for access",
                    "Check if you're using the correct account",
                    "Verify your role permissions"
                ]
                severity = "high"
                
            elif status_code >= 500:
                category = ErrorType.SERVER
                user_message = "🔧 Server error occurred. Please try again later."
                suggestions = [
                    "Try again in a few minutes",
                    "Contact support if the problem persists",
                    "Check system status page"
                ]
                severity = "high"
                
            else:
                category = ErrorType.SERVER
                user_message = f"❌ Request failed with status {status_code}."
                suggestions = [
                    "Try again",
                    "Check your input data",
                    "Contact support if needed"
                ]
                severity = "medium"
                
        elif "validation" in error_str or "invalid" in error_str:
            category = ErrorType.VALIDATION
            user_message = "⚠️ Invalid input provided. Please check your data."
            suggestions = [
                "Review your input for errors",
                "Check required fields",
                "Follow the input format guidelines"
            ]
            severity = "low"
            
        else:
            category = ErrorType.SYSTEM
            user_message = "❌ An unexpected error occurred. Please try again."
            suggestions = [
                "Try refreshing the page",
                "Clear browser cache",
                "Contact support if the problem persists"
            ]
            severity = "medium"
        
        return {
            "category": category,
            "error_type": error_type,
            "message": str(error),
            "user_message": user_message,
            "suggestions": suggestions,
            "severity": severity,
            "operation": operation,
            "timestamp": datetime.now().isoformat(),
            "stack_trace": traceback.format_exc()
        }
    
    def _store_error(self, error_info: Dict[str, Any]):
        """Store error for debugging and analytics"""
        self.error_count += 1
        self.last_errors.append(error_info)
        
        # Keep only recent errors
        if len(self.last_errors) > self.max_stored_errors:
            self.last_errors = self.last_errors[-self.max_stored_errors:]
        
        # Update session state
        if "error_count" not in st.session_state:
            st.session_state.error_count = 0
        st.session_state.error_count += 1
    
    def _display_error_message(
        self,
        error_info: Dict[str, Any],
        retry_callback: Callable = None
    ):
        """Display user-friendly error message"""
        
        severity = error_info["severity"]
        user_message = error_info["user_message"]
        suggestions = error_info["suggestions"]
        
        # Display error based on severity
        if severity == "high":
            st.error(user_message)
        elif severity == "medium":
            st.warning(user_message)
        else:
            st.info(user_message)
        
        # Show suggestions in an expander
        if suggestions:
            with st.expander("💡 Troubleshooting Tips", expanded=False):
                for i, suggestion in enumerate(suggestions, 1):
                    st.write(f"{i}. {suggestion}")
        
        # Show retry button if callback provided
        if retry_callback:
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("🔄 Retry", key=f"retry_{error_info['timestamp']}"):
                    try:
                        retry_callback()
                        st.success("✅ Retry successful!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Retry failed: {str(e)}")
            
            with col2:
                if st.button("📋 Report Issue", key=f"report_{error_info['timestamp']}"):
                    self._show_error_report_form(error_info)
    
    def _show_error_report_form(self, error_info: Dict[str, Any]):
        """Show error reporting form"""
        st.session_state.show_error_report = True
        st.session_state.error_to_report = error_info
    
    def safe_request(
        self,
        request_func: Callable,
        operation: str = "request",
        max_retries: int = 3,
        retry_delay: float = 1.0,
        show_progress: bool = True,
        **kwargs
    ) -> Optional[Any]:
        """
        Safely execute a request with automatic retry and error handling
        
        Args:
            request_func: Function to execute
            operation: Description of the operation
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            show_progress: Whether to show progress indicators
            **kwargs: Arguments to pass to request_func
            
        Returns:
            Request result or None if failed
        """
        
        for attempt in range(max_retries + 1):
            try:
                if show_progress and attempt > 0:
                    st.info(f"🔄 Retrying {operation} (attempt {attempt + 1}/{max_retries + 1})...")
                
                result = request_func(**kwargs)
                
                if show_progress and attempt > 0:
                    st.success(f"✅ {operation} successful after {attempt + 1} attempts")
                
                return result
                
            except Exception as e:
                if attempt < max_retries:
                    if show_progress:
                        st.warning(f"⚠️ {operation} failed, retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 1.5  # Exponential backoff
                else:
                    # Final attempt failed
                    self.handle_request_error(e, operation, show_user_message=True)
                    return None
    
    def validate_backend_connection(self, backend_url: str) -> bool:
        """
        Validate backend connection with comprehensive error handling
        
        Args:
            backend_url: Backend URL to test
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = requests.get(f"{backend_url}/health", timeout=5)
            
            if response.status_code == 200:
                health_data = response.json()
                
                # Check component health
                components = health_data.get("components", {})
                unhealthy_components = [
                    comp for comp, status in components.items() 
                    if status in ["error", "degraded"]
                ]
                
                if unhealthy_components:
                    st.warning(f"⚠️ Backend connected but some components are unhealthy: {', '.join(unhealthy_components)}")
                    return True  # Still usable
                else:
                    st.success("✅ Backend connection healthy")
                    return True
            else:
                st.error(f"❌ Backend responded with status {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            st.error("🔌 Cannot connect to backend server")
            st.info("💡 Make sure the backend is running: `python run.py`")
            return False
            
        except requests.exceptions.Timeout:
            st.error("⏰ Backend connection timed out")
            return False
            
        except Exception as e:
            st.error(f"❌ Backend connection error: {str(e)}")
            return False
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for debugging"""
        return {
            "total_errors": self.error_count,
            "recent_errors": len(self.last_errors),
            "error_categories": self._get_error_category_counts(),
            "last_error": self.last_errors[-1] if self.last_errors else None
        }
    
    def _get_error_category_counts(self) -> Dict[str, int]:
        """Get count of errors by category"""
        category_counts = {}
        for error in self.last_errors:
            category = error["category"].value
            category_counts[category] = category_counts.get(category, 0) + 1
        return category_counts
    
    def clear_error_history(self):
        """Clear error history"""
        self.last_errors = []
        self.error_count = 0
        if "error_count" in st.session_state:
            st.session_state.error_count = 0


# Global error handler instance
frontend_error_handler = FrontendErrorHandler()


def safe_api_call(
    url: str,
    method: str = "GET",
    operation: str = "API call",
    show_spinner: bool = True,
    spinner_text: str = None,
    **kwargs
) -> Optional[requests.Response]:
    """
    Safely make API calls with comprehensive error handling
    
    Args:
        url: API endpoint URL
        method: HTTP method
        operation: Description of the operation
        show_spinner: Whether to show spinner
        spinner_text: Custom spinner text
        **kwargs: Additional arguments for requests
        
    Returns:
        Response object or None if failed
    """
    
    def make_request():
        return requests.request(method, url, **kwargs)
    
    if show_spinner:
        with st.spinner(spinner_text or f"🔄 {operation}..."):
            return frontend_error_handler.safe_request(
                make_request,
                operation=operation,
                max_retries=2
            )
    else:
        return frontend_error_handler.safe_request(
            make_request,
            operation=operation,
            max_retries=2
        )


def handle_session_error():
    """Handle session-related errors"""
    st.error("🔐 Your session has expired or is invalid")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Refresh Page"):
            st.rerun()
    
    with col2:
        if st.button("🚪 Go to Login"):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


def show_error_report_dialog():
    """Show error reporting dialog if requested"""
    if st.session_state.get("show_error_report", False):
        error_info = st.session_state.get("error_to_report", {})
        
        st.subheader("📋 Report Error")
        
        with st.form("error_report_form"):
            st.write("**Error Details:**")
            st.code(f"Operation: {error_info.get('operation', 'Unknown')}")
            st.code(f"Error: {error_info.get('message', 'Unknown')}")
            st.code(f"Time: {error_info.get('timestamp', 'Unknown')}")
            
            user_description = st.text_area(
                "Describe what you were trying to do:",
                placeholder="Please describe the steps that led to this error..."
            )
            
            user_email = st.text_input(
                "Your email (optional):",
                placeholder="your.email@company.com"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.form_submit_button("📤 Send Report"):
                    # In a real application, you would send this to your support system
                    st.success("✅ Error report sent successfully!")
                    st.session_state.show_error_report = False
                    st.session_state.error_to_report = {}
                    st.rerun()
            
            with col2:
                if st.form_submit_button("❌ Cancel"):
                    st.session_state.show_error_report = False
                    st.session_state.error_to_report = {}
                    st.rerun()


def display_error_statistics():
    """Display error statistics in sidebar"""
    if st.session_state.get("error_count", 0) > 0:
        with st.sidebar:
            st.divider()
            st.subheader("⚠️ Error Statistics")
            
            stats = frontend_error_handler.get_error_statistics()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Errors", stats["total_errors"])
            with col2:
                st.metric("Recent", stats["recent_errors"])
            
            if stats["error_categories"]:
                st.write("**By Category:**")
                for category, count in stats["error_categories"].items():
                    st.write(f"• {category.title()}: {count}")
            
            if st.button("🗑️ Clear Error History"):
                frontend_error_handler.clear_error_history()
                st.success("Error history cleared")
                st.rerun()


# Export main functions
__all__ = [
    'frontend_error_handler', 'safe_api_call', 'handle_session_error',
    'show_error_report_dialog', 'display_error_statistics'
]