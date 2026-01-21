"""
Advanced RAG Pipeline
Complete orchestration of enhanced RAG with all components
"""

import sys
import os
from typing import Dict, List, Any, Optional
import logging

# Add parent directory to path for module imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    # Try importing with module prefix (when called from backend)
    from llm_integration.llm_manager import LLMManager
    from llm_integration.prompt_templates import PromptTemplates
    from llm_integration.reranker import DocumentReranker
    from llm_integration.response_formatter import ResponseFormatter
    from llm_integration.confidence_scorer import ConfidenceScorer
    from llm_integration.config import LLMConfig
except ImportError:
    # Fall back to relative imports (when running standalone tests)
    from llm_manager import LLMManager
    from prompt_templates import PromptTemplates
    from reranker import DocumentReranker
    from response_formatter import ResponseFormatter
    from confidence_scorer import ConfidenceScorer
    from config import LLMConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedRAGPipeline:
    """
    Complete RAG pipeline with:
    - Query processing
    - Vector retrieval (external)
    - Re-ranking
    - LLM generation
    - Response formatting
    - Confidence scoring
    """
    
    def __init__(
        self,
        llm_provider: Optional[str] = None,
        enable_reranking: bool = True,
        enable_confidence: bool = True
    ):
        """
        Initialize RAG pipeline
        
        Args:
            llm_provider: Specific LLM provider to use (None for auto-select)
            enable_reranking: Enable document re-ranking
            enable_confidence: Enable confidence scoring
        """
        logger.info("🚀 Initializing Advanced RAG Pipeline...")
        
        # Initialize components
        self.llm_manager = LLMManager()
        self.prompt_templates = PromptTemplates()
        self.reranker = DocumentReranker() if enable_reranking else None
        self.formatter = ResponseFormatter()
        self.confidence_scorer = ConfidenceScorer() if enable_confidence else None
        
        self.enable_reranking = enable_reranking
        self.enable_confidence = enable_confidence
        
        # Configuration - use very low threshold to not filter valid results
        self.max_context_chunks = LLMConfig.MAX_CONTEXT_CHUNKS
        self.relevance_threshold = -100.0  # Accept all reranked results
        
        logger.info(f"✅ Pipeline initialized with provider: {self.llm_manager.provider.value}")
        logger.info(f"   Re-ranking: {'ON' if enable_reranking else 'OFF'}")
        logger.info(f"   Confidence scoring: {'ON' if enable_confidence else 'OFF'}")
    
    def process_query(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        user_role: str,
        accessible_departments: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete RAG pipeline execution
        
        Args:
            query: User's query
            retrieved_chunks: Chunks from vector search (already RBAC-filtered)
            user_role: User's role
            accessible_departments: Departments user can access
            metadata: Additional metadata
        
        Returns:
            Complete RAG response with answer, sources, and confidence
        """
        try:
            logger.info(f"📝 Processing query: '{query[:50]}...'")
            logger.info(f"   User role: {user_role}")
            logger.info(f"   Retrieved chunks: {len(retrieved_chunks)}")
            
            # Step 1: Handle empty retrieval
            if not retrieved_chunks:
                return self._handle_no_context(query, user_role, accessible_departments)
            
            # Step 2: Re-rank documents (if enabled)
            if self.enable_reranking and self.reranker:
                logger.info("🔄 Re-ranking documents...")
                reranked_chunks = self.reranker.rerank(query, retrieved_chunks)
                if reranked_chunks:
                    logger.info(f"   Top score after re-ranking: {reranked_chunks[0].get('rerank_score', 0):.4f}")
                else:
                    logger.warning("   No documents passed re-ranking threshold")
            else:
                reranked_chunks = retrieved_chunks
            
            # Step 3: Apply relevance threshold and select top-K
            filtered_chunks = self._filter_and_select(reranked_chunks)
            logger.info(f"   Chunks after filtering: {len(filtered_chunks)}")
            
            if not filtered_chunks:
                return self._handle_low_relevance(query, user_role, accessible_departments)
            
            # Step 4: Deduplicate (if enabled)
            if self.enable_reranking and self.reranker:
                logger.info("🔍 Deduplicating documents...")
                deduplicated_chunks = self.reranker.deduplicate(filtered_chunks)
                logger.info(f"   Chunks after deduplication: {len(deduplicated_chunks)}")
            else:
                deduplicated_chunks = filtered_chunks
            
            # Step 5: Format chunks for prompt
            formatted_chunks = self._format_chunks_for_prompt(deduplicated_chunks)
            
            # Step 6: Generate prompts
            system_prompt = self.prompt_templates.get_system_prompt(
                user_role,
                accessible_departments
            )
            
            user_prompt = self.prompt_templates.get_user_prompt(
                query,
                formatted_chunks,
                user_role
            )
            
            # Step 7: Generate answer with LLM
            logger.info("🤖 Generating answer with LLM...")
            answer = self.llm_manager.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=LLMConfig.OPENAI_MAX_TOKENS,
                temperature=LLMConfig.OPENAI_TEMPERATURE
            )
            logger.info(f"   Answer generated ({len(answer)} chars)")
            
            # Step 8: Format response
            logger.info("📋 Formatting response...")
            response = self.formatter.format_response(
                answer=answer,
                sources=deduplicated_chunks,
                metadata={
                    **(metadata or {}),
                    "user_role": user_role,
                    "accessible_departments": accessible_departments,
                    "llm_provider": self.llm_manager.provider.value,
                    "chunks_retrieved": len(retrieved_chunks),
                    "chunks_used": len(deduplicated_chunks),
                    "reranking_enabled": self.enable_reranking
                }
            )
            
            # Step 9: Calculate confidence (if enabled)
            if self.enable_confidence and self.confidence_scorer:
                logger.info("📊 Calculating confidence...")
                confidence_result = self.confidence_scorer.calculate_confidence(
                    answer=answer,
                    sources=deduplicated_chunks,
                    query=query,
                    metadata=response.get('metadata', {})
                )
                response['confidence'] = confidence_result
                
                # Add warning if needed
                if self.confidence_scorer.should_display_warning(confidence_result):
                    response['warning'] = self.confidence_scorer.get_warning_message(confidence_result)
            
            # Step 10: Add source summary
            response = self.formatter.add_source_summary(response)
            
            logger.info("✅ RAG pipeline completed successfully")
            return response
            
        except Exception as e:
            import traceback
            logger.error(f"❌ Error in RAG pipeline: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return self._handle_error(query, user_role, str(e))
    
    def _filter_and_select(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter by relevance threshold and select top-K
        
        Args:
            chunks: Ranked chunks
        
        Returns:
            Filtered and limited chunks
        """
        # Get score field (could be 'rerank_score' or 'score')
        filtered = []
        for chunk in chunks:
            score = chunk.get('rerank_score', chunk.get('score', 0))
            if score >= self.relevance_threshold:
                filtered.append(chunk)
        
        # Select top-K
        return filtered[:self.max_context_chunks]
    
    def _format_chunks_for_prompt(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format chunks for prompt template
        
        Args:
            chunks: Source chunks
        
        Returns:
            Formatted chunks
        """
        formatted = []
        for chunk in chunks:
            formatted.append({
                "id": chunk.get('id', chunk.get('chunk_id', 'unknown')),
                "text": chunk.get('text', chunk.get('content', '')),
                "department": chunk.get('department', 'Unknown'),
                "source": chunk.get('source', chunk.get('source_file', 'Unknown'))
            })
        return formatted
    
    def _handle_no_context(
        self,
        query: str,
        user_role: str,
        accessible_departments: List[str]
    ) -> Dict[str, Any]:
        """
        Handle case when no documents are retrieved
        
        Args:
            query: User query
            user_role: User's role
            accessible_departments: Accessible departments
        
        Returns:
            No-context response
        """
        logger.warning("⚠️ No documents retrieved")
        
        answer = self.prompt_templates.get_no_context_prompt(
            query,
            user_role,
            accessible_departments
        )
        
        return {
            "answer": answer,
            "sources": [],
            "citations": [],
            "has_citations": False,
            "citation_count": 0,
            "metadata": {
                "user_role": user_role,
                "accessible_departments": accessible_departments,
                "status": "no_context",
                "chunks_retrieved": 0,
                "chunks_used": 0
            },
            "source_summary": {
                "total_sources": 0,
                "source_files": [],
                "departments": {}
            }
        }
    
    def _handle_low_relevance(
        self,
        query: str,
        user_role: str,
        accessible_departments: List[str]
    ) -> Dict[str, Any]:
        """
        Handle case when all documents are below relevance threshold
        
        Args:
            query: User query
            user_role: User's role
            accessible_departments: Accessible departments
        
        Returns:
            Low-relevance response
        """
        logger.warning("⚠️ All documents below relevance threshold")
        
        answer = f"""I found some potentially related information, but it doesn't seem directly relevant to your question about: "{query}"

As a {user_role}, you have access to {', '.join(accessible_departments)} department information. However, the available documents don't contain information that clearly answers your specific question.

Please try:
- Rephrasing your question
- Being more specific about what you're looking for
- Asking about related topics within your accessible departments"""
        
        return {
            "answer": answer,
            "sources": [],
            "citations": [],
            "has_citations": False,
            "metadata": {
                "user_role": user_role,
                "accessible_departments": accessible_departments,
                "status": "low_relevance"
            },
            "source_summary": {
                "total_sources": 0,
                "source_files": [],
                "departments": {}
            }
        }
    
    def _handle_error(
        self,
        query: str,
        user_role: str,
        error_message: str
    ) -> Dict[str, Any]:
        """
        Handle pipeline errors gracefully
        
        Args:
            query: User query
            user_role: User's role
            error_message: Error description
        
        Returns:
            Error response
        """
        logger.error(f"Pipeline error: {error_message}")
        
        return {
            "answer": "I apologize, but I encountered an error while processing your question. Please try again or contact support if the issue persists.",
            "sources": [],
            "citations": [],
            "has_citations": False,
            "metadata": {
                "user_role": user_role,
                "status": "error",
                "error": error_message
            },
            "source_summary": {
                "total_sources": 0,
                "source_files": [],
                "departments": {}
            }
        }
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """Get information about pipeline configuration"""
        return {
            "llm_provider": self.llm_manager.provider.value,
            "llm_model": self.llm_manager._get_model_name(),
            "reranking_enabled": self.enable_reranking,
            "confidence_scoring_enabled": self.enable_confidence,
            "max_context_chunks": self.max_context_chunks,
            "relevance_threshold": self.relevance_threshold
        }


# Test function
if __name__ == "__main__":
    print("🧪 Testing Advanced RAG Pipeline\n")
    
    # Initialize pipeline
    pipeline = AdvancedRAGPipeline(
        enable_reranking=True,
        enable_confidence=True
    )
    
    # Display configuration
    print("=" * 60)
    print("PIPELINE CONFIGURATION:")
    print("=" * 60)
    info = pipeline.get_pipeline_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    print()
    
    # Test with sample data
    print("=" * 60)
    print("TEST: Sample RAG Query")
    print("=" * 60)
    
    query = "What was the Q4 2024 revenue?"
    
    # Simulate retrieved chunks (normally from vector DB)
    retrieved_chunks = [
        {
            "id": "chunk_001",
            "text": "Q4 2024 revenue was $5.2M, representing a 15% increase from Q3. This growth was driven by new customer acquisitions.",
            "department": "Finance",
            "source": "quarterly_financial_report.md",
            "chunk_index": 5,
            "score": 0.85
        },
        {
            "id": "chunk_002",
            "text": "Operating expenses in Q4 decreased by 8% to $3.1M through cost optimization.",
            "department": "Finance",
            "source": "financial_summary.md",
            "chunk_index": 12,
            "score": 0.72
        },
        {
            "id": "chunk_003",
            "text": "The company's revenue strategy focuses on sustainable growth and customer retention.",
            "department": "Finance",
            "source": "annual_report.md",
            "chunk_index": 3,
            "score": 0.45
        }
    ]
    
    # Process query
    print(f"\nQuery: {query}")
    print(f"Retrieved chunks: {len(retrieved_chunks)}")
    print(f"User role: finance_employee")
    print("\nProcessing...\n")
    
    result = pipeline.process_query(
        query=query,
        retrieved_chunks=retrieved_chunks,
        user_role="finance_employee",
        accessible_departments=["Finance", "General"]
    )
    
    # Display result
    print("\n" + "=" * 60)
    print("RESULT:")
    print("=" * 60)
    print(pipeline.formatter.format_for_display(result))
    
    # Display confidence if available
    if 'confidence' in result:
        print("\n" + "=" * 60)
        print("CONFIDENCE METRICS:")
        print("=" * 60)
        conf = result['confidence']
        print(f"Overall: {conf['overall_confidence']}% ({conf['confidence_level']})")
        print(f"Reliability: {conf['reliability_flag']}")
        print(f"\nInterpretation: {conf['interpretation']}")
        
        if 'warning' in result:
            print(f"\n{result['warning']}")
