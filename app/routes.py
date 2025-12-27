from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List

# --- UPDATED IMPORTS ---
# Using the '.' ensures Python looks in the current 'app' folder, 
# which removes the yellow squiggly lines in VS Code.
try:
    from .rag_pipeline import FinSolveRAGPipeline
    from .auth_utils import get_current_user 
    from utils.functions import format_chat_response
except ImportError:
    # Fallback for different execution contexts
    from rag_pipeline import FinSolveRAGPipeline
    from auth_utils import get_current_user
    from utils.functions import format_chat_response

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

@router.post("/chat")
async def chat_endpoint(
    request: QueryRequest, 
    # This Depends(get_current_user) is what was causing your error.
    # Ensure this function exists in auth_utils.py
    current_user: dict = Depends(get_current_user)
):
    try:
        # 1. Role and Username Extraction
        # Extracted from the JWT payload returned by get_current_user
        user_role = current_user.get("role", "guest")
        username = current_user.get("username", "User") 

        # 2. RBAC-aware Pipeline
        # We pass the role to the pipeline to filter documents
        pipeline = FinSolveRAGPipeline(role=user_role)
        results = pipeline.run_pipeline(request.query)
        
        # 3. Handle Empty Results (Access Restriction)
        if not results:
            return {
                "answer": f"Access Denied: Your current role ({user_role}) does not have permission to view documents relevant to this query.", 
                "sources": []
            }
            
        # 4. Data Extraction for Response
        sources = [res.get('doc_id') for res in results if 'doc_id' in res]
        
        # 5. Final Formatted Response
        # Uses the helper function from app/utils/functions.py
        return format_chat_response(
            username=username,
            role=user_role,
            message="Search complete. Relevant data found.",
            sources=list(set(sources)) # Remove duplicate filenames
        )
        
    except Exception as e:
        print(f"Error in /chat endpoint: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal Server Error: {str(e)}"
        )