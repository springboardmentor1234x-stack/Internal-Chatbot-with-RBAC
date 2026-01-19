from backend.auth.permissions import Permissions

ROLE_PERMISSIONS = {
    # -------------------
    # Basic roles
    # -------------------
    "intern": {
        Permissions.SEARCH_DOCS,
        Permissions.RAG_QUERY,
        Permissions.VIEW_DOCUMENT,
        Permissions.DOWNLOAD_DATASET,     # ✅ allow LLM for general docs
    },

    "employee": {
        Permissions.SEARCH_DOCS,
        Permissions.RAG_QUERY,    
        Permissions.VIEW_DOCUMENT,  
        Permissions.DOWNLOAD_DATASET,   # ✅ employees can ask LLM
    },

    "manager": {
        Permissions.SEARCH_DOCS,
        Permissions.RAG_QUERY,  
        Permissions.VIEW_DOCUMENT,
        Permissions.DOWNLOAD_DATASET,      # managers can ask questions
    },

    # -------------------
    # Department employees
    # -------------------
    "engineering_employee": {
        Permissions.SEARCH_DOCS,
        Permissions.RAG_QUERY,
        Permissions.VIEW_DOCUMENT,
        Permissions.DOWNLOAD_DATASET, 
    },

    "marketing_employee": {
        Permissions.SEARCH_DOCS,
        Permissions.RAG_QUERY,
        Permissions.VIEW_DOCUMENT,
        Permissions.DOWNLOAD_DATASET,
    },

    "finance_employee": {
        Permissions.SEARCH_DOCS,
        Permissions.RAG_QUERY,
        Permissions.VIEW_DOCUMENT,
        Permissions.DOWNLOAD_DATASET,
    },

    "hr_employee": {
        Permissions.SEARCH_DOCS,
        Permissions.RAG_QUERY,
        Permissions.VIEW_DOCUMENT,
        Permissions.DOWNLOAD_DATASET, 
    },

    # -------------------
    # Department managers
    # -------------------
    "engineering_manager": {
        Permissions.SEARCH_DOCS,
        Permissions.RAG_QUERY,
        Permissions.VIEW_DOCUMENT,
        Permissions.DOWNLOAD_DATASET, 
    },

    "marketing_manager": {
        Permissions.SEARCH_DOCS,
        Permissions.RAG_QUERY,
        Permissions.VIEW_DOCUMENT,
        Permissions.DOWNLOAD_DATASET, 
    },

    "finance_manager": {
        Permissions.SEARCH_DOCS,
        Permissions.RAG_QUERY,
        Permissions.VIEW_DOCUMENT,
        Permissions.DOWNLOAD_DATASET, 
    },

    "hr_manager": {
        Permissions.SEARCH_DOCS,
        Permissions.RAG_QUERY,
        Permissions.VIEW_DOCUMENT,
        Permissions.DOWNLOAD_DATASET, 
    },

    # -------------------
    # Admin & C-Level
    # -------------------
    "admin": {
        Permissions.SEARCH_DOCS,
        Permissions.RAG_QUERY,
        Permissions.VIEW_ADMIN_METRICS,
        Permissions.VIEW_AUDIT_LOGS,   
        Permissions.MANAGE_USERS,
        Permissions.VIEW_DOCUMENT,
        Permissions.DOWNLOAD_DATASET, 

    },

    "c_level": {
        Permissions.SEARCH_DOCS,
        Permissions.RAG_QUERY,
        Permissions.VIEW_FINANCE_DOCS,
        Permissions.VIEW_DOCUMENT,
        Permissions.DOWNLOAD_DATASET, 
    }
}
