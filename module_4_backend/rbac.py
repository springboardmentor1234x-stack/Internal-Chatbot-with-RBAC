"""
RBAC (Role-Based Access Control)
Permission checking and role resolution
Applied at both API level and data level
"""

from typing import List, Set
from fastapi import HTTPException, status

# RBAC Rules from requirements:
# Rule 1: Deny by default
# Rule 2: Get effective roles
# Rule 3a: Allow-list from metadata (effective role == role match)
# Rule 3b: Permission-based access
# Rule 4: Admin override (admin can access all)
# Rule 5: Role union (any matching role grants access)
# Rule 6: Check for explicit deny (future enhancement)


# Role hierarchy and permissions
ROLE_PERMISSIONS = {
    "admin": ["Finance", "Marketing", "HR", "Engineering", "General"],
    "finance_employee": ["Finance", "General"],
    "marketing_employee": ["Marketing", "General"],
    "hr_employee": ["HR", "General"],
    "engineering_employee": ["Engineering", "General"],
    "employee": ["General"]
}


def get_effective_roles(user_role: str) -> List[str]:
    """
    Get effective accessible roles for a user
    Rule 2: Get effective roles based on user's role
    """
    return ROLE_PERMISSIONS.get(user_role, ["General"])


def check_department_access(user_role: str, department: str) -> bool:
    """
    Check if user role has access to a department
    
    Rules applied:
    - Rule 1: Deny by default
    - Rule 4: Admin override (admin can access all)
    - Rule 3a: Allow-list from metadata
    """
    # Rule 4: Admin override
    if user_role == "admin":
        return True
    
    # Rule 3a: Check allow-list
    allowed_departments = ROLE_PERMISSIONS.get(user_role, [])
    
    # Rule 1: Deny by default (if not in allowed list)
    return department in allowed_departments


def filter_by_rbac(chunks_metadata: List[dict], user_role: str) -> List[int]:
    """
    Filter chunk indices by RBAC rules
    
    Rules applied:
    - Rule 5: Role union (any matching role grants access)
    - Rule 3a: Allow-list from metadata
    
    Returns: List of allowed chunk indices
    """
    allowed_indices = []
    effective_departments = get_effective_roles(user_role)
    
    for idx, metadata in enumerate(chunks_metadata):
        chunk_department = metadata.get('department', '')
        accessible_roles = metadata.get('accessible_roles', [])
        
        # Rule 4: Admin override
        if user_role == "admin":
            allowed_indices.append(idx)
            continue
        
        # Rule 5: Role union - check if any accessible role matches
        # Rule 3a: Allow-list check
        if chunk_department in effective_departments:
            allowed_indices.append(idx)
        elif user_role in accessible_roles:
            allowed_indices.append(idx)
    
    return allowed_indices


def require_permission(user_role: str, required_departments: List[str]):
    """
    API-level RBAC check
    Raises HTTPException if user doesn't have required permissions
    
    Use this for endpoint protection
    """
    effective_departments = get_effective_roles(user_role)
    
    # Admin has access to everything
    if user_role == "admin":
        return True
    
    # Check if user has access to at least one required department
    has_access = any(dept in effective_departments for dept in required_departments)
    
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required: {required_departments}"
        )
    
    return True


def check_permission(user_role: str, permission: str) -> bool:
    """
    Check if a user role has a specific permission
    
    Args:
        user_role: User's role (e.g., "admin", "finance_employee")
        permission: Permission to check (e.g., "manage_users", "query_data")
    
    Returns:
        True if user has permission, False otherwise
    """
    # Define API-level permissions
    API_PERMISSIONS = {
        "admin": ["manage_users", "query_data", "view_stats", "view_all_logs"],
        "finance_employee": ["query_data", "view_stats"],
        "marketing_employee": ["query_data", "view_stats"],
        "hr_employee": ["query_data", "view_stats"],
        "engineering_employee": ["query_data", "view_stats"],
        "employee": ["query_data"]
    }
    
    # Admin has all permissions
    if user_role == "admin":
        return True
    
    allowed_permissions = API_PERMISSIONS.get(user_role, [])
    return permission in allowed_permissions


def get_user_role_permissions(user_role: str) -> List[str]:
    """
    Get all permissions for a user role
    
    Args:
        user_role: User's role
    
    Returns:
        List of permissions
    """
    API_PERMISSIONS = {
        "admin": ["manage_users", "query_data", "view_stats", "view_all_logs"],
        "finance_employee": ["query_data", "view_stats"],
        "marketing_employee": ["query_data", "view_stats"],
        "hr_employee": ["query_data", "view_stats"],
        "engineering_employee": ["query_data", "view_stats"],
        "employee": ["query_data"]
    }
    
    return API_PERMISSIONS.get(user_role, [])
