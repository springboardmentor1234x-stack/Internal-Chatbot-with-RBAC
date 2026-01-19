# rag_ui without cache logic
# import streamlit as st
# import requests
# from datetime import datetime
# from auth_ui import trigger_logout
# from urllib.parse import quote
# from pathlib import Path
# from admin_audit_ui import admin_audit_ui

# API_BASE = "http://127.0.0.1:8000"

# # =========================================================
# # Helpers
# # =========================================================
# def evidence_label(score: float) -> str:
#     """
#     Evidence strength label.
#     IMPORTANT: This does NOT judge answer quality.
#     """
#     if score >= 0.60:
#         return "🟢 High relevance"
#     elif score >= 0.45:
#         return "🟡 Medium relevance"
#     return "🔴 Low relevance"


# def ensure_session_state():
#     if "messages" not in st.session_state:
#         st.session_state.messages = []
#     if "scroll_to" not in st.session_state:
#         st.session_state.scroll_to = None
#     if "view" not in st.session_state:
#         st.session_state.view = "chat"


# def force_logout(message: str):
#     st.session_state.clear()
#     st.error(message)
#     st.stop()


# def fetch_file(download_path: str, headers: dict):
#     try:
#         safe_url = quote(f"{API_BASE}{download_path}", safe="/:")
#         response = requests.get(safe_url, headers=headers, timeout=60)
#     except requests.exceptions.RequestException:
#         st.error("🚨 Backend unavailable during download.")
#         return None

#     if response.status_code == 401:
#         force_logout("⏰ Session expired. Please login again.")
#     if response.status_code == 403:
#         st.error("🚫 You are not authorized to download this dataset.")
#         return None
#     if response.status_code == 404:
#         st.error("📄 Dataset not found on server.")
#         return None
#     if response.status_code != 200:
#         st.error(f"❌ Download failed (status {response.status_code}).")
#         return None

#     return response.content


# # =========================================================
# # Main UI
# # =========================================================
# def rag_ui():
#     if not st.session_state.get("logged_in"):
#         force_logout("Session expired. Please login again.")

#     ensure_session_state()

#     username = st.session_state.user
#     role = st.session_state.role
#     token = st.session_state.access_token

#     headers = {"Authorization": f"Bearer {token}"}

#     # =====================================================
#     # Admin Audit View
#     # =====================================================
#     if st.session_state.view == "audit":
#         admin_audit_ui()
#         return

#     # ---------------- Header ----------------
#     st.title("💬 Internal Knowledge Chat")
#     st.caption(f"👤 **{username}** | Role: **{role}**")

#     if "login_time" in st.session_state:
#         st.caption(
#             f"🕒 Logged in at "
#             f"{st.session_state.login_time.strftime('%d %b %Y, %I:%M:%S %p')}"
#         )

#     # =====================================================
#     # Sidebar
#     # =====================================================
#     with st.sidebar:
#         st.header("🧭 Session")
#         st.write(f"**User:** {username}")
#         st.write(f"**Role:** {role}")
#         st.divider()

#         if "admin" in role.lower():
#             if st.button("📜 View Audit Logs"):
#                 st.session_state.view = "audit"
#                 st.rerun()

#         st.divider()

#         st.subheader("🕘 Conversation")
#         for idx, m in enumerate(st.session_state.messages):
#             if m["role"] == "user":
#                 if st.button(m["content"], key=f"nav_{idx}"):
#                     st.session_state.scroll_to = idx

#         st.divider()

#         if st.button("🧹 Clear chat"):
#             st.session_state.messages = []
#             st.session_state.scroll_to = None
#             st.rerun()

#         st.divider()

#         if st.button("🚪 Logout"):
#             trigger_logout()

#     # =====================================================
#     # Render Chat
#     # =====================================================
#     scroll_to = st.session_state.scroll_to

#     for i, msg in enumerate(st.session_state.messages):
#         with st.chat_message(msg["role"]):
#             if scroll_to == i:
#                 st.markdown("🔹 **Selected message**")

#             st.markdown(msg["content"])

#             # -------------------------------------------------
#             # 🔐 FIX-1: Sources shown ONLY if citations exist
#             # -------------------------------------------------
#             citations = msg.get("citations")
#             if msg["role"] == "assistant" and isinstance(citations, list) and citations:

#                 st.caption(
#                     "ℹ️ The answer above is generated **only from the authorized documents below**."
#                 )

