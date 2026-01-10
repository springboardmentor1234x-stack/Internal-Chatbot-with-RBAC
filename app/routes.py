from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

# --- UPDATED IMPORTS ---
try:
    from .rag_pipeline_enhanced import rag_pipeline
    from .auth_utils import get_current_user, check_permission
    from .accuracy_enhancer import accuracy_enhancer
    from .query_optimizer import query_optimizer
except ImportError:
    # Fallback for different execution contexts
    from rag_pipeline_enhanced import rag_pipeline
    from auth_utils import get_current_user, check_permission
    from accuracy_enhancer import accuracy_enhancer
    from query_optimizer import query_optimizer

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
    Chat endpoint with role-based access control.
    Users can only access documents their role permits.
    """
    try:
        # 1. Extract user information from JWT token
        user_role = current_user.get("role", "Employee")
        username = current_user.get("username", "User")

        # 2. Optimize query for better accuracy
        optimization_result = query_optimizer.optimize_query(request.query, user_role)
        optimized_query = optimization_result.get("optimized_query", request.query)
        
        # 3. Check if user has permission to search
        if not check_permission(user_role, "read:general"):
            raise HTTPException(
                status_code=403,
                detail=f"Access denied: Role '{user_role}' does not have search permissions",
            )

        # 4. Run enhanced RAG pipeline with optimized query
        rag_result = rag_pipeline.run_pipeline(optimized_query, user_role)

        # 5. Handle errors from RAG pipeline
        if rag_result.get("error"):
            if "No accessible documents found" in rag_result.get("error", ""):
                return format_chat_response(
                    username=username,
                    role=user_role,
                    message=f"No information found that you have access to. Your role ({user_role}) may not have permission to view documents related to this query.",
                    sources=[],
                )
            else:
                raise HTTPException(status_code=500, detail=rag_result["error"])

        # 6. Enhanced accuracy validation and improvement
        validation_result = accuracy_enhancer.validate_response_accuracy(
            request.query, rag_result
        )
        
        # 7. Enhanced response formatting with accuracy metrics
        citations = rag_result.get("citations", [])
        enhanced_accuracy = validation_result.get("enhanced_accuracy", rag_result.get("accuracy_score", 0.0))
        
        # Create enhanced response with accuracy information
        response = format_chat_response(
            username=username,
            role=user_role,
            message=rag_result["response"],
            sources=rag_result["sources"],
            citations=citations
        )
        
        # Add comprehensive accuracy and performance metrics
        response.update({
            "accuracy_score": enhanced_accuracy,
            "original_accuracy": rag_result.get("accuracy_score", 0.0),
            "validation_score": validation_result.get("validation_score", 0.0),
            "confidence_level": validation_result.get("confidence_level", "low"),
            "query_category": rag_result.get("query_category", "general"),
            "total_chunks_analyzed": rag_result.get("total_chunks_analyzed", 0),
            "quality_metrics": validation_result.get("quality_metrics", {}),
            "improvement_suggestions": validation_result.get("improvement_suggestions", []),
            "query_optimization": {
                "original_query": request.query,
                "optimized_query": optimized_query,
                "optimization_score": optimization_result.get("optimization_score", 0.0),
                "query_intent": optimization_result.get("query_intent", "general"),
                "expanded_terms": optimization_result.get("expanded_terms", []),
                "suggested_alternatives": optimization_result.get("suggested_alternatives", [])
            }
        })
        
        return response

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"Error in /chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.get("/user/profile")
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile information."""
    return {
        "username": current_user.get("username"),
        "role": current_user.get("role"),
        "permissions": current_user.get("permissions", []),
    }


