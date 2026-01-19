# backend/auth/rbac.py

from fastapi import Depends, HTTPException, status
from backend.auth.role_permissions import ROLE_PERMISSIONS
from backend.auth.dependencies import get_current_user
from backend.auth.permissions import Permissions
from data.database.audit import log_action


def require_permission(permission: Permissions):
    def rbac_checker(user=Depends(get_current_user)):
        try:
            role = user.get("role")
            username = user.get("sub", "unknown")

            # Defensive: role missing or malformed
            if not role:
                _safe_audit(
                    username=username,
                    role=None,
                    action="RBAC_INVALID_ROLE",
                    query=permission.value
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )

            allowed_permissions = ROLE_PERMISSIONS.get(role, set())

            # ❌ Permission denied
            if permission not in allowed_permissions:
                _safe_audit(
                    username=username,
                    role=role,
                    action="RBAC_DENIED",
                    query=permission.value,
                    documents=[]
                )

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to perform this action"
                )

            # ✅ Permission allowed (optional but good for audit trail)
            _safe_audit(
                username=username,
                role=role,
                action="RBAC_ALLOWED",
                query=permission.value
            )

            return True

        except HTTPException:
            # Re-raise expected RBAC failures
            raise

        except Exception:
            # 🔥 Unexpected RBAC failure must not leak internals
            _safe_audit(
                username="unknown",
                role=None,
                action="RBAC_ERROR",
                query=permission.value
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

    return rbac_checker


# -------------------------------------------------
# AUDIT SAFETY WRAPPER
# -------------------------------------------------
def _safe_audit(**kwargs):
    try:
        log_action(**kwargs)
    except Exception:
        pass  # Audit logging must NEVER break RBAC
