from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from .security import SECRET_KEY, ALGORITHM, oauth2_scheme
from .database import get_user_from_db

# 1. Define Permission Map
# Map your database roles to specific action permissions
PERMISSION_MAP = {
    "Admin": ["admin:all"],
    "Finance": ["read:finance", "write:finance"],
    "Marketing": ["read:marketing", "read:search"],
    "Engineering": ["read:engineering", "read:search"],
    "Employee": ["read:search"],
    "Intern": ["read:search"] # Matching your test case requirements
}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token: missing subject")
        
        user = get_user_from_db(username)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

# 2. Implement require_permission
def require_permission(required_perm: str):
    def decorator(current_user: dict = Depends(get_current_user)):
        role = current_user.get("role")
        user_perms = PERMISSION_MAP.get(role, [])
        
        # Admin bypass or permission check
        if "admin:all" in user_perms or required_perm in user_perms:
            return current_user
        
        raise HTTPException(
            status_code=403, 
            detail=f"Role '{role}' does not have permission: {required_perm}"
        )
    return decorator