from ingestion.loader import ingest_documents
from chunking.chunker import chunk_documents
from normalization.normalizer import normalize_chunks
from embeddings.embedder import SentenceTransformerEmbedder, embed_chunks
from vectorstore.retriever import VectorStore
from llm.client import MockLLMClient
from rag.orchestrator import run_rag

# -----------------------------
# BOOTSTRAP SYSTEM
# -----------------------------

docs = ingest_documents("datasets/Fintech-data")
chunks = chunk_documents(docs)
normalized_chunks = normalize_chunks(chunks)

embedder = SentenceTransformerEmbedder()
embedded_chunks = embed_chunks(normalized_chunks, embedder)

vector_store = VectorStore(embedded_chunks)
llm = MockLLMClient()

# -----------------------------
# RUN RAG
# -----------------------------

user_context = {
    "user_id": "u1",
    "role": "ENGINEER",
}

response = run_rag(
    user_context=user_context,
    action="ASK_QUESTION",
    user_query="Explain the system architecture",
    embedder=embedder,
    vector_store=vector_store,
    llm_client=llm,
)

print("\nFINAL RAG RESPONSE:\n")
print(response)
