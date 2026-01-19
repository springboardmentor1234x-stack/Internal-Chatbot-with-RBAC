from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

# ==================== AUTHENTICATION MODELS ====================

class LoginRequest(BaseModel):
    username: str = Field(..., description="Username", min_length=3, max_length=50)
    password: str = Field(..., description="Password", min_length=6)
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "demo_user",
                    "password": "Demo@123"
                }
            ]
        }
    }

class LoginResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiry in seconds")
    user_info: Dict[str, Any] = Field(..., description="User information")

class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="JWT refresh token")

class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiry in seconds")

class UserInfo(BaseModel):
    username: str
    role: str
    user_id: int
    accessible_departments: List[str] = []

# ==================== RAG QUERY MODELS ====================

class RAGQueryRequest(BaseModel):
    query: str = Field(..., description="Search query", min_length=1, max_length=500)
    top_k: int = Field(default=5, description="Number of results to return", ge=1, le=20)
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "What was Q1 revenue growth?",
                    "top_k": 5
                }
            ]
        }
    }

class RAGResult(BaseModel):
    chunk_id: str = Field(..., description="Unique chunk identifier")
    content: str = Field(..., description="Document content")
    similarity: float = Field(..., description="Similarity score", ge=0, le=1)
    metadata: Dict[str, Any] = Field(..., description="Document metadata")

class RAGQueryResponse(BaseModel):
    query: str = Field(..., description="Original query")
    normalized_query: str = Field(..., description="Normalized query")
    results: List[RAGResult] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total number of results")
    accessible_departments: List[str] = Field(..., description="Departments user can access")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")

# ==================== USER MANAGEMENT MODELS ====================

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    role: str = Field(..., description="User role")

class UserUpdate(BaseModel):
    is_active: Optional[bool] = None
    role: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool
    created_at: Optional[str] = None

# ==================== AUDIT LOG MODELS ====================

class AuditLogQuery(BaseModel):
    limit: int = Field(default=50, ge=1, le=500)

# ==================== SYSTEM STATUS MODELS ====================

class SystemStatus(BaseModel):
    status: str = Field(default="healthy")
    timestamp: str
    components: Dict[str, str]

class PipelineStats(BaseModel):
    similarity_threshold: float
    total_chunks: int
    total_embeddings: int
    llm_model: str
    llm_provider: str