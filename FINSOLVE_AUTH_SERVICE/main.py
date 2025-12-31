# app/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from .database import get_user_from_db, verify_password
from auth_utils import create_access_token, require_permission
from datetime import timedelta

app = FastAPI(title="Internal Chatbot RBAC")

@app.post("/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user_from_db(form_data.username)
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/search")
async def search_data(current_user: dict = Depends(require_permission("read:search"))):
    return {"status": "allowed", "data": "FinSolve Search Results"}

@app.get("/finance-secure")
async def finance_data(current_user: dict = Depends(require_permission("read:finance"))):
    return {"status": "allowed", "data": "Confidential Finance Data"}