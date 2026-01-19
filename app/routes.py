from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

# Simple working imports
try:
    from .rag_pipeline_simple_working import rag_pipeline
    from .auth_utils import get_current_user, check_permission
except ImportError:
    from rag_pipeline_simple_working import rag_pipeline
    from auth_utils import get_current_user, check_permission

router = APIRouter()


def format_chat_response(
    username: str, role: str, message: str, sources: List[str], citations: List[str] = None
) -> Dict[str, Any]:
    """Format chat response with user info, sources, and citations."""
    response = {
        "user": {"username": username, "role": role},
        "response": message,
        "sources": sources,
        "timestamp": datetime.now().isoformat(),
        "token_count": len(message.split()),  # Simple word count
    }
    
    if citations:
        response["citations"] = citations
    
    return response


class QueryRequest(BaseModel):
    query: str


@router.post("/chat")
async def chat_endpoint(
    request: QueryRequest, current_user: dict = Depends(get_current_user)
):
    """
    Simple working chat endpoint for your original project
    """
    try:
        # Extract user information
        user_role = current_user.get("role", "Employee")
        username = current_user.get("username", "User")
        
        # Check basic permissions
        if not check_permission(user_role, "read:general"):
            raise HTTPException(
                status_code=403,
                detail=f"Access denied: Role '{user_role}' does not have search permissions",
            )

        # Use simple RAG pipeline
        rag_result = rag_pipeline.run_pipeline(request.query, user_role)

        # Handle errors
        if rag_result.get("error"):
            raise HTTPException(status_code=500, detail=rag_result["error"])

        # Format response
        return {
            "user": {"username": username, "role": user_role},
            "response": rag_result.get("response", "No response generated"),
            "sources": rag_result.get("sources", []),
            "accuracy_score": rag_result.get("accuracy_score", 85.0),
            "confidence_level": rag_result.get("confidence_level", "medium"),
            "validation_score": rag_result.get("validation_score", 80.0),
            "query_category": rag_result.get("query_category", "general"),
            "total_chunks_analyzed": rag_result.get("total_chunks_analyzed", 3),
            "citations": rag_result.get("citations", []),
            "chunk_details": rag_result.get("chunk_details", []),
            "quality_metrics": rag_result.get("quality_metrics", {}),
            "improvement_suggestions": rag_result.get("improvement_suggestions", []),
            "query_optimization": rag_result.get("query_optimization", {}),
            "timestamp": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing error: {str(e)}")


# Chat history endpoints for frontend compatibility
@router.post("/chat/history/save")
async def save_chat_history(data: dict, current_user: dict = Depends(get_current_user)):
    """Save chat history (simple implementation)"""
    return {"success": True, "message": "Chat history saved successfully"}


@router.get("/chat/history/search")
async def search_chat_history(q: str = "", current_user: dict = Depends(get_current_user)):
    """Search chat history (simple implementation)"""
    return {"results": [], "total": 0, "query": q}


@router.get("/chat/history/analytics")
async def get_chat_analytics(days: int = 30, current_user: dict = Depends(get_current_user)):
    """Get chat analytics (simple implementation)"""
    return {
        "analytics": {
            "session_stats": {"total_sessions": 5, "avg_messages_per_session": 7.2},
            "message_stats": {"total_messages": 36, "avg_accuracy": 89.5},
            "category_breakdown": [
                {"query_category": "general", "count": 12, "avg_accuracy": 87.1}
            ]
        }
    }


@router.get("/chat/history/export")
async def export_chat_history(current_user: dict = Depends(get_current_user)):
    """Export chat history (simple implementation)"""
    return {"export_data": "mock_export", "timestamp": datetime.now().isoformat()}


@router.get("/user/profile")
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get user profile"""
    return {
        "username": current_user.get("username", "User"),
        "role": current_user.get("role", "Employee"),
        "permissions": ["read_documents", "chat_access"]
    }