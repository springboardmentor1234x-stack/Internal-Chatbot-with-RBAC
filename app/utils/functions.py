def format_chat_response(username, role, message, sources=None):
    """
    Formats the chatbot response based on the user's role.
    This helps the UI display the 'Internal Chatbot' content.
    """
    return {
        "username": username,
        "role": role,
        "content": f"[{role.upper()}] Response: {message}",
        "sources": sources or [],
        "status": "success"
    }