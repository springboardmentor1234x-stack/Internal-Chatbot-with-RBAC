from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any

from auth_utils import authenticate_user, create_access_token, get_current_user_role
from rag_pipeline import get_rag_chain, reset_vector_store

# --- Pydantic Models ---

class Token(BaseModel):
    """Model for the login response."""
    access_token: str
    token_type: str
    role: str # Include role in the response for the frontend

class QueryRequest(BaseModel):
    """Model for the chatbot query request."""
    query: str

class ChatResponse(BaseModel):
    """Model for the chatbot response."""
    answer: str
    sources: Dict[str, Any]

# --- FastAPI App Initialization ---
app = FastAPI(title="RBAC RAG Chatbot Backend")

# --- Startup/Pre-processing Endpoint (Optional but useful) ---
@app.post("/reset_db")
def reset_db_endpoint():
    """Endpoint to clean up and re-index the RAG documents."""
    # NOTE: Run this after adding new documents or changing the RAG logic.
    result = reset_vector_store()
    # Re-create the vector store
    get_rag_chain("C-Level") 
    return {"message": f"Database reset and re-indexed. {result}"}


# --- Authentication Route ---

@app.post("/token", response_model=Token)
async def login_for_access_token(credentials: dict):
    """
    API endpoint for user login. Returns a JWT token and the user's role.
    Expected input: {"username": "...", "password": "..."}
    """
    username = credentials.get("username")
    password = credentials.get("password")

    user_role = authenticate_user(username, password)
    
    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create the JWT token, including the user's role in the payload
    access_token = create_access_token(data={"username": username, "role": user_role})
    
    return {"access_token": access_token, "token_type": "bearer", "role": user_role}


# --- Chatbot Route (The core RAG endpoint) ---

@app.post("/chat", response_model=ChatResponse)
async def chat_query(
    request: QueryRequest, 
    user_role: str = Depends(get_current_user_role) # RBAC is enforced by this dependency
):
    """
    Accepts a user query, applies role-based document filtering in the RAG pipeline, 
    and returns a context-rich answer.
    """
    try:
        # Get the RAG chain configured with the user's specific role
        rag_chain = get_rag_chain(user_role)
        
        # Invoke the chain
        result = rag_chain.invoke({"input": request.query})
        
        # Extract the answer and sources for the response model
        answer = result["answer"]
        source_files = list(set([doc.metadata.get("source_file") for doc in result["context"] if doc.metadata.get("source_file")]))
        
        return ChatResponse(
            answer=answer,
            sources={"retrieved_sources": source_files, "user_role": user_role}
        )

    except Exception as e:
        # In a real application, you'd log the error, but this provides a debug message.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG processing failed: {str(e)}",
        )

# Command to run the backend: uvicorn routes:app --reload