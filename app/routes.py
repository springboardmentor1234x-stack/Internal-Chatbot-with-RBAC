from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List

# --- UPDATED IMPORTS ---
try:
    from .rag_pipeline import rag_pipeline
    from .auth_utils import get_current_user, check_permission
    from .utils.functions import format_chat_response
except ImportError:
    # Fallback for different execution contexts
    from rag_pipeline import rag_pipeline
    from auth_utils import get_current_user, check_permission
    from utils.functions import format_chat_response

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

@router.post("/chat")
async def chat_endpoint(
    request: QueryRequest, 
    current_user: dict = Depends(get_current_user)
):
    """
    Chat endpoint with role-based access control.
    Users can only access documents their role permits.
    """
    try:
        # 1. Extract user information from JWT token
        user_role = current_user.get("role", "Employee")
        username = current_user.get("username", "User") 

        # 2. Check if user has permission to search
        if not check_permission(user_role, "read:general"):
            raise HTTPException(
                status_code=403, 
                detail=f"Access denied: Role '{user_role}' does not have search permissions"
            )

        # 3. Run RAG pipeline with role-based filtering
        rag_result = rag_pipeline.run_pipeline(request.query, user_role)
        
        # 4. Handle errors from RAG pipeline
        if rag_result.get("error"):
            if "No accessible documents found" in rag_result.get("error", ""):
                return format_chat_response(
                    username=username,
                    role=user_role,
                    message=f"No information found that you have access to. Your role ({user_role}) may not have permission to view documents related to this query.",
                    sources=[]
                )
            else:
                raise HTTPException(status_code=500, detail=rag_result["error"])
        
        # 5. Return successful response
        return format_chat_response(
            username=username,
            role=user_role,
            message=rag_result["response"],
            sources=rag_result["sources"]
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"Error in /chat endpoint: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal Server Error: {str(e)}"
        )

@router.get("/user/profile")
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile information."""
    return {
        "username": current_user.get("username"),
        "role": current_user.get("role"),
        "permissions": current_user.get("permissions", [])
    }