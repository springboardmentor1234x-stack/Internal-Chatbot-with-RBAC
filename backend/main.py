from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from passlib.context import CryptContext
import chromadb
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

import os

# =========================
# CONFIG
# =========================

SECRET_KEY = os.getenv("JWT_SECRET", "changeme")  # move to .env later
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

CHROMA_PERSIST_DIR = "../ingestion/chroma_db"
COLLECTION_NAME = "fintech_documents"

security = HTTPBearer()
app = FastAPI()

# =========================
# DATABASE (SQLite)
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
# CHROMA + MODELS
# =========================

client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
collection = client.get_or_create_collection(COLLECTION_NAME)

embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
llm = pipeline(
    "text2text-generation",
    model="google/flan-t5-base",
    max_length=256
)

# =========================
# SCHEMAS
# =========================

class LoginRequest(BaseModel):
    username: str
    password: str

class QueryRequest(BaseModel):
    query: str

# =========================
# AUTH HELPERS
# =========================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# =========================
# REGISTER (TEMP – FOR DEV)
# =========================

@app.post("/register")
def register(
    username: str,
    password: str,
    role: str,
    db: Session = Depends(get_db)
):
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
def login(
    req: LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == req.username).first()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        data={
            "sub": user.username,
            "role": user.role
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }

# =========================
# RAG HELPERS
# =========================

def clean_context(chunks):
    return [
        c.replace("###", "").replace("---", "").strip()
        for c in chunks if c.strip()
    ]

def build_prompt(context, query):
    return f"""
You are a helpful internal company assistant.

Answer the question using ONLY the information in the context.
Do not invent anything.

Context:
{context}

Question:
{query}

Answer:
"""

# =========================
# QUERY (JWT + RBAC)
# =========================

@app.post("/query")
def query_docs(
    req: QueryRequest,
    user=Depends(get_current_user)
):
    role = user["role"].lower()
    username = user["sub"]

    query_embedding = embedder.encode(req.query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5
    )

    docs, sources = [], set()

    for doc, meta in zip(
        results["documents"][0],
        results["metadatas"][0]
    ):
        allowed_roles = [
            r.lower() for r in meta["roles_allowed"].split("|")
        ]
        if role in allowed_roles:
            docs.append(doc)
            sources.add(meta["source"])

    if not docs:
        return {
            "user": username,
            "role": role,
            "answer": "That information is not available.",
            "sources": []
        }

    context = "\n\n".join(clean_context(docs))
    prompt = build_prompt(context, req.query)

    response = llm(
        prompt,
        max_new_tokens=200,
        do_sample=False
    )[0]["generated_text"]

    return {
        "user": username,
        "role": role,
        "answer": response.strip(),
        "sources": list(sources)
    }

@app.get("/")
def root():
    return {"status": "Backend running", "docs": "/docs"}
