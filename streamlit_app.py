import streamlit as st
from auth import authenticate, init_db, create_user
from rag_engine import search, get_query_suggestions

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="Secure RBAC Chatbot", layout="wide")

# ----------------------------
# SESSION STATE INIT
# ----------------------------
if "role" not in st.session_state:
    st.session_state.role = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_query" not in st.session_state:
    st.session_state.selected_query = ""

# ----------------------------
# INIT DB & USERS
# ----------------------------
init_db()

DEFAULT_USERS = [
    ("admin", "admin123", "C-Level"),
    ("hr", "hr123", "HR"),
    ("fin", "fin123", "Finance"),
    ("mkt", "mkt123", "Marketing"),
    ("eng", "eng123", "Engineering"),
    ("emp", "emp123", "Employee")
]

for u, p, r in DEFAULT_USERS:
    create_user(u, p, r)

# ----------------------------
# LOGIN UI
# ----------------------------
if not st.session_state.role:
    st.title("🔐 Secure Internal Chatbot")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        role = authenticate(username, password)
        if role:
            st.session_state.role = role
            st.success(f"Logged in as {role}")
            st.rerun()
        else:
            st.error("Invalid credentials")

# ----------------------------
# MAIN APP (LOGGED IN)
# ----------------------------
else:
    st.sidebar.success(f"Role: {st.session_state.role}")
    if st.sidebar.button("Logout"):
        st.session_state.role = None
        st.session_state.messages = []
        st.session_state.selected_query = ""
        st.rerun()

    # ---- Question Input ----
    q = st.text_input(
        "Ask your question",
        value=st.session_state.selected_query
    )

    # ---- Query Suggestions ----
    st.markdown("#### 🔍 Suggested questions")

    suggestions = get_query_suggestions(st.session_state.role)

    cols = st.columns(len(suggestions))
    for i, suggestion in enumerate(suggestions):
        if cols[i].button(suggestion):
            st.session_state.selected_query = suggestion
            st.rerun()

    # ---- Ask Button ----
    if st.button("Ask"):
        ans, docs = search(
            q,
            st.session_state.role,
            st.session_state.messages
        )

        st.write(ans)

        if docs:
            with st.expander("Sources"):
                for d in docs:
                    st.write(d.metadata.get("source"))

        # reset selected query after ask
        st.session_state.selected_query = ""
