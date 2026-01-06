from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Callable, Dict

from auth.auth_handler import AuthHandler
from services.audit_logger import AuditLogger
from auth.token_blacklist import TokenBlacklist

token_blacklist = TokenBlacklist()

# Initialize dependencies
security = HTTPBearer()

class RBACMiddleware:
    """RBAC middleware for FastAPI endpoint protection"""
    
    def __init__(self, audit_logger: AuditLogger = None):
        self.auth_handler = AuthHandler()
        self.audit_logger = audit_logger or AuditLogger()
    
    def get_user_from_token(
        self, 
        credentials: HTTPAuthorizationCredentials,
        request: Request = None
    ) -> Dict:
        """Extract and validate user from JWT token"""
        if not credentials:
            ip_address = request.client.host if request else None
            self.audit_logger.log_access_attempt(
                username="unknown",
                role="unknown",
                endpoint="unknown",
                permission="unknown",
                allowed=False,
                reason="Missing authorization token",
                ip_address=ip_address
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        token = credentials.credentials
        
        if token_blacklist.is_blacklisted(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been invalidated"
            )

        try:
            user_info = self.auth_handler.get_current_user(token)
            if not user_info:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials"
                )
            return user_info
        except Exception as e:
            ip_address = request.client.host if request else None
            self.audit_logger.log_access_attempt(
                username="unknown",
                role="unknown",
                endpoint=str(request.url) if request else "unknown",
                permission="unknown",
                allowed=False,
                reason=f"Invalid token: {str(e)}",
                ip_address=ip_address
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    def check_permission(
        self,
        user_info: Dict,
        required_permission: str,
        endpoint: str,
        rbac_engine = None,
        ip_address: str = None
    ) -> bool:
        """Check if user has required permission using RAG RBAC engine"""
        username = user_info["username"]
        role = user_info["role"]
        
        # If RBAC engine provided, use it (for RAG-integrated permission checking)
        if rbac_engine:
            has_access = rbac_engine.has_permission(required_permission)
            
            if not has_access:
                self.audit_logger.log_access_attempt(
                    username=username,
                    role=role,
                    endpoint=endpoint,
                    permission=required_permission,
                    allowed=False,
                    reason="Insufficient permissions",
                    ip_address=ip_address
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {required_permission}"
                )
            
            # Log successful access
            self.audit_logger.log_access_attempt(
                username=username,
                role=role,
                endpoint=endpoint,
                permission=required_permission,
                allowed=True,
                reason="Access granted",
                ip_address=ip_address
            )
            
            return True
        
        # Fallback: Basic admin check
        if role == "admin":
            self.audit_logger.log_access_attempt(
                username=username,
                role=role,
                endpoint=endpoint,
                permission=required_permission,
                allowed=True,
                reason="Admin access granted",
                ip_address=ip_address
            )
            return True
        
        # For non-admin without RBAC engine, deny by default
        self.audit_logger.log_access_attempt(
            username=username,
            role=role,
            endpoint=endpoint,
            permission=required_permission,
            allowed=False,
            reason="RBAC engine not configured",
            ip_address=ip_address
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Required: {required_permission}"
        )


# Initialize singleton instance
rbac_middleware = RBACMiddleware()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    request: Request = None
) -> Dict:
    """Dependency to get current authenticated user"""
    return rbac_middleware.get_user_from_token(credentials, request)


def require_authentication():
    """Dependency that requires valid authentication"""
    return Depends(get_current_user)