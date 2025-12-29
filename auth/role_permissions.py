# # auth/role_permissions.py

# from auth.permissions import Permissions

# ROLE_PERMISSIONS = {
#     "intern": {
#         Permissions.SEARCH_DOCS,
#     },
#     "employee": {
#         Permissions.SEARCH_DOCS,
#     },
#     "admin": {
#         Permissions.SEARCH_DOCS,
#         Permissions.VIEW_ADMIN_METRICS,
#         Permissions.MANAGE_USERS,
#     },
#     "c_level": {
#         Permissions.SEARCH_DOCS,
#         Permissions.VIEW_FINANCE_DOCS,
#     }
# }
from auth.permissions import Permissions

ROLE_PERMISSIONS = {
    "intern": {
        Permissions.SEARCH_DOCS,
    },
    "employee": {
        Permissions.SEARCH_DOCS,
    },
    "finance_employee": {
        Permissions.SEARCH_DOCS,
    },
    "admin": {
        Permissions.SEARCH_DOCS,
        Permissions.VIEW_ADMIN_METRICS,
        Permissions.MANAGE_USERS,
    },
    "c_level": {
        Permissions.SEARCH_DOCS,
        Permissions.VIEW_FINANCE_DOCS,
    }
}
