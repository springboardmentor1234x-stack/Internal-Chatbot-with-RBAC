"""
Admin panel component for user management and logs
"""

import streamlit as st
from utils.api_client import APIClient
from config.settings import AVAILABLE_ROLES

def render_admin_panel(api_client: APIClient):
    """Render admin panel with tabs"""
    
    st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h1>🔧 Admin Dashboard</h1>
            <p style='color: #666;'>Manage users, view logs, and monitor system</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    # Tabs for different admin sections
    tab1, tab2, tab3, tab4 = st.tabs(["👥 User Management", "📋 Audit Logs", "📊 System Info", "👁️ User Activity"])
    
    with tab1:
        render_user_management(api_client)
    
    with tab2:
        render_audit_logs(api_client)
    
    with tab3:
        render_system_info(api_client)
    
    with tab4:
        render_user_activity(api_client)


def render_user_management(api_client: APIClient):
    """Render user management section"""
    
    st.subheader("👥 User Management")
    
    # Action buttons
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("Manage user accounts, roles, and permissions")
    
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    # Load users
    try:
        with st.spinner("Loading users..."):
            users = api_client.list_users()
        
        if not users:
            st.info("No users found")
            return
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Users", len(users))
        with col2:
            active_count = sum(1 for u in users if u.get('is_active', False))
            st.metric("Active Users", active_count)
        with col3:
            admin_count = sum(1 for u in users if u.get('role', '').lower() == 'admin')
            st.metric("Admins", admin_count)
        
        st.markdown("---")
        
        # User table
        st.markdown("### User List")
        
        for user in users:
            with st.expander(f"👤 {user['username']} ({user['role']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Username:** {user['username']}")
                    st.markdown(f"**Role:** {user['role']}")
                    st.markdown(f"**User ID:** {user['id']}")
                    
                    status = "✅ Active" if user.get('is_active', False) else "❌ Inactive"
                    st.markdown(f"**Status:** {status}")
                    
                    if 'created_at' in user:
                        st.markdown(f"**Created:** {user['created_at']}")
                
                with col2:
                    st.markdown("**Actions:**")
                    
                    # Toggle active status
                    new_status = not user.get('is_active', False)
                    status_label = "Deactivate" if user.get('is_active', False) else "Activate"
                    
                    if st.button(
                        f"🔄 {status_label}",
                        key=f"toggle_{user['username']}",
                        use_container_width=True
                    ):
                        try:
                            api_client.update_user(
                                username=user['username'],
                                is_active=new_status
                            )
                            st.success(f"User {status_label.lower()}d successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed: {str(e)}")
                    
                    # Change role
                    new_role = st.selectbox(
                        "Change Role",
                        AVAILABLE_ROLES,
                        index=AVAILABLE_ROLES.index(user['role']) if user['role'] in AVAILABLE_ROLES else 0,
                        key=f"role_{user['username']}"
                    )
                    
                    if new_role != user['role']:
                        if st.button(
                            "💾 Save Role",
                            key=f"save_role_{user['username']}",
                            use_container_width=True
                        ):
                            try:
                                api_client.update_user(
                                    username=user['username'],
                                    role=new_role
                                )
                                st.success(f"Role updated to {new_role}!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed: {str(e)}")
        
        st.markdown("---")
        
        # Create new user
        st.markdown("### ➕ Create New User")
        
        with st.form("create_user_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                new_username = st.text_input("Username")
            
            with col2:
                new_password = st.text_input("Password", type="password")
            
            with col3:
                new_role = st.selectbox("Role", AVAILABLE_ROLES)
            
            submit = st.form_submit_button("✨ Create User", use_container_width=True)
            
            if submit:
                if not new_username or not new_password:
                    st.error("Username and password are required")
                else:
                    try:
                        api_client.create_user(
                            username=new_username,
                            password=new_password,
                            role=new_role
                        )
                        st.success(f"✅ User '{new_username}' created successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to create user: {str(e)}")
    
    except Exception as e:
        st.error(f"Failed to load users: {str(e)}")


def render_audit_logs(api_client: APIClient):
    """Render audit logs section"""
    
    st.subheader("📋 Audit Logs")
    
    # Log type selector
    log_type = st.selectbox(
        "Select Log Type",
        ["Authentication", "Access Control", "RAG Pipeline"],
        key="log_type_select"
    )
    
    limit = st.slider("Number of logs", 10, 200, 50, 10)
    
    if st.button("🔄 Refresh Logs", use_container_width=True):
        st.rerun()
    
    try:
        with st.spinner(f"Loading {log_type} logs..."):
            if log_type == "Authentication":
                logs = api_client.get_auth_logs(limit)
            elif log_type == "Access Control":
                logs = api_client.get_access_logs(limit)
            else:
                logs = api_client.get_rag_logs(limit)
        
        if not logs:
            st.info("No logs found")
            return
        
        st.success(f"✅ Loaded {len(logs)} log entries")
        
        # Display logs
        for log in logs:
            timestamp = log.get('timestamp', 'Unknown')
            event_type = log.get('event_type', 'Unknown')
            
            # Color code by event type
            if 'success' in log and not log['success']:
                color = "#dc3545"
                icon = "❌"
            elif 'allowed' in log and not log['allowed']:
                color = "#ffc107"
                icon = "⚠️"
            else:
                color = "#28a745"
                icon = "✅"
            
            with st.expander(f"{icon} {timestamp} - {event_type}"):
                for key, value in log.items():
                    if key not in ['timestamp', 'event_type']:
                        st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
    
    except Exception as e:
        st.error(f"Failed to load logs: {str(e)}")


def render_user_activity(api_client: APIClient):
    """Render user activity section"""
    
    st.subheader("👁️ User Activity Tracking")
    
    # Username input
    username = st.text_input("Enter username to view activity", key="activity_username")
    
    limit = st.slider("Number of activity logs", 10, 100, 20, 10, key="activity_limit")
    
    if st.button("🔍 Load Activity", use_container_width=True):
        if not username:
            st.error("Please enter a username")
        else:
            try:
                with st.spinner(f"Loading activity for {username}..."):
                    activity = api_client.get_user_activity(username, limit)
                
                st.success(f"✅ Loaded activity for {username}")
                
                # Display activity sections
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🔐 Authentication Activity")
                    auth_logs = activity.get("authentication_logs", [])
                    if auth_logs:
                        for log in auth_logs:
                            status = "✅" if log.get('success', False) else "❌"
                            st.markdown(f"{status} {log.get('action', 'N/A')} - {log.get('timestamp', 'N/A')}")
                    else:
                        st.info("No authentication logs")
                
                with col2:
                    st.markdown("### 🔒 Access Activity")
                    access_logs = activity.get("access_logs", [])
                    if access_logs:
                        for log in access_logs:
                            status = "✅" if log.get('allowed', False) else "❌"
                            st.markdown(f"{status} {log.get('endpoint', 'N/A')} - {log.get('timestamp', 'N/A')}")
                    else:
                        st.info("No access logs")
                
                # RAG activity
                st.markdown("### 🤖 RAG Query Activity")
                rag_logs = activity.get("rag_logs", [])
                if rag_logs:
                    for log in rag_logs:
                        event = log.get('event_type', 'N/A')
                        timestamp = log.get('timestamp', 'N/A')
                        st.markdown(f"📝 {event} - {timestamp}")
                else:
                    st.info("No RAG logs")
            
            except Exception as e:
                st.error(f"Failed to load user activity: {str(e)}")


def render_system_info(api_client: APIClient):
    """Render system information"""
    
    st.subheader("📊 System Information")
    
    try:
        # Health check
        with st.spinner("Checking system health..."):
            health = api_client.health_check()
        
        # Display status
        status = health.get("status", "unknown")
        
        if status == "healthy":
            st.success("✅ System Status: Healthy")
        else:
            st.error("❌ System Status: Issues Detected")
        
        st.markdown("---")
        
        # Components status
        st.markdown("### Component Status")
        
        components = health.get("components", {})
        
        cols = st.columns(len(components))
        
        for i, (component, status) in enumerate(components.items()):
            with cols[i]:
                if status == "operational":
                    st.success(f"✅ {component.replace('_', ' ').title()}")
                else:
                    st.error(f"❌ {component.replace('_', ' ').title()}")
        
        st.markdown("---")
        
        # Pipeline stats
        st.markdown("### Pipeline Statistics")
        
        stats = api_client.get_pipeline_stats()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Chunks", stats.get('total_chunks', 0))
        
        with col2:
            st.metric("Total Embeddings", stats.get('total_embeddings', 0))
        
        with col3:
            st.metric("Similarity Threshold", stats.get('similarity_threshold', 0))
        
        st.markdown("---")
        
        st.markdown("### System Configuration")
        
        llm_provider = stats.get('llm_provider', 'Unknown')
        llm_model = stats.get('llm_model', 'Not configured')
        
        st.markdown(f"**LLM Provider:** {llm_provider}")
        
        if llm_model and llm_model != 'Not configured' and llm_model.lower() != 'unknown':
            st.markdown(f"**LLM Model:** {llm_model}")
        else:
            st.warning("**LLM Model:** Not configured or unavailable")
        
        st.markdown(f"**Timestamp:** {health.get('timestamp', 'Unknown')}")
    
    except Exception as e:
        st.error(f"Failed to load system information: {str(e)}")