import streamlit as st
import requests
import os
import time
from datetime import datetime, timedelta

# The URL where your FastAPI backend is running
BACKEND_URL = "http://127.0.0.1:8000"

# Session state initialization
def initialize_session_state():
    """Initialize all session state variables with default values"""
    default_states = {
        "authenticated": False,
        "username": "",
        "access_token": "",
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
    """Check if session has expired (30 minutes of inactivity)"""
    if not st.session_state.get("last_activity"):
        return False
    
    # Check for session expiry (30 minutes of inactivity)
    expiry_time = st.session_state.last_activity + timedelta(minutes=30)
    is_expired = datetime.now() > expiry_time
    
    # Also check if authentication token is still valid
    if st.session_state.get("authenticated") and st.session_state.get("access_token"):
        try:
            headers = {"Authorization": f"Bearer {st.session_state.get('access_token')}"}
            response = requests.get(f"{BACKEND_URL}/api/v1/user/profile", headers=headers, timeout=5)
            if response.status_code == 401:
                # Token is invalid/expired
                return True
        except:
            # Network error, assume session is still valid for now
            pass
    
    return is_expired

def clear_session():
    """Clear all session state data"""
    keys_to_keep = ["theme_preference"]  # Keep user preferences
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
            del st.session_state[key]
    initialize_session_state()


def view_document(filename):
    """Display document content in a modal-like expander"""
    file_path = os.path.join("data", "raw", filename)

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
        except Exception as e:
            st.error(f"Error reading {filename}: {str(e)}")
    else:
        st.error(f"Document {filename} not found at {file_path}")


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
    """Enhanced login interface with session management"""
    st.title("🔐 FinSolve Internal Chatbot - Login")
    st.markdown("**Role-Based Access Control (RBAC) System**")

    # Check for session expiry message
    if st.session_state.get("session_expired"):
        st.warning("⏰ Your session has expired. Please login again.")
        st.session_state.session_expired = False

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
            if not username or not password:
                st.error("Please enter both username and password")
                return

            # Show login spinner
            with st.spinner("🔐 Authenticating..."):
                try:
                    # Updated to match the FastAPI endpoint
                    response = requests.post(
                        f"{BACKEND_URL}/auth/login",
                        data={"username": username, "password": password},
                        timeout=10
                    )

                    if response.status_code == 200:
                        data = response.json()
                        
                        # Set session state with role fetched from backend
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.access_token = data["access_token"]
                        st.session_state.login_time = datetime.now()
                        st.session_state.last_activity = datetime.now()
                        st.session_state.chat_session_id = f"{username}_{int(time.time())}"
                        st.session_state.error_count = 0
                        
                        # Fetch and store user role as read-only immediately after login
                        try:
                            headers = {"Authorization": f"Bearer {data['access_token']}"}
                            profile_response = requests.get(
                                f"{BACKEND_URL}/api/v1/user/profile", headers=headers, timeout=5
                            )
                            if profile_response.status_code == 200:
                                profile = profile_response.json()
                                # Store role as read-only in session state
                                st.session_state.user_role = profile.get('role', 'Employee')
                            else:
                                st.session_state.user_role = 'Employee'  # Default fallback
                        except:
                            st.session_state.user_role = 'Employee'  # Default fallback
                        
                        st.success("✅ Login successful!")
                        time.sleep(1)  # Brief pause for user feedback
                        st.rerun()
                    else:
                        error_detail = response.json().get("detail", "Login failed")
                        st.error(f"❌ {error_detail}")
                        st.session_state.error_count = st.session_state.get("error_count", 0) + 1
                        
                except requests.exceptions.Timeout:
                    st.error("⏰ Login request timed out. Please try again.")
                except requests.exceptions.ConnectionError:
                    st.error(
                        "🔌 Cannot connect to backend. Make sure FastAPI is running on http://127.0.0.1:8000"
                    )
                except Exception as e:
                    st.error(f"❌ Login error: {str(e)}")
                    st.session_state.error_count = st.session_state.get("error_count", 0) + 1

    # Show connection status
    with st.expander("🔧 System Status", expanded=False):
        try:
            health_response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            if health_response.status_code == 200:
                st.success("✅ Backend server is running")
            else:
                st.warning("⚠️ Backend server responding with errors")
        except:
            st.error("❌ Backend server is not accessible")
            st.info("💡 Make sure to run: `python run.py`")


def main_chat_interface():
    """Enhanced main chat interface with session expiry and read-only role management"""
    
    # Check session expiry first
    if is_session_expired():
        st.warning("⏰ Your session has expired due to inactivity. Please login again.")
        st.session_state.session_expired = True
        clear_session()
        time.sleep(2)  # Brief pause to show the message
        st.rerun()
    
    # Update activity timestamp on every interaction
    update_activity()
    
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
        
        # Chat controls
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
        
        # Export chat option
        if st.session_state.get('messages'):
            if st.button("📥 Export Chat", use_container_width=True):
                chat_export = []
                for msg in st.session_state.messages:
                    chat_export.append({
                        "role": msg["role"],
                        "content": msg["content"],
                        "timestamp": datetime.now().isoformat(),
                        "sources": msg.get("sources", []),
                        "accuracy": msg.get("accuracy", 0)
                    })
                
                st.download_button(
                    label="💾 Download Chat History",
                    data=str(chat_export),
                    file_name=f"chat_history_{st.session_state.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

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
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if message.get("sources"):
                            st.caption(f"📄 Sources: {len(message['sources'])} documents")
                    
                    with col2:
                        if message.get("accuracy"):
                            accuracy = message["accuracy"]
                            if accuracy >= 90:
                                st.caption(f"🎯 Accuracy: {accuracy:.1f}%")
                            elif accuracy >= 80:
                                st.caption(f"✅ Accuracy: {accuracy:.1f}%")
                            elif accuracy >= 70:
                                st.caption(f"⚠️ Accuracy: {accuracy:.1f}%")
                            else:
                                st.caption(f"❌ Accuracy: {accuracy:.1f}%")
                    
                    with col3:
                        st.caption(f"🕒 Message #{i+1}")
                    
                    # Detailed sources and citations in expander
                    if message.get("sources"):
                        with st.expander("📋 View Sources & Citations", expanded=False):
                            sources = message.get("sources", [])
                            citations = message.get("citations", [])
                            
                            for j, source in enumerate(sources, 1):
                                st.write(f"**{j}.** {source}")
                                
                                # Display citation if available
                                if citations and j <= len(citations):
                                    st.caption(f"📖 **Citation:** {citations[j-1]}")
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

    # Enhanced chat input with processing state
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

            # Get bot response with enhanced spinner and error handling
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
                        headers = {
                            "Authorization": f"Bearer {st.session_state.get('access_token')}"
                        }
                        
                        # Update spinner message
                        st.session_state.current_spinner = spinner_messages[1]
                        
                        response = requests.post(
                            f"{BACKEND_URL}/api/v1/chat",
                            json={"query": prompt},
                            headers=headers,
                            timeout=30
                        )

                        if response.status_code == 200:
                            data = response.json()
                            bot_message = data.get("response", "No response received")
                            sources = data.get("sources", [])
                            accuracy = data.get("accuracy_score", 0)

                            # Display response
                            st.markdown(bot_message)
                            
                            # Enhanced accuracy display with color coding
                            if accuracy > 0:
                                # Add to session accuracy tracking
                                if 'session_accuracy' not in st.session_state:
                                    st.session_state.session_accuracy = []
                                st.session_state.session_accuracy.append(accuracy)
                                
                                # Color-coded accuracy display
                                if accuracy >= 90:
                                    st.success(f"🎯 **Excellent Accuracy:** {accuracy:.1f}%")
                                elif accuracy >= 80:
                                    st.info(f"✅ **Good Accuracy:** {accuracy:.1f}%")
                                elif accuracy >= 70:
                                    st.warning(f"⚠️ **Fair Accuracy:** {accuracy:.1f}%")
                                else:
                                    st.error(f"❌ **Low Accuracy:** {accuracy:.1f}% - Consider rephrasing your question")
                            
                            # Enhanced source display with citations
                            if sources:
                                st.success(f"📄 **Found {len(sources)} relevant sources**")
                                
                                # Check if citations are available
                                citations = data.get("citations", [])
                                
                                with st.expander("📋 View All Sources & Citations", expanded=False):
                                    for i, source in enumerate(sources, 1):
                                        st.write(f"**{i}.** {source}")
                                        
                                        # Display citation if available
                                        if citations and i <= len(citations):
                                            st.caption(f"📖 Citation: {citations[i-1]}")
                                            st.markdown("---")
                                
                                st.info("💡 **Tip:** Use the 'Available Documents' section above to view full documents!")

                            # Performance metrics in a nice layout
                            if data.get("query_category") or data.get("total_chunks_analyzed"):
                                st.divider()
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    if data.get("query_category"):
                                        st.metric("🔍 Category", data["query_category"].title())
                                with col2:
                                    if data.get("total_chunks_analyzed"):
                                        st.metric("📊 Chunks Analyzed", data["total_chunks_analyzed"])
                                with col3:
                                    if accuracy > 0:
                                        st.metric("📈 Accuracy Score", f"{accuracy:.1f}%")

                            # Add bot response to chat history with citations
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": bot_message,
                                "sources": sources,
                                "citations": data.get("citations", []),
                                "accuracy": accuracy,
                                "timestamp": datetime.now().isoformat(),
                                "query_category": data.get("query_category", ""),
                                "chunks_analyzed": data.get("total_chunks_analyzed", 0)
                            })
                            
                        elif response.status_code == 401:
                            st.error("🔐 Session expired. Please login again.")
                            st.session_state.session_expired = True
                            clear_session()
                            time.sleep(2)
                            st.rerun()
                        elif response.status_code == 403:
                            st.error("🚫 Access denied. You don't have permission for this request.")
                        else:
                            error_detail = response.json().get("detail", "Unknown error")
                            st.error(f"❌ Error {response.status_code}: {error_detail}")

                    except requests.exceptions.Timeout:
                        st.error("⏰ Request timed out. The server might be busy. Please try again.")
                    except requests.exceptions.ConnectionError:
                        st.error("🔌 Cannot connect to backend. Make sure FastAPI is running.")
                        st.info("💡 **Troubleshooting:** Run `python run.py` in your terminal")
                    except Exception as e:
                        st.error(f"❌ Request failed: {str(e)}")
                        st.info("🔄 Please try refreshing the page or logging in again")
                    
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
