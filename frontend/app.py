"""
Main Streamlit Application
Entry point for the RAG Chatbot frontend
"""

import streamlit as st
from utils.api_client import APIClient
from utils.session_manager import SessionManager
from components.login import render_login
from components.chat import render_chat
from components.sidebar import render_sidebar
from components.admin import render_admin_panel
from config.settings import APP_TITLE, APP_ICON, PAGE_LAYOUT, API_BASE_URL

# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=PAGE_LAYOUT,
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': """
        ## Company Internal RAG Chatbot
        
        A secure, role-based document retrieval system with AI assistance.
        
        **Features:**
        - 🔐 JWT Authentication
        - 🛡️ Role-Based Access Control
        - 🔍 Vector Similarity Search
        - 🤖 AI-Powered Responses
        - 📊 Source Citations
        - 📝 Complete Audit Logging
        
        © 2026 Company Internal Systems
        """
    }
)

# Custom CSS for modern UI
st.markdown("""
    <style>
        /* Main app styling */
        .main {
            padding: 1rem;
        }
        
        /* Chat message styling */
        .stChatMessage {
            background-color: #0f172a;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        
        /* Button styling */
        .stButton button {
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        /* Input styling */
        .stTextInput input {
            border-radius: 8px;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: #0f172a;
            border-radius: 8px;
            font-weight: 600;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            padding: 1rem;
        }
        
        /* Success/Error/Warning boxes */
        .stAlert {
            border-radius: 8px;
            padding: 1rem;
        }
        
        /* Metrics styling */
        .stMetric {
            background-color: #0f172a;
            padding: 1rem;
            border-radius: 8px;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
SessionManager.initialize()

# Initialize API client
if "api_client" not in st.session_state:
    st.session_state.api_client = APIClient(base_url=API_BASE_URL)

def main():
    """Main application logic"""
    
    api_client = st.session_state.api_client
    
    # Check if logged in
    if not st.session_state.logged_in:
        # Show login page
        render_login(api_client)
    
    else:
        # Check if admin
        is_admin = SessionManager.is_admin()
        
        # Render sidebar
        render_sidebar(api_client, is_admin)
        
        # Main content area
        if is_admin and st.session_state.get("admin_view"):
            render_admin_panel(api_client)
        else:
            render_chat(api_client)
        
        # Auto-refresh token if expiring soon
        if api_client.is_token_expiring_soon():
            if api_client.refresh_access_token():
                st.toast("✅ Session refreshed automatically", icon="🔄")

if __name__ == "__main__":
    main()
