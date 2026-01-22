from fastapi import HTTPException, Header
from security import verify_token

# Permission → allowed roles
PERMISSION_MAP = {
    "search": ["intern", "finance", "admin"],
    "finance_only": ["finance", "admin"],
    "admin_only": ["admin"]
}
def require_permission(permission: str):
    def checker(authorization: str = Header(None)):

        # Missing token
        if not authorization:
            raise HTTPException(status_code=401, detail="Missing token")

        token = authorization.split(" ")[1]
        payload = verify_token(token)

        # Invalid token
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")

        role = payload.get("role")

        # Unknown role
        if role not in ["intern", "finance", "admin"]:
            raise HTTPException(status_code=403, detail="Unknown role")

        # No permission
        if role not in PERMISSION_MAP.get(permission, []):
            raise HTTPException(status_code=403, detail="Permission denied")

        return payload

    return checker
