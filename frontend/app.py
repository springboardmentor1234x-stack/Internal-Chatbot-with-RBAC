import streamlit as st
import requests
import os
import time
import json
from datetime import datetime, timedelta

# Import enhanced error handling
from error_handler_frontend import (
    frontend_error_handler, safe_api_call, handle_session_error,
    show_error_report_dialog, display_error_statistics
)

# The URL where your FastAPI backend is running
BACKEND_URL = "http://127.0.0.1:8001"

# Session state initialization
def initialize_session_state():
    """Initialize all session state variables with default values"""
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
        "theme_preference": "light"
    }
    
    for key, default_value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def update_activity():
    """Update last activity timestamp"""
    st.session_state.last_activity = datetime.now()

def is_session_expired():
    """Check if session has expired (30 minutes of inactivity) with enhanced error handling"""
    if not st.session_state.get("last_activity"):
        return False
    
    try:
        # Check for session expiry (30 minutes of inactivity)
        expiry_time = st.session_state.last_activity + timedelta(minutes=30)
        is_expired = datetime.now() > expiry_time
        
        # Also check if authentication token is still valid
        if st.session_state.get("authenticated") and st.session_state.get("access_token"):
            try:
                response = safe_api_call(
                    f"{BACKEND_URL}/api/v1/user/profile",
                    method="GET",
                    headers={"Authorization": f"Bearer {st.session_state.get('access_token')}"},
                    operation="Check session validity",
                    show_spinner=False,
                    timeout=5
                )
                
                if response and response.status_code == 401:
                    # Try to refresh the token before declaring session expired
                    if st.session_state.get("refresh_token"):
                        if refresh_access_token():
                            return False  # Successfully refreshed, session is still valid
                    # Token refresh failed or no refresh token available
                    return True
                elif response is None:
                    # Network error, assume session is still valid for now
                    pass
                    
            except Exception as e:
                # Log error but don't fail session check
                frontend_error_handler.handle_request_error(
                    e, "session validation", show_user_message=False
                )
        
        return is_expired
        
    except Exception as e:
        # Log error but assume session is valid to avoid blocking user
        frontend_error_handler.handle_request_error(
            e, "session expiry check", show_user_message=False
        )
        return False


def refresh_access_token():
    """Attempt to refresh the access token using the refresh token with enhanced error handling."""
    refresh_token = st.session_state.get("refresh_token")
    if not refresh_token:
        return False
    
    try:
        response = safe_api_call(
            f"{BACKEND_URL}/auth/refresh",
            method="POST",
            params={"refresh_token": refresh_token},
            operation="Refresh access token",
            show_spinner=False,
            timeout=10
        )
        
        if response and response.status_code == 200:
            data = response.json()
            # Update access token
            st.session_state.access_token = data["access_token"]
            # Reset activity timestamp
            st.session_state.last_activity = datetime.now()
            return True
        else:
            # Refresh token is invalid or expired
            return False
            
    except Exception as e:
        frontend_error_handler.handle_request_error(
            e, "token refresh", show_user_message=False
        )
        return False

def clear_session():
    """Clear all session state data"""
    keys_to_keep = ["theme_preference"]  # Keep user preferences
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
            del st.session_state[key]
    initialize_session_state()


def view_document(filename):
    """Display document content in a modal-like expander with enhanced error handling"""
    file_path = os.path.join("data", "raw", filename)

    try:
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Create a unique key for each document viewer
                with st.expander(f"📖 Viewing: {filename}", expanded=True):
                    st.markdown("---")
                    st.markdown(content)
                    st.markdown("---")
                    if st.button(f"Close {filename}", key=f"close_{filename}"):
                        st.rerun()
                        
            except UnicodeDecodeError:
                st.error(f"❌ Cannot read {filename}: File encoding not supported")
                st.info("💡 Please ensure the file is saved in UTF-8 encoding")
            except PermissionError:
                st.error(f"❌ Cannot read {filename}: Permission denied")
                st.info("💡 Check file permissions or contact administrator")
            except Exception as e:
                st.error(f"❌ Error reading {filename}: {str(e)}")
                frontend_error_handler.handle_request_error(
                    e, f"reading document {filename}", show_user_message=False
                )
        else:
            st.error(f"❌ Document {filename} not found at {file_path}")
            st.info("💡 Contact administrator to ensure document is available")
            
    except Exception as e:
        st.error(f"❌ Unexpected error accessing document: {str(e)}")
        frontend_error_handler.handle_request_error(
            e, f"accessing document {filename}", show_user_message=False
        )


def check_user_access(filename, user_role):
    """Check if user has access to a specific document"""
    document_permissions = {
        "quarterly_financial_report.md": ["Finance", "C-Level"],
        "market_report_q4_2024.md": ["Marketing", "C-Level"],
        "employee_handbook.md": [
            "HR",
            "Employee",
            "C-Level",
            "Finance",
            "Marketing",
            "Engineering",
        ],
        "engineering_master_doc.md": ["Engineering", "C-Level"],
    }

    allowed_roles = document_permissions.get(filename, ["Employee"])
    return user_role in allowed_roles


