import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
import os
import sys

# 1. Standardize the path to ensure local imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 2. Local Imports
from routes import router as chat_router
from database import authenticate_user, init_database
from auth_utils import (
    create_token, 
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    verify_token
)

# Initialize database on startup
init_database()

app = FastAPI(title="FinSolve Internal Chatbot API")

# 3. --- CORS MIDDLEWARE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, including your Streamlit app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- AUTHENTICATION ENDPOINTS ---

@app.post("/auth/login", tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint that returns JWT token."""
    user = authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_token(
        {"sub": user["username"], "role": user["role"]}, 
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_token(
        {"sub": user["username"]}, 
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token, 
        "token_type": "bearer",
        "user": {
            "username": user["username"],
            "role": user["role"]
        }
    }

@app.post("/auth/refresh", tags=["Authentication"])
async def refresh(refresh_token: str):
    """Refresh access token using refresh token."""
    try:
        payload = verify_token(refresh_token)
        username = payload.get("username")
        
        from database import get_user_from_db
        user = get_user_from_db(username)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
            
        new_access_token = create_token(
            {"sub": user["username"], "role": user["role"]}, 
            timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return {"access_token": new_access_token, "token_type": "bearer"}
    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

# --- CHAT ROUTES ---
app.include_router(chat_router, prefix="/api/v1")

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "Online", "message": "FinSolve Internal Chatbot API is running"}

@app.get("/api/v1/setup-vector-store", tags=["Setup"])
def setup_vector_store():
    """Initialize the vector store with documents."""
    try:
        from rag_pipeline import rag_pipeline
        rag_pipeline.setup_vector_store()
        return {"status": "success", "message": "Vector store setup completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting up vector store: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)