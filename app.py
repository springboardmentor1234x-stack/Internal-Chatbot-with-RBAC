import streamlit as st
import requests

st.set_page_config(page_title="Fintech RAG Assistant", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    [data-testid="stSidebar"] {
        background-color: #161b22;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 Fintech RAG Assistant")
st.markdown("---")

with st.sidebar:
    st.header("Settings")
    role = st.selectbox(
        "Select your Role:",
        ["Admin", "HR_Manager", "Marketing_Manager", "Intern"]
    )
    st.info(f"Access Level: {role}")
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about company data..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        response = requests.get(
            "http://127.0.0.1:8000/ask",
            params={"role": role, "question": prompt}
        )
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "No answer found.")
            sources = data.get("sources", [])

            with st.chat_message("assistant"):
                st.markdown(answer)
                if sources:
                    with st.expander("📚 View Sources"):
                        for src in sources:
                            st.markdown(f"- **{src}**")
            
            st.session_state.messages.append({"role": "assistant", "content": answer})
        else:
            st.error("Backend Error")

    except Exception as e:
        st.error(f"Connection Error: {e}")