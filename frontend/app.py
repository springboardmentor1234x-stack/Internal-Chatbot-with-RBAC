
# # app.py

import streamlit as st
import requests
from datetime import datetime
import jwt

API = "http://127.0.0.1:8000"

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="FinBot",
    layout="wide",
    page_icon="🤖"
)

# ---------- GREETING ----------
def get_greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "🌅 Good Morning"
    elif hour < 17:
        return "🌤️ Good Afternoon"
    else:
        return "🌙 Good Evening"

# ---------- SESSION STATE ----------
defaults = {
    "token": None,
    "role": None,
    "chat": [],
    "sources": {},
    "welcomed": False,
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ---------- SIDEBAR ----------
st.sidebar.title("🤖 FinBot")

now = datetime.now()
st.sidebar.markdown(
    f"""
📅 **Date:** {now.strftime("%A, %d %B %Y")}  
⏰ **Time:** {now.strftime("%I:%M %p")}
"""
)

st.sidebar.divider()
st.sidebar.subheader("📚 Sources")

if st.session_state.sources:
    for doc, chunks in st.session_state.sources.items():
        with st.sidebar.expander(f"📄 {doc}"):
            for text in chunks:
                st.markdown(f"• {text}")
else:
    st.sidebar.caption("Sources will appear after a response")

st.sidebar.divider()

# ================= LOGIN =================
if not st.session_state.token:
    st.title("🔐 FinBot Login")

    username = st.text_input("👤 Username")
    password = st.text_input("🔑 Password", type="password")

    if st.button("➡️ Login"):
        try:
            response = requests.post(
                f"{API}/login",
                json={"username": username, "password": password}
            )

            if response.status_code == 200:
                token = response.json()["access_token"]
                st.session_state.token = token

                decoded = jwt.decode(token, options={"verify_signature": False})
                st.session_state.role = decoded.get("role")

                st.success("✅ Login successful")
                st.rerun()
            else:
                st.error("❌ Invalid credentials")

        except requests.exceptions.ConnectionError:
            st.error("🚫 Backend server is not running")

# ================= MAIN APP =================
else:
    st.sidebar.success(f"🔐 Role: {st.session_state.role}")

    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()

    # ---------- HEADER ----------
    st.markdown(
        f"""
## {get_greeting()}, **{st.session_state.role.capitalize()}** 👋  
🤖 **FinBot** is ready to help you.
"""
    )

    if not st.session_state.welcomed:
        st.success("🎉 Ask questions only from authorized documents.")
        st.session_state.welcomed = True

    # ---------- INPUT + CLEAR CHAT ----------
    col1, col2 = st.columns([4, 1])

    with col1:
        with st.form("chat_form", clear_on_submit=True):
            query = st.text_input(
                "💬 How can I help you today?",
                placeholder="E.g. What is the leave policy?"
            )
            send = st.form_submit_button("📤 Send")

    with col2:
        if st.button("🧹 Clear Chat"):
            st.session_state.chat = []
            st.session_state.sources = {}
            st.success("🧼 Chat cleared")
            st.rerun()

    # ---------- SEND ----------
    if send and query.strip():
        with st.spinner("🤖 FinBot is thinking..."):
            try:
                response = requests.post(
                    f"{API}/chat",
                    json={
                        "query": query,
                        "token": st.session_state.token
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    st.session_state.chat.append(
                        (query, data.get("answer", ""), datetime.now())
                    )
                    st.session_state.sources = data.get("sources", {})

                elif response.status_code == 403:
                    st.error("🚫 Access denied")
                else:
                    st.error("❌ Error processing request")

            except requests.exceptions.ConnectionError:
                st.error("🚫 Cannot connect to backend")

    st.divider()

    # ---------- CHAT HISTORY ----------
    for q, a, t in reversed(st.session_state.chat):
        st.markdown("### 👤 You")
        st.markdown(q)

        st.markdown("### 🤖 FinBot")
        st.markdown(a)

        st.caption(t.strftime("%d %B %Y | %I:%M %p"))
        st.divider()
