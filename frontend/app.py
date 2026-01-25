import streamlit as st
import requests
import jwt
import pandas as pd
from pathlib import Path
from datetime import datetime

BACKEND_URL = "http://127.0.0.1:8000"

# Correct project path
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
SOURCE_DIR = PROJECT_ROOT / "Fintech-data"

SESSION_DURATION_MINUTES = 10

st.set_page_config(page_title="Internal RBAC Chatbot", page_icon="💬", layout="wide")

# ---------------- SESSION STATE INIT ----------------
defaults = {
    "auth_status": "unauthenticated",
    "token": None,
    "login_time": None,
    "login_error": None,
    "login_username": "",
    "login_password": "",
    "messages": [],
    "last_sources": [],
    "audit_logs": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------- HELPERS ----------------
def decode_token(token):
    try:
        return jwt.decode(token, options={"verify_signature": False})
    except:
        return None

def remaining_session_time():
    if not st.session_state.login_time:
        return 0
    elapsed = (datetime.utcnow() - st.session_state.login_time).total_seconds()
    return max(0, int(SESSION_DURATION_MINUTES * 60 - elapsed))

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## 🔐 User Panel")

    if st.session_state.auth_status == "authenticated":
        payload = decode_token(st.session_state.token)
        role = payload.get("role", "").lower() if payload else ""

        if payload:
            st.write("**Username:**", payload.get("sub"))
            st.write("**Role:**", payload.get("role"))

        remaining = remaining_session_time()
        st.progress(remaining / (SESSION_DURATION_MINUTES * 60))
        st.caption(f"⏳ Session expires in {remaining//60}:{remaining%60:02d}")

        if remaining <= 0:
            st.session_state.clear()
            st.session_state.auth_status = "expired"
            st.rerun()

        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.session_state.auth_status = "unauthenticated"
            st.rerun()

        # -------- ADMIN AUDIT LOGS --------
        if role == "admin":
            st.markdown("---")
            st.subheader("📜 Audit Logs")

            if st.button("Load Logs"):
                try:
                    r = requests.get(
                        f"{BACKEND_URL}/admin/audit-logs",
                        headers={"Authorization": f"Bearer {st.session_state.token}"},
                        timeout=30,
                    )
                    if r.status_code == 200:
                        st.session_state.audit_logs = "".join(r.json().get("logs", []))
                except:
                    st.session_state.audit_logs = None

            if st.session_state.audit_logs:
                lines = st.session_state.audit_logs.strip().split("\n")
                parsed = []

                for line in lines:
                    parts = line.split()

                    if "LOGIN" in line:
                        parsed.append({
                            "Time": parts[0] + " " + parts[1],
                            "Action": "LOGIN",
                            "User": parts[3],
                            "Role": parts[5],
                            "File": "-"
                        })
                    elif "DOWNLOAD" in line:
                        parsed.append({
                            "Time": parts[0] + " " + parts[1],
                            "Action": "DOWNLOAD",
                            "User": parts[3],
                            "Role": parts[5],
                            "File": parts[7]
                        })

                if parsed:
                    df = pd.DataFrame(parsed)
                    st.dataframe(df, use_container_width=True, height=250)

# ---------------- MAIN ----------------
st.title("Company Internal Chatbot")

# ---------------- LOGIN ----------------
if st.session_state.auth_status == "unauthenticated":
    st.subheader("Login")

    if st.session_state.login_error:
        st.error(st.session_state.login_error)

    with st.form("login_form"):
        st.text_input("Username", key="login_username")
        st.text_input("Password", type="password", key="login_password")
        submit = st.form_submit_button("Login")

    if submit:
        try:
            r = requests.post(
                f"{BACKEND_URL}/login",
                json={
                    "username": st.session_state.login_username,
                    "password": st.session_state.login_password,
                },
                timeout=10,
            )
            if r.status_code == 200:
                st.session_state.token = r.json()["access_token"]
                st.session_state.login_time = datetime.utcnow()
                st.session_state.auth_status = "authenticated"
                st.rerun()
            else:
                st.session_state.login_error = "Invalid credentials"
        except:
            st.session_state.login_error = "Backend not reachable"

# ---------------- CHAT ----------------
elif st.session_state.auth_status == "authenticated":
    st.subheader("💬 Chat")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ---- SHOW SOURCES + DOWNLOAD ----
    if st.session_state.last_sources:
        st.markdown("### 📂 Sources")
        for src in st.session_state.last_sources:

            # 🔥 SEARCH RECURSIVELY INSIDE Fintech-data
            file_matches = list(SOURCE_DIR.rglob(src))

            if file_matches:
                file_path = file_matches[0]
                with open(file_path, "rb") as f:
                    st.download_button(
                        label=f"Download {src}",
                        data=f,
                        file_name=src,
                        use_container_width=True
                    )
            else:
                st.warning(f"{src} not found locally.")

    user_input = st.chat_input("Ask a question...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.spinner("Thinking..."):
            try:
                r = requests.post(
                    f"{BACKEND_URL}/query",
                    headers={"Authorization": f"Bearer {st.session_state.token}"},
                    json={"query": user_input},
                    timeout=180,
                )
                if r.status_code == 200:
                    data = r.json()
                    answer = data.get("answer", "")
                    st.session_state.last_sources = data.get("sources", [])
                else:
                    answer = f"⚠️ Backend error: {r.text}"
                    st.session_state.last_sources = []
            except Exception as e:
                answer = f"⚠️ Request failed: {e}"
                st.session_state.last_sources = []

        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()

elif st.session_state.auth_status == "expired":
    st.error("🔒 Session expired. Please log in again.")
