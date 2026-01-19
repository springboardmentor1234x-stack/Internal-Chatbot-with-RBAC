from enum import Enum

class Permissions(str, Enum):
    SEARCH_DOCS = "search_docs"
    RAG_QUERY = "rag_query"          # ✅ ADD THIS
    VIEW_ADMIN_METRICS = "view_admin_metrics"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    MANAGE_USERS = "manage_users"
    VIEW_FINANCE_DOCS = "view_finance_docs"
    VIEW_DOCUMENT = "view_document"
    DOWNLOAD_DATASET = "download_dataset"