def login():
    """Enhanced login interface with comprehensive error handling and session management"""
    st.title("🔐 FinSolve Internal Chatbot - Login")
    st.markdown("**Role-Based Access Control (RBAC) System**")

    # Check for session expiry message
    if st.session_state.get("session_expired"):
        st.warning("⏰ Your session has expired. Please login again.")
        st.session_state.session_expired = False

    # Validate backend connection first
    if not frontend_error_handler.validate_backend_connection(BACKEND_URL):
        st.stop()  # Stop execution if backend is not available

    # Show available test accounts (collapsed by default for security)
    with st.expander("🔧 Demo Test Accounts", expanded=False):
        st.markdown(
            """
        **For demonstration purposes only:**
        
        All test accounts use password: `password123`
        
        - **admin** → C-Level access (all documents)
        - **finance_user** → Finance department access
        - **marketing_user** → Marketing department access  
        - **hr_user** → HR department access
        - **engineering_user** → Engineering department access
        - **employee** → General employee access
        
        *Note: In production, use secure authentication with proper user management.*
        """
        )

    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            submit = st.form_submit_button("🚀 Login", use_container_width=True)
        with col2:
            if st.form_submit_button("🔄 Clear", use_container_width=True):
                st.rerun()

        if submit:
            # Validate input
            if not username or not password:
                st.error("❌ Please enter both username and password")
                return

            # Show login spinner with enhanced error handling
            with st.spinner("🔐 Authenticating..."):
                try:
                    response = safe_api_call(
                        f"{BACKEND_URL}/auth/login",
                        method="POST",
                        data={"username": username, "password": password},
                        operation="User login",
                        timeout=10
                    )

                    if response and response.status_code == 200:
                        data = response.json()
                        
                        # Set session state with role fetched from backend
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.access_token = data["access_token"]
                        st.session_state.refresh_token = data.get("refresh_token", "")
                        st.session_state.login_time = datetime.now()
                        st.session_state.last_activity = datetime.now()
                        st.session_state.chat_session_id = f"{username}_{int(time.time())}"
                        st.session_state.error_count = 0
                        
                        # Fetch and store user role as read-only immediately after login
                        try:
                            profile_response = safe_api_call(
                                f"{BACKEND_URL}/api/v1/user/profile",
                                method="GET",
                                headers={"Authorization": f"Bearer {data['access_token']}"},
                                operation="Fetch user profile",
                                show_spinner=False,
                                timeout=5
                            )
                            
                            if profile_response and profile_response.status_code == 200:
                                profile = profile_response.json()
                                # Store role as read-only in session state
                                st.session_state.user_role = profile.get('role', 'Employee')
                            else:
                                st.session_state.user_role = 'Employee'  # Default fallback
                                
                        except Exception as e:
                            st.session_state.user_role = 'Employee'  # Default fallback
                            frontend_error_handler.handle_request_error(
                                e, "fetch user profile", show_user_message=False
                            )
                        
                        st.success("✅ Login successful!")
                        time.sleep(1)  # Brief pause for user feedback
                        st.rerun()
                        
                    elif response:
                        # Handle specific error responses
                        try:
                            error_data = response.json()
                            error_detail = error_data.get("detail", "Login failed")
                            
                            if response.status_code == 401:
                                st.error(f"🔐 {error_detail}")
                                st.info("💡 Check your username and password")
                            elif response.status_code == 403:
                                st.error(f"🚫 {error_detail}")
                                st.info("💡 Your account may be locked or disabled")
                            else:
                                st.error(f"❌ Login failed: {error_detail}")
                                
                        except json.JSONDecodeError:
                            st.error(f"❌ Login failed with status {response.status_code}")
                        
                        st.session_state.error_count = st.session_state.get("error_count", 0) + 1
                    else:
                        # Response is None (handled by safe_api_call)
                        st.session_state.error_count = st.session_state.get("error_count", 0) + 1
                        
                except Exception as e:
                    frontend_error_handler.handle_request_error(e, "login")
                    st.session_state.error_count = st.session_state.get("error_count", 0) + 1

    # Show connection status with enhanced information
    with st.expander("🔧 System Status", expanded=False):
        try:
            health_response = safe_api_call(
                f"{BACKEND_URL}/health",
                method="GET",
                operation="Health check",
                show_spinner=False,
                timeout=5
            )
            
            if health_response and health_response.status_code == 200:
                health_data = health_response.json()
                st.success("✅ Backend server is running")
                
                # Show component status
                components = health_data.get("components", {})
                if components:
                    st.write("**Component Status:**")
                    for component, status in components.items():
                        if status == "healthy":
                            st.write(f"✅ {component.title()}: {status}")
                        elif status == "degraded":
                            st.write(f"⚠️ {component.title()}: {status}")
                        else:
                            st.write(f"❌ {component.title()}: {status}")
                
                # Show error statistics if available
                error_stats = health_data.get("error_stats", {})
                if error_stats.get("total_errors", 0) > 0:
                    st.write(f"**Recent Errors:** {error_stats['total_errors']}")
                    
            else:
                st.warning("⚠️ Backend server responding with errors")
                
        except Exception as e:
            st.error("❌ Backend server is not accessible")
            st.info("💡 Make sure to run: `python run.py`")
            frontend_error_handler.handle_request_error(
                e, "backend health check", show_user_message=False
            )


