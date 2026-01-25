from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from passlib.context import CryptContext
import chromadb
from sentence_transformers import SentenceTransformer
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import requests
from functools import lru_cache

load_dotenv()

# =========================
# CONFIG
# =========================

SECRET_KEY = os.getenv("JWT_SECRET", "changeme")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10

CHROMA_PERSIST_DIR = "../ingestion/chroma_db"
COLLECTION_NAME = "fintech_documents"

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi3"   # ✅ LIGHTWEIGHT MODEL

OLLAMA_TIMEOUT = 180

security = HTTPBearer()
app = FastAPI()

# =========================
# DATABASE
# =========================

DATABASE_URL = "sqlite:///./users.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# CHROMA + EMBEDDINGS
# =========================

client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
collection = client.get_or_create_collection(COLLECTION_NAME)

embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", "device=cpu")
embedder.max_seq_length = 256
@lru_cache(maxsize=128)
def embed_query(text: str):
    return embedder.encode(text).tolist()


# =========================
# SCHEMAS
# =========================

class LoginRequest(BaseModel):
    username: str
    password: str

class QueryRequest(BaseModel):
    query: str

class DownloadLog(BaseModel):
    source: str

# =========================
# AUTH HELPERS
# =========================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        return jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# =========================
# REGISTER
# =========================

@app.post("/register")
def register(username: str, password: str, role: str, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        username=username,
        hashed_password=hash_password(password),
        role=role
    )
    db.add(user)
    db.commit()
    return {"msg": "User created"}

# =========================
# LOGIN
# =========================

@app.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.username, "role": user.role})

    with open("audit_log.txt", "a") as log:
        log.write(f"{datetime.now()} LOGIN {user.username} ROLE {user.role}\n")

    return {"access_token": token, "token_type": "bearer"}

# =========================
# RAG HELPERS
# =========================

def dedupe_docs(docs):
    return list(dict.fromkeys(docs))

def trim_context(text, max_chars=600):
    return text[:max_chars]

def build_prompt(context, query):
    return f"""
You are an internal company assistant.

Rules:
- Use ONLY the information in the context
- Do NOT invent facts
- Answer in clear bullet points
- Be concise and professional

Context:
{context}

Question:
{query}

Answer:
"""

def ollama_generate(prompt: str):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=OLLAMA_TIMEOUT
        )
        response.raise_for_status()
        return response.json().get("response", "")
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="LLM response timed out. Please try again."
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="LLM generation failed"
        )

# =========================
# QUERY
# =========================

@app.post("/query")
def query_docs(req: QueryRequest, user=Depends(get_current_user)):
    role = user["role"].lower()
    username = user["sub"]

    query_embedding = embed_query(req.query)


    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    docs = []
    sources = set()

    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):

       roles_allowed = meta.get("roles_allowed", "")
       allowed_roles = [r.lower() for r in roles_allowed.split("|")] if roles_allowed else []

    if role == "admin" or role in allowed_roles:
         docs.append(doc)
         sources.add(meta.get("source", "unknown"))


    if not docs:
        return {
            "user": username,
            "role": role,
            "answer": "That information is not available.",
            "sources": []
        }

    context = trim_context("\n\n".join(dedupe_docs(docs)))
    prompt = build_prompt(context, req.query)
    answer = ollama_generate(prompt)

    return {
        "user": username,
        "role": role,
        "answer": answer.strip(),
        "sources": list(sources)
    }

# =========================
# AUDIT LOGS
# =========================

@app.post("/log_download")
def log_download(data: DownloadLog, user=Depends(get_current_user)):
    with open("audit_log.txt", "a") as log:
        log.write(
            f"{datetime.now()} DOWNLOAD {user['sub']} ROLE {user['role']} FILE {data.source}\n"
        )
    return {"status": "logged"}

@app.get("/admin/audit-logs")
def get_audit_logs(user=Depends(get_current_user)):
    if user.get("role", "").lower() != "admin":

        raise HTTPException(status_code=403, detail="Access denied")

    if not os.path.exists("audit_log.txt"):
        return {"logs": []}

    with open("audit_log.txt", "r") as log:
        return {"logs": log.readlines()}

# =========================
# STARTUP WARM-UP
# =========================

@app.on_event("startup")
def warm_up_model():
    try:
        requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": "hello"},
            timeout=OLLAMA_TIMEOUT
        )
    except:
        pass

@app.get("/")
def root():
    return {"status": "Backend running", "docs": "/docs"}
