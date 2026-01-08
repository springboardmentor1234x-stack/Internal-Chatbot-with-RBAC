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
        # User message with custom styling (right-aligned with different color)
        st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 1rem;
                border-radius: 12px;
                margin: 0.5rem 0 0.5rem auto;
                max-width: 80%;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            '>
                <div style='display: flex; align-items: flex-start; justify-content: flex-end;'>
                    <div style='margin-right: 0.5rem; text-align: right;'>
                        {content}
                    </div>
                    <div style='font-size: 1.5rem;'>👤</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    else:
        # Assistant message (left-aligned with different styling)
        st.markdown(f"""
            <div style='
                background: #0f172a;
                color: #e2e8f0;
                padding: 1rem;
                border-radius: 12px;
                margin: 0.5rem auto 0.5rem 0;
                max-width: 85%;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                border-left: 4px solid #667eea;
            '>
                <div style='display: flex; align-items: flex-start;'>
                    <div style='font-size: 1.5rem; margin-right: 0.5rem;'>🤖</div>
                    <div style='flex: 1;'>
                        {content}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Show confidence if available
        if st.session_state.show_confidence and "confidence" in message:
            confidence = message["confidence"]
            confidence_score = message.get("confidence_score", 0)
            
            # Color code confidence
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
                    margin: 0.5rem 0;
                    border-radius: 5px;
                    max-width: 85%;
                '>
                    {icon} <strong>Confidence:</strong> {confidence} ({confidence_score:.2%})
                </div>
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
        
        # Show model info if available
        if "model" in message and message["model"]:
            model_name = message["model"]
            if model_name and model_name.lower() != 'unknown':
                st.caption(f"🤖 Model: {model_name}")
        
        # Show error if present
        if "error" in message and message["error"]:
            st.warning(f"⚠️ Note: {message['error']}")


def render_chat(api_client: APIClient):
    """Render main chat interface"""
    
    # Header
    render_chat_header()
    
    # Welcome message for new chat
    if len(st.session_state.messages) == 0:
        st.markdown(f"""
            <div style='
                background: #0f172a;
                color: #e2e8f0;
                padding: 1.5rem;
                border-radius: 12px;
                margin: 1rem 0;
                border-left: 4px solid #667eea;
            '>
                <div style='display: flex; align-items: flex-start;'>
                    <div style='font-size: 2rem; margin-right: 1rem;'>🤖</div>
                    <div>
                        {WELCOME_MESSAGE.replace(chr(10), '<br>')}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
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
        render_message_with_sources({
            "role": "user",
            "content": prompt
        })
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
                model = response.get("model")
                error = response.get("error")
                
                # Display answer
                render_message_with_sources({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                    "confidence": confidence,
                    "confidence_score": confidence_score,
                    "model": model,
                    "error": error
                })
                
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
                st.markdown(f"""
                    <div style="
                        background: rgba(234,179,8,0.15);
                        padding: 1rem;
                        border-radius: 8px;
                        border-left: 4px solid #eab308;
                    ">
                    {"Sorry, there was an error processing your request."}
                    </div>
                    """, unsafe_allow_html=True)
                
                SessionManager.add_message(
                    "assistant",
                    "Sorry, there was an error processing your request.",
                    sources=[],
                    error=str(e)
                )
        
    # Show typing indicator at bottom
    st.markdown("<br>", unsafe_allow_html=True)