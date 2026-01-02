import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

# Configuration from environment
SECRET_KEY = os.getenv("SECRET_KEY", "your_super_secret_key_change_in_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def create_token(data: dict, expires_delta: timedelta = None):
    """Generates the JWT token for the user."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    """Verifies and decodes JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"username": username, "role": role}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Dependency to get current user from token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
        return {"username": username, "role": role}
    except jwt.PyJWTError:
        raise credentials_exception

# Role-based permissions mapping
ROLE_PERMISSIONS = {
    "Admin": ["read:all", "write:all"],
    "C-Level": ["read:all"],
    "Finance": ["read:finance", "read:general"],
    "Marketing": ["read:marketing", "read:general"],
    "HR": ["read:hr", "read:general"],
    "Engineering": ["read:engineering", "read:general"],
    "Employee": ["read:general"],
    "Intern": ["read:general"]
}

def check_permission(user_role: str, required_permission: str) -> bool:
    """Check if user role has required permission."""
    user_permissions = ROLE_PERMISSIONS.get(user_role, [])
    return required_permission in user_permissions or "read:all" in user_permissions

def require_permission(required_permission: str):
    """Decorator to require specific permission for endpoints."""
    def permission_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        if not check_permission(user_role, required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: {required_permission} permission required"
            )
        return current_user
    return permission_checker