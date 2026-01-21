"""
Role Access Visualization
Generate a visual representation of role-based access
"""

def print_role_hierarchy():
    """Print ASCII diagram of role hierarchy"""
    
    diagram = """
╔════════════════════════════════════════════════════════════════════════════╗
║                    ROLE-BASED ACCESS CONTROL HIERARCHY                     ║
╚════════════════════════════════════════════════════════════════════════════╝

                                   ┌─────────┐
                                   │  ADMIN  │
                                   │ (ALL 5) │
                                   └────┬────┘
                                        │
                              Full Access to Everything
                                        │
                    ┌───────────────────┴───────────────────┐
                    │                                       │
                ┌───▼────┐                          ┌──────▼──────┐
                │C-LEVEL │                          │ DEPARTMENTS │
                │ (ALL 5)│                          └──────┬──────┘
                └────────┘                                 │
              Read-Only All                                │
                                    ┌───────────┬──────────┼──────────┬──────────┐
                                    │           │          │          │          │
                            ┌───────▼──┐  ┌─────▼────┐ ┌──▼─────┐ ┌─▼────────┐ │
                            │ FINANCE  │  │MARKETING │ │   HR   │ │ENGINEER  │ │
                            └───┬──────┘  └────┬─────┘ └───┬────┘ └────┬─────┘ │
                                │              │           │           │        │
                        ┌───────┴────┐   ┌─────┴─────┐  ┌──┴───┐  ┌───┴────┐   │
                        │            │   │           │  │      │  │        │   │
                    ┌───▼──┐    ┌────▼─┐ │      ┌────▼┐ │  ┌───▼┐ │    ┌───▼┐  │
                    │ MGR  │    │ EMP  │ │      │ MGR │ │  │MGR │ │    │MGR │  │
                    │(F+G) │    │(F+G) │ │      │(M+G)│ │  │(H+G││ │    │(E+G│  │
                    │ R/W/D│    │  R   │ │      │R/W/D│ │  │R/W/││ │    │R/W/│  │
                    └──────┘    └──────┘ │      └─────┘ │  └────┘ │    └────┘  │
                                         │              │         │            │
                                    ┌────▼─┐       ┌───▼┐   ┌────▼┐           │
                                    │ EMP  │       │EMP │   │ EMP │           │
                                    │(M+G) │       │(H+G│   │(E+G)│           │
                                    │  R   │       │ R  │   │  R  │           │
                                    └──────┘       └────┘   └─────┘           │
                                                                               │
                                                                        ┌──────▼─────┐
                                                                        │  EMPLOYEE  │
                                                                        │  (General) │
                                                                        │     R      │
                                                                        └────────────┘

LEGEND:
━━━━━━
• F = Finance   M = Marketing   H = HR   E = Engineering   G = General
• R = Read      W = Write       D = Delete
• MGR = Manager EMP = Employee
• (F+G) = Access to Finance + General departments

ACCESS MATRIX:
━━━━━━━━━━━━━━
┌─────────────────────┬─────────┬──────────┬─────┬─────────────┬─────────┬─────────────┐
│ Role                │ Finance │ Marketing│ HR  │ Engineering │ General │ Permissions │
├─────────────────────┼─────────┼──────────┼─────┼─────────────┼─────────┼─────────────┤
│ admin               │    ✓    │    ✓     │  ✓  │      ✓      │    ✓    │  R/W/D/A    │
│ c_level             │    ✓    │    ✓     │  ✓  │      ✓      │    ✓    │     R       │
│ finance_manager     │    ✓    │    ✗     │  ✗  │      ✗      │    ✓    │   R/W/D     │
│ finance_employee    │    ✓    │    ✗     │  ✗  │      ✗      │    ✓    │     R       │
│ marketing_manager   │    ✗    │    ✓     │  ✗  │      ✗      │    ✓    │   R/W/D     │
│ marketing_employee  │    ✗    │    ✓     │  ✗  │      ✗      │    ✓    │     R       │
│ hr_manager          │    ✗    │    ✗     │  ✓  │      ✗      │    ✓    │   R/W/D     │
│ hr_employee         │    ✗    │    ✗     │  ✓  │      ✗      │    ✓    │     R       │
│ engineering_manager │    ✗    │    ✗     │  ✗  │      ✓      │    ✓    │   R/W/D     │
│ engineering_employee│    ✗    │    ✗     │  ✗  │      ✓      │    ✓    │     R       │
│ employee            │    ✗    │    ✗     │  ✗  │      ✗      │    ✓    │     R       │
└─────────────────────┴─────────┴──────────┴─────┴─────────────┴─────────┴─────────────┘

DOCUMENT COUNT BY ROLE:
━━━━━━━━━━━━━━━━━━━━━━━
┌─────────────────────┬──────────────┐
│ Role                │ # Documents  │
├─────────────────────┼──────────────┤
│ admin               │     10       │
│ c_level             │     10       │
│ finance_manager     │      3       │
│ finance_employee    │      3       │
│ marketing_manager   │      6       │
│ marketing_employee  │      6       │
│ hr_manager          │      2       │
│ hr_employee         │      2       │
│ engineering_manager │      2       │
│ engineering_employee│      2       │
│ employee            │      1       │
└─────────────────────┴──────────────┘
"""
    
    print(diagram)


