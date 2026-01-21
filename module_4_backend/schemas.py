"""
Pydantic Schemas
Request/Response models for API validation
"""

from pydantic import BaseModel, validator, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from models import VALID_ROLES


# ============= Authentication Schemas =============

class UserLogin(BaseModel):
    """Login request schema"""
    username: str
    password: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenResponse(BaseModel):
    """Enhanced token response with user info"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    role: str


class TokenData(BaseModel):
    """Token payload data"""
    username: str
    role: str
    type: str  # "access" or "refresh"


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


# Alias for backward compatibility
TokenRefresh = RefreshTokenRequest


# ============= User Schemas =============

class UserCreate(BaseModel):
    """User creation schema"""
    username: str
    email: EmailStr
    password: str
    role: str
    
    @validator('role')
    def validate_role(cls, v):
        if v not in VALID_ROLES:
            raise ValueError(f"Invalid role. Must be one of: {', '.join(VALID_ROLES)}")
        return v


class UserResponse(BaseModel):
    """User response schema"""
    id: int
    username: str
    role: str
    is_active: bool
    
    class Config:
        from_attributes = True


# ============= RAG Query Schemas =============

class RAGQuery(BaseModel):
    """RAG query request"""
    query: str
    top_k: Optional[int] = 5


# Alias for backward compatibility
RAGQueryRequest = RAGQuery


class SourceInfo(BaseModel):
    """Source information for RAG response"""
    source_id: str
    document_name: str
    department: str
    chunk_index: int
    relevance_score: float
    content_preview: str


class ChunkResult(BaseModel):
    """Single chunk result with source attribution"""
    chunk_id: str
    text: str
    score: float
    department: str
    source_file: str


class RAGResponse(BaseModel):
    """RAG response with answer and sources"""
    query: str
    processed_query: str
    answer: str
    sources: List[SourceInfo]
    metadata: Dict[str, Any]


# Alias for backward compatibility
RAGQueryResponse = RAGResponse


# ============= Advanced RAG Schemas (Module 5) =============

class ConfidenceMetrics(BaseModel):
    """Confidence scoring metrics for RAG response"""
    overall_confidence: float
    retrieval_quality: float
    citation_coverage: float
    answer_completeness: float
    confidence_level: str  # "high", "medium", "low"


class AdvancedRAGResponse(BaseModel):
    """Enhanced RAG response with confidence scoring and LLM generation"""
    query: str
    processed_query: str
    answer: str
    sources: List[SourceInfo]
    confidence: ConfidenceMetrics
    metadata: Dict[str, Any]


# ============= User Statistics Schemas =============

class UserStatsResponse(BaseModel):
    """User statistics and query history"""
    user_id: int
    username: str
    role: str
    total_queries: int
    permissions: List[str]
    accessible_departments: List[str]  # Added for frontend display
    recent_queries: List[Dict[str, Any]]
    account_created: Optional[str]
    last_login: Optional[str]


# ============= Model Configuration Schemas =============

class ModelConfigRequest(BaseModel):
    """Model configuration request"""
    model_provider: str  # "openai", "huggingface", "ollama"
    api_key: Optional[str] = None  # Required for OpenAI and HuggingFace
    model_name: Optional[str] = None  # Specific model to use
    
    @validator('model_provider')
    def validate_provider(cls, v):
        valid_providers = ['openai', 'huggingface', 'ollama']
        if v.lower() not in valid_providers:
            raise ValueError(f"Provider must be one of {valid_providers}")
        return v.lower()


class ModelConfigResponse(BaseModel):
    """Model configuration response"""
    success: bool
    message: str
    provider: str
    model_name: Optional[str] = None


# ============= Conversation Schemas =============

class ChatMessageCreate(BaseModel):
    """Create a new chat message"""
    role: str  # 'user' or 'assistant'
    content: str
    sources: Optional[List[Dict[str, Any]]] = None
    confidence: Optional[Dict[str, Any]] = None


class ChatMessageResponse(BaseModel):
    """Chat message response"""
    id: int
    role: str
    content: str
    sources: Optional[List[Dict[str, Any]]] = None
    confidence: Optional[Dict[str, Any]] = None
    timestamp: str
    
    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    """Create a new conversation"""
    title: Optional[str] = "New Chat"


class ConversationResponse(BaseModel):
    """Conversation response"""
    id: int
    title: str
    created_at: str
    updated_at: str
    message_count: int = 0
    
    class Config:
        from_attributes = True


class ConversationDetailResponse(BaseModel):
    """Conversation detail with messages"""
    id: int
    title: str
    created_at: str
    updated_at: str
    messages: List[ChatMessageResponse]
    
    class Config:
        from_attributes = True


class ConversationUpdateTitle(BaseModel):
    """Update conversation title"""
    title: str
