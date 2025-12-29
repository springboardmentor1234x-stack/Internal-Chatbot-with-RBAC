from typing import List, Dict


class Permission:  
    # Read permissions
    READ_GENERAL = "read:general"
    READ_FINANCE = "read:finance"
    READ_ENGINEERING = "read:engineering"
    READ_MARKETING = "read:marketing"
    
    # Write permissions
    WRITE_FINANCE = "write:finance"
    WRITE_ENGINEERING = "write:engineering"
    WRITE_MARKETING = "write:marketing"
    
    # Delete permissions
    DELETE_FINANCE = "delete:finance"
    DELETE_ENGINEERING = "delete:engineering"
    DELETE_MARKETING = "delete:marketing"
    
    # Admin wildcard (grants all permissions)
    ADMIN_ALL = "*"


class Role:
    INTERN = "intern"
    FINANCE_EMPLOYEE = "finance_employee"
    ADMIN = "admin"



# This is the core RBAC configuration
# Define which permissions each role has

ROLE_PERMISSIONS: Dict[str, List[str]] = {
    # Intern: Can only read general company information
    Role.INTERN: [
        Permission.READ_GENERAL
    ],
    
    # Finance Employee: Can read finance-related data
    Role.FINANCE_EMPLOYEE: [
        Permission.READ_FINANCE
    ],
    
    # Admin: Has all permissions (wildcard)
    Role.ADMIN: [
        Permission.ADMIN_ALL
    ]
}


def get_permissions_for_role(role: str) -> List[str]:
    return ROLE_PERMISSIONS.get(role, [])


def role_has_permission(role: str, permission: str) -> bool:
    role_perms = get_permissions_for_role(role)
    
    # Check for admin wildcard
    if Permission.ADMIN_ALL in role_perms:
        return True
    
    # Check for specific permission
    return permission in role_perms


def get_all_roles() -> List[str]:
    return list(ROLE_PERMISSIONS.keys())


def get_all_permissions() -> List[str]:
    return [
        Permission.READ_GENERAL,
        Permission.READ_FINANCE,
        Permission.READ_ENGINEERING,
        Permission.READ_MARKETING,
        Permission.WRITE_FINANCE,
        Permission.WRITE_ENGINEERING,
        Permission.WRITE_MARKETING,
        Permission.DELETE_FINANCE,
        Permission.DELETE_ENGINEERING,
        Permission.DELETE_MARKETING,
        Permission.ADMIN_ALL
    ]