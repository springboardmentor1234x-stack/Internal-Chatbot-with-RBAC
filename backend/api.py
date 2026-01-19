# backend/api.py

from dotenv import load_dotenv
from contextlib import asynccontextmanager
from pathlib import Path
import json

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

load_dotenv()

# -----------------------------------------------------
# Database
# -----------------------------------------------------
from data.database.db import get_db
from data.database.crud import get_user_by_username
from data.database.init_db import init_db
from data.database.audit import log_action, get_audit_logs

# -----------------------------------------------------
# RAG
# -----------------------------------------------------
from backend.semantic_search.semantic_search import semantic_search
from backend.rag.orchestrator import run_rag_pipeline

# -----------------------------------------------------
# Auth
# -----------------------------------------------------
from backend.auth.auth_utils import verify_password
from backend.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    verify_token
)
from backend.auth.dependencies import get_current_user
from backend.auth.token_blacklist import token_blacklist

# -----------------------------------------------------
# RBAC
# -----------------------------------------------------
from backend.auth.permissions import Permissions
from backend.auth.rbac import require_permission

from backend.admin import router as admin_router

# ======================================================
# RBAC JSON LOADER (NEW – REQUIRED)
# ======================================================
# ======================================================
# RBAC JSON LOADER (FIXED PATH ✅)
# ======================================================
BASE_DIR = Path(__file__).resolve().parent      # backend/
RBAC_PATH = BASE_DIR / "RBAC" / "rbac.json"

with open(RBAC_PATH, "r", encoding="utf-8") as f:
    RBAC_DATA = json.load(f)

ROLES = RBAC_DATA["roles"]



def resolve_permissions(role: str) -> set:
    """
    Resolve permissions including inherited roles
    """
    visited = set()
    permissions = set()

    def walk(r):
        if r in visited:
            return
        visited.add(r)

        role_data = ROLES.get(r, {})
        permissions.update(role_data.get("permissions", []))

        for parent in role_data.get("inherits", []):
            walk(parent)

    walk(role)
    return permissions


# ======================================================
# FastAPI App
# ======================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Company Internal Chatbot (RBAC + RAG)",
    lifespan=lifespan
)

app.include_router(admin_router)

# ======================================================
# Schemas
# ======================================================
class LoginRequest(BaseModel):
    username: str
    password: str


class SearchRequest(BaseModel):
    query: str
    top_k: int = 3


class AskRequest(BaseModel):
    query: str
    top_k: int = 5


class RefreshRequest(BaseModel):
    refresh_token: str


# ======================================================
# Health
# ======================================================
@app.get("/health")
def health_check():
    return {"status": "ok"}


# ======================================================
# LOGIN
# ======================================================
@app.post("/auth/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = get_user_by_username(db, request.username)

        if not user or not user.is_active:
            log_action(username=request.username, action="LOGIN_FAILED")
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not verify_password(request.password, user.hashed_password):
            log_action(
                username=request.username,
                role=user.role.role_name,
                action="LOGIN_FAILED"
            )
            raise HTTPException(status_code=401, detail="Invalid credentials")

        role_name = user.role.role_name

        log_action(
            user_id=user.user_id,
            username=user.username,
            role=role_name,
            action="LOGIN"
        )

        return {
            "access_token": create_access_token(
                subject=user.username,
                role=role_name,
                user_id=user.user_id
            ),
            "refresh_token": create_refresh_token(
                subject=user.username,
                role=role_name,
                user_id=user.user_id
            ),
            "token_type": "bearer"
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Authentication service unavailable"
        )


# ======================================================
# USER PROFILE
# ======================================================
@app.get("/user/profile")
def get_user_profile(current_user: dict = Depends(get_current_user)):
    return {
        "username": current_user["sub"],
        "role": current_user["role"],
        "user_id": current_user["user_id"]
    }


# ======================================================
# LOGOUT
# ======================================================
@app.post("/auth/logout")
def logout(current_user: dict = Depends(get_current_user)):
    token_blacklist.blacklist(current_user["raw_token"])

    log_action(
        user_id=current_user["user_id"],
        username=current_user["sub"],
        role=current_user["role"],
        action="LOGOUT"
    )

    return {"detail": "Logged out"}


# ======================================================
# REFRESH TOKEN
# ======================================================
@app.post("/auth/refresh")
def refresh_access_token(request: RefreshRequest):
    payload = verify_token(request.refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    return {
        "access_token": create_access_token(
            subject=payload["sub"],
            role=payload["role"],
            user_id=payload["user_id"]
        ),
        "token_type": "bearer"
    }


# ======================================================
# SEARCH
# ======================================================
@app.post("/search")
def search_docs(
    request: SearchRequest,
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(require_permission(Permissions.SEARCH_DOCS))
):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    output = semantic_search(
        query=request.query,
        user_role=current_user["role"],
        final_k=min(request.top_k, 10)
    )

    safe_results = [
        {
            "score": score,
            "document": res.get("document"),
            "metadata": res.get("metadata", {})
        }
        for score, res in output.get("results", [])
    ]

    log_action(
        user_id=current_user["user_id"],
        username=current_user["sub"],
        role=current_user["role"],
        action="SEARCH",
        query=request.query,
        documents=[r["document"] for r in safe_results]
    )

    return {
        "authorized_chunks": output["authorized_count"],
        "results": safe_results
    }


# ======================================================
# ASK (RAG)
# ======================================================
@app.post("/ask")
def ask_question(
    request: AskRequest,
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(require_permission(Permissions.RAG_QUERY))
):
    rag_result = run_rag_pipeline(
        user=current_user,
        query=request.query,
        top_k=min(request.top_k, 5)
    )

    log_action(
        user_id=current_user["user_id"],
        username=current_user["sub"],
        role=current_user["role"],
        action="RAG_QUERY",
        query=request.query,
        documents=[c.get("doc_name") for c in rag_result.get("citations", [])]
    )

    return rag_result


# ======================================================
# ADMIN AUDIT (UNCHANGED)
# ======================================================
@app.get("/admin/audit/logs")
def view_audit_logs(
    db: Session = Depends(get_db),
    _: bool = Depends(require_permission(Permissions.VIEW_AUDIT_LOGS))
):
    return [
        {
            "user_id": log.user_id,
            "username": log.username,
            "role": log.role,
            "action": log.action,
            "query": log.query,
            "documents": log.get_documents(),
            "timestamp": log.timestamp
        }
        for log in get_audit_logs(db)
    ]


# ======================================================
# SECURE DOWNLOAD (RBAC.JSON ENFORCED ✅)
# ======================================================
@app.get("/downloads/normalized_datasets/{department}/{filename}")
def download_normalized_dataset(
    department: str,
    filename: str,
    current_user: dict = Depends(get_current_user)
):
    department = department.strip().lower()

    if not filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Invalid file")

    role = current_user["role"]
    permissions = resolve_permissions(role)

    # Admin wildcard support
    if "*" not in permissions:
        required_permission = f"read:{department}"
        if required_permission not in permissions:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to download this dataset"
            )

    base_dir = Path("normalized_datasets").resolve()
    file_path = (base_dir / department / filename).resolve()

    if not str(file_path).startswith(str(base_dir)):
        raise HTTPException(status_code=403, detail="Invalid path")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    log_action(
        user_id=current_user["user_id"],
        username=current_user["sub"],
        role=current_user["role"],
        action="DOWNLOAD_DATASET",
        documents=[filename]
    )

    return FileResponse(file_path)
