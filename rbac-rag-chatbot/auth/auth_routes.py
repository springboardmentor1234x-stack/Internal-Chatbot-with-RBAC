from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from auth.jwt_handler import create_access_token, create_refresh_token

router = APIRouter(prefix="/auth", tags=["auth"])

# MOCK USERS (replace with DB later)
USERS = {
    "alice": {"password": "password123", "role": "ENGINEERING"},
    "bob": {"password": "password123", "role": "FINANCE"},
}


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(req: LoginRequest):
    user = USERS.get(req.username)

    if not user or user["password"] != req.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token_data = {
        "sub": req.username,
        "role": user["role"]
    }

    return {
        "access_token": create_access_token(token_data),
        "refresh_token": create_refresh_token(token_data),
        "token_type": "bearer"
    }