def main_chat_interface():
    """Enhanced main chat interface with comprehensive error handling and session management"""
    
    # Check session expiry first
    if is_session_expired():
        st.warning("⏰ Your session has expired due to inactivity. Please login again.")
        st.session_state.session_expired = True
        clear_session()
        time.sleep(2)  # Brief pause to show the message
        st.rerun()
    
    # Update activity timestamp on every interaction
    update_activity()
    
    # Show error report dialog if requested
    show_error_report_dialog()
    
    # Display error statistics in sidebar
    display_error_statistics()
    
    # Sidebar with enhanced user info and controls
    with st.sidebar:
        st.title("👤 User Profile")
        st.write(f"**Username:** {st.session_state.get('username', 'Unknown')}")
        
        # Session info
        if st.session_state.get("login_time"):
            login_duration = datetime.now() - st.session_state.login_time
            st.write(f"**Session:** {str(login_duration).split('.')[0]}")

        # Get user profile from backend and store role as read-only
        user_role = st.session_state.get('user_role', 'Employee')  # Use cached role first
        
        try:
            headers = {
                "Authorization": f"Bearer {st.session_state.get('access_token')}"
            }
            profile_response = requests.get(
                f"{BACKEND_URL}/api/v1/user/profile", headers=headers, timeout=5
            )
            if profile_response.status_code == 200:
                profile = profile_response.json()
                # Store role as read-only in session state (only update if different)
                fetched_role = profile.get('role', 'Employee')
                if st.session_state.get('user_role') != fetched_role:
                    st.session_state.user_role = fetched_role
                user_role = fetched_role
                
                st.write(f"**Role:** {user_role} (Read-only)")
                st.write(f"**Permissions:** {len(profile.get('permissions', []))} permissions")
                
                # Show session expiry countdown
                if st.session_state.get("last_activity"):
                    time_remaining = timedelta(minutes=30) - (datetime.now() - st.session_state.last_activity)
                    if time_remaining.total_seconds() > 0:
                        minutes_left = int(time_remaining.total_seconds() // 60)
                        st.write(f"**Session Expires:** {minutes_left} min")
                        
                        # Warning when less than 5 minutes left
                        if minutes_left <= 5:
                            st.warning(f"⏰ Session expires in {minutes_left} minutes!")
                    else:
                        st.error("⏰ Session expired!")
                        
            elif profile_response.status_code == 401:
                st.error("🔐 Session expired - Please login again")
                st.session_state.session_expired = True
                clear_session()
                st.rerun()
            else:
                st.write("**Role:** Unable to fetch")
                # Use cached role if available
                if st.session_state.get('user_role'):
                    st.write(f"**Cached Role:** {st.session_state.user_role} (Read-only)")
                    user_role = st.session_state.user_role
        except requests.exceptions.Timeout:
            st.write("**Role:** Request timeout")
            # Use cached role if available
            if st.session_state.get('user_role'):
                st.write(f"**Cached Role:** {st.session_state.user_role} (Read-only)")
                user_role = st.session_state.user_role
        except:
            st.write("**Role:** Connection error")
            # Use cached role if available
            if st.session_state.get('user_role'):
                st.write(f"**Cached Role:** {st.session_state.user_role} (Read-only)")
                user_role = st.session_state.user_role

        # Chat statistics
        st.divider()
        st.subheader("📊 Chat Statistics")
        st.write(f"**Total Queries:** {st.session_state.get('total_queries', 0)}")
        st.write(f"**Messages:** {len(st.session_state.get('messages', []))}")
        
        # Average accuracy
        if st.session_state.get('session_accuracy'):
            avg_accuracy = sum(st.session_state.session_accuracy) / len(st.session_state.session_accuracy)
            st.write(f"**Avg Accuracy:** {avg_accuracy:.1f}%")
        
        # Enhanced chat controls with history features
        st.divider()
        st.subheader("🎛️ Chat Controls")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True, help="Clear all chat messages"):
                st.session_state.messages = []
                st.session_state.session_accuracy = []
                st.success("✅ Chat cleared!")
                time.sleep(1)
                st.rerun()
        
        with col2:
            if st.button("🔄 Refresh", use_container_width=True, help="Refresh the interface"):
                st.rerun()
        
        # Save current session
        if st.session_state.get('messages') and len(st.session_state.messages) > 0:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save Session", use_container_width=True, help="Save current chat to history"):
                    try:
                        session_id = st.session_state.get('chat_session_id', f"{st.session_state.username}_{int(time.time())}")
                        
                        headers = {"Authorization": f"Bearer {st.session_state.get('access_token')}"}
                        save_response = requests.post(
                            f"{BACKEND_URL}/api/v1/chat/history/save",
                            json={
                                "session_id": session_id,
                                "messages": st.session_state.messages,
                                "metadata": {
                                    "total_queries": st.session_state.get('total_queries', 0),
                                    "avg_accuracy": sum(st.session_state.get('session_accuracy', [])) / len(st.session_state.get('session_accuracy', [1])),
                                    "session_duration": str(datetime.now() - st.session_state.get('login_time', datetime.now())),
                                    "user_role": st.session_state.get('user_role', 'Employee')
                                }
                            },
                            headers=headers,
                            timeout=10
                        )
                        
                        if save_response.status_code == 200:
                            st.success("✅ Session saved to history!")
                        else:
                            st.error("❌ Failed to save session")
                    except Exception as e:
                        st.error(f"❌ Save error: {str(e)}")
            
            with col2:
                # Search chat history
                if st.button("🔍 Search History", use_container_width=True, help="Search your chat history"):
                    st.session_state.show_history_search = True
                    st.rerun()
        
        # Chat history search interface
        if st.session_state.get('show_history_search', False):
            st.divider()
            st.subheader("🔍 Search Chat History")
            
            search_query = st.text_input("Search your previous conversations:", placeholder="Enter keywords to search...")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🔍 Search", use_container_width=True):
                    if search_query and len(search_query.strip()) >= 2:
                        try:
                            headers = {"Authorization": f"Bearer {st.session_state.get('access_token')}"}
                            search_response = requests.get(
                                f"{BACKEND_URL}/api/v1/chat/history/search",
                                params={"q": search_query, "limit": 10},
                                headers=headers,
                                timeout=10
                            )
                            
                            if search_response.status_code == 200:
                                results = search_response.json()
                                st.session_state.search_results = results.get("results", [])
                                st.success(f"✅ Found {len(st.session_state.search_results)} results")
                            else:
                                st.error("❌ Search failed")
                        except Exception as e:
                            st.error(f"❌ Search error: {str(e)}")
                    else:
                        st.warning("⚠️ Please enter at least 2 characters")
            
            with col2:
                if st.button("📊 Analytics", use_container_width=True):
                    try:
                        headers = {"Authorization": f"Bearer {st.session_state.get('access_token')}"}
                        analytics_response = requests.get(
                            f"{BACKEND_URL}/api/v1/chat/history/analytics",
                            params={"days": 30},
                            headers=headers,
                            timeout=10
                        )
                        
                        if analytics_response.status_code == 200:
                            st.session_state.chat_analytics = analytics_response.json().get("analytics", {})
                            st.success("✅ Analytics loaded")
                        else:
                            st.error("❌ Analytics failed")
                    except Exception as e:
                        st.error(f"❌ Analytics error: {str(e)}")
            
            with col3:
                if st.button("❌ Close Search", use_container_width=True):
                    st.session_state.show_history_search = False
                    st.session_state.search_results = []
                    st.session_state.chat_analytics = {}
                    st.rerun()
            
            # Display search results
            if st.session_state.get('search_results'):
                st.subheader("🔍 Search Results")
                for i, result in enumerate(st.session_state.search_results[:5]):
                    with st.expander(f"Result {i+1}: {result.get('content', '')[:100]}..."):
                        st.write(f"**Role:** {result.get('role', 'Unknown')}")
                        st.write(f"**Date:** {result.get('timestamp', 'Unknown')}")
                        st.write(f"**Content:** {result.get('content', '')}")
                        if result.get('accuracy_score'):
                            st.write(f"**Accuracy:** {result.get('accuracy_score', 0):.1f}%")
                        if result.get('sources'):
                            st.write(f"**Sources:** {', '.join(result.get('sources', []))}")
            
            # Display analytics
            if st.session_state.get('chat_analytics'):
                st.subheader("📊 Your Chat Analytics (Last 30 Days)")
                analytics = st.session_state.chat_analytics
                
                col1, col2, col3, col4 = st.columns(4)
                
                session_stats = analytics.get('session_stats', {})
                message_stats = analytics.get('message_stats', {})
                
                with col1:
                    st.metric("Total Sessions", session_stats.get('total_sessions', 0))
                with col2:
                    st.metric("Total Messages", message_stats.get('total_messages', 0))
                with col3:
                    avg_acc = message_stats.get('avg_accuracy', 0)
                    st.metric("Avg Accuracy", f"{avg_acc:.1f}%" if avg_acc else "N/A")
                with col4:
                    avg_msgs = session_stats.get('avg_messages_per_session', 0)
                    st.metric("Avg Msgs/Session", f"{avg_msgs:.1f}" if avg_msgs else "N/A")
                
                # Category breakdown
                if analytics.get('category_breakdown'):
                    st.subheader("📈 Query Categories")
                    for category in analytics['category_breakdown']:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**{category.get('query_category', 'Unknown').title()}**")
                        with col2:
                            st.write(f"{category.get('count', 0)} queries ({category.get('avg_accuracy', 0):.1f}% avg)")
        
        # Export chat option (enhanced)
        if st.session_state.get('messages'):
            st.divider()
            if st.button("📥 Export Current Chat", use_container_width=True):
                chat_export = []
                for msg in st.session_state.messages:
                    chat_export.append({
                        "role": msg["role"],
                        "content": msg["content"],
                        "timestamp": msg.get("timestamp", datetime.now().isoformat()),
                        "sources": msg.get("sources", []),
                        "accuracy_score": msg.get("accuracy_score", 0),
                        "confidence_level": msg.get("confidence_level", "unknown"),
                        "quality_metrics": msg.get("quality_metrics", {}),
                        "query_category": msg.get("query_category", "")
                    })
                
                st.download_button(
                    label="💾 Download Current Chat",
                    data=json.dumps(chat_export, indent=2),
                    file_name=f"current_chat_{st.session_state.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            # Export complete history
            if st.button("📚 Export Complete History", use_container_width=True):
                try:
                    headers = {"Authorization": f"Bearer {st.session_state.get('access_token')}"}
                    export_response = requests.get(
                        f"{BACKEND_URL}/api/v1/chat/history/export",
                        params={"format": "json"},
                        headers=headers,
                        timeout=30
                    )
                    
                    if export_response.status_code == 200:
                        st.download_button(
                            label="💾 Download Complete History",
                            data=export_response.content,
                            file_name=f"complete_history_{st.session_state.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json",
                            use_container_width=True
                        )
                    else:
                        st.error("❌ Export failed")
                except Exception as e:
                    st.error(f"❌ Export error: {str(e)}")

        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            clear_session()
            st.success("✅ Logged out successfully!")
            time.sleep(1)
            st.rerun()

    # Main chat interface
    st.title("🤖 FinSolve Internal Chatbot")
    
    # Session expiry warning banner
    if st.session_state.get("last_activity"):
        time_remaining = timedelta(minutes=30) - (datetime.now() - st.session_state.last_activity)
        if time_remaining.total_seconds() > 0:
            minutes_left = int(time_remaining.total_seconds() // 60)
            if minutes_left <= 5:
                st.error(f"⏰ **Session Warning:** Your session will expire in {minutes_left} minutes. Please save any important information!")
            elif minutes_left <= 10:
                st.warning(f"⏰ **Session Notice:** Your session will expire in {minutes_left} minutes.")
        else:
            st.error("⏰ **Session Expired:** Please refresh the page to login again.")
    
    # Status bar with session expiry indicator
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        st.markdown(f"**Welcome, {st.session_state.get('username', 'User')}!** Ask questions about company documents")
    with col2:
        if st.session_state.get('processing'):
            st.markdown("🔄 **Processing...**")
        else:
            st.markdown("✅ **Ready**")
    with col3:
        # Display read-only role from session state
        cached_role = st.session_state.get('user_role', 'Employee')
        st.markdown(f"**Role:** {cached_role}")
    with col4:
        # Session expiry indicator
        if st.session_state.get("last_activity"):
            time_remaining = timedelta(minutes=30) - (datetime.now() - st.session_state.last_activity)
            if time_remaining.total_seconds() > 0:
                minutes_left = int(time_remaining.total_seconds() // 60)
                if minutes_left <= 5:
                    st.markdown(f"⏰ **{minutes_left}min left**")
                else:
                    st.markdown(f"🕒 **{minutes_left}min**")
            else:
                st.markdown("⏰ **Expired**")

    # Display chat messages with enhanced formatting
    chat_container = st.container()
    with chat_container:
        for i, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Enhanced message metadata
                if message["role"] == "assistant":
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            if message.get("sources"):
                                st.caption(f"📄 Sources: {len(message['sources'])} documents")
                        
                        with col2:
                            if message.get("accuracy_score"):
                                accuracy = message["accuracy_score"]
                                if accuracy >= 90:
                                    st.caption(f"🎯 Accuracy: {accuracy:.1f}%")
                                elif accuracy >= 80:
                                    st.caption(f"✅ Accuracy: {accuracy:.1f}%")
                                elif accuracy >= 70:
                                    st.caption(f"⚠️ Accuracy: {accuracy:.1f}%")
                                else:
                                    st.caption(f"❌ Accuracy: {accuracy:.1f}%")
                        
                        with col3:
                            if message.get("confidence_level"):
                                confidence = message["confidence_level"]
                                confidence_icons = {
                                    "very_high": "🔥",
                                    "high": "✨",
                                    "medium": "⭐",
                                    "low": "⚠️",
                                    "very_low": "❌"
                                }
                                icon = confidence_icons.get(confidence, "❓")
                                st.caption(f"{icon} Confidence: {confidence.replace('_', ' ').title()}")
                        
                        with col4:
                            st.caption(f"🕒 Message #{i+1}")
                        
                        # Enhanced accuracy metrics in expander
                        if message.get("quality_metrics") or message.get("improvement_suggestions"):
                            with st.expander("📊 Accuracy Analysis", expanded=False):
                                
                                # Quality metrics
                                if message.get("quality_metrics"):
                                    st.subheader("Quality Metrics")
                                    metrics = message["quality_metrics"]
                                    
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        for metric, score in list(metrics.items())[:3]:
                                            metric_name = metric.replace("_", " ").title()
                                            st.metric(metric_name, f"{score:.1f}%")
                                    
                                    with col2:
                                        for metric, score in list(metrics.items())[3:]:
                                            metric_name = metric.replace("_", " ").title()
                                            st.metric(metric_name, f"{score:.1f}%")
                                
                                # Improvement suggestions
                                if message.get("improvement_suggestions"):
                                    st.subheader("💡 Improvement Suggestions")
                                    for suggestion in message["improvement_suggestions"]:
                                        st.write(f"• {suggestion}")
                                
                                # Query optimization info
                                if message.get("query_optimization"):
                                    opt_info = message["query_optimization"]
                                    st.subheader("🔍 Query Analysis")
                                    
                                    if opt_info.get("optimized_query") != opt_info.get("original_query"):
                                        st.write(f"**Original:** {opt_info.get('original_query', 'N/A')}")
                                        st.write(f"**Optimized:** {opt_info.get('optimized_query', 'N/A')}")
                                    
                                    if opt_info.get("expanded_terms"):
                                        st.write("**Expanded Terms:**")
                                        for term in opt_info["expanded_terms"]:
                                            st.caption(f"• {term}")
                        
                        # Detailed sources, citations, and chunks in expander
                        if message.get("sources"):
                            with st.expander("📋 View Sources, Citations & Chunk Analysis", expanded=False):
                                sources = message.get("sources", [])
                                citations = message.get("citations", [])
                                chunk_details = message.get("chunk_details", [])
                                
                                for j, source in enumerate(sources, 1):
                                    st.write(f"**{j}. {source}**")
                                    
                                    # Display citation if available
                                    if citations and j <= len(citations):
                                        st.caption(f"📖 **Citation:** {citations[j-1]}")
                                    
                                    # Display chunk details if available
                                    if chunk_details and j <= len(chunk_details):
                                        chunk_info = chunk_details[j-1]
                                        document_name = chunk_info.get("document_name", source)
                                        chunks = chunk_info.get("chunks", [])
                                        
                                        if chunks:
                                            st.write(f"🔍 **Document:** {document_name}")
                                            st.write(f"📊 **Found {len(chunks)} relevant chunks**")
                                            
                                            # Show chunk summary table
                                            chunk_summary = []
                                            for chunk in chunks[:3]:
                                                chunk_summary.append({
                                                    "Chunk ID": chunk.get("chunk_id", "N/A"),
                                                    "Type": chunk.get("type", "N/A").title(),
                                                    "Score": f"{chunk.get('score', 0):.3f}",
                                                    "Words": chunk.get("word_count", 0)
                                                })
                                            
                                            if chunk_summary:
                                                import pandas as pd
                                                df = pd.DataFrame(chunk_summary)
                                                st.dataframe(df, use_container_width=True)
                                    
                                    st.markdown("---")

    # Document viewer section (enhanced) - using read-only role from session state
    user_role = st.session_state.get('user_role', 'Employee')  # Get read-only role from session state
    
    with st.expander("📄 Available Documents (Click to View)", expanded=False):
        st.info("💡 **Tip:** Click on any document you have access to for detailed viewing")
        
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("� FinaQncial Documents")
            if check_user_access("quarterly_financial_report.md", user_role):
                if st.button("📈 Quarterly Financial Report", key="fin_report"):
                    view_document("quarterly_financial_report.md")
            else:
                st.write("�  Access Denied - Finance role required")

            st.subheader("� HR  Documents")
            if check_user_access("employee_handbook.md", user_role):
                if st.button("📋 Employee Handbook", key="hr_handbook"):
                    view_document("employee_handbook.md")
            else:
                st.write("🔒 Access Denied - HR role required")

        with col2:
            st.subheader("📈 Marketing Documents")
            if check_user_access("market_report_q4_2024.md", user_role):
                if st.button("📊 Q4 2024 Market Report", key="marketing_report"):
                    view_document("market_report_q4_2024.md")
            else:
                st.write("🔒 Access Denied - Marketing role required")

            st.subheader("⚙️ Engineering Documents")
            if check_user_access("engineering_master_doc.md", user_role):
                if st.button("🔧 Engineering Master Doc", key="eng_doc"):
                    view_document("engineering_master_doc.md")
            else:
                st.write("🔒 Access Denied - Engineering role required")

    # Enhanced chat input with processing state and error handling
    if not st.session_state.get('processing', False):
        if prompt := st.chat_input("Ask about company documents...", disabled=st.session_state.get('processing', False)):
            # Set processing state
            st.session_state.processing = True
            st.session_state.total_queries = st.session_state.get('total_queries', 0) + 1
            
            # Add user message to chat history
            st.session_state.messages.append({
                "role": "user", 
                "content": prompt,
                "sources": [],
                "citations": []
            })

            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)

            # Get bot response with enhanced error handling
            with st.chat_message("assistant"):
                # Multiple spinner messages for better UX
                spinner_messages = [
                    "🔍 Searching documents...",
                    "🧠 Processing with AI...",
                    "📊 Calculating accuracy...",
                    "✨ Generating response..."
                ]
                
                current_spinner = spinner_messages[0]
                
                with st.spinner(current_spinner):
                    try:
                        # Make API request with enhanced error handling
                        response = safe_api_call(
                            f"{BACKEND_URL}/api/v1/chat",
                            method="POST",
                            json={"query": prompt},
                            headers={"Authorization": f"Bearer {st.session_state.get('access_token')}"},
                            operation="Chat query",
                            timeout=30
                        )

                        if response and response.status_code == 200:
                            data = response.json()
                            bot_message = data.get("response", "No response received")
                            sources = data.get("sources", [])
                            accuracy = data.get("accuracy_score", 0)

                            # Display response
                            st.markdown(bot_message)
                            
                            # Enhanced accuracy display with color coding
                            accuracy = data.get("accuracy_score", 0)
                            if accuracy > 0:
                                # Add to session accuracy tracking
                                if 'session_accuracy' not in st.session_state:
                                    st.session_state.session_accuracy = []
                                st.session_state.session_accuracy.append(accuracy)
                                
                                # Color-coded accuracy display with enhanced metrics
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    if accuracy >= 90:
                                        st.success(f"🎯 **Excellent Accuracy:** {accuracy:.1f}%")
                                    elif accuracy >= 80:
                                        st.info(f"✅ **Good Accuracy:** {accuracy:.1f}%")
                                    elif accuracy >= 70:
                                        st.warning(f"⚠️ **Fair Accuracy:** {accuracy:.1f}%")
                                    else:
                                        st.error(f"❌ **Low Accuracy:** {accuracy:.1f}% - Consider rephrasing your question")
                                
                                with col2:
                                    confidence = data.get("confidence_level", "unknown")
                                    confidence_display = confidence.replace("_", " ").title()
                                    confidence_icons = {
                                        "Very High": "🔥",
                                        "High": "✨", 
                                        "Medium": "⭐",
                                        "Low": "⚠️",
                                        "Very Low": "❌"
                                    }
                                    icon = confidence_icons.get(confidence_display, "❓")
                                    st.info(f"{icon} **Confidence:** {confidence_display}")
                                
                                with col3:
                                    validation_score = data.get("validation_score", 0)
                                    if validation_score > 0:
                                        st.info(f"📊 **Validation:** {validation_score:.1f}%")
                            
                            # Enhanced source display with citations and chunk details
                            if sources:
                                st.success(f"📄 **Found {len(sources)} relevant sources**")
                                
                                # Check if citations and chunk details are available
                                citations = data.get("citations", [])
                                chunk_details = data.get("chunk_details", [])
                                
                                with st.expander("📋 View All Sources, Citations & Chunk Analysis", expanded=False):
                                    for i, source in enumerate(sources, 1):
                                        st.write(f"**{i}. {source}**")
                                        
                                        # Display citation if available
                                        if citations and i <= len(citations):
                                            st.caption(f"📖 **Citation:** {citations[i-1]}")
                                        
                                        # Display chunk details if available
                                        if chunk_details and i <= len(chunk_details):
                                            chunk_info = chunk_details[i-1]
                                            document_name = chunk_info.get("document_name", source)
                                            chunks = chunk_info.get("chunks", [])
                                            
                                            if chunks:
                                                st.write(f"🔍 **Document:** {document_name}")
                                                st.write(f"📊 **Found {len(chunks)} relevant chunks:**")
                                                
                                                # Create a table for chunk information
                                                chunk_data = []
                                                for chunk in chunks[:3]:  # Show top 3 chunks
                                                    chunk_data.append({
                                                        "Chunk ID": chunk.get("chunk_id", "N/A"),
                                                        "Type": chunk.get("type", "N/A").title(),
                                                        "Relevance Score": f"{chunk.get('relevance_score', 0):.1f}",
                                                        "Match Score": f"{chunk.get('score', 0):.3f}",
                                                        "Words": chunk.get("word_count", 0),
                                                        "Preview": chunk.get("content", "")[:100] + "..." if len(chunk.get("content", "")) > 100 else chunk.get("content", "")
                                                    })
                                                
                                                # Display chunk table
                                                if chunk_data:
                                                    import pandas as pd
                                                    df = pd.DataFrame(chunk_data)
                                                    st.dataframe(df, use_container_width=True)
                                                
                                                # Show detailed chunk content in sub-expanders
                                                for j, chunk in enumerate(chunks[:3], 1):
                                                    with st.expander(f"📝 Chunk {j}: {chunk.get('chunk_id', 'N/A')}", expanded=False):
                                                        col1, col2, col3 = st.columns(3)
                                                        with col1:
                                                            st.metric("Relevance Score", f"{chunk.get('relevance_score', 0):.1f}")
                                                        with col2:
                                                            st.metric("Match Score", f"{chunk.get('score', 0):.3f}")
                                                        with col3:
                                                            st.metric("Word Count", chunk.get('word_count', 0))
                                                        
                                                        st.write("**Content:**")
                                                        st.text_area("", chunk.get("content", ""), height=150, key=f"chunk_{i}_{j}", disabled=True)
                                                        
                                                        # Show keywords if available
                                                        keywords = chunk.get("keywords", [])
                                                        if keywords:
                                                            st.write("**Keywords Found:**")
                                                            st.write(", ".join(keywords[:10]))  # Show first 10 keywords
                                        
                                        st.markdown("---")
                                
                                st.info("💡 **Tip:** Use the 'Available Documents' section above to view full documents!")

                            # Enhanced performance metrics in a nice layout
                            if data.get("query_category") or data.get("total_chunks_analyzed"):
                                st.divider()
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    if data.get("query_category"):
                                        st.metric("🔍 Category", data["query_category"].title())
                                with col2:
                                    if data.get("total_chunks_analyzed"):
                                        st.metric("📊 Chunks Analyzed", data["total_chunks_analyzed"])
                                with col3:
                                    if accuracy > 0:
                                        st.metric("📈 Accuracy Score", f"{accuracy:.1f}%")
                                with col4:
                                    original_accuracy = data.get("original_accuracy", 0)
                                    if original_accuracy > 0 and original_accuracy != accuracy:
                                        improvement = accuracy - original_accuracy
                                        st.metric("🚀 Improvement", f"+{improvement:.1f}%")

                            # Query optimization insights
                            query_opt = data.get("query_optimization", {})
                            if query_opt.get("optimization_score", 0) > 0:
                                with st.expander("🔍 Query Analysis & Optimization", expanded=False):
                                    opt_score = query_opt.get("optimization_score", 0)
                                    st.metric("Optimization Score", f"{opt_score:.1f}%")
                                    
                                    if query_opt.get("optimized_query") != query_opt.get("original_query"):
                                        st.write("**Query Enhancement:**")
                                        st.write(f"Original: {query_opt.get('original_query', 'N/A')}")
                                        st.write(f"Optimized: {query_opt.get('optimized_query', 'N/A')}")
                                    
                                    if query_opt.get("expanded_terms"):
                                        st.write("**Expanded Terms:**")
                                        for term in query_opt["expanded_terms"]:
                                            st.caption(f"• {term}")
                                    
                                    if query_opt.get("suggested_alternatives"):
                                        st.write("**Alternative Queries:**")
                                        for alt in query_opt["suggested_alternatives"]:
                                            st.caption(f"• {alt}")

                            # Improvement suggestions
                            improvement_suggestions = data.get("improvement_suggestions", [])
                            if improvement_suggestions:
                                with st.expander("💡 Suggestions for Better Results", expanded=False):
                                    st.write("**To improve accuracy, try:**")
                                    for suggestion in improvement_suggestions:
                                        st.write(f"• {suggestion}")

                            # Add bot response to chat history with enhanced metadata
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": bot_message,
                                "sources": sources,
                                "citations": data.get("citations", []),
                                "chunk_details": data.get("chunk_details", []),
                                "accuracy_score": accuracy,
                                "original_accuracy": data.get("original_accuracy", 0),
                                "validation_score": data.get("validation_score", 0),
                                "confidence_level": data.get("confidence_level", "unknown"),
                                "quality_metrics": data.get("quality_metrics", {}),
                                "improvement_suggestions": improvement_suggestions,
                                "query_optimization": query_opt,
                                "timestamp": datetime.now().isoformat(),
                                "query_category": data.get("query_category", ""),
                                "chunks_analyzed": data.get("total_chunks_analyzed", 0)
                            })
                            
                        elif response and response.status_code == 401:
                            # Handle authentication errors with token refresh
                            if refresh_access_token():
                                # Token refreshed successfully, retry the request
                                retry_response = safe_api_call(
                                    f"{BACKEND_URL}/api/v1/chat",
                                    method="POST",
                                    json={"query": prompt},
                                    headers={"Authorization": f"Bearer {st.session_state.get('access_token')}"},
                                    operation="Chat query (retry)",
                                    show_spinner=False,
                                    timeout=30
                                )
                                
                                if retry_response and retry_response.status_code == 200:
                                    # Process the successful response (same as above)
                                    data = retry_response.json()
                                    bot_message = data.get("response", "No response received")
                                    sources = data.get("sources", [])
                                    accuracy = data.get("accuracy_score", 0)
                                    st.markdown(bot_message)
                                    # Continue with normal processing...
                                else:
                                    handle_session_error()
                            else:
                                handle_session_error()
                                
                        elif response and response.status_code == 403:
                            st.error("🚫 Access denied. You don't have permission for this request.")
                            st.info("💡 Contact your administrator to request access to this information")
                            
                        elif response:
                            # Handle other HTTP errors
                            try:
                                error_data = response.json()
                                error_detail = error_data.get("detail", "Unknown error")
                                st.error(f"❌ Error {response.status_code}: {error_detail}")
                                
                                # Show suggestions if available
                                if isinstance(error_data, dict) and "error" in error_data:
                                    error_info = error_data["error"]
                                    suggestions = error_info.get("suggestions", [])
                                    if suggestions:
                                        with st.expander("💡 Suggestions", expanded=False):
                                            for suggestion in suggestions:
                                                st.write(f"• {suggestion}")
                                                
                            except json.JSONDecodeError:
                                st.error(f"❌ Server error (Status: {response.status_code})")
                        else:
                            # Response is None (handled by safe_api_call)
                            st.error("❌ Failed to get response from server")
                            st.info("🔄 Please try again or check your connection")

                    except Exception as e:
                        # Handle unexpected errors
                        frontend_error_handler.handle_request_error(e, "chat query")
                    
                    finally:
                        # Reset processing state
                        st.session_state.processing = False
                        st.rerun()
    else:
        st.info("🔄 Processing your previous message... Please wait.")
        
    # Auto-scroll to bottom (JavaScript injection)
    st.markdown("""
    <script>
    var element = window.parent.document.querySelector('.main');
    element.scrollTop = element.scrollHeight;
    </script>
    """, unsafe_allow_html=True)


# --- MAIN APP LOGIC ---
def main():
    """Enhanced main application with comprehensive session management"""
    
    # Configure Streamlit page
    st.set_page_config(
        page_title="FinSolve Internal Chatbot",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Custom CSS for better UI
    st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    .stButton > button {
        width: 100%;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
    }
    .assistant-message {
        background-color: #f3e5f5;
    }
    .accuracy-excellent {
        color: #4caf50;
        font-weight: bold;
    }
    .accuracy-good {
        color: #2196f3;
        font-weight: bold;
    }
    .accuracy-fair {
        color: #ff9800;
        font-weight: bold;
    }
    .accuracy-poor {
        color: #f44336;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Check authentication and route to appropriate interface
    if not st.session_state.get("authenticated", False):
        login()
    else:
        main_chat_interface()


if __name__ == "__main__":
    main()
