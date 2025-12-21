import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

# This imports the specific logic from your rag_pipeline.py file
from rag_pipeline import run_rag_query

# 1. Initialize the FastAPI app 
# This variable name 'app' MUST match the name in your uvicorn command
app = FastAPI(
    title="FinSolve Internal RAG Chatbot",
    description="Backend API for role-based document retrieval",
    version="1.0.0"
)

# 2. Define the Request Body
# This defines what the API expects to receive from the user/frontend
class ChatRequest(BaseModel):
    question: str
    role: str  # Options based on your DOCUMENT_MAP: "Finance", "HR", "Marketing", "Engineering", "Employee", "C-Level"

# 3. Health Check Route
@app.get("/")
def read_root():
    return {"status": "Online", "message": "The RAG Backend is running successfully."}

# 4. The Main Chat Endpoint
@app.post("/chat")
async def chat_with_bot(request: ChatRequest):
    """
    Takes a question and a user role, queries the RBAC RAG pipeline, 
    and returns the authorized answer.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    try:
        # Call the function in your rag_pipeline.py
        # This handles the vector search, role filtering, and LLM generation
        answer = run_rag_query(request.question, request.role)
        
        return {
            "role_context": request.role,
            "answer": answer
        }
    
    except Exception as e:
        # Returns a 500 error if something crashes in the AI pipeline
        raise HTTPException(status_code=500, detail=f"RAG Pipeline Error: {str(e)}")

# 5. Run the Server
if __name__ == "__main__":
    # This starts the Uvicorn server on your local machine at port 8000
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)