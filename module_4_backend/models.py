"""
Database Models
User and QueryLog models for SQLite with RBAC
"""

import bcrypt
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

# Valid roles
VALID_ROLES = [
    "admin",
    "finance_employee",
    "marketing_employee", 
    "hr_employee",
    "engineering_employee",
    "employee"
]


class User(Base):
    """User model with authentication and RBAC"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # RBAC role
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship to query logs
    query_logs = relationship("QueryLog", back_populates="user")
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hashed password using bcrypt"""
        try:
            password_bytes = password.encode('utf-8')
            hashed_bytes = self.hashed_password.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except:
            return False
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password for storage using bcrypt"""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}', active={self.is_active})>"


class QueryLog(Base):
    """Query log model for audit trail and analytics"""
    __tablename__ = "query_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    query = Column(Text, nullable=False)
    processed_query = Column(Text, nullable=True)
    response = Column(Text, nullable=True)
    sources_accessed = Column(Integer, default=0)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to user
    user = relationship("User", back_populates="query_logs")
    
    def __repr__(self):
        return f"<QueryLog(user_id={self.user_id}, query='{self.query[:50]}...', timestamp={self.timestamp})>"


class Conversation(Base):
    """Conversation model for persistent chat history"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False, default="New Chat")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", backref="conversations")
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id}, title='{self.title}')>"


class ChatMessage(Base):
    """Chat message model for storing individual messages in a conversation"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    sources = Column(Text, nullable=True)  # JSON string of sources
    confidence = Column(Text, nullable=True)  # JSON string of confidence data
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to conversation
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, role='{self.role}', content='{self.content[:30]}...')>"


def validate_role(role: str) -> bool:
    """Validate if role is in allowed list"""
    return role in VALID_ROLES
