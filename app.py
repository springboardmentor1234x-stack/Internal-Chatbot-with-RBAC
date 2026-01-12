import streamlit as st
import requests

# --- 1. Credentials & Role Database ---
# Unique IDs and passwords are kept here in the frontend
USER_DB = {
    "tony_eng": {"password": "eng123", "role": "Engineering_Lead"},
    "sam_fin": {"password": "fin123", "role": "Finance_Manager"},
    "natasha_hr": {"password": "hr123", "role": "HR_Manager"},
    "bruce_mkt": {"password": "mkt123", "role": "Marketing_Manager"},
    "peter_intern": {"password": "intern123", "role": "Intern"},
    "shashank_ceo": {"password": "ceo123", "role": "C-Level"}
}

st.set_page_config(page_title="FinSolve Secure Assistant", layout="wide")

# Initialize Session States
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- 2. Login UI ---
if not st.session_state.logged_in:
    st.title("🔐 FinSolve Secure Login")
    with st.container(border=True):
        username = st.text_input("Username (ID)")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", use_container_width=True):
            user_data = USER_DB.get(username)
            if user_data and user_data["password"] == password:
                # Clear session for fresh login isolation
                st.session_state.messages = []
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = user_data["role"]
                st.rerun()
            else:
                st.error("Invalid ID or Password")

# --- 3. Main Chat UI ---
else:
    with st.sidebar:
        st.title(f"👤 {st.session_state.role}")
        st.write(f"ID: {st.session_state.username}")
        st.divider()
        
        if st.button("➕ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        if st.button("📜 View History", use_container_width=True):
            st.info("Past Session Summary:\n" + "\n".join(st.session_state.chat_history[-5:]))

        if st.button("🚪 Logout", use_container_width=True, type="primary"):
            st.session_state.logged_in = False
            st.rerun()

    st.title("🛡️ FinSolve Secure Chat")
    
    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "sources" in msg and msg["sources"]:
                st.caption(f"📚 **Sources:** {', '.join(msg['sources'])}")

    # Chat Input with Processing Spinner
    if prompt := st.chat_input("Ask a question about company data..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # Spinning processing indicator
            with st.spinner("🤖 Analyzing secure data..."):
                try:
                    # Pass only the ROLE to the backend
                    response = requests.get(
                        "http://127.0.0.1:8000/ask", 
                        params={"role": st.session_state.role, "query": prompt},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.markdown(data["answer"])
                        if data["sources"]:
                            st.caption(f"📚 **Sources:** {', '.join(data['sources'])}")
                        
                        st.session_state.messages.append({
                            "role": "assistant", "content": data["answer"], "sources": data["sources"]
                        })
                    elif response.status_code == 403:
                        st.error(f"🚫 403 Forbidden: {response.json()['detail']}")
                except Exception as e:
                    st.error(f"❌ Connection Error: {str(e)}")