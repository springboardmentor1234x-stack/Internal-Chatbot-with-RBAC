# auth/rbac.py

from fastapi import Depends, HTTPException, status
from auth.role_permissions import ROLE_PERMISSIONS
from auth.dependencies import get_current_user   # your existing function

def require_permission(permission: str):
    def rbac_checker(user=Depends(get_current_user)):
        role = user.get("role")

        allowed_permissions = ROLE_PERMISSIONS.get(role, set())

        if permission not in allowed_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action"
            )

        return True

    return rbac_checker
