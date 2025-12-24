import numpy as np
from typing import List, Dict, Any, Optional
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

class VectorRetriever:
    def __init__(
        self,
        chroma_client,
        chunks: List[Dict[str, Any]],
        metadata: List[Dict[str, Any]],
        embeddings: np.ndarray,
        model_name: str = "all-MiniLM-L6-v2"
    ):
        self.chroma_client = chroma_client
        self.chunks = chunks
        self.metadata = metadata
        self.embeddings = embeddings
        
        # Load embedding model
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        logger.info("✓ Embedding model loaded")
        
        # Create embedding lookup dictionary
        self.embedding_lookup = {
            chunk["chunk_id"]: embeddings[i]
            for i, chunk in enumerate(chunks)
        }
        
        # Create chunk lookup dictionary
        self.chunk_lookup = {
            chunk["chunk_id"]: chunk
            for chunk in chunks
        }
        
        # Create metadata lookup dictionary
        self.metadata_lookup = {
            chunk["chunk_id"]: metadata[i]
            for i, chunk in enumerate(chunks)
        }
    
    def embed_query(self, query: str) -> np.ndarray:
        embedding = self.model.encode([query])[0]
        return embedding.reshape(1, -1)
    
    def custom_knn(
        self,
        query_embedding: np.ndarray,
        department: Optional[str] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        # Filter by department if specified
        if department:
            dept_lower = department.lower()
            valid_indices = [
                i for i, meta in enumerate(self.metadata)
                if meta.get("department", "").lower() == dept_lower
            ]
            
            if not valid_indices:
                logger.warning(f"No chunks found for department: {department}")
                return []
            
            filtered_embeddings = self.embeddings[valid_indices]
            filtered_chunks = [self.chunks[i] for i in valid_indices]
            filtered_metadata = [self.metadata[i] for i in valid_indices]
        else:
            filtered_embeddings = self.embeddings
            filtered_chunks = self.chunks
            filtered_metadata = self.metadata
        
        # Compute cosine similarities
        similarities = cosine_similarity(query_embedding, filtered_embeddings)[0]
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Build results
        results = []
        for idx in top_indices:
            chunk = filtered_chunks[idx]
            meta = filtered_metadata[idx]
            
            results.append({
                "id": chunk["chunk_id"],
                "content": chunk["content"],
                "metadata": meta,
                "similarity": float(similarities[idx])
            })
        
        return results
    
    def chroma_search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        try:
            collections = self.chroma_client.list_collections()

            if not collections:
                logger.warning("No collections found in ChromaDB")
                return []

            all_results = []

            for col in collections:
                try:
                    collection = self.chroma_client.get_collection(name=col.name)

                    results = collection.query(
                        query_embeddings=[query_embedding.flatten().tolist()],
                        n_results=top_k
                    )

                    for i in range(len(results["ids"][0])):
                        chunk_id = results["ids"][0][i]
                        distance = results["distances"][0][i]

                        similarity = 1 - distance  # cosine similarity

                        all_results.append({
                            "id": chunk_id,
                            "content": self.chunk_lookup.get(chunk_id, {}).get("content", ""),
                            "metadata": self.metadata_lookup.get(chunk_id, {}),
                            "similarity": float(similarity)
                        })

                except Exception as col_err:
                    logger.error(
                        f"Error querying collection {col.name}: {str(col_err)}"
                    )

            # Sort globally by similarity
            all_results.sort(key=lambda x: x["similarity"], reverse=True)

            return all_results[: top_k * 2]

        except Exception as e:
            logger.error(f"Global ChromaDB search error: {str(e)}")
            return []
    
    def hybrid_search(
        self,
        query_embedding: np.ndarray,
        department: Optional[str] = None,
        top_k: int = 10,
        use_chroma: bool = True
    ) -> List[Dict[str, Any]]:
        
        results = []
        
        # Get results from custom KNN
        knn_results = self.custom_knn(query_embedding, department, top_k)
        results.extend(knn_results)
        
        # Optionally add ChromaDB results
        if use_chroma and department:
            chroma_results = self.chroma_search(query_embedding, department, top_k)
            results.extend(chroma_results)
        
        # Remove duplicates based on chunk_id
        seen_ids = set()
        unique_results = []
        
        for result in results:
            if result["id"] not in seen_ids:
                seen_ids.add(result["id"])
                unique_results.append(result)
        
        # Sort by similarity
        unique_results.sort(key=lambda x: x["similarity"], reverse=True)
        
        return unique_results
    
    def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        return self.chunk_lookup.get(chunk_id)
    
    def get_metadata_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        return self.metadata_lookup.get(chunk_id)
    
    def get_embedding_by_id(self, chunk_id: str) -> Optional[np.ndarray]:
        return self.embedding_lookup.get(chunk_id)
    
    def search_by_keywords(
        self,
        keywords: List[str],
        department: Optional[str] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        # Filter by department
        if department:
            dept_lower = department.lower()
            filtered_chunks = [
                (i, chunk) for i, chunk in enumerate(self.chunks)
                if self.metadata[i].get("department", "").lower() == dept_lower
            ]
        else:
            filtered_chunks = list(enumerate(self.chunks))
        
        # Score chunks by keyword matches
        scored_chunks = []
        for idx, chunk in filtered_chunks:
            content_lower = chunk["content"].lower()
            score = sum(content_lower.count(kw.lower()) for kw in keywords)
            
            if score > 0:
                scored_chunks.append({
                    "id": chunk["chunk_id"],
                    "content": chunk["content"],
                    "metadata": self.metadata[idx],
                    "similarity": float(score) / len(keywords)  # Normalize
                })
        
        # Sort by score
        scored_chunks.sort(key=lambda x: x["similarity"], reverse=True)
        
        return scored_chunks[:top_k]