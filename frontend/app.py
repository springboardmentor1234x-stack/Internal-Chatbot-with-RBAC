import streamlit as st
import requests
import jwt
from pathlib import Path

# -------------------------------
# CONFIG
# -------------------------------
BACKEND_URL = "http://127.0.0.1:8000"
SOURCE_DIR = Path("../Fintech-data")

st.set_page_config(
    page_title="Internal RBAC Chatbot",
    page_icon="💬",
    layout="wide",
)

# -------------------------------
# SESSION STATE INIT
# -------------------------------
if "auth_status" not in st.session_state:
    st.session_state.auth_status = "unauthenticated"

if "token" not in st.session_state:
    st.session_state.token = None

if "login_error" not in st.session_state:
    st.session_state.login_error = None

if "login_username" not in st.session_state:
    st.session_state.login_username = ""

if "login_password" not in st.session_state:
    st.session_state.login_password = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------------
# HELPERS
# -------------------------------
def decode_token(token):
    try:
        return jwt.decode(token, options={"verify_signature": False})
    except Exception:
        return None

# -------------------------------
# SIDEBAR
# -------------------------------
with st.sidebar:
    st.markdown("## 🔐 User Panel")

    if st.session_state.auth_status == "authenticated":
        payload = decode_token(st.session_state.token)

        if payload:
            st.write("**Username:**", payload.get("sub"))
            st.write("**Role:**", payload.get("role"))

        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.session_state.auth_status = "unauthenticated"
            st.rerun()
    else:
        st.info("🔓 Not logged in")

# -------------------------------
# MAIN UI
# -------------------------------
st.title("Company Internal Chatbot")

# ---------- LOGIN ----------
if st.session_state.auth_status == "unauthenticated":
    st.subheader("Login")

    if st.session_state.login_error:
        st.error(st.session_state.login_error)

    with st.form("login_form"):
        st.text_input("Username", key="login_username")
        st.text_input("Password", type="password", key="login_password")
        submit = st.form_submit_button("Login")

    if submit:
        st.session_state.auth_status = "logging_in"
        st.session_state.login_error = None
        st.rerun()

# ---------- LOGGING IN ----------
elif st.session_state.auth_status == "logging_in":
    with st.spinner("Logging in..."):
        try:
            response = requests.post(
                f"{BACKEND_URL}/login",
                json={
                    "username": st.session_state.login_username,
                    "password": st.session_state.login_password,
                },
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                st.session_state.token = data["access_token"]
                st.session_state.auth_status = "authenticated"
                st.rerun()

            elif response.status_code == 401:
                st.session_state.auth_status = "unauthenticated"
                st.session_state.login_error = "Invalid username or password"
                st.rerun()

            else:
                st.session_state.auth_status = "unauthenticated"
                st.session_state.login_error = "Login failed"
                st.rerun()

        except requests.exceptions.RequestException:
            st.session_state.auth_status = "unauthenticated"
            st.session_state.login_error = "Backend not reachable"
            st.rerun()

# ---------- CHAT ----------
elif st.session_state.auth_status == "authenticated":
    st.subheader("💬 Chat")

    # Show chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            if msg["role"] == "assistant" and msg.get("sources"):
                with st.expander("📄 Sources"):
                    for i, src in enumerate(msg["sources"]):
                        matches = list(SOURCE_DIR.rglob(src))
                        if matches:
                            file_path = matches[0]
                            with open(file_path, "rb") as f:
                                st.download_button(
                                    label=f"⬇️ Download {src}",
                                    data=f,
                                    file_name=src,
                                    key=f"download_{src}_{i}"
                                )

    user_input = st.chat_input("Ask a question...")

    if user_input:
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/query",
                        headers={
                            "Authorization": f"Bearer {st.session_state.token}"
                        },
                        json={"query": user_input},
                        timeout=120,
                    )

                    if response.status_code == 200:
                        data = response.json()
                        answer = data["answer"]
                        sources = data.get("sources", [])

                    elif response.status_code == 401:
                        st.session_state.clear()
                        st.session_state.auth_status = "expired"
                        st.rerun()

                    elif response.status_code == 403:
                        answer = "⛔ You are not authorized to access this information."
                        sources = []

                    else:
                        answer = f"⚠️ Backend error ({response.status_code})"
                        sources = []

                except requests.exceptions.RequestException as e:
                    answer = f"⚠️ Request failed: {e}"
                    sources = []

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": sources,
        })
        st.rerun()

# ---------- SESSION EXPIRED ----------
elif st.session_state.auth_status == "expired":
    st.error("🔒 Session expired. Please log in again.")
