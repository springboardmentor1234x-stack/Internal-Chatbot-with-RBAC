import streamlit as st
from utils.api_client import APIClient

def render_login(api_client: APIClient):
    """Render login interface"""
    st.title("🔐 Company Internal Chatbot")
    st.markdown("---")
    
    with st.form("login_form"):
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if not username or not password:
                st.error("Please enter both username and password")
            else:
                try:
                    with st.spinner("Authenticating..."):
                        result = api_client.login(username, password)
                    
                    st.session_state.logged_in = True
                    st.session_state.user_info = {
                        "username": result["username"],
                        "role": result["role"],
                        "department": result["department"]
                    }
                    st.success(f"Welcome, {result['username']}!")
                    st.rerun()
                
                except Exception as e:
                    st.error(f"Login failed: {str(e)}")
    
    # Sample credentials info
    with st.expander("📋 Sample Login Credentials"):
        st.markdown("""
        **Admin/C-Level:**
        - Username: `admin` | Password: `admin123`
        
        **Finance:**
        - Username: `finance_user` | Password: `finance123`
        
        **Marketing:**
        - Username: `marketing_user` | Password: `marketing123`
        
        **HR:**
        - Username: `hr_user` | Password: `hr123`
        
        **Engineering:**
        - Username: `eng_user` | Password: `eng123`
        
        **Employee:**
        - Username: `employee` | Password: `employee123`
        """)