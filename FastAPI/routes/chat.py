from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Create a router for chatbot endpoints
router = APIRouter(
    prefix="/chat",
    tags=["Chatbot"]
)

# Request model using Pydantic
class ChatRequest(BaseModel):
    query: str
    role: str

# Chat endpoint
@router.post("/")
def chat(request: ChatRequest):
    """
    Accepts user query and role.
    Applies role-based access control.
    Returns chatbot response.
    """

    # Placeholder response (RBAC + embeddings will be integrated later)
    return {
        "role": request.role,
        "query": request.query,
        "response": "Response generated based on role-based access control"
    }
