

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.api import auth, chatbot
from backend.db import user_db

app = FastAPI()

# ---------------- INIT DB ----------------
user_db.init_db()

# ---------------- ROOT ----------------
@app.get("/")
def root():
    return {"message": "FinBot API running"}

# ---------------- LOGIN ----------------
class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(req: LoginRequest):
    user = user_db.get_user(req.username)

    if not user or not auth.verify_password(req.password, user[2]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = auth.create_access_token({
        "sub": user[1],   # username
        "role": user[3]   # role
    })

    return {"access_token": token}

# ---------------- CHAT ----------------
class ChatRequest(BaseModel):
    query: str
    token: str

@app.post("/chat")
def chat(req: ChatRequest):
    payload = auth.decode_access_token(req.token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    role = payload["role"]

    # chatbot.get_answer already returns {answer, sources}
    return chatbot.get_answer(req.query, role)
