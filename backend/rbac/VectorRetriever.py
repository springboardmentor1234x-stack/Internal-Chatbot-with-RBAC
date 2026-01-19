import numpy as np
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from services.audit_logger import AuditLogger
from functools import lru_cache

class VectorRetriever:
    """Vector-based document retrieval using ChromaDB"""
    
    def __init__(
        self,
        chroma_client,
        chunks: List[Dict[str, Any]],
        metadata: List[Dict[str, Any]],
        embeddings: np.ndarray,
        model_name: str = "all-MiniLM-L6-v2",
        audit_logger: AuditLogger = None
    ):
        self.chroma_client = chroma_client
        self.chunks = chunks
        self.metadata = metadata
        self.embeddings = embeddings
        self._query_embedding_cache = {}
        self.audit_logger = audit_logger or AuditLogger()
        
        @lru_cache(maxsize=1)
        def load_embedding_model(model_name):
            return SentenceTransformer(model_name)

        # Load embedding model
        self.audit_logger.log_info(f"Loading embedding model: {model_name}")
        self.model = load_embedding_model(model_name)
        
        # Create lookup dictionaries
        self.embedding_lookup = {
            chunk["chunk_id"]: embeddings[i]
            for i, chunk in enumerate(chunks)
        }
        
        self.chunk_lookup = {
            chunk["chunk_id"]: chunk
            for chunk in chunks
        }
        
        self.metadata_lookup = {
            chunk["chunk_id"]: metadata[i]
            for i, chunk in enumerate(chunks)
        }
        
        self.audit_logger.log_component_init("Vector Retriever", model_name)
    
    def embed_query(self, query: str) -> np.ndarray:
        if query in self._query_embedding_cache:
            return self._query_embedding_cache[query]

        embedding = self.model.encode([query])[0].reshape(1, -1)
        self._query_embedding_cache[query] = embedding
        return embedding
    
    def department_specific_search(
        self,
        query_embedding: np.ndarray,
        departments: List[str],
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search across multiple departments using ChromaDB collections
        
        Args:
            query_embedding: Query vector
            departments: List of accessible departments
            top_k: Number of results to retrieve per department
            
        Returns:
            List of search results with metadata
        """
        if not departments:
            self.audit_logger.log_warning("No accessible departments provided")
            return []
        
        try:
            collections = self.chroma_client.list_collections()
            
            if not collections:
                self.audit_logger.log_warning("No collections found in ChromaDB")
                return []
            
            collection_names = {col.name.lower() for col in collections}
            all_results = []
            
            # Search each accessible department
            for dept in departments:
                if dept == "hr":
                    dept = "human_resource"
                
                dept_lower = dept.lower()
                
                # Check if department collection exists
                if dept_lower not in collection_names:
                    self.audit_logger.log_warning(
                        f"Collection not found for department: {dept}"
                    )
                    continue
                
                try:
                    collection = self.chroma_client.get_collection(name=dept_lower)
                    
                    results = collection.query(
                        query_embeddings=[query_embedding.flatten().tolist()],
                        n_results=top_k
                    )
                    
                    # Process results
                    for i in range(len(results["ids"][0])):
                        chunk_id = results["ids"][0][i]
                        distance = results["distances"][0][i]
                        similarity = 1 - distance  # Convert distance to similarity
                        
                        chunk_data = self.chunk_lookup.get(chunk_id, {})
                        metadata = self.metadata_lookup.get(chunk_id, {})
                        
                        all_results.append({
                            "id": chunk_id,
                            "content": chunk_data.get("content", ""),
                            "metadata": metadata,
                            "similarity": float(similarity)
                        })
                
                except Exception as col_err:
                    self.audit_logger.log_error(
                        f"Collection Query Error",
                        f"Error querying {dept}: {str(col_err)}"
                    )
            
            # Sort globally by similarity
            all_results.sort(key=lambda x: x["similarity"], reverse=True)
            
            return all_results
        
        except Exception as e:
            self.audit_logger.log_error("ChromaDB Search Error", str(e))
            return []
    
    def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve chunk by ID"""
        return self.chunk_lookup.get(chunk_id)
    
    def get_metadata_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve metadata by chunk ID"""
        return self.metadata_lookup.get(chunk_id)
    
    def get_embedding_by_id(self, chunk_id: str) -> Optional[np.ndarray]:
        """Retrieve embedding by chunk ID"""
        return self.embedding_lookup.get(chunk_id)