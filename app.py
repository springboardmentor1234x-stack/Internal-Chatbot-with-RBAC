from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag_engine import search
from auth import authenticate, init_db

app = FastAPI(title="Internal Chatbot API")
init_db()

class QueryRequest(BaseModel):
    username: str
    password: str
    query: str

@app.get("/")
def home():
    return {"status": "Internal Chatbot API is running"}

@app.post("/chat")
def chat(req: QueryRequest):
    role = authenticate(req.username, req.password)
    if not role:
        raise HTTPException(status_code=401, detail="Invalid user")

    docs = search(req.query, role)
    context = "\n".join([d.page_content[:500] for d in docs])

    return {
        "role": role,
        "query": req.query,
        "sources": [d.metadata["source"] for d in docs],
        "context": context
    }
