# from fastapi import FastAPI, HTTPException, Depends
# from pydantic import BaseModel

# # Semantic search
# from semantic_search.semantic_search import semantic_search

# # Auth imports
# from auth.auth_utils import verify_password
# from auth.jwt_handler import create_access_token, create_refresh_token
# from auth.dependencies import get_current_user

# app = FastAPI(title="Company Internal Chatbot (RBAC)")

# # -------------------------------------------------
# # Dummy User Database (TEMP)

# fake_users = {
#     "admin@example.com": {
#         "username": "admin@example.com",
#         "hashed_password": "$2b$12$mQxIw8iOW2SHKIovquiexuves1FkakwBWoTPGiuWbonNbbZmcVbJm",
#         "role": "admin"
#     }
# }

# # -------------------------------------------------
# # Schemas
# # -------------------------------------------------
# class LoginRequest(BaseModel):
#     username: str
#     password: str


# class SearchRequest(BaseModel):
#     query: str
#     top_k: int = 3


# # -------------------------------------------------
# # Health Check
# # -------------------------------------------------
# @app.get("/")
# def health_check():
#     return {"status": "FastAPI is running"}


# # -------------------------------------------------
# # Login API (JWT Issuer)
# # -------------------------------------------------
# @app.post("/login")
# def login(request: LoginRequest):
#     user = fake_users.get(request.username)

