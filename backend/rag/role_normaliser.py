ROLE_ALIASES = {
    # Intern
    "intern": "intern",

    # Employees
    "employee": "employee",
    "engineering_employee": "engineering_employee",
    "finance_employee": "finance_employee",
    "hr_employee": "hr_employee",
    "marketing_employee": "marketing_employee",

    # Managers (KEEP DOMAIN)
    "manager": "manager",
    "engineering_manager": "engineering_manager",
    "finance_manager": "finance_manager",
    "hr_manager": "hr_manager",
    "marketing_manager": "marketing_manager",

    # Executives
    "c_level": "c_level",

    # Admin
    "admin": "admin"
}

def normalize_role(role: str) -> str:
    normalized = ROLE_ALIASES.get(role, role)
    print(f"[ROLE-NORMALIZER] raw={role}, normalized={normalized}")
    return normalized
