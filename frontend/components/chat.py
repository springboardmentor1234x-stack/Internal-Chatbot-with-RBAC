import streamlit as st
from utils.api_client import APIClient

def render_chat(api_client: APIClient):
    """Render chat interface"""
    user_info = st.session_state.user_info
    
    # Header with user info
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.title("💬 Company Chatbot")
    with col2:
        st.info(f"**Role:** {user_info['role']}")
    with col3:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.messages = []
            st.rerun()
    
    st.markdown(f"**User:** {user_info['username']} | **Department:** {user_info['department']}")
    st.markdown("---")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            if message["role"] == "assistant" and "sources" in message:
                with st.expander("📚 View Sources"):
                    for i, source in enumerate(message["sources"], 1):
                        st.markdown(f"""
                        **Source {i}:** `{source['chunk_id']}`  
                        **Document:** {source['document']}  
                        **Department:** {source['department']}  
                        **Similarity:** {source['similarity']}  
                        **Excerpt:** {source['excerpt']}
                        """)
                        st.markdown("---")
                
                if "confidence" in message:
                    st.caption(f"🎯 Confidence: {message['confidence']}")
    
    # Chat input
    if prompt := st.chat_input("Ask a question about company information..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = api_client.send_message(prompt)
                    
                    answer = response["answer"]
                    sources = response.get("sources", [])
                    confidence = response.get("confidence", "N/A")
                    
                    st.markdown(answer)
                    
                    # Show sources
                    if sources:
                        with st.expander("📚 View Sources"):
                            for i, source in enumerate(sources, 1):
                                st.markdown(f"""
                                **Source {i}:** `{source['chunk_id']}`  
                                **Document:** {source['document']}  
                                **Department:** {source['department']}  
                                **Similarity:** {source['similarity']}  
                                **Excerpt:** {source['excerpt']}
                                """)
                                st.markdown("---")
                    
                    st.caption(f"🎯 Confidence: {confidence}")
                    
                    # Add to message history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                        "confidence": confidence
                    })
                
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "sources": []
                    })