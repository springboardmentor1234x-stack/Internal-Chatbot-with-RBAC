"""
Confidence Scorer
Calculate confidence metrics for RAG responses
"""

from typing import List, Dict, Any
import re
import logging

logger = logging.getLogger(__name__)


class ConfidenceScorer:
    """Calculate confidence scores for RAG responses"""
    
    def __init__(self):
        """Initialize confidence scorer"""
        self.weights = {
            "retrieval_quality": 0.35,      # How relevant are retrieved docs
            "citation_coverage": 0.25,       # Are sources properly cited
            "answer_completeness": 0.20,     # Is answer complete
            "source_consistency": 0.20       # Are sources consistent
        }
    
    def calculate_confidence(
        self,
        answer: str,
        sources: List[Dict[str, Any]],
        query: str,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Calculate overall confidence score
        
        Args:
            answer: Generated answer text
            sources: Retrieved source documents
            query: Original user query
            metadata: Additional metadata
        
        Returns:
            Confidence metrics dictionary
        """
        # Calculate individual components
        retrieval_score = self._calculate_retrieval_quality(sources)
        citation_score = self._calculate_citation_coverage(answer, sources)
        completeness_score = self._calculate_answer_completeness(answer, query)
        consistency_score = self._calculate_source_consistency(sources)
        
        # Ensure all scores are 0-1
        retrieval_score = max(0.0, min(1.0, retrieval_score))
        citation_score = max(0.0, min(1.0, citation_score))
        completeness_score = max(0.0, min(1.0, completeness_score))
        consistency_score = max(0.0, min(1.0, consistency_score))
        
        # Debug logging
        logger.info(f"Confidence scores - Retrieval: {retrieval_score:.2f}, Citation: {citation_score:.2f}, Completeness: {completeness_score:.2f}, Consistency: {consistency_score:.2f}")
        
        # Weighted combination
        overall_confidence = (
            self.weights["retrieval_quality"] * retrieval_score +
            self.weights["citation_coverage"] * citation_score +
            self.weights["answer_completeness"] * completeness_score +
            self.weights["source_consistency"] * consistency_score
        )
        
        # Determine confidence level
        confidence_level = self._get_confidence_level(overall_confidence)
        
        return {
            "overall_confidence": round(overall_confidence * 100, 2),
            "confidence_level": confidence_level,
            "components": {
                "retrieval_quality": round(retrieval_score * 100, 2),
                "citation_coverage": round(citation_score * 100, 2),
                "answer_completeness": round(completeness_score * 100, 2),
                "source_consistency": round(consistency_score * 100, 2)
            },
            "interpretation": self._interpret_confidence(overall_confidence),
            "reliability_flag": "HIGH" if overall_confidence >= 0.7 else "MEDIUM" if overall_confidence >= 0.5 else "LOW"
        }
    
    def _calculate_retrieval_quality(self, sources: List[Dict[str, Any]]) -> float:
        """
        Calculate quality of retrieved documents
        
        Args:
            sources: Retrieved source documents with scores
        
        Returns:
            Retrieval quality score (0-1)
        """
        if not sources:
            return 0.0
        
        # Extract relevance scores (could be 'score', 'rerank_score', or 'relevance_score')
        scores = []
        for source in sources:
            score = source.get('rerank_score')
            if score is None:
                score = source.get('score', source.get('relevance_score', 0))
            scores.append(score)
        
        if not scores:
            return 0.0
        
        # Normalize scores based on type
        # Rerank scores (cross-encoder logits) need normalization
        # Check if we have rerank_scores (they can be negative/large)
        has_rerank = any('rerank_score' in src for src in sources)
        
        if has_rerank:
            # Cross-encoder scores are logits (unbounded, can be very negative or positive)
            # Use sigmoid to normalize: 1 / (1 + exp(-x))
            import math
            normalized_scores = []
            for s in scores:
                # Apply sigmoid function for smooth 0-1 mapping
                # This handles any range of values properly
                try:
                    sigmoid = 1 / (1 + math.exp(-s))
                    normalized_scores.append(sigmoid)
                except (OverflowError, ValueError):
                    # For very large positive values, sigmoid -> 1
                    # For very large negative values, sigmoid -> 0
                    if s > 0:
                        normalized_scores.append(1.0)
                    else:
                        normalized_scores.append(0.0)
            scores = normalized_scores
        else:
            # Regular similarity scores should already be 0-1
            # But clamp just in case
            scores = [max(0.0, min(1.0, s)) for s in scores]
        
        # Average of top scores
        avg_score = sum(scores) / len(scores)
        
        # Bonus for having multiple high-quality sources
        high_quality_count = sum(1 for s in scores if s > 0.7)
        quality_bonus = min(high_quality_count * 0.1, 0.3)
        
        return min(avg_score + quality_bonus, 1.0)
    
    def _calculate_citation_coverage(self, answer: str, sources: List[Dict[str, Any]]) -> float:
        """
        Calculate how well sources are cited in answer
        
        Args:
            answer: Generated answer
            sources: Source documents
        
        Returns:
            Citation coverage score (0-1)
        """
        # Extract citations from answer
        citation_pattern = r'\[(chunk|source)_\w+\]'
        citations = re.findall(citation_pattern, answer.lower())
        
        if not sources:
            return 1.0 if not citations else 0.5
        
        if not citations:
            # No citations is bad
            return 0.3
        
        # Check how many sources were cited
        source_ids = [s.get('id', '').lower() for s in sources]
        cited_sources = set()
        for citation in citations:
            for source_id in source_ids:
                if citation in source_id or source_id in str(citation):
                    cited_sources.add(source_id)
        
        # Coverage ratio
        coverage_ratio = len(cited_sources) / len(sources)
        
        # Bonus for multiple citations (shows thoroughness)
        citation_density = len(citations) / max(len(answer.split('.')), 1)
        density_bonus = min(citation_density * 0.2, 0.2)
        
        return min(coverage_ratio + density_bonus, 1.0)
    
    def _calculate_answer_completeness(self, answer: str, query: str) -> float:
        """
        Estimate if answer is complete based on length and structure
        
        Args:
            answer: Generated answer
            query: Original query
        
        Returns:
            Completeness score (0-1)
        """
        # Basic length check
        answer_length = len(answer.split())
        
        # Too short answers are likely incomplete
        if answer_length < 10:
            return 0.3
        
        # Check for refusal phrases
        refusal_phrases = [
            "don't have",
            "don't know",
            "not available",
            "cannot answer",
            "insufficient information",
            "not enough information"
        ]
        
        answer_lower = answer.lower()
        if any(phrase in answer_lower for phrase in refusal_phrases):
            # Honest refusal is better than hallucination
            return 0.6
        
        # Length-based score (20-200 words is ideal)
        if 20 <= answer_length <= 200:
            length_score = 1.0
        elif answer_length < 20:
            length_score = answer_length / 20
        else:
            length_score = max(0.7, 1.0 - (answer_length - 200) / 400)
        
        # Check for question words addressed
        query_words = set(query.lower().split())
        answer_words = set(answer_lower.split())
        word_overlap = len(query_words & answer_words) / max(len(query_words), 1)
        
        return (length_score * 0.6 + word_overlap * 0.4)
    
    def _calculate_source_consistency(self, sources: List[Dict[str, Any]]) -> float:
        """
        Check if sources are from consistent departments/topics
        
        Args:
            sources: Source documents
        
        Returns:
            Consistency score (0-1)
        """
        if not sources:
            return 0.0
        
        if len(sources) == 1:
            return 1.0
        
        # Check department consistency
        departments = [s.get('department', 'Unknown') for s in sources]
        unique_departments = set(departments)
        
        # If all from same department - very consistent
        if len(unique_departments) == 1:
            return 1.0
        
        # If from 2-3 related departments - good
        if len(unique_departments) <= 3:
            consistency = 1.0 - (len(unique_departments) - 1) * 0.15
        else:
            # Too many departments might indicate scattered results
            consistency = 0.6
        
        # Check score variance (lower variance = more consistent)
        scores = [s.get('rerank_score', s.get('score', 0)) for s in sources]
        if scores and len(scores) > 1:
            score_range = max(scores) - min(scores)
            variance_penalty = score_range * 0.2
            consistency -= variance_penalty
        
        return max(consistency, 0.0)
    
    def _get_confidence_level(self, confidence: float) -> str:
        """
        Convert confidence score to level
        
        Args:
            confidence: Confidence score (0-1)
        
        Returns:
            Confidence level string
        """
        if confidence >= 0.8:
            return "VERY HIGH"
        elif confidence >= 0.7:
            return "HIGH"
        elif confidence >= 0.5:
            return "MEDIUM"
        elif confidence >= 0.3:
            return "LOW"
        else:
            return "VERY LOW"
    
    def _interpret_confidence(self, confidence: float) -> str:
        """
        Provide interpretation of confidence score
        
        Args:
            confidence: Confidence score (0-1)
        
        Returns:
            Human-readable interpretation
        """
        if confidence >= 0.8:
            return "Answer is highly reliable with strong source support and proper citations."
        elif confidence >= 0.7:
            return "Answer is reliable with good source support. Minor improvements possible."
        elif confidence >= 0.5:
            return "Answer is moderately reliable. Consider verifying with additional sources."
        elif confidence >= 0.3:
            return "Answer has limited reliability. Use with caution and verify independently."
        else:
            return "Answer has low reliability. Insufficient or inconsistent source support."
    
    def should_display_warning(self, confidence_result: Dict[str, Any]) -> bool:
        """
        Determine if low confidence warning should be shown
        
        Args:
            confidence_result: Result from calculate_confidence
        
        Returns:
            True if warning should be displayed
        """
        overall = confidence_result.get('overall_confidence', 0)
        components = confidence_result.get('components', {})
        
        # Show warning if overall low OR any critical component is very low
        if overall < 50:
            return True
        
        if components.get('retrieval_quality', 100) < 40:
            return True
        
        if components.get('citation_coverage', 100) < 30:
            return True
        
        return False
    
    def get_warning_message(self, confidence_result: Dict[str, Any]) -> str:
        """
        Generate appropriate warning message
        
        Args:
            confidence_result: Result from calculate_confidence
        
        Returns:
            Warning message string
        """
        components = confidence_result.get('components', {})
        issues = []
        
        if components.get('retrieval_quality', 100) < 50:
            issues.append("low-quality source documents")
        
        if components.get('citation_coverage', 100) < 40:
            issues.append("insufficient source citations")
        
        if components.get('answer_completeness', 100) < 50:
            issues.append("potentially incomplete answer")
        
        if components.get('source_consistency', 100) < 50:
            issues.append("inconsistent sources")
        
        if issues:
            return f"⚠️ Low confidence due to: {', '.join(issues)}. Please verify this information."
        else:
            return "⚠️ This answer has low confidence. Please verify independently."


# Test function
if __name__ == "__main__":
    print("🧪 Testing Confidence Scorer\n")
    
    # Initialize scorer
    scorer = ConfidenceScorer()
    
    # Test Case 1: High confidence answer
    print("=" * 60)
    print("TEST CASE 1: High Confidence Answer")
    print("=" * 60)
    
    answer1 = """Based on the financial reports, Q4 2024 revenue was $5.2M [chunk_001], 
    representing a 15% increase from Q3 [chunk_001]. Operating expenses decreased by 8% 
    to $3.1M [chunk_002], resulting in improved profit margins of 22% [chunk_002]."""
    
    sources1 = [
        {
            "id": "chunk_001",
            "department": "Finance",
            "rerank_score": 0.92
        },
        {
            "id": "chunk_002",
            "department": "Finance",
            "rerank_score": 0.88
        }
    ]
    
    result1 = scorer.calculate_confidence(
        answer1,
        sources1,
        "What was Q4 2024 revenue?"
    )
    
    print(f"\nOverall Confidence: {result1['overall_confidence']}%")
    print(f"Level: {result1['confidence_level']}")
    print(f"Reliability: {result1['reliability_flag']}")
    print(f"\nInterpretation: {result1['interpretation']}")
    print(f"\nComponents:")
    for key, value in result1['components'].items():
        print(f"  {key}: {value}%")
    
    # Test Case 2: Low confidence answer
    print("\n\n" + "=" * 60)
    print("TEST CASE 2: Low Confidence Answer")
    print("=" * 60)
    
    answer2 = """I don't have enough information to answer this question."""
    
    sources2 = [
        {
            "id": "chunk_003",
            "department": "Marketing",
            "rerank_score": 0.35
        }
    ]
    
    result2 = scorer.calculate_confidence(
        answer2,
        sources2,
        "What was the marketing budget?"
    )
    
    print(f"\nOverall Confidence: {result2['overall_confidence']}%")
    print(f"Level: {result2['confidence_level']}")
    print(f"Reliability: {result2['reliability_flag']}")
    print(f"\nInterpretation: {result2['interpretation']}")
    
    if scorer.should_display_warning(result2):
        print(f"\n{scorer.get_warning_message(result2)}")
    
    print(f"\nComponents:")
    for key, value in result2['components'].items():
        print(f"  {key}: {value}%")
