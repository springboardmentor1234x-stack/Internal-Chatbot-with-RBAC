import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import timedelta
import jwt
import os
import sys

# 1. Standardize the path to ensure local imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 2. Local Imports with error handling
try:
    from routes import router as chat_router
    from database import get_user_from_db, PWD_CONTEXT, update_login_attempt
    from auth_utils import (
        create_token, decode_token, validate_token_expiry,
        ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS,
        SECRET_KEY, ALGORITHM,
    )
    from error_handler import (
        error_handler, FinSolveError, AuthenticationError, ValidationError,
        handle_exceptions, logger, ErrorSeverity
    )
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

app = FastAPI(
    title="FinSolve Backend API",
    description="Enhanced FinSolve API with comprehensive error handling",
    version="1.1.0"
)

# 3. --- CORS MIDDLEWARE ---
# This fixes the "Cannot connect to Backend" error in Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, including your Streamlit app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler for FinSolveError
@app.exception_handler(FinSolveError)
async def finsolve_error_handler(request: Request, exc: FinSolveError):
    """Handle FinSolveError exceptions globally"""
    logger.error(f"FinSolveError in {request.url}: {exc.message}")
    
    return JSONResponse(
        status_code=400 if exc.category.value in ["validation", "user_input"] else 500,
        content={
            "error": exc.to_dict(),
            "success": False,
            "timestamp": exc.timestamp
        }
    )


# Global exception handler for unexpected errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unexpected exceptions"""
    error_response = error_handler.handle_error(
        exc,
        context={
            "url": str(request.url),
            "method": request.method,
            "client": str(request.client) if request.client else "unknown"
        }
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": error_response,
            "success": False,
            "message": "An unexpected error occurred"
        }
    )


from fastapi.security import OAuth2PasswordRequestForm

# --- AUTHENTICATION ENDPOINTS ---


