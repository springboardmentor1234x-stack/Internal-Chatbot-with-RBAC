"""
Streamlit Frontend for Secure RAG Chatbot
Module 6: Beautiful UI with RBAC and Advanced RAG
"""

import streamlit as st
import requests
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="Secure RAG Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend API configuration
API_BASE_URL = "http://localhost:8000"

def apply_custom_css():
    """Apply custom CSS based on theme mode"""
    # Color scheme based on mode
    if st.session_state.dark_mode:
        bg_color = "#1a1a1a"
        text_color = "#e0e0e0"
        card_bg = "#2d2d2d"
        border_color = "#404040"
        user_msg_bg = "#1e3a5f"
        user_msg_border = "#2196f3"
        assistant_msg_bg = "#2d2d2d"
        assistant_msg_border = "#505050"
        sidebar_bg = "#252525"
        input_bg = "#2d2d2d"
        input_border = "#404040"
    else:
        bg_color = "#ffffff"
        text_color = "#1a1a1a"
        card_bg = "#ffffff"
        border_color = "#e0e0e0"
        user_msg_bg = "#e3f2fd"
        user_msg_border = "#2196f3"
        assistant_msg_bg = "#f5f5f5"
        assistant_msg_border = "#9e9e9e"
        sidebar_bg = "#f0f2f6"
        input_bg = "#ffffff"
        input_border = "#bdbdbd"
    
    st.markdown(f"""
    <style>
        /* HIDE STREAMLIT HEADER COMPLETELY */
        header[data-testid="stHeader"] {{
            display: none !important;
            visibility: hidden !important;
            height: 0px !important;
            position: absolute !important;
        }}
        
        /* Force color scheme everywhere */
        .stApp {{
            background-color: {bg_color} !important;
        }}
        
        /* Main container */
        .main {{
            padding: 2rem;
            background-color: {bg_color} !important;
        }}
        
        /* All view containers */
        [data-testid="stAppViewContainer"] {{
            background-color: {bg_color} !important;
        }}
        
        /* Block container */
        .block-container {{
            background-color: {bg_color} !important;
            padding-top: 1rem !important;
        }}
        
        /* Make all text visible */
        .stMarkdown, p, span, div {{
            color: {text_color} !important;
        }}
        
        /* Chat messages */
        .user-message {{
            background-color: {user_msg_bg};
            padding: 1.2rem;
            border-radius: 15px;
            margin: 0.8rem 0;
            margin-left: 15%;
            border: 2px solid {user_msg_border};
            color: {text_color} !important;
            font-size: 1.05rem;
        }}
        
        .user-message strong {{
            color: {"#90caf9" if st.session_state.dark_mode else "#1565c0"} !important;
            font-size: 1.1rem;
        }}
        
        .assistant-message {{
            background-color: {assistant_msg_bg};
            padding: 1.2rem;
            border-radius: 15px;
            margin: 0.8rem 0;
            margin-right: 15%;
            border: 2px solid {assistant_msg_border};
            color: {text_color} !important;
            font-size: 1.05rem;
            line-height: 1.6;
        }}
        
        .assistant-message strong {{
            color: {"#b0b0b0" if st.session_state.dark_mode else "#424242"} !important;
            font-size: 1.1rem;
        }}
        
        /* Confidence badges */
        .confidence-high {{
            background-color: #4caf50;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 12px;
            font-weight: bold;
            font-size: 1.1rem;
            display: inline-block;
        }}
        
        .confidence-medium {{
            background-color: #ff9800;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 12px;
            font-weight: bold;
            font-size: 1.1rem;
            display: inline-block;
        }}
        
        .confidence-low {{
            background-color: #f44336;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 12px;
            font-weight: bold;
            font-size: 1.1rem;
            display: inline-block;
        }}
        
        /* Department badges */
        .dept-badge {{
            display: inline-block;
            padding: 0.5rem 1rem;
            border-radius: 10px;
            margin: 0.3rem 0.2rem;
            font-size: 1rem;
            font-weight: 700;
            border: 2px solid;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        
        .dept-finance {{
            background-color: #2196f3;
            color: white !important;
            border-color: #1976d2;
        }}
        
        .dept-marketing {{
            background-color: #e91e63;
            color: white !important;
            border-color: #c2185b;
        }}
        
        .dept-hr {{
            background-color: #9c27b0;
            color: white !important;
            border-color: #7b1fa2;
        }}
        
        .dept-engineering {{
            background-color: #4caf50;
            color: white !important;
            border-color: #388e3c;
        }}
        
        .dept-general {{
            background-color: #ff9800;
            color: white !important;
            border-color: #f57c00;
        }}
        
        /* Source cards */
        .source-card {{
            background-color: {card_bg};
            border-left: 5px solid #2196f3;
            padding: 1.2rem;
            margin: 0.8rem 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,{"0.3" if st.session_state.dark_mode else "0.1"});
            color: {text_color} !important;
        }}
        
        .source-card strong {{
            color: {"#90caf9" if st.session_state.dark_mode else "#1565c0"} !important;
            font-size: 1.05rem;
        }}
        
        /* Expander content */
        .streamlit-expanderContent {{
            background-color: {card_bg};
            padding: 1rem;
            color: {text_color} !important;
        }}
        
        /* Metrics */
        [data-testid="stMetricValue"] {{
            color: {text_color} !important;
            font-size: 1.5rem !important;
            font-weight: 600 !important;
        }}
        
        [data-testid="stMetricLabel"] {{
            color: {text_color} !important;
            font-size: 1rem !important;
            font-weight: 500 !important;
        }}
        
        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: {sidebar_bg};
        }}
        
        [data-testid="stSidebar"] .stMarkdown {{
            color: {text_color} !important;
        }}
        
        [data-testid="stSidebar"] h3 {{
            color: {text_color} !important;
            font-size: 1.3rem !important;
            font-weight: 700 !important;
        }}
        
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {{
            color: {text_color} !important;
            font-size: 1rem !important;
        }}
        
        [data-testid="stSidebar"] strong {{
            color: {text_color} !important;
            font-weight: 700 !important;
        }}
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {{
            color: {text_color} !important;
            font-weight: 700 !important;
        }}
        
        /* Title in main area */
        .main h1 {{
            color: {text_color} !important;
            font-size: 2.5rem !important;
            font-weight: 700 !important;
            margin-bottom: 1.5rem !important;
        }}
        
        /* Buttons - make them more visible */
        .stButton > button {{
            background-color: #2196f3 !important;
            color: white !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            border: 2px solid #1976d2 !important;
            padding: 0.6rem 1.2rem !important;
            border-radius: 8px !important;
        }}
        
        .stButton > button:hover {{
            background-color: #1976d2 !important;
            border-color: #0d47a1 !important;
        }}
        
        /* Form submit button - make it stand out */
        .stForm button[kind="primary"] {{
            background-color: #4caf50 !important;
            color: white !important;
            font-weight: 700 !important;
            font-size: 1.1rem !important;
            border: 2px solid #388e3c !important;
        }}
        
        .stForm button[kind="primary"]:hover {{
            background-color: #388e3c !important;
        }}
        
        /* Text inputs */
        .stTextInput > div > div > input {{
            color: {text_color} !important;
            font-size: 1rem !important;
            background-color: {input_bg} !important;
            border: 2px solid {input_border} !important;
        }}
        
        .stTextInput > label {{
            color: {text_color} !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
        }}
        
        /* Selectbox (Dropdown) - Fix for light mode */
        .stSelectbox > label {{
            color: {text_color} !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
        }}
        
        .stSelectbox > div > div {{
            background-color: {input_bg} !important;
            border: 2px solid {input_border} !important;
        }}
        
        .stSelectbox [data-baseweb="select"] {{
            background-color: {input_bg} !important;
        }}
        
        .stSelectbox [data-baseweb="select"] > div {{
            background-color: {input_bg} !important;
            color: {text_color} !important;
            border: 2px solid {input_border} !important;
        }}
        
        .stSelectbox option {{
            background-color: {input_bg} !important;
            color: {text_color} !important;
        }}
        
        /* Dropdown menu items */
        [data-baseweb="popover"] {{
            background-color: {input_bg} !important;
        }}
        
        [role="option"] {{
            background-color: {input_bg} !important;
            color: {text_color} !important;
        }}
        
        [role="option"]:hover {{
            background-color: {("#404040" if st.session_state.dark_mode else "#e0e0e0")} !important;
        }}
        
        /* Slider */
        .stSlider > label {{
            color: {text_color} !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
        }}
        
        /* Toggle */
        .stCheckbox > label {{
            color: {text_color} !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
        }}
        
        /* Login container */
        .login-container {{
            max-width: 400px;
            margin: 5rem auto;
            padding: 2rem;
            background-color: {card_bg};
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, {"0.4" if st.session_state.dark_mode else "0.15"});
            border: 2px solid {border_color};
        }}
        
        /* Theme toggle button */
        .theme-toggle {{
            position: fixed;
            top: 1rem;
            right: 1rem;
            z-index: 999999;
            background-color: {("#2196f3" if st.session_state.dark_mode else "#1976d2")} !important;
            color: white !important;
            border: none !important;
            padding: 0.5rem 1rem !important;
            border-radius: 20px !important;
            cursor: pointer;
            font-size: 1.2rem;
        }}
    </style>
    """, unsafe_allow_html=True)

