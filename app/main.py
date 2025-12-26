import uvicorn
<<<<<<< HEAD
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
import jwt
import os
import sys

# 1. Standardize the path so Python knows where to look
# This ensures that even if you run from the root, it finds the local files
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 2. Local Imports (Note: No 'app.' prefix since we are inside the app folder)
from routes import router as chat_router
from database import get_user_from_db 
from auth_utils import (
    create_token, 
    require_permission,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECRET_KEY,
    ALGORITHM
)

app = FastAPI(title="FinSolve Backend API")

=======
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router as chat_router

app = FastAPI(title="FinSolve Backend API")

# Fixes the "Cannot connect" error by allowing cross-port communication
>>>>>>> e9687b9d5c258ced9b544b6625ce2877d88a17ab
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD
# --- AUTHENTICATION ENDPOINTS ---

@app.post("/auth/login", tags=["Authentication"])
async def login(username: str):
    user = get_user_from_db(username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials"
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
        "token_type": "bearer"
    }

@app.post("/auth/refresh", tags=["Authentication"])
async def refresh(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        
        user = get_user_from_db(username)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
            
        new_access_token = create_token(
            {"sub": user["username"], "role": user["role"]}, 
            timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return {"access_token": new_access_token}
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

# --- RBAC TEST ENDPOINTS ---

@app.get("/api/v1/search", tags=["RBAC Test"])
async def search_endpoint(user=Depends(require_permission("search"))):
    return {"message": f"Access Granted for {user['sub']} (Role: {user['role']})"}

@app.get("/api/v1/finance/reports", tags=["RBAC Test"])
async def finance_endpoint(user=Depends(require_permission("view_reports"))):
    return {"message": "Confidential financial data accessed."}

# --- EXISTING ROUTES ---

app.include_router(chat_router, prefix="/api/v1")

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "Online", "message": "FinSolve API is running"}

if __name__ == "__main__":
    # Use "main:app" because we are running from inside the app directory
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
=======
# Connects your endpoints defined in routes.py
app.include_router(chat_router, prefix="/api/v1")

@app.get("/")
def health_check():
    return {"status": "Online", "message": "FastAPI is running on port 8000"}

if __name__ == "__main__":
    # Standard FastAPI port is 8000
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
>>>>>>> e9687b9d5c258ced9b544b6625ce2877d88a17ab
