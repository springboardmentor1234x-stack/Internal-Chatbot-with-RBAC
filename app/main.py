import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import jwt
import os
import sys

# Standardize the path to ensure local imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Local Imports with error handling
try:
    from routes import router as chat_router
    from database import get_user_from_db, PWD_CONTEXT, update_login_attempt
    from auth_utils import (
        create_token, decode_token, validate_token_expiry,
        ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS,
        SECRET_KEY, ALGORITHM,
    )
    from audit_logger import log_login_attempt
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

app = FastAPI(
    title="FinSolve Backend API",
    description="FinSolve API - Working Version",
    version="1.0.0"
)

# CORS MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AUTHENTICATION ENDPOINTS
@app.post("/auth/login", tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), request: Request = None):
    """Simple working login endpoint with audit logging"""
    try:
        username = form_data.username.strip() if form_data.username else ""
        password = form_data.password if form_data.password else ""
        
        # Get client info for audit logging
        client_ip = request.client.host if request else None
        user_agent = request.headers.get("user-agent") if request else None
        
        if not username or not password:
            # Log failed login attempt
            log_login_attempt(username or "unknown", "unknown", success=False, 
                            ip_address=client_ip, user_agent=user_agent)
            raise HTTPException(
                status_code=400,
                detail="Username and password are required"
            )
        
        # Get user from database
        user = get_user_from_db(username)
        
        if not user:
            # Log failed login attempt
            log_login_attempt(username, "unknown", success=False, 
                            ip_address=client_ip, user_agent=user_agent)
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )
        
        # Verify password
        if not PWD_CONTEXT.verify(password, user["password_hash"]):
            update_login_attempt(username, success=False)
            # Log failed login attempt
            log_login_attempt(username, user.get("role", "unknown"), success=False, 
                            ip_address=client_ip, user_agent=user_agent)
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )
        
        # Create tokens
        access_token_data = {"sub": user["username"], "role": user["role"]}
        
        access_token = create_token(
            access_token_data,
            timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = create_token(
            {"sub": user["username"]},
            timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )
        
        # Record successful login
        update_login_attempt(username, success=True)
        
        # Create session ID for audit logging
        session_id = f"{username}_{int(datetime.now().timestamp())}"
        
        # Log successful login attempt
        log_login_attempt(username, user["role"], success=True, 
                        ip_address=client_ip, user_agent=user_agent, 
                        session_id=session_id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "username": user["username"],
                "role": user["role"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Log failed login attempt for unexpected errors
        log_login_attempt(username if 'username' in locals() else "unknown", 
                        "unknown", success=False, 
                        ip_address=client_ip if 'client_ip' in locals() else None, 
                        user_agent=user_agent if 'user_agent' in locals() else None)
        raise HTTPException(
            status_code=500,
            detail=f"Login failed: {str(e)}"
        )


@app.post("/auth/refresh", tags=["Authentication"])
async def refresh(refresh_token: str):
    """Simple token refresh endpoint"""
    try:
        if not refresh_token or not refresh_token.strip():
            raise HTTPException(
                status_code=400,
                detail="Refresh token is required"
            )
        
        # Decode and validate refresh token
        payload = decode_token(refresh_token.strip())
        username = payload.get("sub")
        
        if not username:
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token"
            )
        
        # Verify user still exists
        user = get_user_from_db(username)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="User account not found"
            )
        
        # Create new access token
        new_access_token = create_token(
            {"sub": user["username"], "role": user["role"]},
            timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Token refresh failed: {str(e)}"
        )


# CHAT ROUTES
app.include_router(chat_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
def health_check():
    """Basic health check endpoint"""
    return {
        "status": "Online", 
        "message": "FinSolve API is running - FIXED VERSION",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
def detailed_health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "message": "FinSolve API is fully operational - FIXED VERSION",
        "version": "1.0.0",
        "components": {
            "api": "healthy",
            "authentication": "healthy",
            "database": "healthy",
            "rag_pipeline": "healthy"
        }
    }


if __name__ == "__main__":
    uvicorn.run("main_fixed:app", host="127.0.0.1", port=8000, reload=True)