def print_rbac_rules():
    """Print RBAC enforcement rules"""
    
    rules = """
╔════════════════════════════════════════════════════════════════════════════╗
║                         RBAC ENFORCEMENT RULES                             ║
╚════════════════════════════════════════════════════════════════════════════╝

Rule 1: DENY BY DEFAULT
━━━━━━━━━━━━━━━━━━━━━━━━
• If no explicit permission exists, access is DENIED
• User must have explicit role assignment
• Documents without metadata are inaccessible

Rule 2: GET EFFECTIVE ROLES
━━━━━━━━━━━━━━━━━━━━━━━━━━
• Extract role from JWT token
• Resolve role to department list
• Example: finance_employee → [Finance, General]

Rule 3a: ALLOW-LIST FROM METADATA (Role Match)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Check if user's role has access to document's department
• If user.role.departments ∩ document.department ≠ ∅, ALLOW
• Example: finance_employee can access Finance docs

Rule 3b: PERMISSION-BASED ACCESS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Check if user has required permission (read/write/delete)
• Read-only users cannot modify documents
• Managers can write/delete in their department

Rule 4: ADMIN OVERRIDE
━━━━━━━━━━━━━━━━━━━━━━
• admin role bypasses all restrictions
• Full access to all departments
• Can perform any action (R/W/D/A)

Rule 5: ROLE UNION (Any Matching Role)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• If user has multiple roles, union of permissions applies
• Access granted if ANY role matches
• Example: User with [finance_employee, employee] gets Finance + General

Rule 6: CHECK FOR EXPLICIT DENY (Future Enhancement)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Not implemented yet
• Will allow explicit deny rules that override allow rules
• Format: {"deny": ["finance_employee"], "department": "HR"}

ENFORCEMENT FLOW:
━━━━━━━━━━━━━━━━━

1. User Query Received
         ↓
2. Extract JWT Token
         ↓
3. Validate Token & Get Role
         ↓
4. Apply Rule 1: Check if role exists → If NO, DENY
         ↓
5. Apply Rule 2: Resolve role to departments
         ↓
6. Apply Rule 4: Is admin? → If YES, ALLOW ALL
         ↓
7. Retrieve Documents from Vector DB
         ↓
8. For Each Document:
   ├─ Apply Rule 3a: Check department match
   ├─ Apply Rule 3b: Check permission level
   └─ Apply Rule 5: Check all user roles
         ↓
9. Filter to Allowed Documents Only
         ↓
10. Return Results
"""
    
    print(rules)


if __name__ == "__main__":
    print_role_hierarchy()
    print("\n" * 2)
    print_rbac_rules()
