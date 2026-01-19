# rag/action_rbac.py

from backend.rag.role_normaliser import normalize_role
from data.database.audit import log_action


class ActionRBACError(Exception):
    """Raised when action-level RBAC fails"""
    pass


# ============================================================
# Action → allowed RBAC groups
# ============================================================

ACTION_ROLE_MAP = {
    "RAG_QUERY": {
        "intern",
        "employee",

        # department employees
        "finance_employee",
        "engineering_employee",
        "hr_employee",
        "marketing_employee",

        # managers
        "manager",
        "finance_manager",
        "engineering_manager",
        "hr_manager",
        "marketing_manager",

        # admins
        "admin",
    },

    "ADMIN_RAG_QUERY": {"admin"},
}


# ============================================================
# Domain role → RBAC permission group
# ============================================================


ROLE_GROUP_MAP = {
    # Managers
    "finance_manager": "finance_manager",
    "engineering_manager": "engineering_manager",
    "hr_manager": "hr_manager",
    "marketing_manager": "marketing_manager",

    # Employees
    "finance_employee": "finance_employee",
    "engineering_employee": "engineering_employee",
    "hr_employee": "hr_employee",
    "marketing_employee": "marketing_employee",

    # Base roles
    "intern": "intern",
    "employee": "employee",
    "manager": "manager",
    "admin": "admin",

    # Executives
    "c_level": "admin",
}



def enforce_action_rbac(user: dict, action: str):
    """
    Action-level RBAC enforcement with audit logging.

    - Logs RBAC_DENIED for unauthorized actions
    - Logs RBAC_ALLOWED for authorized actions
    """

    raw_role = user.get("role")
    if not raw_role:
        raise ActionRBACError("User role missing")

    # Username source (JWT-safe)
    username = (
        user.get("sub")
        or user.get("username")
        or "unknown"
    )

    # Step 1: Normalize role
    normalized_role = normalize_role(raw_role)

    # Step 2: Map to RBAC group
    rbac_role = ROLE_GROUP_MAP.get(normalized_role)
    if not rbac_role:
        raise ActionRBACError(
            f"Unknown role '{normalized_role}' – no RBAC mapping found"
        )

    allowed_roles = ACTION_ROLE_MAP.get(action, set())

    # 🔎 Debug (safe to keep)
    print(
        f"[ACTION-RBAC] "
        f"raw={raw_role}, "
        f"normalized={normalized_role}, "
        f"rbac={rbac_role}, "
        f"allowed={allowed_roles}"
    )

    # --------------------------------------------------
    # ❌ RBAC DENIED
    # --------------------------------------------------
    if rbac_role not in allowed_roles:
        log_action(
            username=username,
            role=rbac_role,
            action="RBAC_DENIED",
            query=action,
            documents=[]
        )

        raise ActionRBACError(
            f"Role '{rbac_role}' is not allowed to perform '{action}'"
        )

    # --------------------------------------------------
    # ✅ RBAC ALLOWED (optional but recommended)
    # --------------------------------------------------
    log_action(
        username=username,
        role=rbac_role,
        action="RBAC_ALLOWED",
        query=action,
        documents=[]
    )
