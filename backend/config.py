import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # JWT Settings
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 15
    REFRESH_TOKEN_EXPIRE_DAYS = 7

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Vector DB
    VECTOR_DB_PATH = r"D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC/data/vector_db"
    EMBEDDINGS_PATH = r"D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC/data/chunk_embeddings.npy"
    CHUNKS_PATH = r"D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC/data/all_chunks.json"
    METADATA_PATH = r"D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC/data/all_metadata.json"
    ABBREVIATIONS_PATH = r"D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC/data/ABBREVIATIONS.json"
    RBAC_PERMISSIONS_PATH = r"D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC/data/rbac_permissions.json"
    
    # Embedding Model
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    
    # LLM Settings (Using HuggingFace free API)
    LLM_PROVIDER = "ollama" 
    OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")
    OLLAMA_MODEL = "mistral"
    
    # RAG Settings
    TOP_K_RETRIEVAL = 5
    SIMILARITY_THRESHOLD = 0.3
    MAX_CONTEXT_LENGTH = 2000
    
    # Audit Logging
    AUTH_LOG_FILE = r"D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC/logs/auth_audit.log"
    ACCESS_LOG_FILE = r"D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC/logs/access_audit.log"
    RAG_LOG_FILE = r"D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC/logs/rag_audit.log"

    DEFALUT_USERS = [
            {
                "username": "intern_user",
                "password": "intern123",
                "role": "Intern"
            },
            {
                "username": "finance_user",
                "password": "finance123",
                "role": "Finance Analyst"
            },
            {
                "username": "hr_user",
                "password": "hr123",
                "role": "HR Manager"
            },
            {
                "username": "engineering_user",
                "password": "eng123",
                "role": "Engineering Lead"
            },
            {
                "username": "manager_user",
                "password": "manager123",
                "role": "Manager"
            },
            {
                "username": "admin_user",
                "password": "admin123",
                "role": "Admin"
            }
        ]
