# data/database/audit.py

from data.database.db import SessionLocal
from data.database.models.audit_log import AuditLog
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def log_action(
    username: str,
    action: str,
    role: str = None,
    user_id: int = None,
    query: str = None,
    documents: list = None
):
    """
    Central audit logging function.

    This function is called from:
    - Login / Logout APIs
    - RBAC checks (allowed / denied)
    - Search endpoints
    - RAG pipelines

    Parameters:
    - username  : Authenticated username
    - action    : LOGIN | LOGOUT | SEARCH | RAG_QUERY | RBAC_DENIED | RBAC_ALLOWED
    - role      : User role at time of action
    - user_id   : Database user ID (optional)
    - query     : Search or RAG query
    - documents : List of accessed documents
    """

    db = SessionLocal()

    try:
        audit_log = AuditLog(
            username=username,
            role=role,
            user_id=user_id,
            action=action,
            query=query,
            timestamp=datetime.utcnow()
        )

        # Always store document list (even empty)
        audit_log.set_documents(documents or [])

        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)

        return audit_log

    except Exception:
        db.rollback()
        logging.error("❌ Audit logging failed", exc_info=True)

    finally:
        db.close()

def get_audit_logs(db, limit: int = 100):
    """
    Read-only helper for admin audit viewer
    """
    return (
        db.query(AuditLog)
        .order_by(AuditLog.timestamp.desc())
        .limit(limit)
        .all()
    )