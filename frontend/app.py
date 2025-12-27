import streamlit as st
import requests

# The URL where your FastAPI backend is running
BACKEND_URL = "http://127.0.0.1:8000"

def login():
    # --- UPDATED TITLE FOR LOGIN SCREEN ---
    st.title("🤖 Company Internal Chatbot with RBAC") 

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            try:
                response = requests.post(
                    f"{BACKEND_URL}/login", 
                    json={"username": username, "password": password}
                )
                
                if response.status_code == 200:
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = username 
                    st.rerun()
                else:
                    st.error("Invalid Username or Password (Backend Rejected)")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to the Backend. Is FastAPI running?")

# --- MAIN APP LOGIC ---

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

    # --- UPDATED TITLE FOR MAIN INTERFACE ---
    st.title("🤖 Company Internal Chatbot with RBAC")

    # Chat input
    if prompt := st.chat_input("Ask a question about company documents..."):
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Searching internal documents..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={"query": prompt},
                    headers={"X-User-Role": "C-Level"} 
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