#     if not user:
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     if not verify_password(request.password, user["hashed_password"]):
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     access_token = create_access_token(
#         subject=request.username,
#         role=user["role"]
#     )

#     refresh_token = create_refresh_token(
#         subject=request.username,
#         role=user["role"]
#     )

#     return {
#         "access_token": access_token,
#         "refresh_token": refresh_token,
#         "token_type": "bearer"
#     }


# # -------------------------------------------------
# # JWT + RBAC Protected Search API
# # -------------------------------------------------
# @app.post("/search")
# def search_docs(
#     request: SearchRequest,
#     current_user: dict = Depends(get_current_user)
# ):
#     """
#     JWT protected semantic search
#     """

#     output = semantic_search(
#         query=request.query,
#         user_role=current_user["role"],
#         final_k=request.top_k
#     )

#     results = []
#     for score, res in output["results"]:
#         results.append({
#             "chunk_id": res["chunk_id"],
#             "score": round(score, 4),
#             "document": res["document"],
#             "metadata": res["metadata"]
#         })

#     return {
#         "user": current_user["sub"],
#         "role": current_user["role"],
#         "authorized_chunks": output["authorized_count"],
#         "results": results
#     }

# from fastapi import FastAPI, HTTPException, Depends
# from pydantic import BaseModel

# from sqlalchemy.orm import Session

# # Database imports
# from database.db import get_db
# from database.crud import get_user_by_username
# from database.init_db import init_db

# # Semantic search
# from semantic_search.semantic_search import semantic_search

# # Auth imports
# from auth.auth_utils import verify_password
# from auth.jwt_handler import create_access_token, create_refresh_token
# from auth.dependencies import get_current_user

# # RBAC imports
# from auth.permissions import Permissions
# from auth.rbac import require_permission


# app = FastAPI(title="Company Internal Chatbot (RBAC)")




# # -------------------------------------------------
# # Schemas
# # -------------------------------------------------
# class LoginRequest(BaseModel):
#     username: str
#     password: str


# class SearchRequest(BaseModel):
#     query: str
#     top_k: int = 3


# # -------------------------------------------------
# # Health Check
# # -------------------------------------------------
# @app.get("/")
# def health_check():
#     return {"status": "FastAPI is running"}


# # -------------------------------------------------
# # Login API (JWT Issuer)
# # -------------------------------------------------
# @app.post("/auth/login")
# def login(
#     request: LoginRequest,
#     db: Session = Depends(get_db)
# ):
#     # 1️⃣ Fetch user from DB
#     user = get_user_by_username(db, request.username)

#     if not user:
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     # 2️⃣ Verify password
#     if not verify_password(request.password, user.hashed_password):
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     # 3️⃣ IMPORTANT FIX: role is a relationship
#     role_name = user.role.role_name

#     # 4️⃣ Create tokens
#     access_token = create_access_token(
#         subject=user.username,
#         role=role_name
#     )

#     refresh_token = create_refresh_token(
#         subject=user.username,
#         role=role_name
#     )

#     return {
#         "access_token": access_token,
#         "refresh_token": refresh_token,
#         "token_type": "bearer"
#     }

# @app.post("/auth/refresh")
# def refresh_access_token(
#     current_user: dict = Depends(get_current_user)
# ):
#     """
#     Uses REFRESH token to issue a NEW access token
#     """

#     # 1️⃣ Ensure token type is refresh
#     if current_user.get("type") != "refresh":
#         raise HTTPException(
#             status_code=401,
#             detail="Invalid refresh token"
#         )

#     # 2️⃣ Issue NEW access token
#     new_access_token = create_access_token(
#         subject=current_user["sub"],
#         role=current_user["role"]
#     )

#     return {
#         "access_token": new_access_token,
#         "token_type": "bearer"
#     }




# # -------------------------------------------------
# # JWT + PERMISSION RBAC + DATA RBAC (FINAL FORM)
# # -------------------------------------------------
# @app.post("/search")
# def search_docs(
#     request: SearchRequest,
#     current_user: dict = Depends(get_current_user),
#     _: bool = Depends(require_permission(Permissions.SEARCH_DOCS))
# ):
#     """
#     JWT protected semantic search
#     API-level RBAC: permission enforced
#     Data-level RBAC: enforced inside semantic_search
#     """

#     output = semantic_search(
#         query=request.query,
#         user_role=current_user["role"],
#         final_k=request.top_k
#     )

#     results = []
#     for score, res in output["results"]:
#         results.append({
#             "chunk_id": res["chunk_id"],
#             "score": round(score, 4),
#             "document": res["document"],
#             "metadata": res["metadata"]
#         })

#     return {
#         "user": current_user["sub"],
#         "role": current_user["role"],
#         "authorized_chunks": output["authorized_count"],
#         "results": results
#     }

# @app.get("/admin-metrics")
# def admin_metrics(
#     current_user: dict = Depends(get_current_user),
#     _: bool = Depends(require_permission(Permissions.VIEW_ADMIN_METRICS))
# ):
#     """
#     Admin-only metrics endpoint
#     Demonstrates API-level RBAC clearly
#     """

#     # Dummy metrics for demo (NO DB needed)
#     return {
#         "requested_by": current_user["sub"],
#         "role": current_user["role"],
#         "metrics": {
#             "total_users": 128,
#             "active_users": 96,
#             "total_documents": 342,
#             "total_search_queries_today": 154,
#             "system_status": "healthy"
#         }
#     }


# from fastapi import FastAPI, HTTPException, Depends
# from pydantic import BaseModel
# from sqlalchemy.orm import Session

# # -------------------------------------------------
# # Database imports
# # -------------------------------------------------
# from database.db import get_db
# from database.crud import get_user_by_username
# from database.init_db import init_db




# # -------------------------------------------------
# # Semantic search
# # -------------------------------------------------
# from semantic_search.semantic_search import semantic_search

# # -------------------------------------------------
# # Auth imports
# # -------------------------------------------------
# from auth.auth_utils import verify_password
# from auth.jwt_handler import create_access_token, create_refresh_token
# from auth.dependencies import get_current_user

# # -------------------------------------------------
# # RBAC imports
# # -------------------------------------------------
# from auth.permissions import Permissions
# from auth.rbac import require_permission


# # -------------------------------------------------
# # FastAPI App
# # -------------------------------------------------
# app = FastAPI(title="Company Internal Chatbot (RBAC)")


# # -------------------------------------------------
# # STARTUP EVENT (VERY IMPORTANT)
# # -------------------------------------------------
# @app.on_event("startup")
# def startup_event():
#     init_db()



# # -------------------------------------------------
# # Schemas
# # -------------------------------------------------
# class LoginRequest(BaseModel):
#     username: str
#     password: str


# class SearchRequest(BaseModel):
#     query: str
#     top_k: int = 3


# # -------------------------------------------------
# # Health Check
# # -------------------------------------------------
# @app.get("/")
# def health_check():
#     return {"status": "FastAPI is running"}


# # -------------------------------------------------
# # Login API (JWT Issuer)
# # -------------------------------------------------
# @app.post("/auth/login")
# def login(
#     request: LoginRequest,
#     db: Session = Depends(get_db)
# ):
#     # 1️⃣ Fetch user from DB
#     user = get_user_by_username(db, request.username)

#     if not user:
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     # 2️⃣ Verify password
#     if not verify_password(request.password, user.hashed_password):
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     # 3️⃣ Role comes from relationship
#     role_name = user.role.role_name

#     # 4️⃣ Create tokens
#     access_token = create_access_token(
#         subject=user.username,
#         role=role_name
#     )

#     refresh_token = create_refresh_token(
#         subject=user.username,
#         role=role_name
#     )

#     return {
#         "access_token": access_token,
#         "refresh_token": refresh_token,
#         "token_type": "bearer"
#     }


# # -------------------------------------------------
# # Refresh Token API
# # -------------------------------------------------
# @app.post("/auth/refresh")
# def refresh_access_token(
#     current_user: dict = Depends(get_current_user)
# ):
#     """
#     Uses REFRESH token to issue a NEW access token
#     """

#     if current_user.get("type") != "refresh":
#         raise HTTPException(
#             status_code=401,
#             detail="Invalid refresh token"
#         )

#     new_access_token = create_access_token(
#         subject=current_user["sub"],
#         role=current_user["role"]
#     )

#     return {
#         "access_token": new_access_token,
#         "token_type": "bearer"
#     }


# # -------------------------------------------------
# # SEARCH API (JWT + API RBAC + DATA RBAC)
# # -------------------------------------------------
# @app.post("/search")
# def search_docs(
#     request: SearchRequest,
#     current_user: dict = Depends(get_current_user),
#     _: bool = Depends(require_permission(Permissions.SEARCH_DOCS))
# ):
#     """
#     JWT protected semantic search
#     API-level RBAC enforced
#     Data-level RBAC enforced inside semantic_search
#     """

#     output = semantic_search(
#         query=request.query,
#         user_role=current_user["role"],
#         final_k=request.top_k
#     )

#     results = []
#     for score, res in output["results"]:
#         results.append({
#             "chunk_id": res["chunk_id"],
#             "score": round(score, 4),
#             "document": res["document"],
#             "metadata": res["metadata"]
#         })

#     return {
#         "user": current_user["sub"],
#         "role": current_user["role"],
#         "authorized_chunks": output["authorized_count"],
#         "results": results
#     }


# # -------------------------------------------------
# # ADMIN ONLY API
# # -------------------------------------------------
# @app.get("/admin-metrics")
# def admin_metrics(
#     current_user: dict = Depends(get_current_user),
#     _: bool = Depends(require_permission(Permissions.VIEW_ADMIN_METRICS))
# ):
#     """
#     Admin-only metrics endpoint
#     Demonstrates API-level RBAC clearly
#     """

#     return {
#         "requested_by": current_user["sub"],
#         "role": current_user["role"],
#         "metrics": {
#             "total_users": 128,
#             "active_users": 96,
#             "total_documents": 342,
#             "total_search_queries_today": 154,
#             "system_status": "healthy"
#         }
#     }

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

# -------------------------------------------------
# Database imports
# -------------------------------------------------
from database.db import get_db
from database.crud import get_user_by_username
from database.init_db import init_db

# -------------------------------------------------
# Semantic search
# -------------------------------------------------
from semantic_search.semantic_search import semantic_search

# -------------------------------------------------
# Auth imports
# -------------------------------------------------
from auth.auth_utils import verify_password
from auth.jwt_handler import create_access_token, create_refresh_token
from auth.dependencies import get_current_user

# -------------------------------------------------
# RBAC imports
# -------------------------------------------------
from auth.permissions import Permissions
from auth.rbac import require_permission


# -------------------------------------------------
# LIFESPAN (MODERN STARTUP HOOK)
# -------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs once when the application starts
    """
    init_db()
    yield


# -------------------------------------------------
# FastAPI App
# -------------------------------------------------
app = FastAPI(
    title="Company Internal Chatbot (RBAC)",
    lifespan=lifespan
)


# -------------------------------------------------
# Schemas
# -------------------------------------------------
class LoginRequest(BaseModel):
    username: str
    password: str


class SearchRequest(BaseModel):
    query: str
    top_k: int = 3


# -------------------------------------------------
# Health Check
# -------------------------------------------------
@app.get("/")
def health_check():
    return {"status": "FastAPI is running"}


# -------------------------------------------------
# Login API (JWT Issuer)
# -------------------------------------------------
@app.post("/auth/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    user = get_user_by_username(db, request.username)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    role_name = user.role.role_name

    access_token = create_access_token(
        subject=user.username,
        role=role_name
    )

    refresh_token = create_refresh_token(
        subject=user.username,
        role=role_name
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# -------------------------------------------------
# Refresh Token API
# -------------------------------------------------
@app.post("/auth/refresh")
def refresh_access_token(
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_access_token(
        subject=current_user["sub"],
        role=current_user["role"]
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }


# -------------------------------------------------
# SEARCH API (JWT + API RBAC + DATA RBAC)
# -------------------------------------------------
@app.post("/search")
def search_docs(
    request: SearchRequest,
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(require_permission(Permissions.SEARCH_DOCS))
):
    output = semantic_search(
        query=request.query,
        user_role=current_user["role"],
        final_k=request.top_k
    )

    results = []
    for score, res in output["results"]:
        results.append({
            "chunk_id": res["chunk_id"],
            "score": round(score, 4),
            "document": res["document"],
            "metadata": res["metadata"]
        })

    return {
        "user": current_user["sub"],
        "role": current_user["role"],
        "authorized_chunks": output["authorized_count"],
        "results": results
    }


# -------------------------------------------------
# ADMIN ONLY API
# -------------------------------------------------
@app.get("/admin-metrics")
def admin_metrics(
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(require_permission(Permissions.VIEW_ADMIN_METRICS))
):
    return {
        "requested_by": current_user["sub"],
        "role": current_user["role"],
        "metrics": {
            "total_users": 128,
            "active_users": 96,
            "total_documents": 342,
            "total_search_queries_today": 154,
            "system_status": "healthy"
        }
    }

