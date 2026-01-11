from auth.token_blacklist import token_blacklist
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from datetime import datetime
import time
from typing import Dict

from auth.models import (
    LoginRequest, LoginResponse, RefreshRequest, TokenResponse,
    UserInfo, SystemStatus, PipelineStats,
    UserCreate, UserUpdate, UserResponse,
    AuditLogQuery, UserActivityQuery
)
from models.chat import (
    ChatRequest, ChatResponse, SourceCitation,
    RetrievalOnlyRequest, RetrievalOnlyResponse, RetrievalResult
)
from auth.auth_handler import AuthHandler
from auth.database_manager import DatabaseManager
from services.audit_logger import AuditLogger
from rbac.rbac_middleware import get_current_user
from create_rag import bootstrap_application

# Initialize components
app = FastAPI(
    title="RAG Chatbot API with RBAC",
    description="Secure RAG chatbot with JWT authentication, role-based access control, and LLM integration",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
auth_handler = AuthHandler()
db_manager = DatabaseManager()
audit_logger = AuditLogger()

rag_pipeline = None  # Will be initialized on startup

def build_user_rbac(current_user: Dict):
    from rbac.RBACEngine import RBACEngine
    return RBACEngine(
        user_roles=[current_user["role"]],
        rbac_config=rag_pipeline.rbac.rbac_config,
        audit_logger=audit_logger
    )

from contextlib import contextmanager

@contextmanager
def use_user_rbac(user_rbac):
    original_rbac = rag_pipeline.rbac
    rag_pipeline.rbac = user_rbac
    try:
        yield
    finally:
        rag_pipeline.rbac = original_rbac

def require_admin(current_user: Dict):
    if current_user["role"].lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
def ensure_pipeline_ready():
    if not rag_pipeline:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG pipeline not initialized"
        )

# ==================== STARTUP & HEALTH ====================

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    db_manager.initialize_database()
    # db_manager.seed_users()
    audit_logger.log_info("API server started")

    global rag_pipeline
    rag_pipeline = bootstrap_application(audit_logger)
    audit_logger.log_info("Complete RAG pipeline initialized in FastAPI")

@app.get("/", response_model=SystemStatus)
async def root():
    """API health check"""
    return SystemStatus(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        components={
            "authentication": "operational",
            "database": "operational",
            "rag_pipeline": "operational" if rag_pipeline else "not_initialized",
            "llm_service": "operational" if rag_pipeline and rag_pipeline.llm_service else "not_initialized"
        }
    )


# ==================== AUTHENTICATION ENDPOINTS ====================

