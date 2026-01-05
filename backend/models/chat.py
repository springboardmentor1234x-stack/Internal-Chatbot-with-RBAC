from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ChatRequest(BaseModel):
    """Request model for chat/query endpoint"""
    query: str = Field(
        ...,
        description="User's question or search query",
        min_length=1,
        max_length=1000
    )
    top_k: int = Field(
        default=5,
        description="Number of documents to retrieve",
        ge=1,
        le=20
    )
    max_tokens: int = Field(
        default=500,
        description="Maximum tokens for LLM response",
        ge=100,
        le=2000
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "What was Q1 revenue growth?",
                    "top_k": 5,
                    "max_tokens": 500
                }
            ]
        }
    }

class SourceCitation(BaseModel):
    """Source citation for retrieved documents"""
    chunk_id: str = Field(..., description="Unique chunk identifier")
    document: str = Field(..., description="Source document name")
    department: str = Field(..., description="Department name")
    page: Optional[Any] = Field(None, description="Page number or section")
    similarity: float = Field(..., description="Similarity score", ge=0, le=1)
    excerpt: str = Field(..., description="Content excerpt")

class ChatResponse(BaseModel):
    """Response model for chat/query endpoint"""
    answer: str = Field(..., description="Generated answer from LLM")
    confidence: str = Field(..., description="Confidence level description")
    confidence_score: float = Field(..., description="Numerical confidence score", ge=0, le=1)
    sources: List[SourceCitation] = Field(..., description="Source citations")
    accessible_departments: List[str] = Field(..., description="Departments user can access")
    model: Optional[str] = Field(None, description="LLM model used")
    normalized_query: Optional[str] = Field(None, description="Normalized query")
    error: Optional[str] = Field(None, description="Error message if any")

class RetrievalOnlyRequest(BaseModel):
    """Request model for retrieval-only endpoint"""
    query: str = Field(
        ...,
        description="Search query",
        min_length=1,
        max_length=1000
    )
    top_k: int = Field(
        default=5,
        description="Number of documents to retrieve",
        ge=1,
        le=20
    )

class RetrievalResult(BaseModel):
    """Single retrieval result"""
    chunk_id: str
    content: str
    similarity: float
    metadata: Dict[str, Any]

class RetrievalOnlyResponse(BaseModel):
    """Response model for retrieval-only endpoint"""
    query: str
    results: List[RetrievalResult]
    total_results: int
    accessible_departments: List[str]