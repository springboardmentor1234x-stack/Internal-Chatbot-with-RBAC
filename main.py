from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

# ---------------- REQUEST MODEL ----------------
class RAGRequest(BaseModel):
    question: str


# ---------------- AUTH & RBAC ----------------
from auth import router as auth_router
from security import verify_token
from rbac import require_permission

# ---------------- DB ----------------
from database import engine, Base

# ---------------- RAG ----------------
from rag_pipeline import generate_answer


# ---------------- APP ----------------
app = FastAPI()

# Bearer scheme (GLOBAL)
bearer_scheme = HTTPBearer()

# Create DB tables
Base.metadata.create_all(bind=engine)

# Include auth routes
app.include_router(auth_router)


# ---------------- SWAGGER AUTH ----------------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Secure RAG Auth Project",
        version="1.0.0",
        description="JWT + RBAC + Secure RAG",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# ---------------- HOME ----------------
@app.get("/")
def home():
    return {"message": "FastAPI server is running 🚀"}


# ---------------- PROTECTED ----------------
@app.get("/protected")
def protected_route(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Token missing")

    token = authorization.split(" ")[1]
    payload = verify_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {
        "message": "Access granted",
        "user": payload["sub"]
    }


# ---------------- RBAC ----------------
@app.get("/search")
def search(user=Depends(require_permission("search"))):
    return {
        "message": "Search allowed",
        "user": user["sub"],
        "role": user["role"]
    }


# ---------------- SECURE RAG ----------------
@app.post("/rag/query")
def query_rag(
    data: RAGRequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    token = credentials.credentials
    payload = verify_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {
        "user": payload["sub"],
        "role": payload["role"],
        "answer": generate_answer(data.question)
    }
