import streamlit as st
import requests
from collections import defaultdict
import sys
import time


import jwt
# -----------------------------
# CONFIG
# -----------------------------

API_BASE_URL = "http://127.0.0.1:8000"
SESSION_TIMEOUT = 10 * 60

st.set_page_config(
    page_title="RBAC RAG Chatbot",
    page_icon="🤖",
    layout="wide"
)

st.markdown(
    """
    <style>
    /* ---------- GLOBAL ---------- */
    body {
        background-color: #0e1117;
        color: #e6e6e6;
    }

    /* ---------- SIDEBAR ---------- */
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #222;
    }

    /* Sidebar headings */
    .sidebar-title {
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 8px;
        color: #f0f0f0;
    }

    .role-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 999px;
        background-color: #1f6feb;
        color: white;
        font-size: 12px;
        font-weight: 600;
        margin-top: 6px;
    }

    /* ---------- CHAT BUBBLES ---------- */

    .chat-user {
        background: linear-gradient(135deg, #134e4a, #115e59);
        color: #ecfeff;
        padding: 14px 16px;
        border-radius: 12px;
        margin-bottom: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }

    .chat-assistant {
        background: linear-gradient(135deg, #1e3a8a, #1e40af);
        color: #eff6ff;
        padding: 14px 16px;
        border-radius: 12px;
        margin-bottom: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }

    .label-user {
        font-weight: 700;
        color: #99f6e4;
        margin-bottom: 4px;
        display: block;
    }

    .label-assistant {
        font-weight: 700;
        color: #bfdbfe;
        margin-bottom: 4px;
        display: block;
    }

    /* ---------- CONFIDENCE ---------- */

    .confidence-low {
        background-color: #3f1d1d;
        color: #fecaca;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 8px;
    }

    .confidence-medium {
        background-color: #3f2f1d;
        color: #fde68a;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 8px;
    }

    .confidence-high {
        background-color: #1f3d2b;
        color: #bbf7d0;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 8px;
    }

    /* ---------- SOURCES ---------- */

    .source-card {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 8px;
    }

    .source-title {
        font-weight: 600;
        color: #e5e7eb;
        margin-bottom: 6px;
    }

    /* ---------- INPUT ---------- */
    input {
        background-color: #020617 !important;
        color: #e5e7eb !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# -----------------------------
# SESSION STATE INITIALIZATION
# -----------------------------

def init_session_state():
    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False

    if "auth_token" not in st.session_state:
        st.session_state.auth_token = None

    if "user" not in st.session_state:
        st.session_state.user = None

    if "role" not in st.session_state:
        st.session_state.role = None

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "history_loaded" not in st.session_state:
        st.session_state.history_loaded = False

    # ✅ NEW: Session timeout tracking
    if "login_time" not in st.session_state:
        st.session_state.login_time = None

    if "last_activity" not in st.session_state:
        st.session_state.last_activity = None


init_session_state()

# -----------------------------
# HELPERS
# -----------------------------

def format_score(score):
    if score is None:
        return "N/A"
    return f"{int(score * 100)}%"

def is_session_expired():
    now = time.time()

    # If no login time exists, session is invalid
    if not st.session_state.login_time:
        return True

    # Absolute timeout (10 min from login)
    if now - st.session_state.login_time > SESSION_TIMEOUT:
        return True

    # Inactivity timeout (10 min since last action)
    if (
        st.session_state.last_activity
        and now - st.session_state.last_activity > SESSION_TIMEOUT
    ):
        return True

    return False

def group_sources_by_document(sources):
    grouped = defaultdict(list)

    for src in sources:
        if isinstance(src, str):
            grouped[src].append({
                "chunk_id": None,
                "score": None,
                "url": None
            })
        else:
            grouped[src["document_title"]].append(src)

    return grouped

def clear_chat_history_backend():
    headers = {
        "Authorization": f"Bearer {st.session_state.auth_token}"
    }

    response = requests.delete(
        f"{API_BASE_URL}/chat/history",
        headers=headers
    )

    return response.status_code == 200


# -----------------------------
# BACKEND API CALLS
# -----------------------------

def fetch_chat_history():
    headers = {
        "Authorization": f"Bearer {st.session_state.auth_token}"
    }

    response = requests.get(
        f"{API_BASE_URL}/chat/history",
        headers=headers
    )

    if response.status_code != 200:
        return []

    return response.json().get("messages", [])


def call_chat_api(query: str):
    headers = {
        "Authorization": f"Bearer {st.session_state.auth_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        f"{API_BASE_URL}/chat",
        headers=headers,
        json={"query": query}
    )

    if response.status_code != 200:
        return {
            "answer": "Error contacting backend.",
            "sources": [],
            "confidence": "low"
        }

    return response.json()


def load_history_if_needed():
    if not st.session_state.history_loaded:
        st.session_state.chat_history = fetch_chat_history()
        st.session_state.history_loaded = True


# -----------------------------
# AUTH UI
# -----------------------------

def show_login():
    st.title("🔐 Login")
    st.write("Please login to access the internal chatbot.")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not username or not password:
            st.error("Please enter username and password")
            return

        with st.spinner("Authenticating..."):
            response = requests.post(
                f"{API_BASE_URL}/auth/login",
                json={
                    "username": username,
                    "password": password
                }
            )

        if response.status_code != 200:
            st.error("Invalid username or password")
            return

        data = response.json()
        access_token = data["access_token"]

        # decode JWT payload (no verification needed here)
        payload = jwt.decode(access_token, options={"verify_signature": False})
        st.write("JWT payload:", payload)

        st.session_state.auth_token = access_token
        st.session_state.user = payload.get("sub") or payload.get("username")
        st.session_state.role = payload.get("role")

        st.session_state.is_authenticated = True
        st.session_state.history_loaded = False

        st.session_state.login_time = time.time()
        st.session_state.last_activity = time.time()
        
        st.query_params["token"] = access_token
        st.success("Login successful!")
        st.rerun()


def logout():
    st.session_state.clear()
    st.rerun()


# -----------------------------
# CHAT UI (WITH SIDEBAR)
# -----------------------------

def show_chat():
    # Load history once
    load_history_if_needed()

    # ---------- SIDEBAR ----------
    with st.sidebar:
        st.markdown("## 👤 User")
        st.markdown(f"**User:** `{st.session_state.user}`")
        st.markdown(
            f"<span class='role-badge'>{st.session_state.role}</span>",
            unsafe_allow_html=True
        )

        st.divider()
        st.markdown("## 🕘 Chat History")

        if not st.session_state.chat_history:
            st.caption("No previous chats.")
        else:
            for msg in st.session_state.chat_history:
                if msg.get("metadata", {}).get("role") == "USER":
                    st.markdown(f"- {msg['content'][:40]}...")

        st.divider()
        
        if st.session_state.login_time:
            remaining = max(
                0,
                int(SESSION_TIMEOUT - (time.time() - st.session_state.login_time))
            )
            mins = remaining // 60
            secs = remaining % 60
            st.caption(f"⏳ Session expires in: {mins}m {secs}s")


        if st.button("🧹 Clear Chat"):
            st.session_state.last_activity = time.time()   # ✅ NEW

            with st.spinner("Clearing chat history..."):
                success = clear_chat_history_backend()

            if success:
                st.session_state.chat_history = []
                st.session_state.history_loaded = True
                st.rerun()
            else:
                st.error("Failed to clear chat history")

        # ---- PUSH LOGOUT TO BOTTOM ----
        st.markdown("<div style='height: 100%;'></div>", unsafe_allow_html=True)
        st.divider()
        st.button("🚪 Logout", on_click=logout)

    # ---------- MAIN CHAT ----------
    st.title("🤖 RBAC RAG Chatbot")
    st.divider()

    # 🔹 RENDER CHAT HISTORY (THIS PART IS CRUCIAL)
    for msg in st.session_state.chat_history:
        role = msg.get("metadata", {}).get("role")

        if role == "USER":
            st.markdown(
                f"""
                <div class="chat-user">
                    <span class="label-user">You</span><br>
                    {msg['content']}
                </div>
                """,
                unsafe_allow_html=True
            )

        elif role == "ASSISTANT":
            st.markdown(
                f"""
                <div class="chat-assistant">
                    <span class="label-assistant">Assistant</span><br>
                    {msg['content']}
                </div>
                """,
                unsafe_allow_html=True
            )

            confidence = msg.get("metadata", {}).get("confidence", "low")

            if confidence == "high":
                st.success("Confidence: High")
            elif confidence == "medium":
                st.warning("Confidence: Medium")
            else:
                st.error("Confidence: Low")

            sources = msg.get("sources", [])

            if not sources:
                st.info("No sources available for this answer.")
            else:
                grouped_sources = group_sources_by_document(sources)

                with st.expander("📄 Evidence & Sources"):
                    for doc_title, chunks in grouped_sources.items():
                        st.markdown(f"### 📘 {doc_title}")
                        for c in chunks:
                            st.markdown("<div class='source-card'>", unsafe_allow_html=True)

                            cols = st.columns([3, 1, 2])
                            with cols[0]:
                                if c.get("chunk_id"):
                                    st.markdown(f"**Chunk:** `{c['chunk_id']}`")
                            with cols[1]:
                                st.markdown(f"**Relevance:** {format_score(c.get('score'))}")
                            with cols[2]:
                                if c.get("url"):
                                    st.markdown(f"[Open document]({c['url']})")

                            st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    query = st.text_input("Ask a question", key="chat_input")

    if st.button("Send") and query.strip():
        
        st.session_state.last_activity = time.time()

        # 1️⃣ Append USER message first
        st.session_state.chat_history.append({
            "content": query,
            "metadata": {"role": "USER"}
        })

        with st.spinner("Thinking..."):
            response = call_chat_api(query)

        # 2️⃣ Append ASSISTANT message
        st.session_state.chat_history.append({
            "content": response.get("answer", "No response from backend."),
            "metadata": {
                "role": "ASSISTANT",
                "confidence": response.get("confidence", "low")
            },
            "sources": response.get("sources", [])
        })

        # ✅ FORCE ONE CLEAN REFRESH (THIS IS REQUIRED)
        st.rerun()


# -----------------------------
# APP ENTRY (WITH SESSION TIMEOUT)
# -----------------------------

# ✅ CHECK SESSION EXPIRY BEFORE SHOWING UI
if st.session_state.is_authenticated and is_session_expired():
    st.warning("Session expired. Please log in again.")
    st.session_state.clear()
    st.query_params.clear()
    st.stop()

# Normal app flow
if not st.session_state.is_authenticated:
    show_login()
else:
    show_chat()
