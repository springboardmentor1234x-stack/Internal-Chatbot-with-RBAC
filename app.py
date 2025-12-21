import streamlit as st
import requests
import json

# --- Configuration ---
API_BASE_URL = "http://localhost:8000" # Change to your deployment URL

# --- Initial Setup ---
st.set_page_config(
    page_title="RBAC Internal Chatbot", 
    page_icon="🤖", 
    layout="centered"
)
st.title("AI Company Internal Chatbot 🤖")

# Initialize session state for login status and chat history
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "token" not in st.session_state:
    st.session_state.token = None
if "role" not in st.session_state:
    st.session_state.role = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Helper Functions ---

def login(username, password):
    """Sends login request to FastAPI backend."""
    login_url = f"{API_BASE_URL}/token"
    data = {"username": username, "password": password}
    
    try:
        response = requests.post(login_url, json=data)
        if response.status_code == 200:
            token_data = response.json()
            st.session_state.logged_in = True
            st.session_state.token = token_data["access_token"]
            st.session_state.role = token_data["role"]
            st.session_state.messages = [
                {"role": "assistant", "content": f"Welcome, {username}! You are logged in as **{st.session_state.role}**. How can I help you today?"}
            ]
            st.success(f"Login successful! Role: **{st.session_state.role}**")
            st.rerun()
        else:
            st.error("Login failed. Check username and password.")
            st.session_state.token = None
            st.session_state.role = None
    except requests.exceptions.ConnectionError:
        st.error(f"Cannot connect to the backend API at {API_BASE_URL}. Ensure FastAPI is running.")

def logout():
    """Resets session state to log the user out."""
    st.session_state.logged_in = False
    st.session_state.token = None
    st.session_state.role = None
    st.session_state.messages = []
    st.rerun()

def send_chat_query(query: str):
    """Sends the user query to the FastAPI /chat endpoint."""
    chat_url = f"{API_BASE_URL}/chat"
    headers = {
        "Authorization": f"Bearer {st.session_state.token}",
        "Content-Type": "application/json"
    }
    data = {"query": query}
    
    try:
        response = requests.post(chat_url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            st.error("Session expired or unauthorized. Please log in again.")
            logout()
            return {"answer": "Error: Unauthorized access.", "sources": {}}
        else:
            error_detail = response.json().get("detail", "Unknown server error.")
            return {"answer": f"Error from backend: {error_detail}", "sources": {}}
            
    except requests.exceptions.ConnectionError:
        return {"answer": "Error: Could not connect to the backend.", "sources": {}}

# --- Layout ---

if not st.session_state.logged_in:
    # --- Login Interface ---
    st.header("Secure Login")
    with st.form("login_form"):
        username = st.text_input("Username (e.g., finance_user, c_level)", key="username_input")
        password = st.text_input("Password (password123 for all demo accounts)", type="password", key="password_input")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            login(username, password)
    
    st.info(
        "**Demo Accounts:**\n"
        "- **Finance:** `finance_user` (sees financial documents)\n"
        "- **Marketing:** `marketing_user` (sees marketing documents)\n"
        "- **HR:** `hr_user` (sees HR and employee handbook)\n"
        "- **C-Level:** `c_level` (sees all documents)\n"
        "*(Password is `password123` for all)*"
    )

else:
    # --- Chat Interface ---
    
    st.sidebar.title("User Info")
    st.sidebar.write(f"**Role:** {st.session_state.role}")
    st.sidebar.button("Logout", on_click=logout)
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle new user input
    if prompt := st.chat_input("Ask me a question about company documents..."):
        # 1. Display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Get assistant response from backend
        with st.spinner("Processing request... (Retrieval filtered by your role)"):
            response_data = send_chat_query(prompt)
            
            assistant_answer = response_data.get("answer", "I could not generate a response.")
            sources = response_data.get("sources", {}).get("retrieved_sources", [])
            
            # Format the final output
            final_content = assistant_answer
            if sources:
                source_list = "\n".join([f"- {s}" for s in sources])
                final_content += f"\n\n---\n\n**Sources Used (Restricted by Role):**\n{source_list}"

            # 3. Display assistant message and save to history
            with st.chat_message("assistant"):
                st.markdown(final_content)
                
            st.session_state.messages.append({"role": "assistant", "content": final_content})

# Command to run the frontend: streamlit run app.py