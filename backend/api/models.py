# backend/models.py
from pydantic import BaseModel

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ChatRequest(BaseModel):
    query: str
    token: str
