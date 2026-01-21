"""
Document Re-ranker
Re-ranks retrieved documents using cross-encoder for better relevance
Includes deduplication and thresholding
"""

from typing import List, Dict, Any, Optional
from sentence_transformers import CrossEncoder
import logging

logger = logging.getLogger(__name__)


class DocumentReranker:
    """
    Re-rank documents using cross-encoder model
    Removes duplicates and applies relevance threshold
    """
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialize re-ranker
        
        Args:
            model_name: HuggingFace cross-encoder model name
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load cross-encoder model"""
        try:
            logger.info(f"📥 Loading re-ranking model: {self.model_name}")
            self.model = CrossEncoder(self.model_name)
            logger.info("✅ Re-ranking model loaded")
        except Exception as e:
            logger.error(f"❌ Error loading re-ranking model: {e}")
            logger.warning("⚠️  Re-ranking will be skipped")
            self.model = None
    
    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 5,
        threshold: float = -100.0  # Set very low to accept all
    ) -> List[Dict[str, Any]]:
        """
        Re-rank documents based on query relevance
        
        Args:
            query: User query
            documents: List of documents with 'text' and metadata
            top_k: Number of top documents to return
            threshold: Minimum relevance score threshold
        
        Returns:
            Re-ranked list of documents
        """
        if not documents:
            return []
        
        if self.model is None:
            logger.warning("⚠️  Re-ranking model not available, returning original order")
            return documents[:top_k]
        
        try:
            # Prepare query-document pairs
            pairs = [[query, doc.get('text', '')] for doc in documents]
            
            # Get cross-encoder scores
            scores = self.model.predict(pairs)
            
            # Combine scores with documents
            scored_docs = [
                {**doc, 'rerank_score': float(score)}
                for doc, score in zip(documents, scores)
            ]
            
            # Sort by score (descending)
            scored_docs.sort(key=lambda x: x['rerank_score'], reverse=True)
            
            # Apply threshold
            filtered_docs = [
                doc for doc in scored_docs
                if doc['rerank_score'] >= threshold
            ]
            
            # Return top-k
            result = filtered_docs[:top_k]
            
            logger.info(f"✅ Re-ranked {len(documents)} docs → {len(result)} docs (threshold: {threshold})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error during re-ranking: {e}")
            return documents[:top_k]
    
    def deduplicate(
        self,
        documents: List[Dict[str, Any]],
        similarity_threshold: float = 0.95
    ) -> List[Dict[str, Any]]:
        """
        Remove near-duplicate documents based on text similarity
        
        Args:
            documents: List of documents
            similarity_threshold: Threshold for considering documents as duplicates
        
        Returns:
            Deduplicated list of documents
        """
        if len(documents) <= 1:
            return documents
        
        unique_docs = []
        seen_texts = []
        
        for doc in documents:
            text = doc.get('text', '').lower().strip()
            
            # Check if this text is too similar to any seen text
            is_duplicate = False
            for seen_text in seen_texts:
                # Simple similarity: check if one text contains most of the other
                if self._is_similar(text, seen_text, similarity_threshold):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_docs.append(doc)
                seen_texts.append(text)
        
        if len(unique_docs) < len(documents):
            logger.info(f"✅ Deduplication: {len(documents)} docs → {len(unique_docs)} unique docs")
        
        return unique_docs
    
    def _is_similar(self, text1: str, text2: str, threshold: float) -> bool:
        """
        Check if two texts are similar using simple overlap
        
        Args:
            text1: First text
            text2: Second text
            threshold: Similarity threshold
        
        Returns:
            True if texts are similar
        """
        # Simple word-level overlap
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return False
        
        overlap = len(words1.intersection(words2))
        min_len = min(len(words1), len(words2))
        
        similarity = overlap / min_len if min_len > 0 else 0
        
        return similarity >= threshold
    
    def rerank_and_deduplicate(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 5,
        rerank_threshold: float = 0.0,
        similarity_threshold: float = 0.95
    ) -> List[Dict[str, Any]]:
        """
        Combined re-ranking and deduplication
        
        Args:
            query: User query
            documents: List of documents
            top_k: Number of top documents to return
            rerank_threshold: Minimum relevance score
            similarity_threshold: Threshold for deduplication
        
        Returns:
            Re-ranked and deduplicated documents
        """
        # First deduplicate
        unique_docs = self.deduplicate(documents, similarity_threshold)
        
        # Then rerank
        reranked_docs = self.rerank(query, unique_docs, top_k, rerank_threshold)
        
        return reranked_docs


# Test function
if __name__ == "__main__":
    print("🧪 Testing Document Reranker\n")
    
    # Sample documents
    test_docs = [
        {
            "id": "chunk_001",
            "text": "The company revenue in Q4 2024 was $5.2 million, showing strong growth.",
            "department": "Finance"
        },
        {
            "id": "chunk_002",
            "text": "Marketing campaigns in Q4 achieved 25% ROI with total spend of $500K.",
            "department": "Marketing"
        },
        {
            "id": "chunk_003",
            "text": "Q4 2024 revenue reached $5.2M, marking a 15% increase from Q3.",
            "department": "Finance"
        },
        {
            "id": "chunk_004",
            "text": "The employee handbook was updated with new remote work policies.",
            "department": "HR"
        },
        {
            "id": "chunk_005",
            "text": "Revenue in the fourth quarter of 2024 was $5.2 million.",
            "department": "Finance"
        }
    ]
    
    # Initialize reranker
    reranker = DocumentReranker()
    
    # Test query
    query = "What was the Q4 revenue?"
    
    print("📝 Original documents:", len(test_docs))
    for i, doc in enumerate(test_docs, 1):
        print(f"  {i}. [{doc['id']}] {doc['text'][:60]}...")
    
    print("\n🔄 Re-ranking...\n")
    
    # Re-rank
    reranked = reranker.rerank(query, test_docs, top_k=3)
    
    print("📊 Re-ranked documents (top 3):")
    for i, doc in enumerate(reranked, 1):
        score = doc.get('rerank_score', 0)
        print(f"  {i}. [{doc['id']}] Score: {score:.4f}")
        print(f"     {doc['text'][:70]}...")
    
    print("\n🧹 Deduplicating...\n")
    
    # Deduplicate
    unique = reranker.deduplicate(test_docs)
    
    print(f"Unique documents: {len(unique)} (from {len(test_docs)})")
    for doc in unique:
        print(f"  - [{doc['id']}] {doc['department']}")
    
    print("\n✨ Combined re-rank + deduplicate:\n")
    
    # Combined
    final = reranker.rerank_and_deduplicate(query, test_docs, top_k=3)
    
    print(f"Final documents: {len(final)}")
    for i, doc in enumerate(final, 1):
        score = doc.get('rerank_score', 0)
        print(f"  {i}. [{doc['id']}] Score: {score:.4f} - {doc['department']}")
