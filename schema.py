"""Pydantic schemas for request/response validation"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# User schemas
class UserBase(BaseModel):
    """Base user schema"""
    username: str
    email: EmailStr
    full_name: str
    role: str
    department: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating new user"""
    password: str


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


# Authentication schemas
class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenData(BaseModel):
    """Token payload data"""
    username: Optional[str] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request schema"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response schema"""
    access_token: str
    token_type: str
    user: UserResponse


# Chat schemas
class ChatRequest(BaseModel):
    """Chat query request"""
    query: str = Field(..., min_length=1, max_length=1000)
    n_results: int = Field(default=5, ge=1, le=10)
    include_citations: bool = Field(default=True)


class ChatResponse(BaseModel):
    """Chat query response"""
    answer: str
    sources: list
    confidence: dict
    metadata: dict


# Audit log schema
class AuditLogResponse(BaseModel):
    """Audit log response"""
    id: int
    username: Optional[str]
    action: str
    endpoint: Optional[str]
    method: Optional[str]
    status_code: Optional[int]
    timestamp: datetime

    class Config:
        from_attributes = True