# frontend/auth_ui.py
import os
import streamlit as st
import requests
from datetime import datetime
import jwt

# API_BASE = "http://127.0.0.1:8000"
API_BASE = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")



# ======================================================
# 🔐 LOGIN UI
# ======================================================
def login_ui():
    st.subheader("🔐 Login")

    # -----------------------------
    # Inputs
    # -----------------------------
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    login_clicked = st.button("Login")
    if not login_clicked:
        return

    # -----------------------------
    # Input validation
    # -----------------------------
    if not username or not password:
        st.error("Please enter username and password")
        return

    # -----------------------------
    # Authenticate
    # -----------------------------
    with st.spinner("Authenticating..."):
        try:
            response = requests.post(
                f"{API_BASE}/auth/login",
                json={
                    "username": username,
                    "password": password
                },
                timeout=5
            )
        except requests.exceptions.RequestException:
            st.error("🚨 Backend unavailable. Please try again later.")
            return

    if response.status_code != 200:
        st.error("❌ Invalid username or password")
        return

    # -----------------------------
    # Extract token safely
    # -----------------------------
    try:
        token = response.json()["access_token"]
    except Exception:
        st.error("🚨 Invalid authentication response")
        return

    # -----------------------------
    # Fetch user profile
    # -----------------------------
    try:
        profile_res = requests.get(
            f"{API_BASE}/user/profile",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
    except requests.exceptions.RequestException:
        st.error("Failed to fetch user profile")
        return

    if profile_res.status_code != 200:
        st.error("Failed to load user profile")
        return

    user_profile = profile_res.json()

    # -----------------------------
    # ✅ SESSION STATE INITIALIZATION
    # (NO clear(), NO unreachable code)
    # -----------------------------
    st.session_state.logged_in = True
    st.session_state.access_token = token
    st.session_state.user = user_profile.get("username")
    st.session_state.role = user_profile.get("role")
    st.session_state.login_time = datetime.now()

    # -----------------------------
    # ⏰ Decode JWT expiry (UI only)
    # -----------------------------
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        st.session_state.token_expiry = datetime.fromtimestamp(decoded["exp"])
    except Exception:
        st.session_state.token_expiry = None

    st.success("✅ Login successful")
    st.rerun()


# ======================================================
# 🚪 LOGOUT TRIGGER (STATE ONLY)
# ======================================================
def trigger_logout():
    """
    Logout must ONLY mutate state.
    Actual cleanup is handled in app.py
    """
    st.session_state.logout_time = datetime.now()
    st.session_state.logged_out = True
    st.rerun()

