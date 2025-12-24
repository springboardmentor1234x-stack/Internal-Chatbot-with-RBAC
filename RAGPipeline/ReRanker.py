import numpy as np
from typing import List, Dict, Any
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

class ReRanker:
    def __init__(self, similarity_threshold):
        self.threshold = similarity_threshold
        logger.info(f"✓ Re-ranker initialized (threshold: {similarity_threshold})")
    
    def rerank(
        self,
        query_embedding: np.ndarray,
        candidates: List[Dict[str, Any]],
        embedding_lookup: Dict[str, np.ndarray]
    ) -> List[Dict[str, Any]]:
        # Step 1: Re-compute similarities for consistency
        scored = self._rescore_candidates(
            query_embedding,
            candidates,
            embedding_lookup
        )
        
        # Step 2: Apply similarity threshold
        filtered = self._apply_threshold(scored)
        
        if not filtered:
            logger.info("No candidates passed similarity threshold")
            return []
        
        # Step 3: Remove duplicates
        deduped = self._remove_duplicates(filtered)
        
        # Step 4: Sort by similarity (descending)
        deduped.sort(key=lambda x: x["similarity"], reverse=True)
        
        return deduped
    
    def _rescore_candidates(
        self,
        query_embedding: np.ndarray,
        candidates: List[Dict[str, Any]],
        embedding_lookup: Dict[str, np.ndarray]
    ) -> List[Dict[str, Any]]:
        
        scored = []
        
        for candidate in candidates:
            chunk_id = candidate.get("id")
            
            # Get embedding from lookup
            chunk_embedding = embedding_lookup.get(chunk_id)
            
            if chunk_embedding is None:
                logger.warning(f"No embedding found for {chunk_id}")
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
        
        filtered = [
            c for c in candidates
            if c["similarity"] >= self.threshold
        ]

        # filtered = []
        # for c in candidates:
        #     print(c["similarity"])
        #     if c["similarity"] >= self.threshold:
        #         filtered.append(c)
        
        removed = len(candidates) - len(filtered)
        if removed > 0:
            logger.info(f"Removed {removed} low-confidence matches (< {self.threshold})")
        
        return filtered
    
    def _remove_duplicates(
        self,
        candidates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
       
        # Step 1: Remove exact duplicates by chunk_id
        seen_ids = set()
        unique_by_id = []
        
        for candidate in candidates:
            chunk_id = candidate["id"]
            if chunk_id not in seen_ids:
                seen_ids.add(chunk_id)
                unique_by_id.append(candidate)
        
        exact_dupes = len(candidates) - len(unique_by_id)
        if exact_dupes > 0:
            logger.info(f"Removed {exact_dupes} exact duplicates")
        
        # # Step 2: Remove document-level duplicates (keep highest similarity)
        # doc_best = {}
        
        # for candidate in unique_by_id:
        #     source_doc = candidate["metadata"].get("source_document", "")
            
        #     if source_doc not in doc_best:
        #         doc_best[source_doc] = candidate
        #     else:
        #         # Keep the one with higher similarity
        #         if candidate["similarity"] > doc_best[source_doc]["similarity"]:
        #             doc_best[source_doc] = candidate
        
        # unique_by_doc = list(doc_best.values())
        # doc_dupes = len(unique_by_id) - len(unique_by_doc)
        # if doc_dupes > 0:
        #     logger.info(f"Removed {doc_dupes} document-level duplicates")
        
        # Step 3: Remove semantic duplicates (optional, aggressive)
        # This is useful when multiple chunks from the same document are very similar
        # final_unique = self._remove_semantic_duplicates(
        #     unique_by_id,
        #     similarity_threshold=0.95
        # )
        
        # semantic_dupes = len(unique_by_id) - len(final_unique)
        # if semantic_dupes > 0:
        #     logger.info(f"Removed {semantic_dupes} semantic duplicates")
        
        return unique_by_id
    
    def _remove_semantic_duplicates(
        self,
        candidates: List[Dict[str, Any]],
        similarity_threshold: float = 0.95
    ) -> List[Dict[str, Any]]:
        
        if len(candidates) <= 3:
            return candidates
        
        # Simple content-based similarity check
        unique = []
        
        for candidate in candidates:
            content = candidate.get("content", "")
            is_duplicate = False
            
            for existing in unique:
                existing_content = existing.get("content", "")
                
                # Simple overlap check (tokens in common)
                overlap = self._content_overlap(content, existing_content)
                
                if overlap > similarity_threshold:
                    # Keep the one with higher similarity
                    if candidate["similarity"] > existing["similarity"]:
                        unique.remove(existing)
                        unique.append(candidate)
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique.append(candidate)
        
        return unique
    
    def _content_overlap(self, content1: str, content2: str) -> float:
        
        # Tokenize
        tokens1 = set(content1.lower().split())
        tokens2 = set(content2.lower().split())
        
        if not tokens1 or not tokens2:
            return 0.0
        
        # Jaccard similarity
        intersection = tokens1 & tokens2
        union = tokens1 | tokens2
        
        return len(intersection) / len(union) if union else 0.0
    
    def apply_diversity_filter(
        self,
        candidates: List[Dict[str, Any]],
        max_per_source: int = 2
    ) -> List[Dict[str, Any]]:
        
        source_counts = {}
        diverse_results = []
        
        for candidate in candidates:
            source = candidate["metadata"].get("source_document", "")
            count = source_counts.get(source, 0)
            
            if count < max_per_source:
                diverse_results.append(candidate)
                source_counts[source] = count + 1
        
        return diverse_results
    
    def boost_by_metadata(
        self,
        candidates: List[Dict[str, Any]],
        boost_rules: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        
        boosted = []
        
        for candidate in candidates:
            score = candidate["similarity"]
            metadata = candidate.get("metadata", {})
            
            # Apply boosts
            for field, multiplier in boost_rules.items():
                if field in metadata:
                    score *= multiplier
            
            boosted.append({
                **candidate,
                "similarity": min(score, 1.0)  # Cap at 1.0
            })
        
        return boosted