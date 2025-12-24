from typing import List, Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self, normalizer, retriever, rbac, ranker):
        self.normalizer = normalizer
        self.retriever = retriever
        self.rbac = rbac
        self.ranker = ranker
        
        logger.info("✓ RAG Pipeline initialized")
    
    def run(
        self,
        raw_query: str,
        # department: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing Query: \"{raw_query}\"")
        # logger.info(f"Department: {department or 'All'}")
        logger.info(f"{'='*60}\n")
        
        # Step 1: Query Normalization
        logger.info("Step 1: Query Normalization")
        normalized_query = self.normalizer.normalize(raw_query)
        logger.info(f"  Original: {raw_query}")
        logger.info(f"  Normalized: {normalized_query}\n")
        
        # Step 2: Generate query variants
        logger.info("Step 2: Query Expansion")
        query_variants = self.normalizer.generate_variants(normalized_query)
        logger.info(f"  Generated {len(query_variants)} query variants")
        for i, variant in enumerate(query_variants, 1):
            logger.info(f"    {i}. {variant}")
        logger.info("")
        
        # Step 3: Role Resolution
        logger.info("Step 3: Role Resolution")
        effective_roles = self.rbac.resolve_roles()
        logger.info(f"  User Roles: {self.rbac.user_roles}")
        logger.info(f"  Effective Roles (with inheritance): {effective_roles}")
        effective_permissions = self.rbac.get_effective_permissions()
        logger.info(f"  Effective Permissions: {effective_permissions}\n")
        
        # Step 4: Vector Retrieval
        logger.info("Step 4: Vector Retrieval")
        all_candidates = []
        
        for i, variant in enumerate(query_variants, 1):
            logger.info(f"  Retrieving for variant {i}: \"{variant}\"")
            query_emb = self.retriever.embed_query(variant)
            
            candidates = self.retriever.hybrid_search(
                query_emb,
                # department,
                top_k=top_k * 2  # Retrieve more for better re-ranking
            )
            
            logger.info(f"    Retrieved {len(candidates)} candidates")
            all_candidates.extend(candidates)
        
        logger.info(f"  Total candidates before filtering: {len(all_candidates)}\n")
        
        # Step 5: RBAC Filtering
        logger.info("Step 5: RBAC Filtering")
        allowed_candidates = []
        denied_count = 0
        
        for candidate in all_candidates:
            meta = candidate.get("metadata", {})
            
            if self.rbac.is_allowed(meta):
                allowed_candidates.append({
                    "id": candidate.get("id"),
                    "metadata": meta,
                    "similarity": candidate.get("similarity"),
                    "content": candidate.get("content", "")
                })
            else:
                denied_count += 1
        
        logger.info(f"  Allowed: {len(allowed_candidates)}")
        logger.info(f"  Denied: {denied_count}")
        
        if not allowed_candidates:
            logger.warning("  No candidates passed RBAC filtering\n")
            return []
        
        logger.info("")
        
        # Step 6: Re-ranking and Deduplication
        logger.info("Step 6: Re-ranking & Deduplication")
        
        # Use the primary query embedding for re-ranking
        primary_query_emb = self.retriever.embed_query(normalized_query)
        
        ranked_results = self.ranker.rerank(
            primary_query_emb,
            allowed_candidates,
            self.retriever.embedding_lookup
        )
        
        logger.info(f"  After re-ranking: {len(ranked_results)} results")
        logger.info(f"  Returning top {min(top_k, len(ranked_results))} results\n")
        
        # Step 7: Final Results
        final_results = ranked_results[:top_k]
        
        logger.info("Step 7: Final Results")
        for i, result in enumerate(final_results, 1):
            logger.info(f"  {i}. {result['id']} | Similarity: {result['similarity']:.4f}")
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Pipeline Complete: {len(final_results)} results returned")
        logger.info(f"{'='*60}\n")
       
        return final_results
    
    def validate_pipeline(self) -> bool:
        try:
            assert self.normalizer is not None, "Normalizer not initialized"
            assert self.retriever is not None, "Retriever not initialized"
            assert self.rbac is not None, "RBAC Engine not initialized"
            assert self.ranker is not None, "Ranker not initialized"
            
            logger.info("✓ Pipeline validation successful")
            return True
            
        except AssertionError as e:
            logger.error(f"✗ Pipeline validation failed: {str(e)}")
            return False
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        return {
            "user_roles": self.rbac.user_roles,
            "effective_permissions": self.rbac.get_effective_permissions(),
            "similarity_threshold": self.ranker.threshold,
            "total_chunks": len(self.retriever.chunks),
            "total_embeddings": len(self.retriever.embeddings)
        }