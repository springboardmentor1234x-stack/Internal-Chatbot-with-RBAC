from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from datetime import datetime, timedelta
from typing import Dict, List

# Configuration
SECRET_KEY = "your_super_secret_key_finsolve_2024" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Role-based permissions
ROLE_PERMISSIONS = {
    "C-Level": ["read:all", "write:all", "admin:all"],
    "Finance": ["read:finance", "read:general", "write:finance"],
    "Marketing": ["read:marketing", "read:general", "write:marketing"],
    "HR": ["read:hr", "read:general", "write:hr"],
    "Engineering": ["read:engineering", "read:general", "write:engineering"],
    "Employee": ["read:general"]
}

def create_token(data: dict, expires_delta: timedelta) -> str:
    """Create JWT token with expiration."""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise credentials_exception
        
        # Add permissions based on role
        permissions = ROLE_PERMISSIONS.get(role, ["read:general"])
        
        return {
            "username": username, 
            "role": role,
            "permissions": permissions
        }
    except jwt.PyJWTError:
        raise credentials_exception

def check_permission(user_role: str, required_permission: str) -> bool:
    """Check if user role has required permission."""
    user_permissions = ROLE_PERMISSIONS.get(user_role, [])
    
    # C-Level has all permissions
    if "admin:all" in user_permissions:
        return True
    
    # Check specific permission
    if required_permission in user_permissions:
        return True
    
    # Check wildcard permissions
    permission_category = required_permission.split(":")[0]
    if f"{permission_category}:all" in user_permissions:
        return True
    
    return False

def require_permission(required_permission: str):
    """Decorator to require specific permission."""
    def permission_checker(current_user: Dict = Depends(get_current_user)):
        if not check_permission(current_user["role"], required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Required permission '{required_permission}'"
            )
        return current_user
    return permission_checker