"""RBAC Middleware for role-based access control"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from backend.auth.security import verify_token
from typing import Optional


class RBACMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce role-based access control
    
    Checks if user has appropriate role for protected endpoints
    """
    
    # Publicly accessible endpoints (no authentication required)
    PUBLIC_ENDPOINTS = [
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/auth/login"
    ]
    
    # Role-based endpoint permissions
    ROLE_PERMISSIONS = {
        "/api/chat/query": ["admin", "finance", "engineering", "marketing", "hr", "employee"],
        "/api/chat/history": ["admin", "finance", "engineering", "marketing", "hr", "employee"],
        "/api/admin/users": ["admin"],
        "/api/admin/audit-logs": ["admin"],
    }
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request and enforce RBAC
        
        Args:
            request: HTTP request
            call_next: Next middleware/endpoint
            
        Returns:
            Response from next middleware/endpoint
        """
        path = request.url.path
        
        # Skip RBAC for public endpoints
        if any(path.startswith(endpoint) for endpoint in self.PUBLIC_ENDPOINTS):
            return await call_next(request)
        
        # Get authorization header
        auth_header = request.headers.get("Authorization")
        
        # Check if authentication is required
        if not auth_header:
            # Only enforce on protected endpoints
            if not any(path.startswith(endpoint) for endpoint in self.PUBLIC_ENDPOINTS):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
        else:
            # Extract and verify token
            try:
                scheme, token = auth_header.split()
                if scheme.lower() != "bearer":
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid authentication scheme"
                    )
                
                payload = verify_token(token)
                if not payload:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid or expired token"
                    )
                
                user_role = payload.get("role")
                
                # Check role permissions for specific endpoints
                for endpoint, allowed_roles in self.ROLE_PERMISSIONS.items():
                    if path.startswith(endpoint):
                        if user_role not in allowed_roles:
                            raise HTTPException(
                                status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
                            )
                        break
                
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authorization header format"
                )
        
        response = await call_next(request)
        return response