@app.post("/auth/login", response_model=LoginResponse)
async def login(request: Request, credentials: LoginRequest):
    """User login endpoint - Returns access token and refresh token"""
    ip_address = request.client.host
    
    # Get user from database
    user = db_manager.get_user_by_username(credentials.username)
    
    if not user:
        audit_logger.log_auth_attempt(
            username=credentials.username,
            action="login",
            success=False,
            reason="User not found",
            ip_address=ip_address
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check if user is active
    if not user["is_active"]:
        audit_logger.log_auth_attempt(
            username=credentials.username,
            action="login",
            success=False,
            reason="Account disabled",
            ip_address=ip_address
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Verify password
    if not auth_handler.verify_password(credentials.password, user["password_hash"]):
        audit_logger.log_auth_attempt(
            username=credentials.username,
            action="login",
            success=False,
            reason="Invalid password",
            ip_address=ip_address
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Create tokens
    access_token = auth_handler.create_access_token(
        username=user["username"],
        role=user["role"],
        user_id=user["id"]
    )
    refresh_token = auth_handler.create_refresh_token(
        username=user["username"],
        role=user["role"],
        user_id=user["id"]
    )
    
    # Log successful login
    audit_logger.log_auth_attempt(
        username=credentials.username,
        action="login",
        success=True,
        reason="Login successful",
        ip_address=ip_address
    )
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=auth_handler.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_info={
            "username": user["username"],
            "role": user["role"],
            "user_id": user["id"]
        }
    )
security = HTTPBearer()

@app.post("/auth/logout")
async def logout(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: Dict = Depends(get_current_user)
):
    token_blacklist.blacklist(credentials.credentials)

    audit_logger.log_auth_attempt(
        username=current_user["username"],
        action="logout",
        success=True,
        reason="Token invalidated",
        ip_address=request.client.host
    )

    return {"message": "Logout successful"}


@app.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(request: Request, refresh_request: RefreshRequest):
    """Refresh access token using refresh token"""
    ip_address = request.client.host
    
    try:
        # Validate refresh token
        user_info = auth_handler.validate_refresh_token(refresh_request.refresh_token)
        
        if not user_info:
            audit_logger.log_auth_attempt(
                username="unknown",
                action="refresh",
                success=False,
                reason="Invalid refresh token",
                ip_address=ip_address
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Verify user still exists and is active
        user = db_manager.get_user_by_username(user_info["username"])
        if not user or not user["is_active"]:
            audit_logger.log_auth_attempt(
                username=user_info["username"],
                action="refresh",
                success=False,
                reason="User not found or disabled",
                ip_address=ip_address
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account not found or disabled"
            )
        
        # Create new access token
        access_token = auth_handler.create_access_token(
            username=user["username"],
            role=user["role"],
            user_id=user["id"]
        )
        
        audit_logger.log_auth_attempt(
            username=user_info["username"],
            action="refresh",
            success=True,
            reason="Token refreshed",
            ip_address=ip_address
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=auth_handler.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    except Exception as e:
        audit_logger.log_auth_attempt(
            username="unknown",
            action="refresh",
            success=False,
            reason=str(e),
            ip_address=ip_address
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )


@app.get("/auth/me", response_model=UserInfo)
async def get_current_user_info(
    current_user: Dict = Depends(get_current_user)
):
    """Get current user information"""
    # Get accessible departments if RAG pipeline is initialized
    accessible_departments = []
    if rag_pipeline:
        temp_rbac = build_user_rbac(current_user)
        accessible_departments = temp_rbac.get_accessible_departments()
    
    return UserInfo(
        username=current_user["username"],
        role=current_user["role"],
        user_id=current_user["user_id"],
        accessible_departments=accessible_departments
    )


# ==================== CHAT/QUERY ENDPOINTS ====================

@app.post("/chat/query", response_model=ChatResponse)
async def chat_query(
    request: Request,
    chat_request: ChatRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Main chat endpoint - Execute complete RAG pipeline with LLM response
    Returns AI-generated answer with source citations
    """
    ensure_pipeline_ready()

    start_time = time.time()
    
    try:
        # Create user-specific RBAC engine
        user_rbac = build_user_rbac(current_user)
        
        # Execute complete RAG pipeline (retrieval + LLM)
        with use_user_rbac(user_rbac):
            response = rag_pipeline.process_query(
                query=chat_request.query,
                top_k=chat_request.top_k,
                max_tokens=chat_request.max_tokens,
                username=current_user["username"]
            )
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        
        # Log successful query
        audit_logger.log_info(
            f"Chat query completed for {current_user['username']}: "
            f"{len(response.get('sources', []))} sources in {processing_time:.2f}ms"
        )
        
        # Convert sources to SourceCitation models
        sources = [
            SourceCitation(**source)
            for source in response.get("sources", [])
        ]
        
        return ChatResponse(
            answer=response["answer"],
            confidence=response["confidence"],
            confidence_score=response["confidence_score"],
            sources=sources,
            accessible_departments=response["accessible_departments"],
            model=response.get("model"),
            normalized_query=response.get("normalized_query"),
            error=response.get("error")
        )
    
    except Exception as e:
        audit_logger.log_error("Chat Query Error", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query execution failed: {str(e)}"
        )


@app.post("/chat/retrieval-only", response_model=RetrievalOnlyResponse)
async def retrieval_only(
    request: Request,
    retrieval_request: RetrievalOnlyRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Retrieval-only endpoint - Returns raw chunks without LLM generation
    Useful for testing or when you just need document retrieval
    """
    ensure_pipeline_ready()
    
    try:
        # Create user-specific RBAC engine
        
        user_rbac = build_user_rbac(current_user)
        
        with use_user_rbac(user_rbac):
            # Execute retrieval only
            results = rag_pipeline.get_retrieval_only(
                query=retrieval_request.query,
                top_k=retrieval_request.top_k,
                username=current_user["username"]
            )
        
        # Format results
        retrieval_results = [
            RetrievalResult(
                chunk_id=r["id"],
                content=r["content"],
                similarity=r["similarity"],
                metadata=r["metadata"]
            )
            for r in results
        ]
        
        return RetrievalOnlyResponse(
            query=retrieval_request.query,
            results=retrieval_results,
            total_results=len(retrieval_results),
            accessible_departments=user_rbac.get_accessible_departments()
        )
    
    except Exception as e:
        audit_logger.log_error("Retrieval Error", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Retrieval failed: {str(e)}"
        )


@app.get("/chat/stats", response_model=PipelineStats)
async def get_pipeline_stats(
    current_user: Dict = Depends(get_current_user)
):
    """Get RAG pipeline statistics for current user"""
    ensure_pipeline_ready()
    
    # # Create user-specific RBAC engine
    # user_rbac = build_user_rbac(current_user)
    
    stats = rag_pipeline.get_pipeline_stats()
    
    # Update with user-specific info
    # stats["user_roles"] = [current_user["role"]]
    # stats["effective_roles"] = list(user_rbac.resolve_roles())
    # stats["effective_permissions"] = list(user_rbac.get_effective_permissions())
    # stats["accessible_departments"] = user_rbac.get_accessible_departments()
    # stats["is_admin"] = "admin" in user_rbac.resolve_roles()
    # stats["llm_model"] = rag_pipeline.llm_service.llm_model
    
    return PipelineStats(**stats)


# ==================== ADMIN ENDPOINTS ====================

@app.get("/admin/users")
async def list_users(
    current_user: Dict = Depends(get_current_user)
):
    """List all users (admin only)"""
    require_admin(current_user)
    
    users = db_manager.get_all_users()
    return {"users": users}


@app.post("/admin/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: Dict = Depends(get_current_user)
):
    """Create new user (admin only)"""
    require_admin(current_user)
    
    success = db_manager.create_user(
        username=user_data.username,
        password=user_data.password,
        role=user_data.role
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    audit_logger.log_info(
        f"User created by admin {current_user['username']}: {user_data.username}"
    )
    
    user = db_manager.get_user_by_username(user_data.username)
    return UserResponse(**user)


@app.patch("/admin/users/{username}")
async def update_user(
    username: str,
    user_update: UserUpdate,
    current_user: Dict = Depends(get_current_user)
):
    """Update user (admin only)"""
    require_admin(current_user)
    
    user = db_manager.get_user_by_username(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user_update.is_active is not None:
        db_manager.update_user_status(username, user_update.is_active)
    
    if user_update.role is not None:
        db_manager.update_user_role(username, user_update.role)
    
    audit_logger.log_info(
        f"User updated by admin {current_user['username']}: {username}"
    )
    
    return {"message": "User updated successfully"}


# ==================== AUDIT LOG ENDPOINTS ====================

@app.get("/logs/auth")
async def get_auth_logs(
    query: AuditLogQuery = Depends(),
    current_user: Dict = Depends(get_current_user)
):
    """Get authentication logs (admin only)"""
    require_admin(current_user)
    
    logs = audit_logger.get_recent_auth_logs(limit=query.limit)
    return {"logs": logs}


@app.get("/logs/access")
async def get_access_logs(
    query: AuditLogQuery = Depends(),
    current_user: Dict = Depends(get_current_user)
):
    """Get access control logs (admin only)"""
    require_admin(current_user)
    
    logs = audit_logger.get_recent_access_logs(limit=query.limit)
    return {"logs": logs}


@app.get("/logs/rag")
async def get_rag_logs(
    query: AuditLogQuery = Depends(),
    current_user: Dict = Depends(get_current_user)
):
    """Get RAG pipeline logs (admin only)"""
    require_admin(current_user)
    
    logs = audit_logger.get_recent_rag_logs(limit=query.limit)
    return {"logs": logs}


@app.get("/logs/user/{username}")
async def get_user_activity(
    username: str,
    limit: int = 20,
    current_user: Dict = Depends(get_current_user)
):
    """Get activity logs for specific user"""
    require_admin(current_user)
    
    activity = audit_logger.get_user_activity(username, limit)
    return activity

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)