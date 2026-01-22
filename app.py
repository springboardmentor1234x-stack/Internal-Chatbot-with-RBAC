import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Secure RAG Chatbot", layout="wide")

st.title("🔐 Company Internal Chatbot")

# ---------------- LOGIN ----------------
if "token" not in st.session_state:
    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            data={   # ✅ MUST be form data
                "username": username,
                "password": password
            }
        )

        if response.status_code == 200:
            st.session_state.token = response.json()["access_token"]
            st.success("Login successful!")
            st.rerun()   # ✅ correct method
        else:
            st.error("Invalid credentials")

# ---------------- CHAT ----------------
else:
    st.success("Logged in successfully")

    question = st.text_input("Ask a question")

    if st.button("Ask") and question.strip():
        headers = {
            "Authorization": f"Bearer {st.session_state.token}"
        }

        response = requests.post(
            f"{BACKEND_URL}/rag/query",
            params={"question": question},
            headers=headers
        )

        if response.status_code == 200:
            result = response.json()
            st.markdown("### 💬 Answer")
            st.write(result["answer"])
        else:
            st.error("Unauthorized or error occurred")

    if st.button("Logout"):
        del st.session_state.token
        st.rerun()   # ✅ correct method