# Initialize session state FIRST (before applying CSS that uses it)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'access_token' not in st.session_state:
    st.session_state.access_token = None
if 'user_info' not in st.session_state:
    st.session_state.user_info = {}
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'use_advanced_rag' not in st.session_state:
    st.session_state.use_advanced_rag = True
if 'top_k' not in st.session_state:
    st.session_state.top_k = 5
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True  # Dark mode as default
if 'current_conversation_id' not in st.session_state:
    st.session_state.current_conversation_id = None
if 'conversations' not in st.session_state:
    st.session_state.conversations = []

# Apply CSS AFTER session state is initialized
apply_custom_css()


def login(username: str, password: str):
    """Login user and get JWT token"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.logged_in = True
            st.session_state.access_token = data['access_token']
            st.session_state.user_info = {
                'username': data['username'],
                'role': data['role'],
                'user_id': data['user_id']
            }
            return True, "Login successful!"
        else:
            return False, "Invalid username or password"
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def register_user(username: str, password: str, email: str, full_name: str, role: str):
    """Register a new user"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/register",
            json={
                "username": username,
                "password": password,
                "email": email,
                "full_name": full_name,
                "role": role
            }
        )
        
        if response.status_code in [200, 201]:  # Accept both 200 OK and 201 Created
            return True, "Registration successful! Please login."
        elif response.status_code == 409:
            return False, "Username or email already exists"
        else:
            error_detail = response.json().get('detail', 'Registration failed')
            return False, f"Error: {error_detail}"
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def logout():
    """Logout user and clear session"""
    st.session_state.logged_in = False
    st.session_state.access_token = None
    st.session_state.user_info = {}
    st.session_state.chat_history = []
    st.session_state.current_conversation_id = None
    st.session_state.conversations = []