@router.get("/analytics/accuracy")
async def get_accuracy_analytics(current_user: dict = Depends(get_current_user)):
    """Get accuracy analytics and performance metrics."""
    # Check if user has permission to view analytics
    if not check_permission(current_user.get("role", "Employee"), "read:general"):
        raise HTTPException(
            status_code=403,
            detail="Access denied: Insufficient permissions for analytics"
        )
    
    try:
        analytics = accuracy_enhancer.get_accuracy_analytics()
        return {
            "user": current_user.get("username"),
            "analytics": analytics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")


@router.post("/feedback/accuracy")
async def submit_accuracy_feedback(
    feedback_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Submit user feedback on response accuracy."""
    try:
        # Store user feedback for accuracy improvement
        feedback_record = {
            "user": current_user.get("username"),
            "role": current_user.get("role"),
            "timestamp": datetime.now().isoformat(),
            "query": feedback_data.get("query", ""),
            "response_id": feedback_data.get("response_id", ""),
            "user_rating": feedback_data.get("rating", 0),  # 1-5 scale
            "feedback_text": feedback_data.get("feedback", ""),
            "accuracy_issues": feedback_data.get("accuracy_issues", [])
        }
        
        # In a production system, you'd store this in a database
        # For now, we'll just acknowledge the feedback
        
        return {
            "message": "Feedback received successfully",
            "feedback_id": f"fb_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "status": "processed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback error: {str(e)}")


@router.post("/chat/history/save")
async def save_chat_history(
    history_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Save current chat session to persistent storage."""
    try:
        from .chat_history_manager import chat_history_manager
        
        session_id = history_data.get("session_id")
        messages = history_data.get("messages", [])
        session_metadata = history_data.get("metadata", {})
        
        if not session_id or not messages:
            raise HTTPException(status_code=400, detail="Missing session_id or messages")
        
        chat_history_manager.save_session(
            session_id=session_id,
            username=current_user.get("username"),
            user_role=current_user.get("role"),
            messages=messages,
            session_metadata=session_metadata
        )
        
        return {
            "message": "Chat history saved successfully",
            "session_id": session_id,
            "messages_saved": len(messages)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Save error: {str(e)}")


@router.get("/chat/history/sessions")
async def get_user_chat_sessions(
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Get user's recent chat sessions."""
    try:
        from .chat_history_manager import chat_history_manager
        
        sessions = chat_history_manager.get_user_sessions(
            username=current_user.get("username"),
            limit=limit
        )
        
        return {
            "username": current_user.get("username"),
            "sessions": sessions,
            "total_returned": len(sessions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"History error: {str(e)}")


@router.get("/chat/history/session/{session_id}")
async def load_chat_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Load a specific chat session."""
    try:
        from .chat_history_manager import chat_history_manager
        
        session_data = chat_history_manager.load_session(session_id)
        
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Verify user owns this session
        if session_data["username"] != current_user.get("username"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return session_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Load error: {str(e)}")


@router.get("/chat/history/search")
async def search_chat_history(
    q: str,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Search through user's chat history."""
    try:
        from .chat_history_manager import chat_history_manager
        
        if len(q.strip()) < 2:
            raise HTTPException(status_code=400, detail="Search query too short")
        
        results = chat_history_manager.search_messages(
            username=current_user.get("username"),
            query=q,
            limit=limit
        )
        
        return {
            "query": q,
            "results": results,
            "total_found": len(results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.get("/chat/history/analytics")
async def get_chat_analytics(
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """Get user's chat history analytics."""
    try:
        from .chat_history_manager import chat_history_manager
        
        analytics = chat_history_manager.get_user_analytics(
            username=current_user.get("username"),
            days=days
        )
        
        return {
            "username": current_user.get("username"),
            "analytics": analytics,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")


@router.get("/chat/history/export")
async def export_chat_history(
    format: str = "json",
    current_user: dict = Depends(get_current_user)
):
    """Export user's complete chat history."""
    try:
        from .chat_history_manager import chat_history_manager
        
        export_data = chat_history_manager.export_user_history(
            username=current_user.get("username"),
            format=format
        )
        
        filename = f"chat_history_{current_user.get('username')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
        
        from fastapi.responses import Response
        
        return Response(
            content=export_data,
            media_type="application/json" if format == "json" else "text/plain",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")
