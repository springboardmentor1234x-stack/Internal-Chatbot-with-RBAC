from typing import Dict, Set

# Data-level RBAC
# Defines WHICH data domains a role can access

ROLE_TO_DEPARTMENTS = {
    "ENGINEERING": {"engineering", "general"},
    "FINANCE": {"finance", "general"},
    "HR": {"hr", "general"},
    "MARKETING": {"marketing", "general"},
    "ADMIN": {"engineering", "finance", "hr", "marketing", "general"},
}

def get_allowed_departments(user_context: Dict) -> Set[str]:
    role = user_context.get("role")

    if not role:
        return set()

    return ROLE_TO_DEPARTMENTS.get(role, set())


def is_chunk_allowed(chunk_metadata: Dict, user_context: Dict) -> bool:
    allowed_departments = get_allowed_departments(user_context)
    return chunk_metadata.get("department") in allowed_departments