def send_query(query: str):
    """Send query to RAG backend"""
    if not st.session_state.access_token:
        return None, "Not logged in"
    
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    endpoint = "/query/advanced" if st.session_state.use_advanced_rag else "/query"
    
    try:
        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json={"query": query, "top_k": st.session_state.top_k},
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json(), None
        elif response.status_code == 401:
            logout()
            return None, "Session expired. Please login again."
        else:
            return None, f"Error: {response.status_code}"
    except Exception as e:
        return None, f"Connection error: {str(e)}"


# ==================== Conversation Management Functions ====================

def load_conversations():
    """Load all conversations for the current user"""
    if not st.session_state.access_token:
        return []
    
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    try:
        response = requests.get(f"{API_BASE_URL}/conversations", headers=headers)
        if response.status_code == 200:
            st.session_state.conversations = response.json()
            return st.session_state.conversations
    except:
        pass
    return []


def create_new_conversation():
    """Create a new conversation"""
    if not st.session_state.access_token:
        return None
    
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    try:
        response = requests.post(
            f"{API_BASE_URL}/conversations",
            json={"title": "New Chat"},
            headers=headers
        )
        if response.status_code == 201:
            conv = response.json()
            st.session_state.current_conversation_id = conv['id']
            st.session_state.chat_history = []
            load_conversations()  # Refresh list
            return conv
    except:
        pass
    return None