#                 for d_idx, doc in enumerate(citations):
#                     doc_name = doc.get("doc_name", "Unknown document")
#                     download_path = doc.get("download_link")
#                     chunks = doc.get("chunks", [])

#                     with st.expander(f"📚 Source: {doc_name}", expanded=False):

#                         if download_path:
#                             file_bytes = fetch_file(download_path, headers)
#                             if file_bytes:
#                                 filename = Path(download_path).name
#                                 st.download_button(
#                                     label=f"⬇️ Download {doc_name}",
#                                     data=file_bytes,
#                                     file_name=filename,
#                                     mime="text/plain",
#                                     key=f"dl_{i}_{d_idx}"
#                                 )

#                         for chunk in chunks:
#                             chunk_id = chunk.get("chunk_id", "N/A")
#                             score = chunk.get("relevance_score", 0.0)
#                             st.markdown(
#                                 f"- **Chunk {chunk_id}** | {evidence_label(score)}"
#                             )

#     # =====================================================
#     # Chat Input
#     # =====================================================
#     query = st.chat_input("Ask a question")

#     if not query:
#         return

#     st.session_state.messages.append({
#         "role": "user",
#         "content": query
#     })

#     with st.chat_message("assistant"):
#         with st.spinner("🤔 Thinking..."):
#             try:
#                 response = requests.post(
#                     f"{API_BASE}/ask",
#                     json={"query": query, "top_k": 5},
#                     headers=headers,
#                     timeout=120
#                 )
#             except requests.exceptions.RequestException:
#                 st.error("🚨 Backend unavailable.")
#                 return

#         if response.status_code == 401:
#             force_logout("⏰ Session expired.")

#         if response.status_code == 403:
#             st.error("🚫 Access denied by RBAC.")
#             return

#         if response.status_code != 200:
#             st.error("🚨 Server error.")
#             return

#         data = response.json()
#         answer = data.get("answer", "")
#         citations = data.get("citations", [])

#         st.markdown(answer)

#         st.session_state.messages.append({
#             "role": "assistant",
#             "content": answer,
#             "citations": citations
#         })

# rag_ui with cache logic
import streamlit as st
import requests
from datetime import datetime
from auth_ui import trigger_logout
from urllib.parse import quote
from pathlib import Path
from admin_audit_ui import admin_audit_ui

API_BASE = "http://127.0.0.1:8000"

# =========================================================
# Helpers
# =========================================================
def evidence_label(score: float) -> str:
    """
    Evidence strength label.
    IMPORTANT: This does NOT judge answer quality.
    """
    if score >= 0.60:
        return "🟢 High relevance"
    elif score >= 0.45:
        return "🟡 Medium relevance"
    return "🔴 Low relevance"


def normalize_query(query: str) -> str:
    """Normalize query to avoid cache miss"""
    return " ".join(query.strip().lower().split())


def ensure_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "scroll_to" not in st.session_state:
        st.session_state.scroll_to = None

    if "view" not in st.session_state:
        st.session_state.view = "chat"

    # 🔑 In-memory application cache
    if "query_cache" not in st.session_state:
        st.session_state.query_cache = {}


def force_logout(message: str):
    st.session_state.clear()
    st.error(message)
    st.stop()


def fetch_file(download_path: str, headers: dict):
    try:
        safe_url = quote(f"{API_BASE}{download_path}", safe="/:")
        response = requests.get(safe_url, headers=headers, timeout=60)
    except requests.exceptions.RequestException:
        st.error("🚨 Backend unavailable during download.")
        return None

    if response.status_code == 401:
        force_logout("⏰ Session expired. Please login again.")
    if response.status_code == 403:
        st.error("🚫 You are not authorized to download this dataset.")
        return None
    if response.status_code == 404:
        st.error("📄 Dataset not found on server.")
        return None
    if response.status_code != 200:
        st.error(f"❌ Download failed (status {response.status_code}).")
        return None

    return response.content


