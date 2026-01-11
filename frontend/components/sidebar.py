import streamlit as st
from utils.api_client import APIClient
from utils.session_manager import SessionManager
from config.settings import MAX_TOP_K, MAX_TOKENS_LIMIT
import time


def render_sidebar(api_client: APIClient, is_admin: bool):
    """Render sidebar with user info and settings"""

    user_info = st.session_state.user_info

    def get_initials(name: str) -> str:
        parts = name.strip().split()
        if len(parts) == 1:
            return parts[0][0].upper()
        return (parts[0][0] + parts[-1][0]).upper()

    initials = get_initials(user_info["username"])

    with st.sidebar:
        st.markdown("## My Profile")
        
        # Enhanced user info card with better styling
        st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, #0ea5e9 0%, #22c55e 100%);
                padding: 1.2rem;
                border-radius: 14px;
                color: black;
                margin-bottom: 0.6rem;
                box-shadow: 0 6px 14px rgba(0,0,0,0.25);
            '>
                <div style='display: flex; align-items: center; margin-bottom: 0.8rem;'>
                    <div style='
                        background: rgba(0,0,0,0.25);
                        width: 48px;
                        height: 48px;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 24px;
                        margin-right: 12px;                        
                        font-weight: 700;
                        letter-spacing: 1px;
                    '>
                        {initials}
                    </div>
                    <div>
                        <div style='font-size: 1.3rem; font-weight: 600; margin-bottom: 0.2rem;'>
                            {user_info['username']}
                        </div>
                        <div style='font-size: 0.85rem; opacity: 0.9; background: rgba(255,255,255,0.2); padding: 0.15rem 0.6rem; border-radius: 12px; display: inline-block;'>
                            {user_info['role'].replace('_', ' ').title()}
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Logout directly under profile
        if st.button("Logout", use_container_width=True, type="primary"):
            try:
                api_client.logout()
            except:
                pass
            SessionManager.logout()
            st.success("Logged out successfully!")
            time.sleep(0.5)
            st.rerun()
        
        # Session info
        session_duration = SessionManager.get_session_duration()
        if session_duration:
            minutes = session_duration // 60
            seconds = session_duration % 60
            st.caption(f"⏱️ Session: {minutes}m {seconds}s")
        
        # Accessible departments - compact representation
        accessible_depts = user_info.get('accessible_departments', [])
        if accessible_depts:
            dept_count = len(accessible_depts)
            dept_preview = ", ".join(accessible_depts[:2])
            if dept_count > 2:
                dept_preview += f" +{dept_count - 2} more"
            
            st.markdown(f"""
                <div style="
                    background: #f8fafc;
                    padding: 1rem;
                    border-radius: 10px;
                    margin-bottom: 1rem;
                    border-left: 4px solid #667eea;
                    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
                ">
                    <div style="
                        font-size: 0.7rem;
                        letter-spacing: 0.08em;
                        color: #4b5563;
                        margin-bottom: 0.35rem;
                        font-weight: 600;
                    ">
                        📁 ACCESSIBLE DEPARTMENTS
                    </div>
                    <div style="
                        font-size: 0.95rem;
                        font-weight: 500;
                        color: #1f2937;
                        line-height: 1.5;
                    ">
                        {dept_preview}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Expandable full list if more than 2
            if dept_count > 2:
                with st.expander("View all departments"):
                    for dept in accessible_depts:
                        st.markdown(f"• {dept.title()}")
        else:
            st.warning("⚠️ No accessible departments")
        
        
        if SessionManager.is_admin():
            st.markdown("")
            st.markdown("### 🔧 Admin Controls")
            
            # Navigation between admin panel and chat
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("💬 Chat", use_container_width=True, 
                            type="secondary" if st.session_state.get("admin_view") else "primary"):
                    st.session_state.admin_view = None
                    st.rerun()
            
            with col2:
                if st.button("🔧 Admin", use_container_width=True,
                            type="primary" if st.session_state.get("admin_view") else "secondary"):
                    st.session_state.admin_view = "users"
                    st.rerun()
                    
            # View Stats (Admin only)
            if st.button("📊 View Pipeline Stats", use_container_width=True):
                try:
                    with st.spinner("Loading stats..."):
                        stats = api_client.get_pipeline_stats()
                    
                    st.markdown("### 📈 Pipeline Statistics")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Chunks", stats.get('total_chunks', 0))
                    with col2:
                        st.metric("Embeddings", stats.get('total_embeddings', 0))
                    
                    st.markdown(f"**Similarity Threshold:** {stats.get('similarity_threshold', 0)}")
                    
                    # Show LLM info properly
                    llm_model = stats.get('llm_model', 'Unknown')
                    llm_provider = stats.get('llm_provider', 'Unknown')
                    if llm_model and llm_model != 'Unknown':
                        st.markdown(f"**LLM Provider:** {llm_provider}")
                        st.markdown(f"**LLM Model:** {llm_model}")
                    else:
                        st.markdown(f"**LLM Provider:** {llm_provider}")
                        st.markdown("**LLM Model:** Not configured")
                    
                except Exception as e:
                    st.error(f"Failed to load stats: {str(e)}")    
        
        st.markdown("")
        
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
            step=50,
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
        
        st.markdown("")
        
        # Actions
        st.markdown("### 🎯 Actions")
        
        # Clear chat
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            SessionManager.clear_chat()
            st.success("Chat cleared!")
            time.sleep(0.5)
            st.rerun()
        
        # Refresh token if needed
        if api_client.is_token_expiring_soon():
            with st.spinner("Refreshing session..."):
                if api_client.refresh_access_token():
                    st.success("✅ Session refreshed")
                else:
                    st.warning("⚠️ Please login again")
