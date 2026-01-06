"""
Sidebar component with user info and settings
"""

import streamlit as st
from utils.api_client import APIClient
from utils.session_manager import SessionManager
from config.settings import DEFAULT_TOP_K, MAX_TOP_K, DEFAULT_MAX_TOKENS, MAX_TOKENS_LIMIT
import time

def render_sidebar(api_client: APIClient):
    """Render sidebar with user info and settings"""
    
    user_info = st.session_state.user_info
    
    with st.sidebar:
        # User Profile Section
        st.markdown("### 👤 User Profile")
        
        # User info card
        st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 1.5rem;
                border-radius: 10px;
                color: white;
                margin-bottom: 1rem;
            '>
                <h3 style='margin: 0; color: white;'>
                    {user_info['username']}
                </h3>
                <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>
                    Role: <strong>{user_info['role']}</strong>
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Accessible departments
        accessible_depts = user_info.get('accessible_departments', [])
        if accessible_depts:
            st.markdown("**📁 Accessible Departments:**")
            for dept in accessible_depts:
                st.markdown(f"- {dept.title()}")
        else:
            st.warning("⚠️ No accessible departments")
        
        # Session info
        session_duration = SessionManager.get_session_duration()
        if session_duration:
            minutes = session_duration // 60
            seconds = session_duration % 60
            st.caption(f"⏱️ Session: {minutes}m {seconds}s")
        
        st.markdown("---")
        
        # Search Settings
        st.markdown("### ⚙️ Search Settings")
        
        top_k = st.slider(
            "Number of documents",
            min_value=1,
            max_value=MAX_TOP_K,
            value=st.session_state.top_k,
            help="Number of relevant documents to retrieve"
        )
        
        max_tokens = st.slider(
            "Max response length",
            min_value=100,
            max_value=MAX_TOKENS_LIMIT,
            value=st.session_state.max_tokens,
            step=100,
            help="Maximum tokens for AI response"
        )
        
        # Update settings
        SessionManager.update_settings(top_k=top_k, max_tokens=max_tokens)
        
        # Display options
        st.markdown("### 🎨 Display Options")
        
        show_sources = st.checkbox(
            "Show source citations",
            value=st.session_state.show_sources,
            help="Display document sources in responses"
        )
        st.session_state.show_sources = show_sources
        
        show_confidence = st.checkbox(
            "Show confidence scores",
            value=st.session_state.show_confidence,
            help="Display confidence levels"
        )
        st.session_state.show_confidence = show_confidence
        
        st.markdown("---")
        
        # Actions
        st.markdown("### 🎯 Actions")
        
        # Clear chat
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            SessionManager.clear_chat()
            st.success("Chat cleared!")
            time.sleep(0.5)
            st.rerun()
        
        # View stats
        if st.button("📊 View Stats", use_container_width=True):
            try:
                with st.spinner("Loading stats..."):
                    stats = api_client.get_pipeline_stats()
                
                st.markdown("---")
                st.markdown("### 📈 Pipeline Statistics")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Chunks", stats.get('total_chunks', 0))
                with col2:
                    st.metric("Embeddings", stats.get('total_embeddings', 0))
                
                st.markdown(f"**Similarity Threshold:** {stats.get('similarity_threshold', 0)}")
                st.markdown(f"**LLM Model:** {stats.get('llm_model', 'Unknown')}")
                
            except Exception as e:
                st.error(f"Failed to load stats: {str(e)}")
        
        # Refresh token if needed
        if api_client.is_token_expiring_soon():
            with st.spinner("Refreshing session..."):
                if api_client.refresh_access_token():
                    st.success("✅ Session refreshed")
                else:
                    st.warning("⚠️ Please login again")
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True, type="primary"):
            try:
                api_client.logout()
            except:
                pass  # Logout locally anyway
            
            SessionManager.logout()
            st.success("Logged out successfully!")
            time.sleep(0.5)
            st.rerun()
        
        # Footer
        st.markdown("---")
        st.caption("🔒 Secure Session")
        st.caption("📝 All activity is logged")


def render_admin_sidebar(api_client: APIClient):
    """Render admin-specific sidebar options"""
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🔧 Admin Controls")
        
        admin_section = st.selectbox(
            "Admin Section",
            ["Users", "Logs", "System"],
            key="admin_section_select"
        )
        st.session_state.admin_view = admin_section.lower()
        
        if st.button("🔄 Refresh Admin Data", use_container_width=True):
            st.rerun()