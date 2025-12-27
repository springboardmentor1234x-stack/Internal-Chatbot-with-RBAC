from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

# 1. Corrected Imports based on your new structure
# Using 'app.' prefix ensures the package is found correctly
from app.rag_pipeline import FinSolveRAGPipeline
from app.auth_utils import get_current_user  # Changed to get_current_user to access the whole payload
from app.utils.functions import format_chat_response # Using your new functions.py

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

@router.post("/chat")
async def chat_endpoint(
    request: QueryRequest, 
    # We get the full user dict, then extract the role
    current_user: dict = Depends(get_current_user)
):
    try:
        user_role = current_user.get("role", "guest")
        username = current_user.get("sub", "User")

        # 2. Initialize pipeline using the user's role
        # Ensure your rag_pipeline.py is updated to handle this
        pipeline = FinSolveRAGPipeline(user_role)
        results = pipeline.run_pipeline(request.query)
        
        # 3. Handle empty results or access restrictions
        if not results:
            return {
                "answer": "I don't have access to that information based on your role.", 
                "sources": []
            }
            
        # 4. Construct the response using your new utility function
        sources = [res.get('doc_id') for res in results if 'doc_id' in res]
        top_doc = sources[0] if sources else 'Unknown Document'
        
        answer_text = f"Found relevant information in {top_doc} for your query."

        # Using the helper from your app/utils/functions.py
        return format_chat_response(
            username=username,
            role=user_role,
            message=answer_text,
            sources=sources
        )
        
    except Exception as e:
        # 5. Detailed error logging
        print(f"Error in /chat endpoint: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal Server Error: {str(e)}"
        )