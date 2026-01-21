import streamlit as st
import time
from auth import authenticate, init_db, create_user
from rag_engine import search

# 1. Initialize DB and Users
init_db()
DEFAULT_USERS = [
    ("admin", "admin123", "C-Level"),
    ("hr1", "hr123", "HR"),
    ("eng1", "eng123", "Engineering"), 
    ("mkt1", "mkt123", "Marketing"),
    ("fin1", "fin123", "Finance"),
    ("emp1", "emp123", "Employee"),
    ("gen1", "gen123", "General"),  # Added General User
]
for u, p, r in DEFAULT_USERS:
    try:
        create_user(u, p, r)
    except:
        pass 

st.set_page_config(page_title="Secure Internal Chatbot System", layout="wide", page_icon="🔐")

# Session State Management
if "role" not in st.session_state:
    st.session_state.role = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- LOGIN SCREEN (Centered & Clean) ---
if not st.session_state.role:
    _, center_col, _ = st.columns([1, 1.2, 1])
    
    with center_col:
        st.markdown("<h1 style='text-align: center;'>🔐 Secure Internal Chatbot System</h1>", unsafe_allow_html=True)
        with st.form("login"):
            st.subheader("Authentication Required")
            u = st.text_input("Corporate ID")
            p = st.text_input("Access Key", type="password")
            if st.form_submit_button("Sign In", use_container_width=True):
                role = authenticate(u, p)
                if role:
                    st.session_state.role = role
                    st.rerun()
                else:
                    st.error("Invalid Credentials")

# --- CHAT INTERFACE ---
else:
    # Sidebar: Moved restriction and security info here
    with st.sidebar:
        st.header(f"👤 {st.session_state.role}")
        
        # RESTRICTION MESSAGE (Moved from main area to sidebar)
        st.warning(f"**Access Notice:** Your current role (**{st.session_state.role}**) restricts data retrieval to department-authorized files only.")
        
        st.divider()
        if st.button("Clear History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        if st.button("Logout", use_container_width=True):
            st.session_state.role = None
            st.session_state.messages = []
            st.rerun()
        st.divider()
        st.caption("🔒 Secured Session Active")

    # Main Chat Area
    st.title("💬 Corporate Knowledge Assistant")

    # Display History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Handle Input
    if query := st.chat_input("Ask a question..."):
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            
            # Call the search engine
            answer, docs = search(query, st.session_state.role, st.session_state.messages)
            
            # Streaming effect
            for chunk in answer.split():
                full_response += chunk + " "
                time.sleep(0.05)
                response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)
            
            if docs:
                with st.expander("📄 Source Verification"):
                    for d in docs:
                        st.markdown(f"**Source & Rank:** `{d.metadata.get('source', 'Unknown')}`")
                        st.caption(d.page_content[:250] + "...")
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})
