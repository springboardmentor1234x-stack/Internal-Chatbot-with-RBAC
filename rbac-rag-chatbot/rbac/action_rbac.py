from typing import Dict

# Action-level RBAC
# Defines WHAT actions a role can perform

ROLE_TO_ACTIONS = {
    "ENGINEERING": {"ASK_QUESTION"},
    "FINANCE": {"ASK_QUESTION"},
    "HR": {"ASK_QUESTION"},
    "MARKETING": {"ASK_QUESTION"},
    "ADMIN": {"ASK_QUESTION"},
}

def is_action_allowed(user_context: Dict, action: str) -> bool:
    role = user_context.get("role")

    if not role:
        return False

    allowed_actions = ROLE_TO_ACTIONS.get(role, set())
    return action in allowed_actions
