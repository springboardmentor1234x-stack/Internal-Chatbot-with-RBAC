import streamlit as st
from utils.api_client import APIClient
from components.login import render_login
from components.chat import render_chat

# Page config
st.set_page_config(
    page_title="Company Internal Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Initialize API client
if "api_client" not in st.session_state:
    st.session_state.api_client = APIClient()

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Main app logic
def main():
    if not st.session_state.logged_in:
        render_login(st.session_state.api_client)
    else:
        render_chat(st.session_state.api_client)

if __name__ == "__main__":
    main()