from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn

from auth.auth_handler import AuthHandler
from auth.models import LoginRequest, LoginResponse, RefreshRequest, TokenResponse
from rbac.rbac_middleware import RBACMiddleware, require_permission
from rbac.permissions import Permission
from database.db_manager import DatabaseManager
from audit.audit_logger import AuditLogger

# Initialize components
db_manager = DatabaseManager()
auth_handler = AuthHandler()
rbac_middleware = RBACMiddleware()
audit_logger = AuditLogger()
security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database and seed users
    print("🚀 Starting application...")
    db_manager.initialize_database()
    db_manager.seed_users()
    print("✅ Database initialized and users seeded")
    yield
    # Shutdown
    print("🛑 Shutting down application...")


# Initialize FastAPI app
app = FastAPI(
    title="Internal RAG Chatbot API",
    description="Production-grade authentication and RBAC system for FinTech company",
    version="1.0.0",
    lifespan=lifespan
)

@app.post(
    "/auth/login",
    response_model=LoginResponse,
    tags=["Authentication"],
    summary="User Login",
    description="Authenticate user and receive access + refresh tokens"
)
async def login(request: LoginRequest):
    user = db_manager.get_user_by_username(request.username)
    
    if not user:
        audit_logger.log_auth_attempt(request.username, "login", False, "User not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    if not user["is_active"]:
        audit_logger.log_auth_attempt(request.username, "login", False, "User inactive")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )
    
    # Verify password
    if not auth_handler.verify_password(request.password, user["password_hash"]):
        audit_logger.log_auth_attempt(request.username, "login", False, "Invalid password")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Generate tokens
    access_token = auth_handler.create_access_token(user["username"], user["role"])
    refresh_token = auth_handler.create_refresh_token(user["username"], user["role"])
    
    audit_logger.log_auth_attempt(request.username, "login", True, "Login successful")
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=900  # 15 minutes in seconds
    )


@app.post(
    "/auth/refresh",
    response_model=TokenResponse,
    tags=["Authentication"],
    summary="Refresh Access Token",
    description="Use refresh token to obtain a new access token"
)
async def refresh_token(request: RefreshRequest):
    try:
        # Decode and validate refresh token
        payload = auth_handler.decode_token(request.refresh_token)
        
        if payload.get("token_type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        username = payload.get("sub")
        role = payload.get("role")
        
        if not username or not role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Verify user still exists and is active
        user = db_manager.get_user_by_username(username)
        if not user or not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account not found or inactive"
            )
        
        # Generate new access token
        new_access_token = auth_handler.create_access_token(username, role)
        
        audit_logger.log_auth_attempt(username, "refresh", True, "Token refreshed")
        
        return TokenResponse(
            access_token=new_access_token,
            token_type="bearer",
            expires_in=900
        )
        
    except HTTPException:
        raise
    except Exception as e:
        audit_logger.log_auth_attempt("unknown", "refresh", False, str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )


@app.get(
    "/search",
    tags=["RAG Operations"],
    summary="General Search",
    description="Search general company knowledge base (requires read:general permission)"
)
async def search_general(
    query: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    _: dict = Depends(require_permission(Permission.READ_GENERAL))
):
    return {
        "status": "success",
        "message": "Search completed successfully",
        "query": query,
        "results": [
            {
                "id": 1,
                "title": "Company Handbook",
                "snippet": "Welcome to our company...",
                "relevance": 0.95
            },
            {
                "id": 2,
                "title": "General Policies",
                "snippet": "Our general policies include...",
                "relevance": 0.87
            }
        ],
        "permission_checked": "read:general"
    }


@app.get(
    "/finance/report",
    tags=["Finance Operations"],
    summary="Finance Report",
    description="Access financial reports (requires read:finance permission)"
)
async def get_finance_report(
    report_id: str = "Q4-2024",
    credentials: HTTPAuthorizationCredentials = Depends(security),
    _: dict = Depends(require_permission(Permission.READ_FINANCE))
):
    return {
        "status": "success",
        "message": "Finance report retrieved successfully",
        "report": {
            "id": report_id,
            "title": f"Financial Report {report_id}",
            "revenue": "$10,250,000",
            "expenses": "$6,800,000",
            "profit": "$3,450,000",
            "period": "Q4 2024"
        },
        "permission_checked": "read:finance"
    }


@app.get(
    "/engineering/docs",
    tags=["Engineering Operations"],
    summary="Engineering Documentation",
    description="Access engineering documentation (requires read:engineering permission)"
)
async def get_engineering_docs(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    _: dict = Depends(require_permission(Permission.READ_ENGINEERING))
):
    return {
        "status": "success",
        "message": "Engineering documentation retrieved",
        "documents": [
            {
                "title": "API Architecture",
                "category": "backend",
                "last_updated": "2024-12-20"
            },
            {
                "title": "Database Schema",
                "category": "infrastructure",
                "last_updated": "2024-12-15"
            }
        ],
        "permission_checked": "read:engineering"
    }


@app.get(
    "/marketing/campaign",
    tags=["Marketing Operations"],
    summary="Marketing Campaigns",
    description="Access marketing campaign data (requires read:marketing permission)"
)
async def get_marketing_campaign(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    _: dict = Depends(require_permission(Permission.READ_MARKETING))
):
    return {
        "status": "success",
        "message": "Marketing campaign data retrieved",
        "campaigns": [
            {
                "name": "Q4 Product Launch",
                "budget": "$500,000",
                "reach": "1.2M users",
                "status": "active"
            }
        ],
        "permission_checked": "read:marketing"
    }


@app.post(
    "/finance/report",
    tags=["Finance Operations"],
    summary="Create Finance Report",
    description="Create new financial report (requires write:finance permission)"
)
async def create_finance_report(
    report_data: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    _: dict = Depends(require_permission(Permission.WRITE_FINANCE))
):
    return {
        "status": "success",
        "message": "Finance report created successfully",
        "report_id": "FIN-2024-001",
        "permission_checked": "write:finance"
    }


@app.delete(
    "/finance/report/{report_id}",
    tags=["Finance Operations"],
    summary="Delete Finance Report",
    description="Delete financial report (requires delete:finance permission)"
)
async def delete_finance_report(
    report_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    _: dict = Depends(require_permission(Permission.DELETE_FINANCE))
):
    return {
        "status": "success",
        "message": f"Finance report {report_id} deleted successfully",
        "permission_checked": "delete:finance"
    }


@app.get(
    "/",
    tags=["Health"],
    summary="Root endpoint"
)
async def root():
    return {
        "status": "online",
        "service": "Internal RAG Chatbot API",
        "version": "1.0.0",
        "message": "Navigate to /docs for API documentation"
    }


@app.get(
    "/health",
    tags=["Health"],
    summary="Health Check"
)
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "auth": "operational"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )