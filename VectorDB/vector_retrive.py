import json
import numpy as np
from typing import List, Dict, Tuple


class VectorRetriever:
    def __init__(self, embedding_path="embeddings/embedding.json"):
        with open(embedding_path, "r") as f:
            self.embeddings: Dict[str, List[float]] = json.load(f)

    def cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def retrieve(
        self,
        query_embedding: List[float],
        allowed_chunk_ids: List[str],
        top_k: int = 3
    ) -> List[Tuple[str, float]]:
        """
        Returns:
        [
          ('CHUNK_ID', similarity_score),
          ...
        ]
        """

        query_vec = np.array(query_embedding)
        scores = []

        for chunk_id in allowed_chunk_ids:
            if chunk_id not in self.embeddings:
                continue

            chunk_vec = np.array(self.embeddings[chunk_id])
            score = self.cosine_similarity(query_vec, chunk_vec)
            scores.append((chunk_id, float(score)))

        scores.sort(key=lambda x: x[1], reverse=True)
        print("DEBUG SCORE:", chunk_id, score)

        return scores[:top_k]