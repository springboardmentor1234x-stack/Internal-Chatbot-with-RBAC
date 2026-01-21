import streamlit as st
import requests

USER_DB = {
    "tony_eng": {"password": "eng123", "role": "engineering", "level": "Lead"},
    "sam_fin": {"password": "fin123", "role": "finance", "level": "Manager"},
    "natasha_hr": {"password": "hr123", "role": "hr", "level": "Manager"},
    "bruce_mkt": {"password": "mkt123", "role": "marketing", "level": "Manager"},
    "peter_intern": {"password": "intern123", "role": "intern", "level": "Junior"},
    "shashank_ceo": {"password": "ceo123", "role": "admin", "level": "CEO"}
}

st.set_page_config(page_title="FinSolve Secure Assistant", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.logged_in:
    st.title("🔐 FinSolve Secure Login")
    with st.container(border=True):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True):
            user = USER_DB.get(username)
            if user and user["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = user["role"]
                st.session_state.level = user["level"]
                st.session_state.messages = []
                st.rerun()
            else:
                st.error("Invalid credentials")
else:
    with st.sidebar:
        st.title(f"👤 {st.session_state.role.upper()}")
        st.write(f"Level: {st.session_state.level}")
        
        if st.session_state.role in ["admin", "ceo"]:
            target_dept = st.selectbox(
                "Select Department to Query", 
                ["finance", "marketing", "hr", "engineering", "intern"]
            )
        else:
            st.info(f"Access Locked: **{st.session_state.role}**")
            target_dept = st.session_state.role
            
        st.divider()
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        if st.button("Logout", use_container_width=True, type="primary"):
            st.session_state.clear()
            st.rerun()

    st.title("🛡️ FinSolve Secure Chat")
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about company data..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("🤖 Processing..."):
                try:
                    response = requests.get(
                        "http://127.0.0.1:8000/ask", 
                        params={"role": st.session_state.role, "dept": target_dept, "query": prompt},
                        timeout=30
                    )
                    if response.status_code == 200:
                        ans = response.json()["answer"]
                        st.markdown(ans)
                        st.session_state.messages.append({"role": "assistant", "content": ans})
                    else:
                        err = response.json().get('detail', 'Access Denied')
                        st.error(f"Error: {err}")
                except Exception as e:
                    st.error(f"Connection Failed: {e}")