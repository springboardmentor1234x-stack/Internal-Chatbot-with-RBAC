import json
import os
from typing import Set


class RBACEngine:

    def __init__(self, rba_filename: str = "rba.json"):
        # Always resolve path relative to this file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        rba_path = os.path.join(base_dir, rba_filename)

        with open(rba_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.roles = data.get("roles", {})

    def expand_roles(self, user_role: str) -> Set[str]:
        if user_role not in self.roles:
            raise ValueError(f"Unknown role: {user_role}")

        effective_roles: Set[str] = set()
        stack = [user_role]

        while stack:
            role = stack.pop()

            if role in effective_roles:
                continue

            effective_roles.add(role)
            inherited = self.roles.get(role, {}).get("inherits", [])
            stack.extend(inherited)

        return effective_roles


# -----------------------------
# Local Test
# -----------------------------
if __name__ == "__main__":
    engine = RBACEngine()

    print("ADMIN →", engine.expand_roles("admin"))
    print("HR_MANAGER →", engine.expand_roles("hr_manager"))
    print("INTERN →", engine.expand_roles("intern"))
