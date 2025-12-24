from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from rag_pipeline import FinSolveRAGPipeline
from .auth_utils import get_current_user_role

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

@router.post("/chat")
async def chat_endpoint(request: QueryRequest, user_role: str = Depends(get_current_user_role)):
    try:
        # Initialize pipeline using the user's role
        pipeline = FinSolveRAGPipeline(user_role)
        results = pipeline.run_pipeline(request.query)
        
        if not results:
            return {"answer": "I don't have access to that information based on your role.", "sources": []}
            
        answer = f"Found relevant information in {results[0]['doc_id']}."
        return {"answer": answer, "sources": [res['doc_id'] for res in results]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))