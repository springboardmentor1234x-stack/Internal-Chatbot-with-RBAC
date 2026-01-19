# backend/auth/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.auth.jwt_handler import verify_token

# -------------------------------------------------
# HTTP Bearer Security Scheme
# -------------------------------------------------
security = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Authentication dependency

    Flow:
    1. Extract JWT from Authorization header
    2. Verify token (signature, expiry, blacklist, type)
    3. Attach raw token for downstream use (logout, audit)
    4. Return authenticated user context
    """

    # 1️⃣ Extract raw JWT
    token = credentials.credentials

    # 2️⃣ Verify token
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    # 3️⃣ CRITICAL FIX: propagate raw token
    payload["raw_token"] = token

    # 4️⃣ Authenticated user context
    return payload


# from fastapi import Depends, HTTPException, status
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# from backend.auth.jwt_handler import verify_token
# from backend.auth.role_permissions import ROLE_PERMISSIONS

# security = HTTPBearer()

# def get_current_user(
#     credentials: HTTPAuthorizationCredentials = Depends(security)
# ):
#     """
#     1. Extract JWT from Authorization header
#     2. Verify token
#     3. Attach RBAC permissions
#     4. Return enriched user context
#     """

#     token = credentials.credentials
#     payload = verify_token(token)

#     if payload is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid or expired token"
#         )

#     role = payload.get("role")

#     permissions = ROLE_PERMISSIONS.get(role, set())

#     return {
#         "sub": payload.get("sub"),
#         "role": role,
#         "permissions": list(permissions)  # 🔑 THIS FIXES EVERYTHING
#     }
