from typing import List, Set, Dict, Any

class RBACEngine:
    """Role-Based Access Control Engine for document filtering"""
    
    def __init__(self, user_roles: List[str], rbac_config: Dict[str, Any], audit_logger):
        self.user_roles = [r.strip() for r in user_roles]
        self.rbac_config = rbac_config
        self.audit_logger = audit_logger
        
        # Extract configuration sections
        self.role_definitions = rbac_config.get("roles", {})
        self.role_aliases = rbac_config.get("role_aliases", {})
        self.resources = rbac_config.get("resources", {})
        
        # Cache for performance
        self._canonical_roles_cache = None
        self._effective_permissions_cache = None
        self._accessible_departments_cache = None
        
        self.audit_logger.log_component_init("RBAC Engine", f"roles: {self.user_roles}")
    
    def resolve_roles(self) -> Set[str]:
        """Resolve user roles to canonical roles including inheritance"""
        if self._canonical_roles_cache is not None:
            return self._canonical_roles_cache

        canonical_roles = set()

        for role in self.user_roles:
            # Resolve alias → canonical
            canonical = self.role_aliases.get(role, role.lower().replace(" ", "_"))
            canonical_roles.add(canonical)

            # Add inherited roles recursively
            canonical_roles.update(
                self._get_inherited_roles(canonical, visited=set())
            )
        self._canonical_roles_cache = canonical_roles
        return canonical_roles

    def _get_inherited_roles(self, role: str, visited: Set[str]) -> Set[str]:
        """Recursively get all inherited roles"""
        if role in visited:
            return set()

        visited.add(role)
        inherited = set()

        role_def = self.role_definitions.get(role)
        if not role_def:
            return inherited

        for parent_role in role_def.get("inherits", []):
            inherited.add(parent_role)
            inherited.update(
                self._get_inherited_roles(parent_role, visited)
            )
        return inherited
    
    def get_effective_permissions(self) -> Set[str]:
        """Get all effective permissions from resolved roles"""
        if self._effective_permissions_cache is not None:
            return self._effective_permissions_cache

        effective_roles = self.resolve_roles()
        permissions = set()

        for role in effective_roles:
            role_def = self.role_definitions.get(role)
            
            if role_def:
                permissions.update(role_def.get("permissions", []))

        # Admin wildcard handling
        if "*" in permissions:
            self._effective_permissions_cache = {"*"}
            return self._effective_permissions_cache

        self._effective_permissions_cache = permissions
        return permissions
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        permissions = self.get_effective_permissions()
        
        # Admin override
        if "*" in permissions:
            return True
        
        return permission in permissions
    
    def get_accessible_departments(self) -> List[str]:
        """Get list of departments the user can access"""
        if self._accessible_departments_cache is not None:
            return self._accessible_departments_cache
        
        permissions = self.get_effective_permissions()
        effective_roles = self.resolve_roles()
        
        # Admin has access to all departments
        if "*" in permissions or "admin" in effective_roles:
            all_depts = list(self.resources.keys())
            self._accessible_departments_cache = all_depts
            return all_depts
        
        departments = set()
        
        # Extract departments from read permissions
        for perm in permissions:
            if perm.startswith("read:"):
                dept = perm.split(":", 1)[1]
                departments.add(dept)
        
        dept_list = list(departments)
        self._accessible_departments_cache = dept_list
        return dept_list
    
    def is_allowed(self, metadata: Dict[str, Any]) -> bool:
        """Check if user can access document with given metadata"""
        # Deny by default
        if not metadata:
            return False
        
        effective_roles = self.resolve_roles()
        
        # Admin override
        if "admin" in effective_roles:
            return True
        
        # Check allowed roles from metadata
        allowed_roles = metadata.get("allowed_roles", "")
        
        if not allowed_roles:
            # If no allowed roles, check department permission
            department = metadata.get("department", "").lower()
            if department:
                read_permission = f"read:{department}"
                if self.has_permission(read_permission):
                    return True
            return False
        
        # Parse allowed roles
        if isinstance(allowed_roles, str):
            allowed_roles_list = [r.strip() for r in allowed_roles.split(",")]
        else:
            allowed_roles_list = allowed_roles
        
        # Normalize to canonical roles
        canonical_allowed = set()
        for role in allowed_roles_list:
            canonical = self.role_aliases.get(role, role.lower())
            canonical_allowed.add(canonical)
        
        # Check for role intersection
        if effective_roles & canonical_allowed:
            # Check for explicit deny
            explicit_deny = metadata.get("explicit_deny", [])
            if isinstance(explicit_deny, str):
                explicit_deny = [r.strip() for r in explicit_deny.split(",")]
            
            if any(role in effective_roles for role in explicit_deny):
                return False
            
            return True
        
        # Check department permission as fallback
        department = metadata.get("department", "").lower()
        if department:
            read_permission = f"read:{department}"
            if self.has_permission(read_permission):
                return True
        
        return False
    
    def get_role_info(self) -> Dict[str, Any]:
        """Get comprehensive role information for debugging"""
        return {
            "user_roles": self.user_roles,
            "canonical_roles": list(self.resolve_roles()),
            "effective_permissions": list(self.get_effective_permissions()),
            "accessible_departments": self.get_accessible_departments(),
            "is_admin": "admin" in self.resolve_roles()
        }
    
    def clear_cache(self):
        """Clear all cached values"""
        self._canonical_roles_cache = None
        self._effective_permissions_cache = None
        self._accessible_departments_cache = None