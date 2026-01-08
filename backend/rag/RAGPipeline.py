from typing import List, Dict, Any
from services.audit_logger import AuditLogger
from rag.llm_service import LLMService
from rag.prompt_builder import PromptBuilder

class CompleteRAGPipeline:
    """
    Complete RAG Pipeline: Retrieval + LLM Response Generation
    
    Flow:
    1. Query Normalization & Expansion
    2. RBAC Role Resolution (Get Accessible Departments)
    3. Department-Specific Vector Retrieval (Pre-filtered by RBAC)
    4. Re-ranking & Deduplication
    5. Prompt Building with Context
    6. LLM Response Generation
    7. Source Citation Formatting
    8. Return Complete Response
    """
    
    def __init__(
        self,
        normalizer,
        retriever,
        rbac,
        ranker,
        llm_service: LLMService = None,
        prompt_builder: PromptBuilder = None,
        audit_logger: AuditLogger = None
    ):
        self.normalizer = normalizer
        self.retriever = retriever
        self.rbac = rbac
        self.ranker = ranker
        self.llm_service = llm_service or LLMService()
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.audit_logger = audit_logger or AuditLogger()
        
        self.audit_logger.log_component_init("Complete RAG Pipeline")
    
    def process_query(
        self,
        query: str,
        top_k: int = 5,
        max_tokens: int = 500,
        username: str = None
    ) -> Dict[str, Any]:
        """
        Execute complete RAG pipeline: retrieval + LLM generation
        
        Args:
            query: User's raw search query
            top_k: Number of documents to retrieve
            max_tokens: Maximum tokens for LLM response
            username: Username for audit logging
            
        Returns:
            Complete response with answer, confidence, sources
        """
        # Log query start
        self.audit_logger.log_query_start(query, self.rbac.user_roles, username)
        
        # ========== STEP 1: QUERY NORMALIZATION ==========
        normalized_query = self.normalizer.normalize(query)
        self.audit_logger.log_normalization(query, normalized_query)
        
        # ========== STEP 2: QUERY EXPANSION ==========
        query_variants = self.normalizer.generate_variants(normalized_query)
        self.audit_logger.log_query_variants(query_variants)
        
        # ========== STEP 3: RBAC RESOLUTION ==========
        effective_roles = self.rbac.resolve_roles()
        effective_permissions = self.rbac.get_effective_permissions()
        accessible_departments = self.rbac.get_accessible_departments()
        
        self.audit_logger.log_rbac_resolution(
            self.rbac.user_roles,
            effective_roles,
            effective_permissions,
            accessible_departments
        )
        
        # Check department access
        if not accessible_departments:
            self.audit_logger.log_warning("User has no accessible departments")
            self.audit_logger.log_query_complete(0)
            return {
                "answer": "You do not have access to any departments.",
                "confidence": "N/A",
                "confidence_score": 0.0,
                "sources": [],
                "error": "No accessible departments",
                "accessible_departments": []
            }
        
        # ========== STEP 4: VECTOR RETRIEVAL ==========
        self.audit_logger.log_info("Step 4: Vector Retrieval (RBAC Pre-Filtered)")
        
        all_candidates = []
        
        for i, variant in enumerate(query_variants, 1):
            query_emb = self.retriever.embed_query(variant)
            
            candidates = self.retriever.department_specific_search(
                query_emb,
                accessible_departments,
                top_k=top_k * 2
            )
            
            self.audit_logger.log_retrieval(
                i,
                variant,
                len(candidates),
                ", ".join(accessible_departments)
            )
            
            all_candidates.extend(candidates)
        
        self.audit_logger.log_retrieval_summary(
            len(all_candidates),
            accessible_departments
        )
        
        if not all_candidates:
            self.audit_logger.log_warning("No candidates retrieved")
            self.audit_logger.log_query_complete(0)
            return {
                "answer": "I couldn't find any relevant information for your query. Please try rephrasing or contact your administrator.",
                "confidence": "N/A",
                "confidence_score": 0.0,
                "sources": [],
                "accessible_departments": accessible_departments
            }
        
        # ========== STEP 5: RE-RANKING & DEDUPLICATION ==========
        primary_query_emb = self.retriever.embed_query(normalized_query)
        
        ranked_results = self.ranker.rerank(
            primary_query_emb,
            all_candidates,
            self.retriever.embedding_lookup
        )
        
        self.audit_logger.log_reranking(
            len(all_candidates),
            len(ranked_results),
            top_k
        )
        
        if not ranked_results:
            self.audit_logger.log_warning("No results after re-ranking")
            self.audit_logger.log_query_complete(0)
            return {
                "answer": "I found relevant information, but the confidence scores were too low. Please try rephrasing your question.",
                "confidence": "N/A",
                "confidence_score": 0.0,
                "sources": [],
                "accessible_departments": accessible_departments
            }
        
        # Take top-k results
        final_chunks = ranked_results[:top_k]
        
        self.audit_logger.log_final_results(final_chunks, username)
        
        # ========== STEP 6: CALCULATE CONFIDENCE ==========
        avg_similarity = sum(c["similarity"] for c in final_chunks) / len(final_chunks)
        confidence_message = self.prompt_builder.build_confidence_message(avg_similarity)
        
        # ========== STEP 7: BUILD PROMPT ==========
        prompt = self.prompt_builder.build_rag_prompt(
            normalized_query,
            final_chunks,
            self.rbac.user_roles[0] if self.rbac.user_roles else "unknown",
            accessible_departments
        )
        
        # ========== STEP 8: GENERATE LLM RESPONSE ==========
        self.audit_logger.log_info("Step 6: Generating LLM response")
        
        llm_result = self.llm_service.generate_response(prompt, max_tokens)
        
        # ========== STEP 9: FORMAT FINAL RESPONSE ==========
        response = {
            "answer": llm_result.get("response", "Sorry, I couldn't generate a response."),
            "confidence": confidence_message,
            "confidence_score": round(avg_similarity, 3),
            "sources": self._format_sources(final_chunks),
            "accessible_departments": accessible_departments,
            "model": llm_result.get("model", "unknown"),
            "normalized_query": normalized_query
        }
        
        # Add error if present
        if "error" in llm_result:
            response["error"] = llm_result["error"]
        
        self.audit_logger.log_query_complete(len(final_chunks))
        
        return response
    
    def _format_sources(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format source citations for response
        
        Args:
            chunks: Retrieved document chunks
            
        Returns:
            List of formatted source citations
        """
        sources = []
        
        for chunk in chunks:
            metadata = chunk.get("metadata", {})
            content = chunk.get("content", "")
            
            # Truncate long content
            excerpt = content[:100] + "..." if len(content) > 100 else content
            
            sources.append({
                "chunk_id": chunk.get("id", "unknown"),
                "document": metadata.get("source_document", "Unknown"),
                "department": metadata.get("department", "Unknown"),
                "similarity": round(chunk.get("similarity", 0.0), 3),
                "excerpt": excerpt
            })
        
        return sources
    
    def get_retrieval_only(
        self,
        query: str,
        top_k: int = 5,
        username: str = None
    ) -> List[Dict[str, Any]]:
        """
        Execute retrieval pipeline only (no LLM generation)
        Useful for testing or getting raw chunks
        
        Args:
            query: User's raw search query
            top_k: Number of documents to retrieve
            username: Username for audit logging
            
        Returns:
            List of retrieved and ranked documents
        """
        self.audit_logger.log_query_start(query, self.rbac.user_roles, username)
        
        # Normalize query
        normalized_query = self.normalizer.normalize(query)
        
        # Get accessible departments
        accessible_departments = self.rbac.get_accessible_departments()
        
        if not accessible_departments:
            return []
        
        # Retrieve
        query_emb = self.retriever.embed_query(normalized_query)
        candidates = self.retriever.department_specific_search(
            query_emb,
            accessible_departments,
            top_k=top_k * 2
        )
        
        if not candidates:
            return []
        
        # Re-rank
        ranked_results = self.ranker.rerank(
            query_emb,
            candidates,
            self.retriever.embedding_lookup
        )
        
        self.audit_logger.log_query_complete(len(ranked_results))
        
        return ranked_results[:top_k]
    
    def validate_pipeline(self) -> bool:
        """Validate all pipeline components"""
        try:
            assert self.normalizer is not None, "Normalizer not initialized"
            assert self.retriever is not None, "Retriever not initialized"
            assert self.rbac is not None, "RBAC Engine not initialized"
            assert self.ranker is not None, "Ranker not initialized"
            assert self.llm_service is not None, "LLM Service not initialized"
            assert self.prompt_builder is not None, "Prompt Builder not initialized"
            
            self.audit_logger.log_info("✓ Complete pipeline validation successful")
            return True
            
        except AssertionError as e:
            self.audit_logger.log_error("Pipeline Validation", str(e))
            return False
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get comprehensive pipeline statistics"""
        return {
            "user_roles": self.rbac.user_roles,
            "effective_roles": list(self.rbac.resolve_roles()),
            "effective_permissions": list(self.rbac.get_effective_permissions()),
            "accessible_departments": self.rbac.get_accessible_departments(),
            "is_admin": "admin" in self.rbac.resolve_roles(),
            "similarity_threshold": self.ranker.threshold,
            "total_chunks": len(self.retriever.chunks),
            "total_embeddings": len(self.retriever.embeddings),
            "llm_provider": self.llm_service.provider,
            "llm_model": self.llm_service.llm_model
        }