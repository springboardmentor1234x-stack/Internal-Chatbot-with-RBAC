"""Chat API endpoints with RAG integration"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database.database import get_db, User, AuditLog
from backend.database.schemas import ChatRequest, ChatResponse
from backend.auth.dependencies import get_current_active_user
from rag.rag_pipeline import RAGPipeline
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

router = APIRouter()

# Initialize RAG pipeline (singleton)
_rag_pipeline = None

def get_rag_pipeline() -> RAGPipeline:
    """Get or create RAG pipeline instance"""
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline


@router.post("/query", response_model=ChatResponse)
async def chat_query(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Process chat query with RAG pipeline
    
    Args:
        request: Chat query request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Chat response with answer, sources, and confidence
    """
    try:
        # Get RAG pipeline
        pipeline = get_rag_pipeline()
        
        # Query with user's role
        result = pipeline.query(
            user_query=request.query,
            user_role=current_user.role,
            n_results=request.n_results,
            include_citations=request.include_citations
        )
        
        # Log successful query
        audit_log = AuditLog(
            user_id=current_user.id,
            username=current_user.username,
            action="chat_query",
            endpoint="/api/chat/query",
            method="POST",
            status_code=200,
            details=f"Query: {request.query[:100]}... | Confidence: {result['confidence']['level']}"
        )
        db.add(audit_log)
        db.commit()
        
        return result
        
    except Exception as e:
        # Log error
        audit_log = AuditLog(
            user_id=current_user.id,
            username=current_user.username,
            action="chat_query_error",
            endpoint="/api/chat/query",
            method="POST",
            status_code=500,
            details=f"Error: {str(e)}"
        )
        db.add(audit_log)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )


@router.get("/history")
async def get_chat_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = 20
):
    """
    Get user's chat history
    
    Args:
        current_user: Current authenticated user
        db: Database session
        limit: Maximum number of records to return
        
    Returns:
        List of chat queries
    """
    history = db.query(AuditLog).filter(
        AuditLog.user_id == current_user.id,
        AuditLog.action == "chat_query"
    ).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    
    return [{
        "id": log.id,
        "query": log.details.split(" | ")[0].replace("Query: ", ""),
        "timestamp": log.timestamp
    } for log in history]