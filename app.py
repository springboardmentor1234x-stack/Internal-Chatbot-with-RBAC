from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from auth import authenticate, init_db
from rag_engine import search

app = FastAPI()
init_db()

class Chat(BaseModel):
    username: str
    password: str
    query: str

@app.post("/chat")
def chat(req: Chat):
    role = authenticate(req.username, req.password)
    if not role:
        raise HTTPException(401, "Invalid user")

    answer, docs = search(req.query, role)
    return {"role": role, "answer": answer}
