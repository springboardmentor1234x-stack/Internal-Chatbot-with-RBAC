import numpy as np
from typing import List, Dict, Any
from sklearn.metrics.pairwise import cosine_similarity

class ReRanker:
    """Re-rank and deduplicate search results"""
    
    def __init__(self, similarity_threshold: float, audit_logger):
        self.threshold = similarity_threshold
        self.audit_logger = audit_logger
        
        self.audit_logger.log_component_init(
            "Re-ranker", 
            f"threshold: {similarity_threshold}"
        )
    
    def rerank(
        self,
        query_embedding: np.ndarray,
        candidates: List[Dict[str, Any]],
        embedding_lookup: Dict[str, np.ndarray]
    ) -> List[Dict[str, Any]]:
        """
        Re-rank candidates based on similarity and remove duplicates
        
        Args:
            query_embedding: Query vector
            candidates: List of candidate documents
            embedding_lookup: Dictionary mapping chunk IDs to embeddings
            
        Returns:
            Ranked and deduplicated list of results
        """
        # Re-compute similarities for consistency
        scored = self._rescore_candidates(
            query_embedding,
            candidates,
            embedding_lookup
        )
        
        # Apply similarity threshold
        filtered = self._apply_threshold(scored)
        
        if not filtered:
            self.audit_logger.log_info("No candidates passed similarity threshold")
            return []
        
        # Remove duplicates
        deduped = self._remove_duplicates(filtered)
        
        # Sort by similarity (descending)
        deduped.sort(key=lambda x: x["similarity"], reverse=True)
        
        return deduped
    
    def _rescore_candidates(
        self,
        query_embedding: np.ndarray,
        candidates: List[Dict[str, Any]],
        embedding_lookup: Dict[str, np.ndarray]
    ) -> List[Dict[str, Any]]:
        """Re-compute similarity scores"""
        scored = []
        
        for candidate in candidates:
            chunk_id = candidate.get("id")
            
            # Get embedding from lookup
            chunk_embedding = embedding_lookup.get(chunk_id)
            
            if chunk_embedding is None:
                self.audit_logger.log_warning(f"No embedding found for {chunk_id}")
                continue
            
            # Compute cosine similarity
            if chunk_embedding.ndim == 1:
                chunk_embedding = chunk_embedding.reshape(1, -1)
            
            similarity = cosine_similarity(query_embedding, chunk_embedding)[0][0]
            
            scored.append({
                "id": chunk_id,
                "content": candidate.get("content", ""),
                "metadata": candidate.get("metadata", {}),
                "similarity": float(similarity)
            })
        
        return scored
    
    def _apply_threshold(
        self,
        candidates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Filter candidates below similarity threshold"""
        filtered = [
            c for c in candidates
            if c["similarity"] >= self.threshold
        ]
        
        removed = len(candidates) - len(filtered)
        if removed > 0:
            self.audit_logger.log_info(
                f"Removed {removed} low-confidence matches (< {self.threshold})"
            )
        
        return filtered
    
    def _remove_duplicates(
        self,
        candidates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Remove exact duplicate chunks"""
        seen_ids = set()
        unique = []
        
        for candidate in candidates:
            chunk_id = candidate["id"]
            if chunk_id not in seen_ids:
                seen_ids.add(chunk_id)
                unique.append(candidate)
        
        exact_dupes = len(candidates) - len(unique)
        if exact_dupes > 0:
            self.audit_logger.log_info(f"Removed {exact_dupes} exact duplicates")
        
        return unique
    
    def apply_diversity_filter(
        self,
        candidates: List[Dict[str, Any]],
        max_per_source: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Apply diversity filter to limit results per source document
        
        Args:
            candidates: List of candidate documents
            max_per_source: Maximum results per source document
            
        Returns:
            Filtered list with diversity constraint
        """
        source_counts = {}
        diverse_results = []
        
        for candidate in candidates:
            source = candidate["metadata"].get("source_document", "")
            count = source_counts.get(source, 0)
            
            if count < max_per_source:
                diverse_results.append(candidate)
                source_counts[source] = count + 1
        
        return diverse_results