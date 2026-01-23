#!/usr/bin/env python3
"""
Simple Backend for FinSolve Internal Chatbot
Minimal version to get the frontend working
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
import hashlib
from passlib.context import CryptContext

# Initialize FastAPI app
app = FastAPI(
    title="FinSolve Backend API - Simple",
    description="Simple FinSolve API for testing",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Simple user database
USERS_DB = {
    "admin": {
        "username": "admin",
        "password_hash": pwd_context.hash("password123"),
        "role": "C-Level"
    },
    "employee": {
        "username": "employee", 
        "password_hash": pwd_context.hash("password123"),
        "role": "Employee"
    },
    "finance_user": {
        "username": "finance_user",
        "password_hash": pwd_context.hash("password123"),
        "role": "Finance"
    },
    "marketing_user": {
        "username": "marketing_user",
        "password_hash": pwd_context.hash("password123"),
        "role": "Marketing"
    },
    "hr_user": {
        "username": "hr_user",
        "password_hash": pwd_context.hash("password123"),
        "role": "HR"
    },
    "engineering_user": {
        "username": "engineering_user",
        "password_hash": pwd_context.hash("password123"),
        "role": "Engineering"
    }
}

# Pydantic models
class ChatRequest(BaseModel):
    query: str

class UserProfile(BaseModel):
    username: str
    role: str
    permissions: list = []

# Helper functions
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except jwt.PyJWTError:
        return None

def get_current_user(token: str):
    username = verify_token(token)
    if username and username in USERS_DB:
        return USERS_DB[username]
    return None

# Routes
@app.get("/")
def root():
    return {"status": "Online", "message": "FinSolve Simple API is running"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "FinSolve Simple API is fully operational",
        "version": "1.0.0",
        "components": {
            "api": "healthy",
            "authentication": "healthy",
            "database": "healthy"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password
    
    # Check if user exists
    if username not in USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    user = USERS_DB[username]
    
    # Verify password
    if not pwd_context.verify(password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": access_token,  # Simple version uses same token
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "username": user["username"],
            "role": user["role"]
        }
    }

@app.post("/auth/refresh")
def refresh_token(refresh_token: str):
    username = verify_token(refresh_token)
    if not username or username not in USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user = USERS_DB[username]
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@app.get("/api/v1/user/profile")
def get_user_profile(authorization: str = None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.split(" ")[1]
    user = get_current_user(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    return {
        "username": user["username"],
        "role": user["role"],
        "permissions": ["read_documents", "chat_access"]
    }

@app.post("/api/v1/chat")
def chat(request: ChatRequest, authorization: str = None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.split(" ")[1]
    user = get_current_user(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Simple response for testing
    query = request.query.lower()
    
    # Simple keyword-based responses
    if "financial" in query or "finance" in query:
        response = "I found information about financial reports. This is a test response from the simple backend."
        sources = ["quarterly_financial_report.md"]
    elif "marketing" in query or "market" in query:
        response = "I found information about marketing reports. This is a test response from the simple backend."
        sources = ["market_report_q4_2024.md"]
    elif "employee" in query or "hr" in query:
        response = "I found information about employee policies. This is a test response from the simple backend."
        sources = ["employee_handbook.md"]
    elif "engineering" in query or "technical" in query:
        response = "I found information about engineering documentation. This is a test response from the simple backend."
        sources = ["engineering_master_doc.md"]
    else:
        response = f"I received your query: '{request.query}'. This is a test response from the simple backend. The system is working correctly!"
        sources = ["employee_handbook.md"]
    
    return {
        "response": response,
        "sources": sources,
        "accuracy_score": 85.5,
        "confidence_level": "high",
        "validation_score": 90.0,
        "query_category": "general",
        "total_chunks_analyzed": 5,
        "citations": [f"From {source}" for source in sources],
        "chunk_details": [
            {
                "document_name": sources[0] if sources else "test_doc.md",
                "chunks": [
                    {
                        "chunk_id": "chunk_1",
                        "type": "content",
                        "score": 0.85,
                        "relevance_score": 85.0,
                        "word_count": 150,
                        "content": f"This is a test chunk related to your query: {request.query}",
                        "keywords": query.split()[:5]
                    }
                ]
            }
        ],
        "quality_metrics": {
            "relevance": 85.0,
            "completeness": 80.0,
            "accuracy": 85.5,
            "clarity": 90.0
        },
        "improvement_suggestions": [
            "Try being more specific in your query",
            "Include relevant keywords for better results"
        ],
        "query_optimization": {
            "original_query": request.query,
            "optimized_query": request.query,
            "optimization_score": 75.0,
            "expanded_terms": query.split()[:3]
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)