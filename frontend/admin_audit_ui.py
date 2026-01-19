import streamlit as st
import requests
from datetime import datetime

API_BASE = "http://127.0.0.1:8000"

# ======================================================
# Helpers
# ======================================================
def force_logout(message: str):
    st.session_state.clear()
    st.error(message)
    st.stop()


def fetch_audit_logs(headers: dict):
    try:
        response = requests.get(
            f"{API_BASE}/admin/audit/logs",
            headers=headers,
            timeout=10
        )
    except requests.exceptions.RequestException:
        st.error("🚨 Backend unavailable.")
        return None

    if response.status_code == 401:
        force_logout("⏰ Session expired. Please login again.")

    if response.status_code == 403:
        st.error("🚫 You are not authorized to view audit logs.")
        return None

    if response.status_code != 200:
        st.error("🚨 Failed to fetch audit logs.")
        return None

    return response.json()


# ======================================================
# Admin Audit UI
# ======================================================
def admin_audit_ui():
    # ---------------- Auth Guard ----------------
    if not st.session_state.get("logged_in"):
        force_logout("Session expired.")

    role = st.session_state.role
    token = st.session_state.access_token

    if "admin" not in role.lower():
        st.error("🚫 Admin access only.")
        st.stop()

    headers = {"Authorization": f"Bearer {token}"}

    # ---------------- Header ----------------
    st.title("📜 Audit Logs")
    st.caption("Read-only system activity logs (Admin only)")

    # ---------------- Fetch Logs ----------------
    with st.spinner("Loading audit logs..."):
        logs = fetch_audit_logs(headers)

    if not logs:
        st.info("No audit logs available.")
        return

    # ---------------- Filters ----------------
    with st.expander("🔍 Filters", expanded=False):
        usernames = sorted({log["username"] for log in logs})
        actions = sorted({log["action"] for log in logs})

        selected_user = st.selectbox("Filter by user", ["All"] + usernames)
        selected_action = st.selectbox("Filter by action", ["All"] + actions)

    # ---------------- Render Logs ----------------
    for log in logs:
        if selected_user != "All" and log["username"] != selected_user:
            continue
        if selected_action != "All" and log["action"] != selected_action:
            continue

        timestamp = log["timestamp"]
        try:
            timestamp = datetime.fromisoformat(timestamp)
            timestamp = timestamp.strftime("%d %b %Y, %I:%M:%S %p")
        except Exception:
            pass

        with st.expander(
            f"🕒 {timestamp} | 👤 {log['username']} | 🔐 {log['action']}",
            expanded=False
        ):
            st.markdown(f"**Role:** `{log['role']}`")

            if log.get("query"):
                st.markdown(f"**Query:** `{log['query']}`")

            documents = log.get("documents", [])
            if documents:
                st.markdown("**Documents:**")
                for doc in documents:
                    st.markdown(f"- {doc}")
            else:
                st.caption("No documents associated.")

