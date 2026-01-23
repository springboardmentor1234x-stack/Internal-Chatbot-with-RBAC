"""
Advanced Accuracy Improvements for RAG Pipeline
Provides enhanced accuracy validation, response quality assessment,
and intelligent query optimization.
"""

import re
import json
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
from collections import Counter, defaultdict
import streamlit as st

class AdvancedAccuracyEnhancer:
    """Advanced accuracy enhancement system with real-time validation."""
    
    def __init__(self):
        self.accuracy_cache = {}
        self.query_patterns = {}
        self.response_quality_metrics = {}
        self.user_feedback_data = []
        
    def validate_response_quality(self, query: str, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive response quality validation with enhanced metrics."""
        
        quality_assessment = {
            "overall_quality_score": 0.0,
            "accuracy_confidence": "low",
            "quality_metrics": {},
            "improvement_suggestions": [],
            "validation_details": {},
            "response_completeness": 0.0,
            "source_reliability": 0.0,
            "factual_consistency": 0.0
        }
        
        try:
            # 1. Enhanced Source Quality Assessment
            source_quality = self._assess_source_quality(response_data.get("sources", []))
            quality_assessment["quality_metrics"]["source_quality"] = source_quality
            
            # 2. Response Completeness Analysis
            completeness = self._analyze_response_completeness(
                query, response_data.get("response", ""), response_data.get("sources", [])
            )
            quality_assessment["response_completeness"] = completeness
            quality_assessment["quality_metrics"]["completeness"] = completeness
            
            # 3. Factual Consistency Check
            consistency = self._check_factual_consistency(
                response_data.get("response", ""), response_data.get("chunk_details", [])
            )
            quality_assessment["factual_consistency"] = consistency
            quality_assessment["quality_metrics"]["consistency"] = consistency
            
            # 4. Citation Quality Assessment
            citation_quality = self._assess_citation_quality(response_data.get("citations", []))
            quality_assessment["quality_metrics"]["citation_quality"] = citation_quality
            
            # 5. Response Relevance to Query
            relevance = self._calculate_query_response_relevance(query, response_data.get("response", ""))
            quality_assessment["quality_metrics"]["relevance"] = relevance
            
            # 6. Information Density Analysis
            info_density = self._analyze_information_density(response_data.get("response", ""))
            quality_assessment["quality_metrics"]["information_density"] = info_density
            
            # 7. Calculate Overall Quality Score
            weights = {
                "source_quality": 0.20,
                "completeness": 0.25,
                "consistency": 0.20,
                "citation_quality": 0.15,
                "relevance": 0.15,
                "information_density": 0.05
            }
            
            overall_score = sum(
                quality_assessment["quality_metrics"].get(metric, 0) * weight
                for metric, weight in weights.items()
            )
            
            quality_assessment["overall_quality_score"] = min(overall_score, 100.0)
            
            # 8. Determine Confidence Level
            quality_assessment["accuracy_confidence"] = self._determine_confidence_level(overall_score)
            
            # 9. Generate Improvement Suggestions
            quality_assessment["improvement_suggestions"] = self._generate_quality_improvements(
                query, response_data, quality_assessment["quality_metrics"]
            )
            
            # 10. Detailed Validation Results
            quality_assessment["validation_details"] = self._create_validation_details(
                quality_assessment["quality_metrics"]
            )
            
        except Exception as e:
            quality_assessment["error"] = str(e)
            quality_assessment["improvement_suggestions"].append(
                "System error during quality assessment. Please try rephrasing your query."
            )
        
        return quality_assessment
    
    def _assess_source_quality(self, sources: List[str]) -> float:
        """Assess the quality and reliability of sources."""
        if not sources:
            return 0.0
        
        quality_score = 0.0
        
        # Source diversity bonus
        unique_sources = set(sources)
        diversity_score = min(len(unique_sources) / 3, 1.0) * 25  # Max 25 points
        
        # Source type analysis
        source_types = {
            "financial": ["financial", "budget", "revenue", "quarterly"],
            "policy": ["handbook", "policy", "procedure", "guideline"],
            "technical": ["engineering", "technical", "system", "architecture"],
            "strategic": ["market", "strategy", "business", "executive"]
        }
        
        type_coverage = 0
        for source in sources:
            source_lower = source.lower()
            for source_type, keywords in source_types.items():
                if any(keyword in source_lower for keyword in keywords):
                    type_coverage += 10
                    break
        
        type_score = min(type_coverage, 40)  # Max 40 points
        
        # Authority indicators
        authority_score = 0
        authority_indicators = ["department", "official", "master", "handbook", "report"]
        
        for source in sources:
            source_lower = source.lower()
            for indicator in authority_indicators:
                if indicator in source_lower:
                    authority_score += 5
        
        authority_score = min(authority_score, 35)  # Max 35 points
        
        quality_score = diversity_score + type_score + authority_score
        return min(quality_score, 100.0)
    
    def _analyze_response_completeness(self, query: str, response: str, sources: List[str]) -> float:
        """Analyze how complete the response is relative to the query."""
        if not response:
            return 0.0
        
        completeness_score = 0.0
        
        # Query term coverage
        query_terms = set(query.lower().split())
        response_terms = set(response.lower().split())
        
        # Remove common stop words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        query_terms = query_terms - stop_words
        
        if query_terms:
            coverage = len(query_terms.intersection(response_terms)) / len(query_terms)
            completeness_score += coverage * 30  # Max 30 points
        
        # Response structure analysis
        structure_score = 0
        
        # Check for structured elements
        if any(marker in response for marker in ["**", "•", "1.", "2.", "3."]):
            structure_score += 15
        
        # Check for evidence/examples
        if any(indicator in response.lower() for indicator in ["according to", "based on", "for example", "such as"]):
            structure_score += 10
        
        # Check for quantitative information
        if re.search(r'\d+%|\$\d+|\d+\.\d+', response):
            structure_score += 10
        
        completeness_score += structure_score  # Max 35 points
        
        # Source integration
        source_integration = 0
        if sources:
            # Check if response references multiple sources
            if len(sources) > 1:
                source_integration += 15
            
            # Check for proper attribution
            if any(ref in response for ref in ["Source:", "[", "]", "Reference"]):
                source_integration += 10
        
        completeness_score += source_integration  # Max 25 points
        
        # Response length appropriateness
        length_score = 0
        word_count = len(response.split())
        
        if 50 <= word_count <= 500:  # Optimal range
            length_score = 10
        elif 20 <= word_count < 50 or 500 < word_count <= 800:
            length_score = 5
        
        completeness_score += length_score  # Max 10 points
        
        return min(completeness_score, 100.0)
    
    def _check_factual_consistency(self, response: str, chunk_details: List[Dict]) -> float:
        """Check factual consistency between response and source chunks."""
        if not response or not chunk_details:
            return 75.0  # Default assumption of consistency
        
        consistency_score = 75.0  # Base score
        
        # Extract key facts from response
        response_facts = self._extract_key_facts(response)
        
        # Verify facts against source chunks
        verified_facts = 0
        total_facts = len(response_facts)
        
        if total_facts > 0:
            for fact in response_facts:
                for chunk_info in chunk_details:
                    chunks = chunk_info.get("chunks", [])
                    for chunk in chunks:
                        chunk_content = chunk.get("content", "").lower()
                        if fact.lower() in chunk_content:
                            verified_facts += 1
                            break
            
            # Calculate verification ratio
            verification_ratio = verified_facts / total_facts
            consistency_score = 60 + (verification_ratio * 40)  # 60-100 range
        
        # Check for contradictory statements
        contradictions = self._detect_contradictions(response)
        consistency_score -= len(contradictions) * 10  # Penalty for contradictions
        
        # Bonus for specific, verifiable information
        if re.search(r'\d{4}|Q[1-4]|\d+%|\$\d+', response):
            consistency_score += 5
        
        return max(min(consistency_score, 100.0), 0.0)
    
    def _extract_key_facts(self, text: str) -> List[str]:
        """Extract key factual statements from text."""
        facts = []
        
        # Extract sentences with numbers, percentages, or specific dates
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
            
            # Look for factual indicators
            if any(pattern in sentence for pattern in [
                r'\d+%', r'\$\d+', r'\d{4}', r'Q[1-4]', 
                'increased', 'decreased', 'reported', 'according to'
            ]):
                facts.append(sentence)
        
        return facts[:5]  # Limit to top 5 facts
    
    def _detect_contradictions(self, text: str) -> List[str]:
        """Detect potential contradictions in the text."""
        contradictions = []
        text_lower = text.lower()
        
        # Common contradiction patterns
        contradiction_patterns = [
            (r'increase.*decrease', "Contains both increase and decrease"),
            (r'profit.*loss', "Mentions both profit and loss"),
            (r'success.*fail', "Contains both success and failure"),
            (r'high.*low', "Contains both high and low values"),
            (r'more.*less', "Contains both more and less"),
            (r'above.*below', "Contains both above and below")
        ]
        
        for pattern, description in contradiction_patterns:
            if re.search(pattern, text_lower):
                contradictions.append(description)
        
        return contradictions
    
    def _assess_citation_quality(self, citations: List[str]) -> float:
        """Assess the quality of citations provided."""
        if not citations:
            return 50.0  # Neutral score for no citations
        
        quality_score = 0.0
        
        for citation in citations:
            citation_score = 0
            
            # Check for proper citation format
            if "(" in citation and ")" in citation:  # Has parenthetical info
                citation_score += 20
            
            # Check for author information
            if any(term in citation.lower() for term in ["department", "finsolve", "team"]):
                citation_score += 20
            
            # Check for date information
            if re.search(r'\d{4}', citation):
                citation_score += 20
            
            # Check for page/section information
            if any(term in citation for term in ["p.", "pp.", "section", "chapter"]):
                citation_score += 20
            
            # Check for document type
            if any(term in citation.lower() for term in ["report", "handbook", "document", "manual"]):
                citation_score += 20
            
            quality_score += citation_score
        
        # Average across all citations
        average_quality = quality_score / len(citations)
        return min(average_quality, 100.0)
    
    def _calculate_query_response_relevance(self, query: str, response: str) -> float:
        """Calculate how relevant the response is to the query."""
        if not query or not response:
            return 0.0
        
        query_words = set(query.lower().split())
        response_words = set(response.lower().split())
        
        # Remove stop words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were"}
        query_words = query_words - stop_words
        response_words = response_words - stop_words
        
        if not query_words:
            return 50.0
        
        # Direct word overlap
        overlap = len(query_words.intersection(response_words))
        direct_relevance = (overlap / len(query_words)) * 60  # Max 60 points
        
        # Semantic relevance (simplified)
        semantic_score = 0
        
        # Check for query intent fulfillment
        query_lower = query.lower()
        response_lower = response.lower()
        
        intent_patterns = {
            "definition": ["what is", "define", "explain"],
            "quantitative": ["how much", "how many", "cost", "price"],
            "comparison": ["difference", "compare", "vs", "versus"],
            "procedural": ["how to", "steps", "process", "procedure"]
        }
        
        for intent, patterns in intent_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                if intent == "definition" and any(word in response_lower for word in ["is", "means", "refers to"]):
                    semantic_score += 20
                elif intent == "quantitative" and re.search(r'\d+|\$|%', response):
                    semantic_score += 20
                elif intent == "comparison" and any(word in response_lower for word in ["compared to", "versus", "difference"]):
                    semantic_score += 20
                elif intent == "procedural" and any(word in response_lower for word in ["step", "process", "procedure"]):
                    semantic_score += 20
                break
        
        # Context relevance
        context_score = 0
        if len(response.split()) > 50:  # Substantial response
            context_score += 10
        
        if any(marker in response for marker in ["according to", "based on", "source"]):
            context_score += 10
        
        total_relevance = direct_relevance + semantic_score + context_score
        return min(total_relevance, 100.0)
    
    def _analyze_information_density(self, response: str) -> float:
        """Analyze the information density of the response."""
        if not response:
            return 0.0
        
        words = response.split()
        word_count = len(words)
        
        if word_count == 0:
            return 0.0
        
        # Count informative elements
        informative_score = 0
        
        # Numbers and quantitative data
        numbers = len(re.findall(r'\d+', response))
        informative_score += min(numbers * 5, 25)  # Max 25 points
        
        # Specific terms (non-generic words)
        specific_words = [word for word in words if len(word) > 4 and word.isalpha()]
        specificity_ratio = len(specific_words) / word_count
        informative_score += specificity_ratio * 30  # Max 30 points
        
        # Proper nouns and technical terms
        proper_nouns = len(re.findall(r'\b[A-Z][a-z]+\b', response))
        informative_score += min(proper_nouns * 3, 20)  # Max 20 points
        
        # Structured information
        if any(marker in response for marker in ["•", "1.", "2.", "**", "***"]):
            informative_score += 15
        
        # Citations and references
        if any(ref in response for ref in ["Source:", "Reference:", "[", "]"]):
            informative_score += 10
        
        return min(informative_score, 100.0)
    
    def _determine_confidence_level(self, overall_score: float) -> str:
        """Determine confidence level based on overall quality score."""
        if overall_score >= 90:
            return "very_high"
        elif overall_score >= 80:
            return "high"
        elif overall_score >= 70:
            return "medium"
        elif overall_score >= 60:
            return "low"
        else:
            return "very_low"
    
    def _generate_quality_improvements(self, query: str, response_data: Dict[str, Any], quality_metrics: Dict[str, float]) -> List[str]:
        """Generate specific suggestions for improving response quality."""
        suggestions = []
        
        # Source quality improvements
        if quality_metrics.get("source_quality", 0) < 70:
            suggestions.append("Try using more specific keywords to find better source documents")
            if len(response_data.get("sources", [])) < 2:
                suggestions.append("Consider broadening your search terms to find additional relevant sources")
        
        # Completeness improvements
        if quality_metrics.get("completeness", 0) < 70:
            suggestions.append("Your query might benefit from being more specific about what information you need")
            suggestions.append("Try asking follow-up questions to get more detailed information")
        
        # Relevance improvements
        if quality_metrics.get("relevance", 0) < 70:
            suggestions.append("Consider rephrasing your question using different keywords")
            suggestions.append("Make sure your question relates to topics covered in company documents")
        
        # Citation improvements
        if quality_metrics.get("citation_quality", 0) < 70:
            suggestions.append("The response may lack proper source attribution - this could indicate limited source material")
        
        # Information density improvements
        if quality_metrics.get("information_density", 0) < 60:
            suggestions.append("Ask for more specific details or examples to get richer information")
        
        # Query-specific suggestions
        query_lower = query.lower()
        if len(query.split()) < 3:
            suggestions.append("Try adding more descriptive words to your query for better results")
        
        if any(word in query_lower for word in ["cost", "price", "budget", "financial"]):
            suggestions.append("For financial queries, specify time periods (Q1, Q2, etc.) or departments")
        
        return suggestions[:3]  # Limit to top 3 suggestions
    
    def _create_validation_details(self, quality_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Create detailed validation information for transparency."""
        details = {
            "assessment_timestamp": datetime.now().isoformat(),
            "metrics_breakdown": {},
            "quality_indicators": {},
            "recommendations": {}
        }
        
        # Metrics breakdown with interpretations
        for metric, score in quality_metrics.items():
            details["metrics_breakdown"][metric] = {
                "score": round(score, 2),
                "grade": self._score_to_grade(score),
                "interpretation": self._interpret_metric_score(metric, score)
            }
        
        # Overall quality indicators
        avg_score = sum(quality_metrics.values()) / len(quality_metrics) if quality_metrics else 0
        details["quality_indicators"] = {
            "overall_grade": self._score_to_grade(avg_score),
            "strengths": [metric for metric, score in quality_metrics.items() if score >= 80],
            "areas_for_improvement": [metric for metric, score in quality_metrics.items() if score < 70]
        }
        
        return details
    
    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _interpret_metric_score(self, metric: str, score: float) -> str:
        """Provide interpretation for metric scores."""
        interpretations = {
            "source_quality": {
                90: "Excellent source diversity and authority",
                80: "Good source quality with reliable documents",
                70: "Adequate sources but could be more diverse",
                60: "Limited source quality or diversity",
                0: "Poor source quality or very few sources"
            },
            "completeness": {
                90: "Comprehensive response covering all query aspects",
                80: "Well-structured response with good coverage",
                70: "Adequate response but missing some details",
                60: "Incomplete response with significant gaps",
                0: "Very incomplete or inadequate response"
            },
            "relevance": {
                90: "Highly relevant and directly addresses the query",
                80: "Good relevance with minor tangential content",
                70: "Mostly relevant but some off-topic elements",
                60: "Partially relevant with significant off-topic content",
                0: "Poor relevance or doesn't address the query"
            }
        }
        
        metric_interp = interpretations.get(metric, {})
        
        # Find the closest score threshold
        for threshold in sorted(metric_interp.keys(), reverse=True):
            if score >= threshold:
                return metric_interp[threshold]
        
        return "Score interpretation not available"

# Global instance
advanced_accuracy_enhancer = AdvancedAccuracyEnhancer()