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
    OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")
    HF_API_TOKEN = os.getenv("HF_API_TOKEN")
    LLM_PROVIDER = "hf_mistral" # Options: "ollama", "huggingface", "hf_mistral"
    LLM_MODEL = "mistralai/Mistral-7B-Instruct-v0.2" # Options: "mistral", "google/flan-t5-base", "mistralai/Mistral-7B-Instruct-v0.2"
    
    # RAG Settings
    TOP_K_RETRIEVAL = 4
    SIMILARITY_THRESHOLD = 0.3
    MAX_CONTEXT_LENGTH = 2000
    
    # Audit Logging
    AUTH_LOG_FILE = r"D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC/logs/auth_audit.log"
    ACCESS_LOG_FILE = r"D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC/logs/access_audit.log"
    RAG_LOG_FILE = r"D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC/logs/rag_audit.log"

    # DEFAULT_USERS = os.getenv("DEFAULT_USERS",[])