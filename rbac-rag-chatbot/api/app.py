from fastapi import FastAPI, Depends
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles

from rag.orchestrator import run_rag
from embeddings.embedder import SentenceTransformerEmbedder
from vectorstore.chroma_store import ChromaVectorStore
from llm.client import OllamaLLMClient
from api.chat_routes import router as chat_history_router


from auth.auth_routes import router as auth_router
from auth.dependencies import get_current_user

# -----------------------------
# FASTAPI APP
# -----------------------------

app = FastAPI(title="RBAC RAG Chatbot")

app.mount("/docs", StaticFiles(directory="docs"), name="docs")

# -----------------------------
# REGISTER AUTH ROUTES
# -----------------------------

app.include_router(auth_router)
app.include_router(chat_history_router)


# -----------------------------
# BOOTSTRAP RAG COMPONENTS (ONCE)
# -----------------------------
# ❗ No ingestion
# ❗ No embedding
# ❗ No chunking
# ❗ Use persisted ChromaDB

embedder = SentenceTransformerEmbedder()
vector_store = ChromaVectorStore()
llm = OllamaLLMClient(model="mistral")

# -----------------------------
# REQUEST / RESPONSE MODELS
# -----------------------------

class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    answer: str
    sources: list
    confidence: str

# -----------------------------
# CHAT ENDPOINT (JWT PROTECTED)
# -----------------------------

@app.post("/chat", response_model=ChatResponse)
def chat(
    req: ChatRequest,
    user_context: dict = Depends(get_current_user)
):
    """
    Secure chat endpoint.
    User identity & role come ONLY from JWT.
    """

    result = run_rag(
        user_context=user_context,
        action="ASK_QUESTION",
        user_query=req.query,
        embedder=embedder,
        vector_store=vector_store,
        llm_client=llm,
    )

    return result
