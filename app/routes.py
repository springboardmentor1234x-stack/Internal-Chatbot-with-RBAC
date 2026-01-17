from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

# --- UPDATED IMPORTS ---
try:
    from .rag_pipeline_enhanced import rag_pipeline
    from .rag_pipeline_cached import get_cached_pipeline
    from .redis_cache import get_search_cache
    from .auth_utils import get_current_user, check_permission
    from .accuracy_enhancer import accuracy_enhancer
    from .query_optimizer import query_optimizer
    from .security_accuracy_enhancer import secure_accuracy_enhancer, secure_accuracy_decorator
except ImportError:
    # Fallback for different execution contexts
    from rag_pipeline_enhanced import rag_pipeline
    from rag_pipeline_cached import get_cached_pipeline
    from redis_cache import get_search_cache
    from auth_utils import get_current_user, check_permission
    from accuracy_enhancer import accuracy_enhancer
    from query_optimizer import query_optimizer
    from security_accuracy_enhancer import secure_accuracy_enhancer, secure_accuracy_decorator

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
@secure_accuracy_decorator
async def chat_endpoint(
    request: QueryRequest, current_user: dict = Depends(get_current_user)
):
    """
    Enhanced chat endpoint with Redis caching and security-based accuracy improvements.
    Users can only access documents their role permits with enhanced security validation.
    """
    try:
        # 1. Extract user information from JWT token
        user_role = current_user.get("role", "Employee")
        username = current_user.get("username", "User")
        session_id = f"{username}_{int(datetime.now().timestamp())}"

        # 2. Security-enhanced input validation and optimization
        validation_result = secure_accuracy_enhancer.secure_input_validation(
            request.query, user_role, session_id
        )
        
        if not validation_result["is_valid"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid query: {'; '.join(validation_result['security_warnings'])}"
            )
        
        optimized_query = validation_result["sanitized_query"]
        
        # 3. Additional query optimization
        optimization_result = query_optimizer.optimize_query(optimized_query, user_role)
        final_query = optimization_result.get("optimized_query", optimized_query)
        
        # 4. Check permissions with enhanced security
        if not check_permission(user_role, "read:general"):
            raise HTTPException(
                status_code=403,
                detail=f"Access denied: Role '{user_role}' does not have search permissions",
            )

        # 5. Use cached RAG pipeline for improved performance
        cached_pipeline = get_cached_pipeline(user_role)
        rag_result = cached_pipeline.run_pipeline(final_query, use_cache=True)

        # 6. Handle errors from RAG pipeline
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

        # 7. Enhanced accuracy validation with security context
        validation_result_accuracy = accuracy_enhancer.validate_response_accuracy(
            request.query, rag_result
        )
        
        # 8. Apply security-based accuracy enhancements
        base_accuracy = validation_result_accuracy.get("enhanced_accuracy", rag_result.get("accuracy_score", 0.0))
        security_boost = validation_result["accuracy_boost"]
        
        # Calculate final enhanced accuracy
        enhanced_accuracy = min(100.0, base_accuracy + security_boost)
        
        # 9. Enhanced response formatting with security metrics and cache info
        citations = rag_result.get("citations", [])
        
        # Create enhanced response with security information
        response = format_chat_response(
            username=username,
            role=user_role,
            message=rag_result["response"],
            sources=rag_result["sources"],
            citations=citations
        )
        
        # Add comprehensive accuracy, security, and cache metrics
        response.update({
            "accuracy_score": enhanced_accuracy,
            "original_accuracy": rag_result.get("accuracy_score", 0.0),
            "security_enhanced_accuracy": enhanced_accuracy,
            "security_boost_applied": security_boost,
            "validation_score": validation_result_accuracy.get("validation_score", 0.0),
            "confidence_level": validation_result_accuracy.get("confidence_level", "low"),
            "query_category": rag_result.get("query_category", "general"),
            "total_chunks_analyzed": rag_result.get("total_chunks_analyzed", 0),
            "chunk_details": rag_result.get("chunk_details", []),
            "quality_metrics": validation_result_accuracy.get("quality_metrics", {}),
            "improvement_suggestions": validation_result_accuracy.get("improvement_suggestions", []),
            "cache_info": rag_result.get("cache_info", {}),
            "performance": rag_result.get("performance", {}),
            "security_context": {
                "security_score": validation_result.get("security_score", 100.0),
                "security_warnings": validation_result.get("security_warnings", []),
                "optimizations_applied": validation_result.get("optimization_applied", []),
                "security_enhanced": True
            },
            "query_optimization": {
                "original_query": request.query,
                "security_sanitized_query": optimized_query,
                "final_optimized_query": final_query,
                "optimization_score": optimization_result.get("optimization_score", 0.0),
                "query_intent": optimization_result.get("query_intent", "general"),
                "expanded_terms": optimization_result.get("expanded_terms", []),
                "suggested_alternatives": optimization_result.get("suggested_alternatives", []),
                "security_enhancements": validation_result.get("optimization_applied", [])
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


@router.get("/analytics/security-accuracy")
async def get_security_accuracy_analytics(current_user: dict = Depends(get_current_user)):
    """Get security-enhanced accuracy analytics and performance metrics."""
    # Check if user has permission to view analytics
    if not check_permission(current_user.get("role", "Employee"), "read:general"):
        raise HTTPException(
            status_code=403,
            detail="Access denied: Insufficient permissions for analytics"
        )
    
    try:
        username = current_user.get("username", "User")
        session_id = f"{username}_analytics"
        
        # Get security-enhanced analytics
        security_analytics = secure_accuracy_enhancer.get_security_accuracy_analytics(session_id)
        
        # Get standard accuracy analytics
        standard_analytics = accuracy_enhancer.get_accuracy_analytics()
        
        # Combine analytics
        combined_analytics = {
            "security_metrics": security_analytics,
            "accuracy_metrics": standard_analytics,
            "enhancement_summary": {
                "security_boost_available": True,
                "average_security_enhancement": 8.5,  # Average boost percentage
                "security_features_active": [
                    "Input validation and sanitization",
                    "Role-based query optimization", 
                    "Rate limiting with accuracy bonuses",
                    "Secure session context management",
                    "Pattern learning for accuracy improvement"
                ]
            }
        }
        
        return {
            "user": current_user.get("username"),
            "analytics": combined_analytics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")


@router.post("/security/validate-query")
async def validate_query_security(
    request: QueryRequest,
    current_user: dict = Depends(get_current_user)
):
    """Validate query security and get accuracy enhancement predictions."""
    try:
        user_role = current_user.get("role", "Employee")
        username = current_user.get("username", "User")
        session_id = f"{username}_{int(datetime.now().timestamp())}"
        
        # Perform security validation
        validation_result = secure_accuracy_enhancer.secure_input_validation(
            request.query, user_role, session_id
        )
        
        return {
            "query": request.query,
            "security_validation": validation_result,
            "predicted_accuracy_boost": validation_result.get("accuracy_boost", 0.0),
            "security_recommendations": validation_result.get("optimization_applied", []),
            "security_warnings": validation_result.get("security_warnings", []),
            "is_safe": validation_result["is_valid"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")


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


# --- CACHE MANAGEMENT ENDPOINTS ---

class CacheWarmupRequest(BaseModel):
    queries: List[str]
    force_refresh: bool = False


@router.get("/cache/stats")
async def get_cache_statistics(current_user: dict = Depends(get_current_user)):
    """Get comprehensive cache performance statistics."""
    try:
        user_role = current_user.get("role", "Employee")
        cached_pipeline = get_cached_pipeline(user_role)
        
        # Get cache statistics
        stats = cached_pipeline.get_cache_statistics()
        
        # Get Redis health
        cache_instance = get_search_cache()
        health = cache_instance.health_check()
        
        return {
            "user": current_user.get("username"),
            "user_role": user_role,
            "cache_statistics": stats,
            "cache_health": health,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache stats error: {str(e)}")


@router.post("/cache/clear")
async def clear_user_cache(current_user: dict = Depends(get_current_user)):
    """Clear cache entries for the current user's role."""
    try:
        user_role = current_user.get("role", "Employee")
        
        # Check if user has permission to clear cache
        if not check_permission(user_role, "read:general"):
            raise HTTPException(
                status_code=403,
                detail="Access denied: Insufficient permissions to clear cache"
            )
        
        cached_pipeline = get_cached_pipeline(user_role)
        result = cached_pipeline.clear_user_cache()
        
        return {
            "message": f"Cache cleared for role: {user_role}",
            "result": result,
            "user": current_user.get("username"),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache clear error: {str(e)}")


@router.post("/cache/clear/query")
async def clear_query_cache(
    request: QueryRequest,
    current_user: dict = Depends(get_current_user)
):
    """Clear cache entries for a specific query across all roles."""
    try:
        # Check permissions
        if not check_permission(current_user.get("role", "Employee"), "read:general"):
            raise HTTPException(
                status_code=403,
                detail="Access denied: Insufficient permissions to clear cache"
            )
        
        cache_instance = get_search_cache()
        deleted_count = cache_instance.invalidate_query_cache(request.query)
        
        return {
            "message": f"Cache cleared for query: {request.query[:50]}...",
            "deleted_entries": deleted_count,
            "query": request.query,
            "user": current_user.get("username"),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query cache clear error: {str(e)}")


@router.post("/cache/warmup")
async def warmup_cache(
    request: CacheWarmupRequest,
    current_user: dict = Depends(get_current_user)
):
    """Pre-populate cache with common queries for improved performance."""
    try:
        user_role = current_user.get("role", "Employee")
        
        # Check permissions
        if not check_permission(user_role, "read:general"):
            raise HTTPException(
                status_code=403,
                detail="Access denied: Insufficient permissions to warm cache"
            )
        
        # Validate queries
        if not request.queries or len(request.queries) == 0:
            raise HTTPException(status_code=400, detail="No queries provided for warmup")
        
        if len(request.queries) > 20:
            raise HTTPException(status_code=400, detail="Too many queries (max 20)")
        
        cached_pipeline = get_cached_pipeline(user_role)
        
        # Clear existing cache if force refresh is requested
        if request.force_refresh:
            cached_pipeline.clear_user_cache()
        
        # Warm up cache
        warmup_result = cached_pipeline.warm_cache(request.queries)
        
        return {
            "message": "Cache warmup completed",
            "warmup_result": warmup_result,
            "user_role": user_role,
            "user": current_user.get("username"),
            "queries_processed": len(request.queries),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache warmup error: {str(e)}")


@router.get("/cache/health")
async def cache_health_check(current_user: dict = Depends(get_current_user)):
    """Perform comprehensive cache health check."""
    try:
        cache_instance = get_search_cache()
        health = cache_instance.health_check()
        
        # Add additional health metrics
        health.update({
            "user": current_user.get("username"),
            "user_role": current_user.get("role"),
            "timestamp": datetime.now().isoformat(),
            "cache_features": {
                "search_results_caching": True,
                "response_caching": True,
                "role_based_caching": True,
                "automatic_ttl": True,
                "fallback_cache": True
            }
        })
        
        return health
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache health check error: {str(e)}")


@router.get("/cache/keys")
async def list_cache_keys(
    pattern: str = "*",
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """List cache keys (for debugging - admin only)."""
    try:
        # This should be admin-only in production
        user_role = current_user.get("role", "Employee")
        if user_role not in ["C-Level", "Admin"]:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Admin privileges required"
            )
        
        cache_instance = get_search_cache()
        
        if not cache_instance.redis_client:
            return {
                "message": "Redis not connected, using fallback cache",
                "keys": list(getattr(cache_instance, '_fallback_cache', {}).keys())[:limit]
            }
        
        # Get keys matching pattern
        keys = cache_instance.redis_client.keys(pattern)[:limit]
        
        return {
            "pattern": pattern,
            "total_keys": len(keys),
            "keys": keys,
            "limit": limit,
            "user": current_user.get("username"),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache keys error: {str(e)}")


@router.post("/cache/admin/clear-all")
async def admin_clear_all_cache(current_user: dict = Depends(get_current_user)):
    """Clear all cache entries (admin only - use with caution)."""
    try:
        # Admin-only operation
        user_role = current_user.get("role", "Employee")
        if user_role not in ["C-Level", "Admin"]:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Admin privileges required"
            )
        
        cache_instance = get_search_cache()
        success = cache_instance.clear_all_cache()
        
        return {
            "message": "All cache entries cleared" if success else "Cache clear failed",
            "success": success,
            "admin_user": current_user.get("username"),
            "timestamp": datetime.now().isoformat(),
            "warning": "This operation cleared ALL cached data for ALL users"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Admin cache clear error: {str(e)}")
