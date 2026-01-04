import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
import jwt
import os
import sys

# 1. Standardize the path to ensure local imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 2. Local Imports
from routes import router as chat_router
from database import get_user_from_db, PWD_CONTEXT 
from auth_utils import (
    create_token, 
    require_permission,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECRET_KEY,
    ALGORITHM
)

app = FastAPI(title="FinSolve Backend API")

# 3. --- CORS MIDDLEWARE ---
# This fixes the "Cannot connect to Backend" error in Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, including your Streamlit app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.security import OAuth2PasswordRequestForm

# --- AUTHENTICATION ENDPOINTS ---

@app.post("/auth/login", tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user_from_db(form_data.username)
    
    # Secure login check verifying both user existence and password hash
    if not user or not PWD_CONTEXT.verify(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid username or password"
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

# --- CHAT ROUTES ---
app.include_router(chat_router, prefix="/api/v1")

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "Online", "message": "FinSolve API is running"}

if __name__ == "__main__":
    # Ensure uvicorn runs the 'main' instance of 'app'
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)