from typing import List, Dict
from sentence_transformers import SentenceTransformer

# Load model ONLY ONCE (global singleton)
_model = None


class EmbeddingClient:
    """
    LLM-agnostic embedding interface
    """

    def embed(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError


class SentenceTransformerEmbedder(EmbeddingClient):
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        global _model
        if _model is None:
            print(f"🔄 Loading embedding model: {model_name}")
            _model = SentenceTransformer(model_name)
        self.model = _model

    def embed(self, texts):
        return self.model.encode(texts, show_progress_bar=False)


def embed_chunks(chunks, embedder):
    texts = [chunk["text"] for chunk in chunks]
    vectors = embedder.embed(texts)  # already List[List[float]]

    embedded_chunks = []

    for i, chunk in enumerate(chunks):
        embedded_chunks.append({
            "chunk_id": chunk["chunk_id"],
            "text": chunk["text"],
            "metadata": chunk["metadata"],
            "embedding": vectors[i],  # ✅ already a list
        })

    return embedded_chunks
