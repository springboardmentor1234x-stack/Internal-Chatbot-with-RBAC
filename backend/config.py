import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # JWT Settings
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 15
    REFRESH_TOKEN_EXPIRE_DAYS = 7

    HF_API_TOKEN = os.getenv("HF_API_TOKEN")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Database
    DATABASE_URL = "sqlite:///./database/users.db"
    
    # Vector DB
    VECTOR_DB_PATH = r"D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC-Project/data/vector_db"
    EMBEDDINGS_PATH = r"D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC-Project/data/chunk_embeddings.npy"
    CHUNKS_PATH = r"D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC-Project/data/all_chunks.json"
    METADATA_PATH = r"D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC-Project/data/all_metadata.json"
    ABBREVIATIONS_PATH = r"D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC-Project/data/ABBREVIATIONS.json"
    RBAC_PERMISSIONS_PATH = r"D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC-Project/data/rbac_permissions.json"
    
    # Embedding Model
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    
    # LLM Settings (Using HuggingFace free API)
    LLM_PROVIDER = "huggingface"  # or "openai"
    HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
    
    # RAG Settings
    TOP_K_RETRIEVAL = 5
    SIMILARITY_THRESHOLD = 0.3
    MAX_CONTEXT_LENGTH = 2000
    
    # Audit Logging
    AUTH_LOG_FILE = r"D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC-Project/logs/auth_audit.log"
    ACCESS_LOG_FILE = r"D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC-Project/logs/access_audit.log"
    RAG_LOG_FILE = r"D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC-Project/logs/rag_audit.log"

    DEFALUT_USERS = [
            {
                "username": "intern_user",
                "password": "intern123",
                "role": "intern"
            },
            {
                "username": "finance_user",
                "password": "finance123",
                "role": "finance_analyst"
            },
            {
                "username": "hr_user",
                "password": "hr123",
                "role": "hr_manager"
            },
            {
                "username": "engineering_user",
                "password": "eng123",
                "role": "engineering_lead"
            },
            {
                "username": "manager_user",
                "password": "manager123",
                "role": "manager"
            },
            {
                "username": "admin_user",
                "password": "admin123",
                "role": "admin"
            }
        ]
