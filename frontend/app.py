import streamlit as st
import requests
import os

# The URL where your FastAPI backend is running
BACKEND_URL = "http://127.0.0.1:8000"


def view_document(filename):
    """Display document content in a modal-like expander"""
    file_path = os.path.join("data", "raw", filename)

    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Create a unique key for each document viewer
            with st.expander(f"📖 Viewing: {filename}", expanded=True):
                st.markdown("---")
                st.markdown(content)
                st.markdown("---")
                if st.button(f"Close {filename}", key=f"close_{filename}"):
                    st.rerun()
        except Exception as e:
            st.error(f"Error reading {filename}: {str(e)}")
    else:
        st.error(f"Document {filename} not found at {file_path}")


def check_user_access(filename, user_role):
    """Check if user has access to a specific document"""
    document_permissions = {
        "quarterly_financial_report.md": ["Finance", "C-Level"],
        "market_report_q4_2024.md": ["Marketing", "C-Level"],
        "employee_handbook.md": [
            "HR",
            "Employee",
            "C-Level",
            "Finance",
            "Marketing",
            "Engineering",
        ],
        "engineering_master_doc.md": ["Engineering", "C-Level"],
    }

    allowed_roles = document_permissions.get(filename, ["Employee"])
    return user_role in allowed_roles


def login():
    """Login interface"""
    st.title("🔐 FinSolve Internal Chatbot - Login")
    st.markdown("**Role-Based Access Control (RBAC) System**")

    # Show available test accounts (collapsed by default for security)
    with st.expander("🔧 Demo Test Accounts", expanded=False):
        st.markdown(
            """
        **For demonstration purposes only:**
        
        All test accounts use password: `password123`
        
        - **admin** → C-Level access (all documents)
        - **finance_user** → Finance department access
        - **marketing_user** → Marketing department access  
        - **hr_user** → HR department access
        - **engineering_user** → Engineering department access
        - **employee** → General employee access
        
        *Note: In production, use secure authentication with proper user management.*
        """
        )

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("🚀 Login")

        if submit:
            if not username or not password:
                st.error("Please enter both username and password")
                return

            try:
                # Updated to match the FastAPI endpoint
                response = requests.post(
                    f"{BACKEND_URL}/auth/login",
                    data={"username": username, "password": password},
                )

                if response.status_code == 200:
                    data = response.json()
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = username
                    st.session_state["access_token"] = data["access_token"]
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    error_detail = response.json().get("detail", "Login failed")
                    st.error(f"❌ {error_detail}")
            except requests.exceptions.ConnectionError:
                st.error(
                    "🔌 Cannot connect to backend. Make sure FastAPI is running on http://127.0.0.1:8000"
                )
            except Exception as e:
                st.error(f"❌ Login error: {str(e)}")


