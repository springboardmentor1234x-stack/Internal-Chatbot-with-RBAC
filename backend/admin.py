from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from data.database.db import get_db
from data.database.audit import get_audit_logs
from backend.auth.rbac import require_permission
from backend.auth.permissions import Permissions

router = APIRouter()

@router.get("/audit-logs")
def read_audit_logs(
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permissions.VIEW_AUDIT_LOGS))
):
    return get_audit_logs(db)
