from typing import List, Dict
import numpy as np
from rbac.data_rbac import is_chunk_allowed


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


class VectorStore:
    def __init__(self, embedded_chunks: List[Dict]):
        self.vectors = [
            {
                "chunk_id": c["chunk_id"],
                "vector": np.array(c["vector"]),
                "text": c["text"],
                "metadata": c["metadata"],
            }
            for c in embedded_chunks
        ]


    def search(self, query_vector, user_context, top_k=5, threshold=0.3):
        results = []

        knn_results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        for doc, metadata, distance in zip(
            knn_results["documents"][0],
            knn_results["metadatas"][0],
            knn_results["distances"][0]
        ):
            # Convert distance → similarity score
            score = 1 - distance

            # Thresholding
            if score < threshold:
                continue

            # DATA-LEVEL RBAC
            if not is_chunk_allowed(metadata, user_context):
                continue

            results.append({
                "content": doc,
                "metadata": metadata,
                "score": score   # ✅ THIS LINE
            })

        return results