def main_chat_interface():
    """Main chat interface for authenticated users"""
    # Sidebar with user info
    with st.sidebar:
        st.title("👤 User Profile")
        st.write(f"**Username:** {st.session_state.get('username', 'Unknown')}")

        # Get user profile from backend
        try:
            headers = {
                "Authorization": f"Bearer {st.session_state.get('access_token')}"
            }
            profile_response = requests.get(
                f"{BACKEND_URL}/api/v1/user/profile", headers=headers
            )
            if profile_response.status_code == 200:
                profile = profile_response.json()
                st.write(f"**Role:** {profile.get('role', 'Unknown')}")
                st.write(
                    f"**Permissions:** {len(profile.get('permissions', []))} permissions"
                )
            else:
                st.write("**Role:** Unable to fetch")
        except:
            st.write("**Role:** Connection error")

        st.divider()
        if st.button("🚪 Logout"):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # Main chat interface
    st.title("🤖 FinSolve Internal Chatbot")
    st.markdown(
        "**Ask questions about company documents based on your role permissions**"
    )

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                st.caption(f"📄 Sources: {', '.join(message['sources'])}")
            if message.get("accuracy"):
                accuracy = message["accuracy"]
                if accuracy >= 90:
                    st.caption(f"🎯 Accuracy: {accuracy:.1f}%")
                elif accuracy >= 80:
                    st.caption(f"✅ Accuracy: {accuracy:.1f}%")
                elif accuracy >= 70:
                    st.caption(f"⚠️ Accuracy: {accuracy:.1f}%")
                else:
                    st.caption(f"❌ Accuracy: {accuracy:.1f}%")

    # Get user role for document access control
    user_role = "Employee"  # Default
    try:
        headers = {"Authorization": f"Bearer {st.session_state.get('access_token')}"}
        profile_response = requests.get(
            f"{BACKEND_URL}/api/v1/user/profile", headers=headers
        )
        if profile_response.status_code == 200:
            profile = profile_response.json()
            user_role = profile.get("role", "Employee")
    except:
        pass

    # Document viewer section
    with st.expander("📄 Available Documents (Click to View)"):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Financial Documents")
            if check_user_access("quarterly_financial_report.md", user_role):
                if st.button("📈 Quarterly Financial Report"):
                    view_document("quarterly_financial_report.md")
            else:
                st.write("🔒 Access Denied - Finance role required")

            st.subheader("👥 HR Documents")
            if check_user_access("employee_handbook.md", user_role):
                if st.button("📋 Employee Handbook"):
                    view_document("employee_handbook.md")
            else:
                st.write("🔒 Access Denied - HR role required")

        with col2:
            st.subheader("📈 Marketing Documents")
            if check_user_access("market_report_q4_2024.md", user_role):
                if st.button("📊 Q4 2024 Market Report"):
                    view_document("market_report_q4_2024.md")
            else:
                st.write("🔒 Access Denied - Marketing role required")

            st.subheader("⚙️ Engineering Documents")
            if check_user_access("engineering_master_doc.md", user_role):
                if st.button("🔧 Engineering Master Doc"):
                    view_document("engineering_master_doc.md")
            else:
                st.write("🔒 Access Denied - Engineering role required")

    # Chat input
    if prompt := st.chat_input("Ask about company documents..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("🔍 Searching documents..."):
                try:
                    headers = {
                        "Authorization": f"Bearer {st.session_state.get('access_token')}"
                    }
                    response = requests.post(
                        f"{BACKEND_URL}/api/v1/chat",
                        json={"query": prompt},
                        headers=headers,
                    )

                    if response.status_code == 200:
                        data = response.json()
                        bot_message = data.get("response", "No response received")
                        sources = data.get("sources", [])

                        st.markdown(bot_message)
                        
                        # Display accuracy score if available
                        accuracy = data.get("accuracy_score", 0)
                        if accuracy > 0:
                            if accuracy >= 90:
                                st.success(f"🎯 Accuracy: {accuracy:.1f}% (Excellent)")
                            elif accuracy >= 80:
                                st.info(f"✅ Accuracy: {accuracy:.1f}% (Good)")
                            elif accuracy >= 70:
                                st.warning(f"⚠️ Accuracy: {accuracy:.1f}% (Fair)")
                            else:
                                st.error(f"❌ Accuracy: {accuracy:.1f}% (Needs Improvement)")
                        
                        if sources:
                            st.caption("📄 **Sources:**")
                            for i, source in enumerate(sources, 1):
                                st.caption(f"   {i}. {source}")
                            st.info(
                                "💡 **Tip:** Use the 'Available Documents' section above to view full documents!"
                            )

                        # Add performance metrics if available
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if data.get("query_category"):
                                st.caption(f"🔍 Category: {data['query_category'].title()}")
                        with col2:
                            if data.get("total_chunks_analyzed"):
                                st.caption(f"📊 Chunks: {data['total_chunks_analyzed']}")
                        with col3:
                            if accuracy > 0:
                                st.caption(f"📈 Score: {accuracy:.1f}%")

                        # Add bot response to chat history
                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": bot_message,
                                "sources": sources,
                                "accuracy": accuracy
                            }
                        )
                    elif response.status_code == 401:
                        st.error("🔐 Session expired. Please login again.")
                        # Clear session and force re-login
                        for key in list(st.session_state.keys()):
                            del st.session_state[key]
                        st.rerun()
                    elif response.status_code == 403:
                        st.error(
                            "🚫 Access denied. You don't have permission for this request."
                        )
                    else:
                        error_detail = response.json().get("detail", "Unknown error")
                        st.error(f"❌ Error {response.status_code}: {error_detail}")

                except requests.exceptions.ConnectionError:
                    st.error(
                        "🔌 Cannot connect to backend. Make sure FastAPI is running."
                    )
                except Exception as e:
                    st.error(f"❌ Request failed: {str(e)}")


# --- MAIN APP LOGIC ---
def main():
    # Initialize session state
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    # Route to appropriate interface
    if not st.session_state["authenticated"]:
        login()
    else:
        main_chat_interface()


if __name__ == "__main__":
    main()
