from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Callable, Dict, List

from auth.auth_handler import AuthHandler
from rbac.permissions import Permission, ROLE_PERMISSIONS
from audit.audit_logger import AuditLogger

# Initialize dependencies
auth_handler = AuthHandler()
audit_logger = AuditLogger()
security = HTTPBearer()


class RBACMiddleware:   
    def __init__(self):
        self.auth_handler = AuthHandler()
        self.audit_logger = AuditLogger()
    
    def get_user_from_token(self, credentials: HTTPAuthorizationCredentials) -> Dict:
        if not credentials:
            self.audit_logger.log_access_attempt(
                username="unknown",
                role="unknown",
                endpoint="unknown",
                permission="unknown",
                allowed=False,
                reason="Missing authorization token"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        token = credentials.credentials
        
        try:
            user_info = self.auth_handler.get_current_user(token)
            if not user_info:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials"
                )
            return user_info
        except Exception as e:
            self.audit_logger.log_access_attempt(
                username="unknown",
                role="unknown",
                endpoint="unknown",
                permission="unknown",
                allowed=False,
                reason=f"Invalid token: {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    def has_permission(self, user_role: str, required_permission: str) -> bool:        # Get permissions for the role
        role_permissions = ROLE_PERMISSIONS.get(user_role, [])
        
        # Admin has all permissions (wildcard)
        if Permission.ADMIN_ALL in role_permissions:
            return True
        
        # Check if specific permission is granted
        return required_permission in role_permissions
    
    def check_permission(
        self,
        user_info: Dict,
        required_permission: str,
        endpoint: str
    ) -> bool:
        username = user_info["username"]
        role = user_info["role"]
        
        # Check if role exists in our RBAC system
        if role not in ROLE_PERMISSIONS:
            self.audit_logger.log_access_attempt(
                username=username,
                role=role,
                endpoint=endpoint,
                permission=required_permission,
                allowed=False,
                reason="Unknown role"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Unknown role: {role}"
            )
        
        # Check permission
        has_access = self.has_permission(role, required_permission)
        
        if not has_access:
            self.audit_logger.log_access_attempt(
                username=username,
                role=role,
                endpoint=endpoint,
                permission=required_permission,
                allowed=False,
                reason="Insufficient permissions"
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
            reason="Access granted"
        )
        
        return True


# Initialize singleton instance
rbac = RBACMiddleware()


def require_permission(required_permission: str) -> Callable:
    def permission_checker(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> Dict:
        # Extract user from token
        user_info = rbac.get_user_from_token(credentials)
        
        # Get endpoint from request (approximation for audit logging)
        endpoint = "protected_endpoint"
        
        # Check permission
        rbac.check_permission(user_info, required_permission, endpoint)
        
        return user_info
    
    return permission_checker


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    return rbac.get_user_from_token(credentials)