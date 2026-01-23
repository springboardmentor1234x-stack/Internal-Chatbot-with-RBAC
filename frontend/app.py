import streamlit as st
from datetime import datetime
from auth_ui import login_ui
from rag_ui import rag_ui
from admin_audit_ui import admin_audit_ui


# -------------------------------------------------
# Safe CSS Loader
# -------------------------------------------------
def local_css(file_name: str):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception:
        # UI should NEVER crash due to styling
        pass


local_css("frontend/assets/styles.css")

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="Internal Chatbot",
    layout="wide"
)

st.title("🔐 Internal Chatbot with RBAC")

# -------------------------------------------------
# 🔒 SESSION INITIALIZATION (SINGLE SOURCE OF TRUTH)
# -------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "access_token" not in st.session_state:
    st.session_state.access_token = None

if "user" not in st.session_state:
    st.session_state.user = None

if "role" not in st.session_state:
    st.session_state.role = None

if "token_expiry" not in st.session_state:
    st.session_state.token_expiry = None

# 👉 PAGE STATE (ADDED – REQUIRED FOR NAVIGATION)
if "page" not in st.session_state:
    st.session_state.page = "chat"  # default view


# -------------------------------------------------
# 🚪 GLOBAL LOGOUT HANDLER
# -------------------------------------------------
if st.session_state.get("logged_out"):
    logout_time = st.session_state.get("logout_time")

    if logout_time:
        st.success(
            f"✅ Logged out at {logout_time.strftime('%d %b %Y, %I:%M:%S %p')}"
        )
    else:
        st.success("✅ Logged out successfully")

    # HARD CLEANUP
    st.session_state.clear()
    st.stop()

# -------------------------------------------------
# ⏰ TOKEN EXPIRY GUARD (UI-LEVEL SECURITY)
# -------------------------------------------------
expiry = st.session_state.get("token_expiry")

if expiry and datetime.now() > expiry:
    st.warning("⏰ Session expired. Please login again.")
    st.session_state.clear()
    st.stop()

# -------------------------------------------------
# 🌐 GLOBAL BACKEND ERROR GUARD
# -------------------------------------------------
try:
    # -------------------------------------------------
    # 🔐 ROUTING LOGIC (AUTH GATE + PAGE ROUTER)
    # -------------------------------------------------
    if not st.session_state.logged_in or not st.session_state.access_token:
        login_ui()
        st.stop()
    else:
        if st.session_state.page == "chat":
            rag_ui()

        elif st.session_state.page == "admin_audit":
            admin_audit_ui()

        else:
            # Failsafe
            st.session_state.page = "chat"
            st.rerun()

except Exception:
    # NEVER expose stack traces to user
    st.error("🚨 System temporarily unavailable. Please try again later.")
    st.stop()
