import jwt
from datetime import datetime, timedelta
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