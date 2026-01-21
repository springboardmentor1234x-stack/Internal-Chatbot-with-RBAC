"""Audit Middleware for logging all API requests"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from backend.database.database import SessionLocal, AuditLog
from backend.auth.security import verify_token
from datetime import datetime
import time


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all API requests for audit purposes
    
    Logs:
    - User identity (if authenticated)
    - Endpoint accessed
    - HTTP method
    - Response status code
    - IP address
    - User agent
    - Timestamp
    """
    
    # Endpoints to skip audit logging (too noisy)
    SKIP_AUDIT = [
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json"
    ]
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request and log audit information
        
        Args:
            request: HTTP request
            call_next: Next middleware/endpoint
            
        Returns:
            Response from next middleware/endpoint
        """
        path = request.url.path
        
        # Skip audit for certain endpoints
        if any(path.startswith(endpoint) for endpoint in self.SKIP_AUDIT):
            return await call_next(request)
        
        # Extract user information from token
        username = None
        user_id = None
        auth_header = request.headers.get("Authorization")
        
        if auth_header:
            try:
                scheme, token = auth_header.split()
                if scheme.lower() == "bearer":
                    payload = verify_token(token)
                    if payload:
                        username = payload.get("sub")
            except:
                pass
        
        # Get client information
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("User-Agent", "Unknown")
        
        # Process request
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log to database (in background, don't block response)
        try:
            db = SessionLocal()
            
            # Determine action based on endpoint
            action = "api_request"
            if "login" in path:
                action = "login_attempt"
            elif "logout" in path:
                action = "logout"
            elif "chat" in path:
                action = "chat_query"
            
            audit_log = AuditLog(
                username=username,
                action=action,
                endpoint=path,
                method=request.method,
                status_code=response.status_code,
                ip_address=ip_address,
                user_agent=user_agent[:200] if user_agent else None,  # Limit length
                details=f"Response time: {process_time:.3f}s"
            )
            
            db.add(audit_log)
            db.commit()
            db.close()
        except Exception as e:
            # Don't fail the request if audit logging fails
            print(f"Audit logging error: {e}")
        
        return response