def load_conversation_messages(conversation_id: int):
    """Load messages for a specific conversation"""
    if not st.session_state.access_token:
        return []
    
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    try:
        response = requests.get(
            f"{API_BASE_URL}/conversations/{conversation_id}",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            # Convert to chat history format
            messages = []
            for msg in data.get('messages', []):
                message = {
                    'role': msg['role'],
                    'content': msg['content'],
                    'timestamp': msg['timestamp']
                }
                if msg.get('sources'):
                    message['sources'] = msg['sources']
                if msg.get('confidence'):
                    message['confidence'] = msg['confidence']
                messages.append(message)
            return messages
    except:
        pass
    return []


def save_message_to_conversation(conversation_id: int, role: str, content: str, sources=None, confidence=None):
    """Save a message to the conversation"""
    if not st.session_state.access_token:
        return False
    
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    message_data = {
        "role": role,
        "content": content,
        "sources": sources,
        "confidence": confidence
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/conversations/{conversation_id}/messages",
            json=message_data,
            headers=headers
        )
        if response.status_code == 200:
            load_conversations()  # Refresh to update titles
            return True
    except:
        pass
    return False


def delete_conversation(conversation_id: int):
    """Delete a conversation"""
    if not st.session_state.access_token:
        return False
    
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    try:
        response = requests.delete(
            f"{API_BASE_URL}/conversations/{conversation_id}",
            headers=headers
        )
        if response.status_code == 200:
            if st.session_state.current_conversation_id == conversation_id:
                st.session_state.current_conversation_id = None
                st.session_state.chat_history = []
            load_conversations()
            return True
    except:
        pass
    return False


def switch_conversation(conversation_id: int):
    """Switch to a different conversation"""
    st.session_state.current_conversation_id = conversation_id
    st.session_state.chat_history = load_conversation_messages(conversation_id)


def display_login_page():
    """Display login interface"""
    # Initialize show_register in session state
    if 'show_register' not in st.session_state:
        st.session_state.show_register = False
    
    # Theme toggle button at the top
    col_theme1, col_theme2, col_theme3 = st.columns([4, 1, 1])
    with col_theme2:
        theme_icon = "🌙" if not st.session_state.dark_mode else "☀️"
        theme_text = "Dark" if not st.session_state.dark_mode else "Light"
        if st.button(f"{theme_icon} {theme_text} Mode", use_container_width=True):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
    
    st.markdown(f"<h1 style='text-align: center; color: {'#e0e0e0' if st.session_state.dark_mode else '#000000'}; font-size: 3rem; font-weight: 700;'>🤖 Secure RAG Chatbot</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center; color: {'#b0b0b0' if st.session_state.dark_mode else '#424242'}; font-size: 1.5rem; font-weight: 500;'>Role-Based AI Assistant</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Toggle between Login and Register
        if not st.session_state.show_register:
            # LOGIN FORM
            st.markdown("### 🔐 Login")
            
            username = st.text_input("Username", placeholder="Enter your username", key="login_username")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🚀 Login", use_container_width=True):
                    if username and password:
                        with st.spinner("Authenticating..."):
                            success, message = login(username, password)
                        
                        if success:
                            st.success(message)
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.warning("Please enter both username and password")
            
            with col_b:
                if st.button("📝 Register", use_container_width=True):
                    st.session_state.show_register = True
                    st.rerun()
            
            # Help text
            st.markdown("---")
            st.info("👋 **New user?** Click the **Register** button above to create your account!")
        
        else:
            # REGISTRATION FORM
            st.markdown("### 📝 Register New Account")
            
            reg_username = st.text_input("Username", placeholder="Choose a username", key="reg_username")
            reg_email = st.text_input("Email", placeholder="your.email@example.com", key="reg_email")
            reg_fullname = st.text_input("Full Name", placeholder="John Doe", key="reg_fullname")
            reg_password = st.text_input("Password", type="password", placeholder="Choose a strong password", key="reg_password")
            reg_password_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter password", key="reg_password_confirm")
            
            # Role selection
            role_options = {
                "Finance Employee": "finance_employee",
                "Marketing Employee": "marketing_employee",
                "HR Employee": "hr_employee",
                "Engineering Employee": "engineering_employee",
                "General Employee": "general_employee"
            }
            
            role_display = st.selectbox(
                "Select Your Department Role",
                options=list(role_options.keys()),
                help="Choose the department you belong to. This determines which documents you can access."
            )
            role = role_options[role_display]
            
            # Department access info
            dept_access = {
                "finance_employee": ["Finance", "General"],
                "marketing_employee": ["Marketing", "General"],
                "hr_employee": ["HR", "General"],
                "engineering_employee": ["Engineering", "General"],
                "general_employee": ["General"]
            }
            
            st.info(f"📂 **You will have access to:** {', '.join(dept_access[role])}")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("✅ Create Account", use_container_width=True, type="primary"):
                    # Validation
                    if not all([reg_username, reg_email, reg_fullname, reg_password, reg_password_confirm]):
                        st.error("Please fill in all fields")
                    elif reg_password != reg_password_confirm:
                        st.error("Passwords do not match")
                    elif len(reg_password) < 8:
                        st.error("Password must be at least 8 characters long")
                    elif "@" not in reg_email or "." not in reg_email:
                        st.error("Please enter a valid email address")
                    else:
                        with st.spinner("Creating your account..."):
                            success, message = register_user(
                                username=reg_username,
                                password=reg_password,
                                email=reg_email,
                                full_name=reg_fullname,
                                role=role
                            )
                        
                        if success:
                            st.success(message)
                            st.balloons()
                            time.sleep(2)
                            st.session_state.show_register = False
                            st.rerun()
                        else:
                            st.error(message)
            
            with col_b:
                if st.button("🔙 Back to Login", use_container_width=True):
                    st.session_state.show_register = False
                    st.rerun()
            
            # Password requirements
            st.markdown("---")
            with st.expander("🔒 Password Requirements"):
                st.markdown("""
                **For a strong password:**
                - At least 8 characters long
                - Mix of uppercase and lowercase letters (recommended)
                - Include numbers (recommended)
                - Include special characters like !@#$% (recommended)
                """)



def get_dept_badge(department: str) -> str:
    """Get HTML badge for department"""
    dept_classes = {
        'Finance': 'dept-finance',
        'Marketing': 'dept-marketing',
        'HR': 'dept-hr',
        'Engineering': 'dept-engineering',
        'General': 'dept-general'
    }
    
    dept_class = dept_classes.get(department, 'dept-general')
    return f'<span class="dept-badge {dept_class}">{department}</span>'


def get_confidence_badge(confidence: float) -> str:
    """Get HTML badge for confidence level"""
    if confidence >= 70:
        return f'<span class="confidence-high">🟢 {confidence:.1f}% HIGH</span>'
    elif confidence >= 50:
        return f'<span class="confidence-medium">🟡 {confidence:.1f}% MEDIUM</span>'
    else:
        return f'<span class="confidence-low">🔴 {confidence:.1f}% LOW</span>'


def get_suggested_questions(role: str):
    """Get suggested questions based on user role"""
    suggestions = {
        'hr_employee': [
            "What is Krishna Verma's performance rating?",
            "Which employees have leave balances of 15 or more?",
            "What are the steps for applying for maternity leave?",
            "What is the process for requesting annual leave?",
            "What are the company's core values?"
        ],
        'finance_employee': [
            "What was the total revenue for 2024?",
            "What were the main operating expenses?",
            "What is the company's financial strategy?",
            "What is the gross margin percentage?",
            "What are the leave policies?"
        ],
        'marketing_employee': [
            "What were the key marketing initiatives in Q4 2024?",
            "What was the customer acquisition growth?",
            "What marketing campaigns were most successful?",
            "What are the target customer demographics?",
            "What is the marketing budget allocation?"
        ],
        'engineering_employee': [
            "What is FinSolve's system architecture?",
            "What technology stack does FinSolve use?",
            "What are the engineering best practices?",
            "What is the development workflow?",
            "What are the work hours and policies?"
        ],
        'employee': [
            "What are the company's core values?",
            "What is the onboarding process for new employees?",
            "What benefits do employees receive?",
            "What are the leave policies?",
            "What is FinSolve's mission and vision?"
        ],
        'admin': [
            "What was the revenue growth in 2024?",
            "What is Vihaan Garg's leave balance?",
            "What were the marketing campaign results?",
            "What is our system architecture?",
            "What are the company values?"
        ]
    }
    
    # Return suggestions for the role, or default to employee suggestions
    return suggestions.get(role, suggestions['employee'])


def display_chat_interface():
    """Display main chat interface"""
    # Load conversations on first run
    if not st.session_state.conversations:
        load_conversations()
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user_info['username']}")
        st.markdown(f"**Role:** `{st.session_state.user_info['role']}`")
        
        # Get user stats
        try:
            headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
            stats_response = requests.get(f"{API_BASE_URL}/stats", headers=headers)
            if stats_response.status_code == 200:
                stats = stats_response.json()
                
                st.markdown("---")
                st.markdown("### 📊 Your Stats")
                st.metric("Total Queries", stats.get('total_queries', 0))
                
                st.markdown("### 🗂️ Accessible Departments")
                departments = stats.get('accessible_departments', [])
                if departments:
                    dept_html = "<div style='margin-top: 0.5rem;'>"
                    for dept in departments:
                        dept_html += get_dept_badge(dept) + " "
                    dept_html += "</div>"
                    st.markdown(dept_html, unsafe_allow_html=True)
                else:
                    st.info("No departments accessible")
        except:
            pass
        
        st.markdown("---")
        st.markdown("### 💬 Chat History")
        
        # New Chat button
        if st.button("➕ New Chat", use_container_width=True, type="primary"):
            conv = create_new_conversation()
            if conv:
                st.rerun()
        
        # Display conversation list
        if st.session_state.conversations:
            for conv in st.session_state.conversations[:10]:  # Show last 10
                conv_id = conv['id']
                conv_title = conv['title'][:30] + "..." if len(conv['title']) > 30 else conv['title']
                msg_count = conv.get('message_count', 0)
                
                # Highlight current conversation
                is_current = st.session_state.current_conversation_id == conv_id
                
                col_conv, col_del = st.columns([5, 1])
                with col_conv:
                    button_label = f"{'📌 ' if is_current else '💬 '}{conv_title}"
                    if st.button(button_label, key=f"conv_{conv_id}", use_container_width=True):
                        switch_conversation(conv_id)
                        st.rerun()
                with col_del:
                    if st.button("🗑️", key=f"del_{conv_id}", help="Delete conversation"):
                        delete_conversation(conv_id)
                        st.rerun()
        else:
            st.info("No chat history yet. Start a new chat!")
        
        st.markdown("---")
        st.markdown("### ⚙️ Settings")
        
        # Theme toggle
        theme_icon = "🌙" if not st.session_state.dark_mode else "☀️"
        theme_text = "Dark Mode" if not st.session_state.dark_mode else "Light Mode"
        if st.button(f"{theme_icon} {theme_text}", use_container_width=True):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
        
        st.session_state.use_advanced_rag = st.toggle(
            "Advanced RAG Mode",
            value=st.session_state.use_advanced_rag,
            help="Use LLM-powered advanced RAG with confidence scoring"
        )
        
        st.session_state.top_k = st.slider(
            "Top-K Results",
            min_value=1,
            max_value=10,
            value=st.session_state.top_k,
            help="Number of documents to retrieve"
        )
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()
    
    # Main chat area
    st.title("💬 Chat with Your Data")
    
    # Show suggested questions if chat is empty
    if len(st.session_state.chat_history) == 0:
        st.markdown("### 💡 Suggested Questions")
        st.markdown("*Click on a question to ask it*")
        st.markdown("")
        
        user_role = st.session_state.user_info.get('role', 'employee')
        suggestions = get_suggested_questions(user_role)
        
        # Display suggestions in a grid
        cols = st.columns(2)
        for idx, suggestion in enumerate(suggestions):
            with cols[idx % 2]:
                if st.button(f"💬 {suggestion}", key=f"suggestion_{idx}", use_container_width=True):
                    # Create conversation if none exists
                    if not st.session_state.current_conversation_id:
                        conv = create_new_conversation()
                        if not conv:
                            st.error("Failed to create conversation")
                            st.stop()
                    
                    # Add user message to chat
                    st.session_state.chat_history.append({
                        'role': 'user',
                        'content': suggestion,
                        'timestamp': datetime.now()
                    })
                    
                    # Save user message
                    save_message_to_conversation(
                        st.session_state.current_conversation_id,
                        'user', suggestion
                    )
                    
                    # Get response from backend
                    with st.spinner("🤔 Thinking..."):
                        result, error = send_query(suggestion)
                    
                    if result:
                        # Add assistant message to chat
                        assistant_message = {
                            'role': 'assistant',
                            'content': result.get('answer', 'No response'),
                            'sources': result.get('sources', []),
                            'timestamp': datetime.now()
                        }
                        
                        # Add confidence if advanced mode
                        confidence_data = None
                        if st.session_state.use_advanced_rag and 'confidence' in result:
                            assistant_message['confidence'] = result['confidence']
                            confidence_data = result['confidence']
                        
                        st.session_state.chat_history.append(assistant_message)
                        
                        # Save assistant message
                        save_message_to_conversation(
                            st.session_state.current_conversation_id,
                            'assistant',
                            result.get('answer', 'No response'),
                            sources=result.get('sources', []),
                            confidence=confidence_data
                        )
                        
                        st.rerun()
                    else:
                        st.error(f"Error: {error}")
        
        st.markdown("---")
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f"""
                <div class="user-message">
                    <strong>👤 You:</strong><br><br>
                    <span style="color: #000000; font-size: 1.05rem;">{message['content']}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="assistant-message">
                    <strong>🤖 Assistant:</strong><br><br>
                    <span style="color: #000000; font-size: 1.05rem; white-space: pre-wrap;">{message['content']}</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Display sources if available
                if 'sources' in message and message['sources']:
                    with st.expander(f"📄 **Sources ({len(message['sources'])})**", expanded=False):
                        for i, source in enumerate(message['sources'][:5], 1):
                            st.markdown(f"""
                            <div class="source-card">
                                <strong style="font-size: 1.1rem;">📄 Source {i}: {source.get('document_name', 'Unknown')}</strong><br><br>
                                <span style="color: #424242; font-size: 0.95rem;">
                                    <strong>Department:</strong> {get_dept_badge(source.get('department', 'Unknown'))}<br>
                                    <strong>Relevance Score:</strong> <span style="color: #1565c0; font-weight: 600;">{source.get('relevance_score', 0):.4f}</span>
                                </span>
                            </div>
                            """, unsafe_allow_html=True)
                
                # Display confidence if available
                if 'confidence' in message and message['confidence']:
                    conf = message['confidence']
                    with st.expander("📊 **Confidence Metrics**", expanded=False):
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown(get_confidence_badge(conf.get('overall_confidence', 0)), unsafe_allow_html=True)
                        st.markdown("<br><br>", unsafe_allow_html=True)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("🎯 Retrieval Quality", f"{conf.get('retrieval_quality', 0):.1f}%")
                            st.metric("📝 Citation Coverage", f"{conf.get('citation_coverage', 0):.1f}%")
                        with col2:
                            st.metric("✅ Answer Completeness", f"{conf.get('answer_completeness', 0):.1f}%")
                            st.metric("🏆 Confidence Level", conf.get('confidence_level', 'N/A').upper())
    
    # Query input
    st.markdown("---")
    
    with st.form(key='query_form', clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            query = st.text_input(
                "Ask a question",
                placeholder="What would you like to know?",
                label_visibility="collapsed"
            )
        
        with col2:
            submit = st.form_submit_button("🚀 Send", use_container_width=True)
        
        if submit and query:
            # Create conversation if none exists
            if not st.session_state.current_conversation_id:
                conv = create_new_conversation()
                if not conv:
                    st.error("Failed to create conversation")
                    st.stop()
            
            # Add user message to chat
            user_msg = {
                'role': 'user',
                'content': query,
                'timestamp': datetime.now()
            }
            st.session_state.chat_history.append(user_msg)
            
            # Save user message to database
            save_message_to_conversation(
                st.session_state.current_conversation_id,
                'user', query
            )
            
            # Get response from backend
            with st.spinner("🤔 Thinking..."):
                result, error = send_query(query)
            
            if result:
                # Add assistant message to chat
                assistant_message = {
                    'role': 'assistant',
                    'content': result.get('answer', 'No response'),
                    'sources': result.get('sources', []),
                    'timestamp': datetime.now()
                }
                
                # Add confidence if advanced mode
                confidence_data = None
                if st.session_state.use_advanced_rag and 'confidence' in result:
                    assistant_message['confidence'] = result['confidence']
                    confidence_data = result['confidence']
                
                st.session_state.chat_history.append(assistant_message)
                
                # Save assistant message to database
                save_message_to_conversation(
                    st.session_state.current_conversation_id,
                    'assistant',
                    result.get('answer', 'No response'),
                    sources=result.get('sources', []),
                    confidence=confidence_data
                )
                
                st.rerun()
            else:
                st.error(f"Error: {error}")


def main():
    """Main application"""
    if not st.session_state.logged_in:
        display_login_page()
    else:
        display_chat_interface()


if __name__ == "__main__":
    main()
