from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
# Updated import: now that rag_pipeline is in the same 'app' folder
from rag_pipeline import FinSolveRAGPipeline
from .auth_utils import get_current_user_role

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

@router.post("/chat")
async def chat_endpoint(request: QueryRequest, user_role: str = Depends(get_current_user_role)):
    try:
        # 1. Initialize pipeline using the user's role
        # Ensure FinSolveRAGPipeline handles pathing correctly in its own __init__
        pipeline = FinSolveRAGPipeline(user_role)
        results = pipeline.run_pipeline(request.query)
        
        # 2. Handle empty results or access restrictions
        if not results:
            return {
                "answer": "I don't have access to that information based on your role.", 
                "sources": []
            }
            
        # 3. Construct the response
        # Using .get() is safer to avoid KeyErrors if 'doc_id' is missing
        top_doc = results[0].get('doc_id', 'Unknown Document')
        answer = f"Found relevant information in {top_doc}."
        
        return {
            "answer": answer, 
            "sources": [res.get('doc_id') for res in results if 'doc_id' in res]
        }
        
    except Exception as e:
        # 4. Log the error internally and return a clear message
        print(f"Error in /chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error: Check pipeline logs.")