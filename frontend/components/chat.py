"""
Modern chat interface with AI response and source citations
"""

import streamlit as st
from utils.api_client import APIClient
from utils.session_manager import SessionManager
from config.settings import WELCOME_MESSAGE
import time

def render_chat_header():
    """Render chat header with title and info"""
    st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h1>💬 AI Assistant</h1>
            <p style='color: #666;'>Ask questions about company documents and policies</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")


def render_message_with_sources(message: dict):
    """Render a single message with sources"""
    
    role = message["role"]
    content = message["content"]
    
    if role == "user":
        # User message
        with st.chat_message("user", avatar="👤"):
            st.markdown(content)
    
    else:
        # Assistant message
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(content)
            
            # Show confidence if available
            if st.session_state.show_confidence and "confidence" in message:
                confidence = message["confidence"]
                confidence_score = message.get("confidence_score", 0)
                
                # Color code confidence
                if confidence_score >= 0.7:
                    color = "#28a745"  # Green
                    icon = "🟢"
                elif confidence_score >= 0.5:
                    color = "#ffc107"  # Yellow
                    icon = "🟡"
                else:
                    color = "#dc3545"  # Red
                    icon = "🔴"
                
                st.markdown(f"""
                    <div style='
                        background-color: {color}15;
                        border-left: 3px solid {color};
                        padding: 0.5rem 1rem;
                        margin-top: 1rem;
                        border-radius: 5px;
                    '>
                        {icon} <strong>Confidence:</strong> {confidence} ({confidence_score:.2%})
                    </div>z
                """, unsafe_allow_html=True)
            
            # Show sources if available
            if st.session_state.show_sources and "sources" in message and message["sources"]:
                with st.expander("📚 View Source Citations", expanded=False):
                    sources = message["sources"]
                    
                    for i, source in enumerate(sources, 1):
                        st.markdown(f"""
                            <div style='
                                background-color: #0f172a;
                                padding: 1rem;
                                margin-bottom: 0.5rem;
                                border-radius: 8px;
                                border-left: 4px solid #667eea;
                            '>
                                <strong>Source {i}</strong><br>
                                <small>
                                    📄 <strong>Document:</strong> {source.get('document', 'Unknown')}<br>
                                    🏢 <strong>Department:</strong> {source.get('department', 'Unknown')}<br>
                                    📊 <strong>Similarity:</strong> {source.get('similarity', 0):.2%}<br>
                                    🔗 <strong>Chunk ID:</strong> <code>{source.get('chunk_id', 'unknown')}</code>
                                </small>
                                <hr style='margin: 0.5rem 0;'>
                                <small><em>"{source.get('excerpt', 'No excerpt available')}"</em></small>
                            </div>
                        """, unsafe_allow_html=True)
            
            # Show model info
            if "model" in message:
                st.caption(f"🤖 Model: {message['model']}")
            
            # Show error if present
            if "error" in message:
                st.warning(f"⚠️ Note: {message['error']}")


def render_thinking_animation():
    """Show animated thinking indicator"""
    thinking_placeholder = st.empty()
    
    messages = [
        "🔍 Searching documents...",
        "📖 Reading content...",
        "🧠 Analyzing information...",
        "✍️ Generating response..."
    ]
    
    for msg in messages:
        thinking_placeholder.info(msg)
        time.sleep(0.5)
    
    thinking_placeholder.empty()


def render_chat(api_client: APIClient):
    """Render main chat interface"""
    
    # Header
    render_chat_header()
    
    # Welcome message for new chat
    if len(st.session_state.messages) == 0:
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(WELCOME_MESSAGE)
    
    # Display chat history
    for message in st.session_state.messages:
        render_message_with_sources(message)
    
    # Chat input
    if prompt := st.chat_input(
        "💭 Ask a question about company documents...",
        key="chat_input"
    ):
        # Add user message
        SessionManager.add_message("user", prompt)
        
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        
        # Generate assistant response
        with st.chat_message("assistant", avatar="🤖"):
            # Show thinking animation
            with st.spinner("🤔 Thinking..."):
                try:
                    # Call API
                    response = api_client.chat_query(
                        query=prompt,
                        top_k=st.session_state.top_k,
                        max_tokens=st.session_state.max_tokens
                    )
                    
                    # Extract response data
                    answer = response.get("answer", "Sorry, I couldn't generate a response.")
                    sources = response.get("sources", [])
                    confidence = response.get("confidence", "N/A")
                    confidence_score = response.get("confidence_score", 0.0)
                    model = response.get("model", "Unknown")
                    error = response.get("error")
                    
                    # Display answer
                    st.markdown(answer)
                    
                    # Show confidence
                    if st.session_state.show_confidence:
                        if confidence_score >= 0.7:
                            color = "#28a745"
                            icon = "🟢"
                        elif confidence_score >= 0.5:
                            color = "#ffc107"
                            icon = "🟡"
                        else:
                            color = "#dc3545"
                            icon = "🔴"
                        
                        st.markdown(f"""
                            <div style='
                                background-color: {color}15;
                                border-left: 3px solid {color};
                                padding: 0.5rem 1rem;
                                margin-top: 1rem;
                                border-radius: 5px;
                            '>
                                {icon} <strong>Confidence:</strong> {confidence} ({confidence_score:.2%})
                            </div>
                        """, unsafe_allow_html=True)
                    
                    # Show sources
                    if st.session_state.show_sources and sources:
                        with st.expander("📚 View Source Citations", expanded=False):
                            for i, source in enumerate(sources, 1):
                                st.markdown(f"""
                                    <div style='
                                        background-color: #0f172a;
                                        padding: 1rem;
                                        margin-bottom: 0.5rem;
                                        border-radius: 8px;
                                        border-left: 4px solid #667eea;
                                    '>
                                        <strong>Source {i}</strong><br>
                                        <small>
                                            📄 <strong>Document:</strong> {source.get('document', 'Unknown')}<br>
                                            🏢 <strong>Department:</strong> {source.get('department', 'Unknown')}<br>
                                            📊 <strong>Similarity:</strong> {source.get('similarity', 0):.2%}<br>
                                            🔗 <strong>Chunk ID:</strong> <code>{source.get('chunk_id', 'unknown')}</code>
                                        </small>
                                        <hr style='margin: 0.5rem 0;'>
                                        <small><em>"{source.get('excerpt', 'No excerpt available')}"</em></small>
                                    </div>
                                """, unsafe_allow_html=True)
                    
                    # Show model info
                    st.caption(f"🤖 Model: {model}")
                    
                    # Show error if present
                    if error:
                        st.warning(f"⚠️ Note: {error}")
                    
                    # Add to chat history
                    SessionManager.add_message(
                        "assistant",
                        answer,
                        sources=sources,
                        confidence=confidence,
                        confidence_score=confidence_score,
                        model=model,
                        error=error
                    )
                
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    
                    SessionManager.add_message(
                        "assistant",
                        error_msg,
                        sources=[],
                        error=str(e)
                    )
    
    # Show typing indicator at bottom
    st.markdown("<br>", unsafe_allow_html=True)