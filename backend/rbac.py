from fastapi import HTTPException

ROLE_LEVEL = {
    "intern": 1,
    "finance": 2,
    "hr": 2,
    "engineering": 2,
    "admin": 3
}

def enforce_role(user_role, required_level):
    if user_role not in ROLE_LEVEL:
        raise HTTPException(status_code=403, detail="Unknown role")
    if ROLE_LEVEL[user_role] < required_level:
        raise HTTPException(status_code=403, detail="Access denied")
