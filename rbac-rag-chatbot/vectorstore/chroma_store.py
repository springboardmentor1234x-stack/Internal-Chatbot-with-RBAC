import chromadb
from typing import List, Dict


class ChromaVectorStore:
    def __init__(self, persist_dir: str = "vector_db"):
        self.client = chromadb.PersistentClient(path=persist_dir)

        self.collection = self.client.get_or_create_collection(
            name="company_docs",
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(self, embedded_chunks: List[Dict]):
        for chunk in embedded_chunks:
            self.collection.add(
                documents=[chunk["text"]],
                embeddings=[chunk["embedding"]],
                metadatas=[chunk["metadata"]],
                ids=[chunk["chunk_id"]],
            )



    def search(
        self,
        *,
        query_vector,
        user_context,
        top_k: int,
        threshold: float
    ):
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
        )

        filtered = []

        for i, doc in enumerate(results["documents"][0]):
            metadata = results["metadatas"][0][i]
            distance = results["distances"][0][i]

            # Cosine similarity = 1 - cosine distance
            similarity = 1 - distance

            if similarity < threshold:
                continue


            # DATA-LEVEL RBAC
            if metadata["department"] != "general":
                if metadata["department"].upper() != user_context["role"]:
                    continue

            filtered.append({
                "text": doc,
                "metadata": metadata,
                "chunk_id": results["ids"][0][i],
                "score": similarity,
            })

        return filtered
