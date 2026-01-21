import streamlit as st
import requests

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="Company Internal Chatbot", layout="centered")

st.title("🔐 Company Internal Chatbot")

if "token" not in st.session_state:
    st.session_state.token = None

# ---------------- AUTH ----------------
if not st.session_state.token:
    st.subheader("Register / Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    role = st.selectbox("Select Role", [
        "intern",
        "finance",
        "hr",
        "marketing",
        "engineering",
        "admin"
    ])

    col1, col2 = st.columns(2)

    if col1.button("Register"):
        r = requests.post(
            f"{API}/auth/register",
            params={
                "username": username,
                "password": password,
                "role": role
            }
        )
        if r.status_code == 200:
            st.success("User registered successfully")
        else:
            st.error(r.text)

    if col2.button("Login"):
        r = requests.post(
            f"{API}/auth/login",
            params={
                "username": username,
                "password": password
            }
        )
        if r.status_code == 200:
            st.session_state.token = r.json()["access_token"]
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Login failed")

# ---------------- CHAT ----------------
else:
    st.subheader("Ask Company Knowledge Base")

    query = st.text_input("Enter your question")

    if st.button("Ask"):
        headers = {
            "Authorization": f"Bearer {st.session_state.token}"
        }

        r = requests.get(
            f"{API}/search",
            params={"q": query},
            headers=headers
        )

        try:
            data = r.json()
        except:
            st.error("Backend error")
            st.stop()

        if data.get("status") == "success":
            st.markdown("### Answer")
            st.write(data["answer"])

            st.markdown("### Sources")
            for s in data["sources"]:
                st.write("📄", s["source"])
        else:
            st.error(f"{data.get('code')}: {data.get('detail')}")

    if st.button("Logout"):
        st.session_state.token = None
        st.rerun()