# =========================================================
# Main UI
# =========================================================
def rag_ui():
    if not st.session_state.get("logged_in"):
        force_logout("Session expired. Please login again.")

    ensure_session_state()

    username = st.session_state.user
    role = st.session_state.role
    token = st.session_state.access_token

    headers = {"Authorization": f"Bearer {token}"}

    # =====================================================
    # Admin Audit View
    # =====================================================
    if st.session_state.view == "audit":
        admin_audit_ui()
        return

    # ---------------- Header ----------------
    st.title("💬 Internal Knowledge Chat")
    st.caption(f"👤 **{username}** | Role: **{role}**")

    if "login_time" in st.session_state:
        st.caption(
            f"🕒 Logged in at "
            f"{st.session_state.login_time.strftime('%d %b %Y, %I:%M:%S %p')}"
        )

    # =====================================================
    # Sidebar
    # =====================================================
    with st.sidebar:
        st.header("🧭 Session")
        st.write(f"**User:** {username}")
        st.write(f"**Role:** {role}")
        st.divider()

        if "admin" in role.lower():
            if st.button("📜 View Audit Logs"):
                st.session_state.view = "audit"
                st.rerun()

        st.divider()

        st.subheader("🕘 Conversation")
        for idx, m in enumerate(st.session_state.messages):
            if m["role"] == "user":
                if st.button(m["content"], key=f"nav_{idx}"):
                    st.session_state.scroll_to = idx

        st.divider()

        if st.button("🧹 Clear chat"):
            st.session_state.messages = []
            st.session_state.scroll_to = None
            st.rerun()

        # ✅ Clear Cache Button (MANDATORY)
        if st.button("🧹 Clear cache"):
            st.session_state.query_cache.clear()
            st.success("Cache cleared successfully!")
            st.rerun()

        st.divider()

        if st.button("🚪 Logout"):
            trigger_logout()

    # =====================================================
    # Render Chat
    # =====================================================
    scroll_to = st.session_state.scroll_to

    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            if scroll_to == i:
                st.markdown("🔹 **Selected message**")

            st.markdown(msg["content"])

            citations = msg.get("citations")
            if msg["role"] == "assistant" and isinstance(citations, list) and citations:
                st.caption(
                    "ℹ️ The answer above is generated **only from the authorized documents below**."
                )

                for d_idx, doc in enumerate(citations):
                    doc_name = doc.get("doc_name", "Unknown document")
                    download_path = doc.get("download_link")
                    chunks = doc.get("chunks", [])

                    with st.expander(f"📚 Source: {doc_name}", expanded=False):

                        if download_path:
                            file_bytes = fetch_file(download_path, headers)
                            if file_bytes:
                                filename = Path(download_path).name
                                st.download_button(
                                    label=f"⬇️ Download {doc_name}",
                                    data=file_bytes,
                                    file_name=filename,
                                    mime="text/plain",
                                    key=f"dl_{i}_{d_idx}"
                                )

                        for chunk in chunks:
                            chunk_id = chunk.get("chunk_id", "N/A")
                            score = chunk.get("relevance_score", 0.0)
                            st.markdown(
                                f"- **Chunk {chunk_id}** | {evidence_label(score)}"
                            )

    # =====================================================
    # Chat Input + CACHE LOGIC
    # =====================================================
    query = st.chat_input("Ask a question")

    if not query:
        return

    st.session_state.messages.append({
        "role": "user",
        "content": query
    })

    normalized_query = normalize_query(query)
    cache_key = f"{role}::{normalized_query}"

    with st.chat_message("assistant"):

        # 🔍 CACHE HIT
        if cache_key in st.session_state.query_cache:
            st.info("⚡ Retrieved from cache (LLM not called)")
            cached = st.session_state.query_cache[cache_key]
            answer = cached["answer"]
            citations = cached["citations"]
            st.markdown(answer)

        # ❌ CACHE MISS
        else:
            with st.spinner("🤔 Thinking..."):
                try:
                    response = requests.post(
                        f"{API_BASE}/ask",
                        json={"query": query, "top_k": 5},
                        headers=headers,
                        timeout=120
                    )
                except requests.exceptions.RequestException:
                    st.error("🚨 Backend unavailable.")
                    return

            if response.status_code == 401:
                force_logout("⏰ Session expired.")

            if response.status_code == 403:
                st.error("🚫 Access denied by RBAC.")
                return

            if response.status_code != 200:
                st.error("🚨 Server error.")
                return

            data = response.json()
            answer = data.get("answer", "")
            citations = data.get("citations", [])

            st.markdown(answer)

            # 💾 STORE IN CACHE
            st.session_state.query_cache[cache_key] = {
                "answer": answer,
                "citations": citations,
                "timestamp": datetime.now()
            }

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "citations": citations
    })
