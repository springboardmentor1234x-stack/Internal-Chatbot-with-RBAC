
"""FastAPI Main Application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Company Chatbot API",
    description="Internal Chatbot with Role-Based Access Control",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Company Internal Chatbot API"}

@app.post("/query")
def query_documents(query: str, user_role: str = "employee"):
    """Query documents with RBAC filtering"""
    # TODO: Implement query logic
    return {"query": query, "role": user_role}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
