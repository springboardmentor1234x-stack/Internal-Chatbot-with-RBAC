import streamlit as st
import requests
from datetime import datetime

# The URL where your FastAPI backend is running
BACKEND_URL = "http://127.0.0.1:8000"

def login():
    """Login interface for the chatbot."""
    st.title("🤖 Company Internal Chatbot with RBAC") 
    st.markdown("### Please login to access company documents")
    
    # Show available test accounts
    with st.expander("📋 Available Test Accounts"):
        st.markdown("""
        **Test Accounts (all use password: `password123`):**
        - `admin` - Admin role (full access)
        - `clevel_user` - C-Level role (all documents)
        - `finance_user` - Finance role (finance + general docs)
        - `marketing_user` - Marketing role (marketing + general docs)
        - `hr_user` - HR role (HR + general docs)
        - `engineering_user` - Engineering role (engineering + general docs)
        - `employee_user` - Employee role (general docs only)
        - `intern_user` - Intern role (general docs only)
        """)

    with st.form("login_form"):
        username = st.text_input("Username", placeholder="e.g., finance_user")
        password = st.text_input("Password", type="password", placeholder="password123")
        submit = st.form_submit_button("Login")

        if submit:
            if not username or not password:
                st.error("Please enter both username and password")
                return
                
            try:
                # Use OAuth2 form data format for FastAPI
                response = requests.post(
                    f"{BACKEND_URL}/auth/login", 
                    data={"username": username, "password": password},
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Store authentication data in session
                    st.session_state["authenticated"] = True
                    st.session_state["access_token"] = data["access_token"]
                    st.session_state["user"] = data["user"]
                    st.session_state["username"] = data["user"]["username"]
                    st.session_state["role"] = data["user"]["role"]
                    st.success(f"Welcome, {data['user']['username']}! Role: {data['user']['role']}")
                    st.rerun()
                else:
                    error_detail = response.json().get("detail", "Login failed")
                    st.error(f"Login failed: {error_detail}")
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to the backend. Please ensure FastAPI is running on http://127.0.0.1:8000")
            except Exception as e:
                st.error(f"Login error: {str(e)}")

def chat_interface():
    """Main chat interface for authenticated users."""
    # Sidebar with user info
    with st.sidebar:
        st.title("👤 User Profile")
        st.write(f"**Username:** {st.session_state.get('username', 'Unknown')}")
        st.write(f"**Role:** {st.session_state.get('role', 'Unknown')}")
        
        if st.button("🚪 Logout", use_container_width=True):
            # Clear all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📚 Role Permissions")
        role = st.session_state.get('role', 'Unknown')
        if role == "C-Level":
            st.success("✅ Access to ALL documents")
        elif role == "Finance":
            st.info("📊 Finance + General documents")
        elif role == "Marketing":
            st.info("📈 Marketing + General documents")
        elif role == "HR":
            st.info("👥 HR + General documents")
        elif role == "Engineering":
            st.info("⚙️ Engineering + General documents")
        elif role == "Employee":
            st.info("📄 General documents only")
        elif role == "Intern":
            st.info("📄 General documents only")
        else:
            st.warning("❓ Unknown role permissions")

    # Main chat interface
    st.title("🤖 Company Internal Chatbot")
    st.markdown(f"**Logged in as:** {st.session_state.get('username')} ({st.session_state.get('role')})")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                st.caption(f"📚 Sources: {', '.join(message['sources'])}")

    # Chat input
    if prompt := st.chat_input("Ask a question about company documents..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("🔍 Searching internal documents..."):
                try:
                    # Make request with proper authentication
                    headers = {
                        "Authorization": f"Bearer {st.session_state['access_token']}",
                        "Content-Type": "application/json"
                    }
                    
                    response = requests.post(
                        f"{BACKEND_URL}/api/v1/chat",
                        json={"query": prompt},
                        headers=headers
                    )

                    if response.status_code == 200:
                        data = response.json()
                        content = data.get("content", "No response received")
                        sources = data.get("sources", [])
                        
                        # Display response
                        st.markdown(content)
                        if sources:
                            st.caption(f"📚 Sources: {', '.join(sources)}")
                        
                        # Add assistant message to chat history
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": content,
                            "sources": sources
                        })
                        
                    elif response.status_code == 401:
                        st.error("🔒 Authentication expired. Please login again.")
                        # Clear session and force re-login
                        for key in list(st.session_state.keys()):
                            del st.session_state[key]
                        st.rerun()
                    elif response.status_code == 403:
                        st.error("🚫 Access denied. Your role doesn't have permission for this request.")
                    else:
                        error_detail = response.json().get("detail", "Unknown error")
                        st.error(f"❌ Error {response.status_code}: {error_detail}")
                        
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to the backend. Please ensure FastAPI is running.")
                except Exception as e:
                    st.error(f"❌ Request failed: {str(e)}")

# --- MAIN APP LOGIC ---
def main():
    """Main application logic."""
    # Initialize session state
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    # Route to appropriate interface
    if not st.session_state["authenticated"]:
        login()
    else:
        chat_interface()

if __name__ == "__main__":
    main()