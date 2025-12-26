import jwt
from datetime import datetime, timedelta
<<<<<<< HEAD
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = "super-secret-key-change-this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Mock User DB
users_db = {
    "intern": {"role": "intern"},
    "finance": {"role": "finance"},
    "admin": {"role": "admin"},
}

# Permission Mapping
PERMISSION_MAP = {
    "search": ["intern", "finance", "admin"],
    "view_reports": ["finance", "admin"],
    "manage_users": ["admin"]
}

def create_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_permission(permission: str):
    def decorator(current_user: dict = Depends(get_current_user)):
        role = current_user.get("role")
        if role not in PERMISSION_MAP.get(permission, []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail=f"Role '{role}' does not have '{permission}' permission"
            )
        return current_user
    return decorator
=======
from typing import Dict, Any, Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

# --- Configuration ---
# NOTE: In production, these should be securely managed environment variables.
SECRET_KEY = "THIS-IS-A-HIGHLY-INSECURE-SECRET-DO-NOT-USE-IN-PRODUCTION" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dummy User Database for demonstration
# Key: username, Value: (hashed_password, role)
FAKE_USERS_DB: Dict[str, tuple] = {
    "finance_user": (
        "$2b$12$0kL3K8J0j0k7yF0c9c7k4.H2.D5.G3.Y6.Z8.A0.B3.C5.E6.F9.G4",  # Password: password123
        "Finance",
    ),
    "marketing_user": (
        "$2b$12$0kL3K8J0j0k7yF0c9c7k4.H2.D5.G3.Y6.Z8.A0.B3.C5.E6.F9.G4",  # Password: password123
        "Marketing",
    ),
    "hr_user": (
        "$2b$12$0kL3K8J0j0k7yF0c9c7k4.H2.D5.G3.Y6.Z8.A0.B3.C5.E6.F9.G4",  # Password: password123
        "HR",
    ),
    "engineer_user": (
        "$2b$12$0kL3K8J0j0k7yF0c9c7k4.H2.D5.G3.Y6.Z8.A0.B3.C5.E6.F9.G4",  # Password: password123
        "Engineering",
    ),
    "c_level": (
        "$2b$12$0kL3K8J0j0k7yF0c9c7k4.H2.D5.G3.Y6.Z8.A0.B3.C5.E6.F9.G4",  # Password: password123
        "C-Level",
    ),
    "employee_user": (
        "$2b$12$0kL3K8J0j0k7yF0c9c7k4.H2.D5.G3.Y6.Z8.A0.B3.C5.E6.F9.G4",  # Password: password123
        "Employee",
    ),
}

# --- JWT Functions ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Creates a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "sub": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodes a JWT and returns the payload."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

# --- Authentication and RBAC Dependency ---

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def authenticate_user(username: str, password: str) -> Optional[str]:
    """Verifies credentials and returns the user's role if successful."""
    if username in FAKE_USERS_DB:
        hashed_password, role = FAKE_USERS_DB[username]
        # In a real app, use PWD_CONTEXT.verify(password, hashed_password)
        # For simplicity with the placeholder hash, we'll verify this way:
        if PWD_CONTEXT.verify(password, hashed_password):
            return role
    return None

def get_current_user_role(token: str = Depends(oauth2_scheme)) -> str:
    """
    FastAPI dependency that validates the token and returns the user's role.
    This enforces Authentication.
    """
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # The token payload contains the user's role, which is the key for RBAC.
    user_role = payload.get("role")
    if user_role is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing role information",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_role

def check_role_access(required_role: str):
    """
    RBAC dependency: A function that requires a minimum role to access an endpoint.
    (Not used for the chatbot query, but for other restricted APIs).
    """
    def role_checker(current_user_role: str = Depends(get_current_user_role)):
        # For this project, all users can use the chat endpoint, 
        # but the RAG will filter access to documents based on their role.
        # This dependency is available if you needed a true endpoint-level RBAC check.
        pass
        
    return role_checker
>>>>>>> e9687b9d5c258ced9b544b6625ce2877d88a17ab