@app.post("/auth/login", tags=["Authentication"])
@handle_exceptions(return_dict=False)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Enhanced login endpoint with comprehensive error handling and security features
    """
    try:
        # Validate input
        if not form_data.username or not form_data.username.strip():
            raise ValidationError(
                "Username is required",
                details={"field": "username"},
                suggestions=["Please provide a valid username"]
            )
        
        if not form_data.password:
            raise ValidationError(
                "Password is required",
                details={"field": "password"},
                suggestions=["Please provide a password"]
            )
        
        username = form_data.username.strip()
        
        # Get user from database
        user = get_user_from_db(username)
        
        if not user:
            # Record failed attempt for non-existent user (security)
            logger.warning(f"Login attempt for non-existent user: {username}")
            raise AuthenticationError(
                "Invalid username or password",
                details={"username": username, "reason": "user_not_found"},
                suggestions=["Check your username and password", "Contact administrator if you need an account"]
            )
        
        # Verify password
        if not PWD_CONTEXT.verify(form_data.password, user["password_hash"]):
            # Record failed login attempt
            update_login_attempt(username, success=False)
            
            logger.warning(f"Failed login attempt for user: {username}")
            raise AuthenticationError(
                "Invalid username or password",
                details={"username": username, "reason": "invalid_password"},
                suggestions=["Check your password", "Use 'Forgot Password' if available"]
            )
        
        # Create tokens
        access_token_data = {"sub": user["username"], "role": user["role"]}
        refresh_token_data = {"sub": user["username"]}
        
        access_token = create_token(
            access_token_data,
            timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = create_token(
            refresh_token_data,
            timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )
        
        # Record successful login
        update_login_attempt(username, success=True)
        
        logger.info(f"Successful login for user: {username}")
        
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
        
    except (ValidationError, AuthenticationError):
        raise  # Re-raise our custom errors
    except Exception as e:
        logger.error(f"Unexpected error in login: {e}")
        raise AuthenticationError(
            "Login failed due to system error",
            details={"error_type": "system_error"},
            suggestions=["Try again later", "Contact system administrator"]
        )


@app.post("/auth/refresh", tags=["Authentication"])
@handle_exceptions(return_dict=False)
async def refresh(refresh_token: str):
    """
    Enhanced token refresh endpoint with comprehensive validation
    """
    try:
        if not refresh_token or not refresh_token.strip():
            raise ValidationError(
                "Refresh token is required",
                details={"token_provided": bool(refresh_token)},
                suggestions=["Please provide a valid refresh token"]
            )
        
        # Decode and validate refresh token
        payload = decode_token(refresh_token.strip())
        username = payload.get("sub")
        
        if not username:
            raise AuthenticationError(
                "Invalid refresh token: missing user information",
                details={"payload_keys": list(payload.keys())},
                suggestions=["Please log in again"]
            )
        
        # Verify user still exists and is active
        user = get_user_from_db(username)
        if not user:
            logger.warning(f"Refresh token used for non-existent user: {username}")
            raise AuthenticationError(
                "User account not found",
                details={"username": username},
                suggestions=["Please log in again", "Contact administrator"]
            )
        
        # Create new access token
        new_access_token = create_token(
            {"sub": user["username"], "role": user["role"]},
            timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        logger.info(f"Token refreshed for user: {username}")
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except (ValidationError, AuthenticationError):
        raise  # Re-raise our custom errors
    except Exception as e:
        logger.error(f"Unexpected error in token refresh: {e}")
        raise AuthenticationError(
            "Token refresh failed",
            details={"error_type": "system_error"},
            suggestions=["Please log in again", "Contact system administrator"]
        )


@app.post("/auth/validate", tags=["Authentication"])
@handle_exceptions(return_dict=False)
async def validate_token(token: str):
    """
    Validate token and return expiry information
    """
    try:
        validation_result = validate_token_expiry(token)
        
        if not validation_result.get("valid"):
            raise AuthenticationError(
                validation_result.get("error", "Token validation failed"),
                details=validation_result,
                suggestions=validation_result.get("suggestions", ["Please log in again"])
            )
        
        return {
            "valid": True,
            "token_info": validation_result
        }
        
    except AuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error validating token: {e}")
        raise AuthenticationError(
            "Token validation failed",
            details={"error_type": "system_error"},
            suggestions=["Contact system administrator"]
        )


# --- CHAT ROUTES ---
app.include_router(chat_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
@handle_exceptions(return_dict=False)
def health_check():
    """Basic health check endpoint"""
    return {
        "status": "Online", 
        "message": "FinSolve API is running",
        "version": "1.1.0",
        "timestamp": logger.handlers[0].formatter.formatTime(logger.makeRecord(
            "health", 20, "", 0, "", (), None
        ))
    }


@app.get("/health", tags=["Health"])
@handle_exceptions(return_dict=False)
def detailed_health_check():
    """
    Detailed health check endpoint with comprehensive system status
    """
    health_status = {
        "status": "healthy",
        "message": "FinSolve API is fully operational",
        "version": "1.1.0",
        "components": {
            "api": "healthy",
            "authentication": "healthy",
            "database": "unknown",
            "rag_pipeline": "unknown",
            "error_handling": "healthy"
        },
        "uptime": "running",
        "error_stats": {}
    }
    
    try:
        # Test database connectivity
        from database import get_user_from_db
        test_user = get_user_from_db("admin")  # Test with known user
        health_status["components"]["database"] = "healthy" if test_user else "degraded"
        
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        health_status["components"]["database"] = "error"
        health_status["status"] = "degraded"
    
    try:
        # Test RAG pipeline
        from rag_pipeline_enhanced import rag_pipeline
        test_result = rag_pipeline.run_pipeline("test health check", "Employee")
        health_status["components"]["rag_pipeline"] = "healthy" if not test_result.get("error") else "degraded"
        
    except Exception as e:
        logger.warning(f"RAG pipeline health check failed: {e}")
        health_status["components"]["rag_pipeline"] = "error"
        health_status["status"] = "degraded"
    
    try:
        # Get error statistics
        health_status["error_stats"] = error_handler.get_error_stats()
        
    except Exception as e:
        logger.warning(f"Error stats retrieval failed: {e}")
        health_status["error_stats"] = {"error": "Unable to retrieve error statistics"}
    
    # Determine overall status
    component_statuses = list(health_status["components"].values())
    if "error" in component_statuses:
        health_status["status"] = "degraded"
        health_status["message"] = "Some components have issues"
    elif "degraded" in component_statuses:
        health_status["status"] = "degraded"
        health_status["message"] = "Some components are degraded"
    
    return health_status


@app.get("/system/errors", tags=["System"])
@handle_exceptions(return_dict=False)
def get_system_errors():
    """
    Get system error statistics and recent errors
    """
    try:
        error_stats = error_handler.get_error_stats()
        
        # Get database error statistics if available
        try:
            from database import get_error_statistics
            db_stats_result = get_error_statistics()
            if db_stats_result.get("success"):
                error_stats["database_errors"] = db_stats_result["statistics"]
        except Exception as e:
            logger.warning(f"Could not retrieve database error stats: {e}")
        
        return {
            "success": True,
            "error_statistics": error_stats,
            "timestamp": logger.handlers[0].formatter.formatTime(logger.makeRecord(
                "system", 20, "", 0, "", (), None
            ))
        }
        
    except Exception as e:
        logger.error(f"Failed to get system errors: {e}")
        raise FinSolveError(
            f"Failed to retrieve system error information: {str(e)}",
            details={"operation": "get_system_errors"},
            suggestions=["Contact system administrator"]
        )


@app.post("/system/errors/clear", tags=["System"])
@handle_exceptions(return_dict=False)
def clear_error_stats():
    """
    Clear error statistics (admin function)
    """
    try:
        error_handler.clear_error_stats()
        logger.info("Error statistics cleared")
        
        return {
            "success": True,
            "message": "Error statistics cleared successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to clear error stats: {e}")
        raise FinSolveError(
            f"Failed to clear error statistics: {str(e)}",
            details={"operation": "clear_error_stats"},
            suggestions=["Contact system administrator"]
        )


if __name__ == "__main__":
    # Ensure uvicorn runs the 'main' instance of 'app'
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
