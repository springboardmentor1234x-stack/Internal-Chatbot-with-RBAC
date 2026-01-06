"""
Login component for Streamlit frontend
"""

import streamlit as st
from utils.api_client import APIClient
from utils.session_manager import SessionManager
import time

def render_login(api_client: APIClient):
    """Render modern login interface"""
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo and title
        st.markdown("""
            <div style='text-align: center; padding: 2rem 0;'>
                <h1>🤖</h1>
                <h2>Company Internal RAG Chatbot</h2>
                <p style='color: #666; margin-top: 1rem;'>
                    Secure, role-based document retrieval with AI assistance
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Check backend health
        with st.spinner("Checking server connection..."):
            health = api_client.health_check()
        
        if health.get("status") != "healthy":
            st.error("⚠️ Backend server is not available. Please contact IT support.")
            st.stop()
        
        st.success("✅ Connected to server")
        
        # Login form
        with st.form("login_form", clear_on_submit=False):
            st.subheader("🔐 Login")
            
            username = st.text_input(
                "Username",
                placeholder="Enter your username",
                help="Your company username"
            )
            
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                help="Your company password"
            )
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                submit = st.form_submit_button(
                    "🚀 Login",
                    use_container_width=True,
                    type="primary"
                )
            
            with col_btn2:
                help_btn = st.form_submit_button(
                    "❓ Help",
                    use_container_width=True
                )
        
        # Handle login
        if submit:
            if not username or not password:
                st.error("⚠️ Please enter both username and password")
            else:
                # Show loading animation
                with st.spinner("🔄 Authenticating..."):
                    try:
                        result = api_client.login(username, password)
                        
                        if result["success"]:
                            # Get full user info
                            user_info = api_client.get_user_info()
                            
                            # Set session state
                            SessionManager.login(user_info)
                            
                            # Show success message
                            st.success(f"✅ Welcome, {user_info['username']}!")
                            time.sleep(0.5)
                            
                            # Rerun to show main app
                            st.rerun()
                    
                    except Exception as e:
                        st.error(f"❌ Login failed: {str(e)}")
        
        # Help section
        if help_btn:
            st.info("""
                **Need help logging in?**
                
                - Contact your IT administrator for credentials
                - Ensure you're using your company username
                - If you forgot your password, contact HR
            """)
        
        # Sample credentials (only for demo/testing)
        with st.expander("📋 Test Credentials (Demo Only)"):
            st.markdown("""
                **Admin (Full Access):**
                - Username: `admin_user`
                - Password: `admin123`
                
                **Finance Analyst:**
                - Username: `finance_user`
                - Password: `finance123`
                
                **HR Manager:**
                - Username: `hr_user`
                - Password: `hr123`
                
                **Engineering Lead:**
                - Username: `engineering_user`
                - Password: `eng123`
                
                **Marketing Manager:**
                - Username: `marketing_user`
                - Password: `marketing123`
                
                **Manager (Multi-department):**
                - Username: `manager_user`
                - Password: `manager123`
                
                **Intern (No Access):**
                - Username: `intern_user`
                - Password: `intern123`
            """)
        
        # Footer
        st.markdown("---")
        st.markdown("""
            <div style='text-align: center; color: #666; font-size: 0.85rem;'>
                <p>🔒 Secure Authentication | 🛡️ Role-Based Access Control | 📊 Audit Logging</p>
                <p style='margin-top: 0.5rem;'>© 2024 Company Internal Systems</p>
            </div>
        """, unsafe_allow_html=True)