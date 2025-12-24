from typing import List, Set, Dict, Any
import logging

logger = logging.getLogger(__name__)

class RBACEngine:
    def __init__(self, user_roles: List[str], rbac_config: Dict[str, Any]):

        self.user_roles = [r.strip() for r in user_roles]
        self.rbac_config = rbac_config
        
        # Extract configuration sections
        self.role_definitions = rbac_config.get("roles", {})
        self.role_aliases = rbac_config.get("role_aliases", {})
        self.resources = rbac_config.get("resources", {})
        
        # Cache for performance
        self._canonical_roles_cache = None
        self._effective_permissions_cache = None
        
        logger.info(f"✓ RBAC Engine initialized for roles: {self.user_roles}")
    
    def resolve_roles(self) -> Set[str]:
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
        permissions = self.get_effective_permissions()
        
        # Admin override
        if "*" in permissions:
            return True
        
        return permission in permissions
    
    def is_allowed(self, metadata: Dict[str, Any]) -> bool:
        # Rule 1: Deny by default
        if not metadata:
            return False
        
        # Rule 2: Get effective roles
        effective_roles = self.resolve_roles()
        
        # Rule 4: Admin override
        if "admin" in effective_roles:
            return True
        
        # Rule 3a: Allow-list from metadata
        allowed_roles = metadata.get("allowed_roles", "")
        
        if not allowed_roles:
            return False  # No allowed roles specified
        
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
        
        # Rule 6: Role union (any matching role grants access)
        if effective_roles & canonical_allowed:  # Set intersection
            # Rule 7: Check for explicit deny (future enhancement)
            explicit_deny = metadata.get("explicit_deny", [])
            if isinstance(explicit_deny, str):
                explicit_deny = [r.strip() for r in explicit_deny.split(",")]
            
            if any(role in effective_roles for role in explicit_deny):
                return False
            
            return True
        
        # Rule 3b: Permission-based access
        department = metadata.get("department", "").lower()
        if department:
            read_permission = f"read:{department}"
            if self.has_permission(read_permission):
                return True
        
        # Default deny
        return False
    
    def get_accessible_departments(self) -> List[str]:
        permissions = self.get_effective_permissions()
        
        if "*" in permissions:
            return list(self.resources.keys())
        
        departments = []
        for perm in permissions:
            if perm.startswith("read:"):
                dept = perm.split(":")[1]
                departments.append(dept)
        
        return departments
    
    def validate_access(self, department: str) -> bool:
        accessible = self.get_accessible_departments()
        return department.lower() in [d.lower() for d in accessible]
    
    def get_role_info(self) -> Dict[str, Any]:
        return {
            "user_roles": self.user_roles,
            "canonical_roles": list(self.resolve_roles()),
            "effective_permissions": list(self.get_effective_permissions()),
            "accessible_departments": self.get_accessible_departments(),
            "is_admin": "admin" in self.resolve_roles()
        }
    
    def clear_cache(self):
        self._canonical_roles_cache = None
        self._effective_permissions_cache = None