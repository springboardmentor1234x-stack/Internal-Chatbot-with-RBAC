"""
LLM Configuration
Supports multiple LLM providers with fallback mechanism
"""

import os
from enum import Enum
from typing import Optional


class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    HUGGINGFACE = "huggingface"
    LOCAL = "local"


class LLMConfig:
    """LLM configuration with multi-provider support"""
    
    # Provider selection (priority order)
    PROVIDER_PRIORITY = [
        LLMProvider.OPENAI,
        LLMProvider.HUGGINGFACE,
        LLMProvider.LOCAL
    ]
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "500"))
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    
    # HuggingFace Configuration
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
    HUGGINGFACE_MODEL = os.getenv("HUGGINGFACE_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")
    HUGGINGFACE_MAX_TOKENS = int(os.getenv("HUGGINGFACE_MAX_TOKENS", "500"))
    HUGGINGFACE_TEMPERATURE = float(os.getenv("HUGGINGFACE_TEMPERATURE", "0.7"))
    
    # Local Model Configuration
    LOCAL_MODEL_PATH = os.getenv("LOCAL_MODEL_PATH", "")
    LOCAL_MODEL_NAME = os.getenv("LOCAL_MODEL_NAME", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
    LOCAL_MAX_TOKENS = int(os.getenv("LOCAL_MAX_TOKENS", "500"))
    LOCAL_TEMPERATURE = float(os.getenv("LOCAL_TEMPERATURE", "0.7"))
    
    # RAG Configuration
    MAX_CONTEXT_CHUNKS = int(os.getenv("MAX_CONTEXT_CHUNKS", "5"))
    RELEVANCE_THRESHOLD = float(os.getenv("RELEVANCE_THRESHOLD", "0.3"))
    CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))
    
    # Re-ranking Configuration
    RERANK_MODEL = os.getenv("RERANK_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
    ENABLE_RERANKING = os.getenv("ENABLE_RERANKING", "true").lower() == "true"
    
    # Response Configuration
    ENABLE_CITATIONS = os.getenv("ENABLE_CITATIONS", "true").lower() == "true"
    ENABLE_CONFIDENCE_SCORE = os.getenv("ENABLE_CONFIDENCE_SCORE", "true").lower() == "true"
    
    @classmethod
    def get_available_provider(cls) -> Optional[LLMProvider]:
        """Get the first available LLM provider based on configuration"""
        
        # Check HuggingFace (preferred for this project)
        if cls.HUGGINGFACE_API_KEY or cls.HUGGINGFACE_MODEL:
            return LLMProvider.HUGGINGFACE
        
        # Check OpenAI
        if cls.OPENAI_API_KEY:
            return LLMProvider.OPENAI
        
        # Default to local (always available, no API key needed)
        return LLMProvider.LOCAL
    
    @classmethod
    def validate_config(cls) -> dict:
        """Validate configuration and return status"""
        status = {
            "openai": bool(cls.OPENAI_API_KEY),
            "huggingface": bool(cls.HUGGINGFACE_API_KEY) or bool(cls.HUGGINGFACE_MODEL),
            "local": True,  # Always available
            "selected_provider": cls.get_available_provider().value if cls.get_available_provider() else None
        }
        return status


# Environment file template
ENV_TEMPLATE = """
# OpenAI Configuration (Recommended for best quality)
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=500
OPENAI_TEMPERATURE=0.7

# HuggingFace Configuration (Free alternative)
HUGGINGFACE_API_KEY=your-huggingface-token-here
HUGGINGFACE_MODEL=mistralai/Mistral-7B-Instruct-v0.2
HUGGINGFACE_MAX_TOKENS=500
HUGGINGFACE_TEMPERATURE=0.7

# Local Model Configuration (No API key needed)
LOCAL_MODEL_NAME=TinyLlama/TinyLlama-1.1B-Chat-v1.0
LOCAL_MAX_TOKENS=500
LOCAL_TEMPERATURE=0.7

# RAG Configuration
MAX_CONTEXT_CHUNKS=5
RELEVANCE_THRESHOLD=0.3
CONFIDENCE_THRESHOLD=0.5

# Re-ranking Configuration
RERANK_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2
ENABLE_RERANKING=true

# Response Configuration
ENABLE_CITATIONS=true
ENABLE_CONFIDENCE_SCORE=true
"""


if __name__ == "__main__":
    # Validate configuration
    print("🔧 LLM Configuration Status:")
    print("=" * 50)
    
    status = LLMConfig.validate_config()
    for provider, available in status.items():
        icon = "✅" if available else "❌"
        print(f"{icon} {provider}: {'Available' if available else 'Not configured'}")
    
    print("\n📍 Selected Provider:", status.get("selected_provider", "None"))
    
    if not status.get("selected_provider"):
        print("\n⚠️  No LLM provider configured!")
        print("Create a .env file with one of the following:")
        print(ENV_TEMPLATE)
