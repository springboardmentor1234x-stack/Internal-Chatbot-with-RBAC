"""
Configuration settings for Streamlit application
"""

# API Configuration
API_BASE_URL = "http://localhost:8000"
REQUEST_TIMEOUT = 30

# UI Configuration
APP_TITLE = "Company Internal RAG Chatbot"
APP_ICON = "🤖"
PAGE_LAYOUT = "wide"

# Theme Configuration
PRIMARY_COLOR = "#FF4B4B"
BACKGROUND_COLOR = "#FFFFFF"
SECONDARY_BACKGROUND_COLOR = "#F0F2F6"
TEXT_COLOR = "#262730"

# Chat Configuration
DEFAULT_TOP_K = 5
MAX_TOP_K = 20
DEFAULT_MAX_TOKENS = 256
MAX_TOKENS_LIMIT = 500

# Session Configuration
AUTO_REFRESH_TOKEN_THRESHOLD = 120  # seconds
SESSION_TIMEOUT_WARNING = 60  # seconds

# Admin Configuration
AVAILABLE_ROLES = [
    "admin",
    "manager",
    "finance_analyst",
    "hr_manager",
    "engineering_lead",
    "marketing_manager",
    "intern"
]

# UI Messages
WELCOME_MESSAGE = """
👋 Welcome to the Company Internal RAG Chatbot!

I can help you find information from company documents based on your role and department access.

How to use:
- Type your question in the chat input below
- I'll search through accessible documents and provide an answer
- Sources will be cited for transparency
- You can adjust search parameters in the sidebar

Privacy: Your queries and the documents you can access are determined by your role.
"""

ERROR_MESSAGES = {
    "connection_error": "❌ Cannot connect to the backend server. Please contact IT support.",
    "auth_error": "❌ Authentication failed. Please check your credentials.",
    "session_expired": "⏰ Your session has expired. Please login again.",
    "permission_denied": "🚫 You don't have permission to access this resource.",
    "server_error": "⚠️ An error occurred on the server. Please try again later."
}