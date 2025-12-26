import streamlit as st
import requests

# The URL where your FastAPI backend is running
BACKEND_URL = "http://127.0.0.1:8000/api/v1"

def login():
    st.title("🔐 Internal Knowledge Chatbot")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            try:
                # We authenticate against the FastAPI backend
                response = requests.post(
                    f"{BACKEND_URL}/login", 
                    json={"username": username, "password": password}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state["authenticated"] = True
                    # Store the username or role for the API calls
                    st.session_state["username"] = username 
                    st.rerun()
                else:
                    st.error("Invalid Username or Password (Backend Rejected)")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to the Backend. Is FastAPI running?")

# --- MAIN APP LOGIC ---

# Initialize authentication state
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login()
else:
    # --- AUTHORIZED CHAT INTERFACE ---
    st.sidebar.title(f"Welcome, {st.session_state.get('username', 'User')}")
    
    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = None
        st.rerun()

    st.title("🤖 Internal Knowledge Chatbot")

    # Chat input
    if prompt := st.chat_input("Ask a question about company documents..."):
        with st.chat_message("user"):
            st.markdown(prompt)

        # Call the FastAPI Backend Chat Endpoint
        with st.spinner("Searching internal documents..."):
            try:
                # Note: In a real app, you'd send an Auth token here
                response = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={"query": prompt},
                    headers={"X-User-Role": "C-Level"} # Example: manually passing role for testing
                )

                if response.status_code == 200:
                    data = response.json()
                    with st.chat_message("assistant"):
                        st.markdown(data["answer"])
                        if data.get("sources"):
                            st.caption(f"Sources: {', '.join(data['sources'])}")
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Connection failed: {e}")