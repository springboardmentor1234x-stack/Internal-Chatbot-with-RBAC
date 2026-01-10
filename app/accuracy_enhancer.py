"""
Enhanced Accuracy System for RAG Pipeline
Provides real-time accuracy monitoring, validation, and improvement suggestions.
"""

import re
import json
from typing import Dict, List, Tuple, Any
from datetime import datetime
from collections import Counter, defaultdict


class AccuracyEnhancer:
    """
    Advanced accuracy enhancement system for RAG pipeline.
    Monitors, validates, and improves response accuracy in real-time.
    """
    
    def __init__(self):
        self.accuracy_history = []
        self.query_patterns = defaultdict(list)
        self.response_cache = {}
        self.validation_rules = self._load_validation_rules()
        
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules for different query types."""
        return {
            "financial": {
                "required_entities": ["numbers", "percentages", "currencies"],
                "keywords": ["revenue", "profit", "expense", "budget", "quarterly"],
                "min_accuracy": 85.0,
                "citation_required": True
            },
            "hr": {
                "required_entities": ["dates"],
                "keywords": ["policy", "employee", "benefit", "vacation", "handbook"],
                "min_accuracy": 90.0,
                "citation_required": True
            },
            "marketing": {
                "required_entities": ["percentages", "numbers"],
                "keywords": ["campaign", "customer", "market", "engagement"],
                "min_accuracy": 85.0,
                "citation_required": True
            },
            "engineering": {
                "required_entities": [],
                "keywords": ["technical", "system", "architecture", "development"],
                "min_accuracy": 88.0,
                "citation_required": True
            },
            "general": {
                "required_entities": [],
                "keywords": ["company", "mission", "overview"],
                "min_accuracy": 80.0,
                "citation_required": False
            }
        }
    
    def validate_response_accuracy(self, query: str, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive response accuracy validation.
        Returns enhanced accuracy score and improvement suggestions.
        """
        validation_result = {
            "original_accuracy": response_data.get("accuracy_score", 0.0),
            "enhanced_accuracy": 0.0,
            "validation_score": 0.0,
            "improvement_suggestions": [],
            "quality_metrics": {},
            "confidence_level": "low"
        }
        
        try:
            # 1. Determine query category and validation rules
            query_category = self._categorize_query_advanced(query)
            rules = self.validation_rules.get(query_category, self.validation_rules["general"])
            
            # 2. Validate response components
            component_scores = self._validate_response_components(
                query, response_data, rules
            )
            
            # 3. Calculate enhanced accuracy
            enhanced_accuracy = self._calculate_enhanced_accuracy(
                response_data.get("accuracy_score", 0.0),
                component_scores,
                rules
            )
            
            # 4. Generate improvement suggestions
            suggestions = self._generate_improvement_suggestions(
                query, response_data, component_scores, rules
            )
            
            # 5. Calculate confidence level
            confidence = self._calculate_confidence_level(enhanced_accuracy, component_scores)
            
            validation_result.update({
                "enhanced_accuracy": enhanced_accuracy,
                "validation_score": sum(component_scores.values()) / len(component_scores),
                "improvement_suggestions": suggestions,
                "quality_metrics": component_scores,
                "confidence_level": confidence,
                "query_category": query_category
            })
            
            # 6. Store for learning
            self._store_accuracy_data(query, validation_result)
            
        except Exception as e:
            validation_result["error"] = str(e)
            validation_result["improvement_suggestions"].append(
                "System error occurred during validation. Please try rephrasing your query."
            )
        
        return validation_result
    
    def _categorize_query_advanced(self, query: str) -> str:
        """Advanced query categorization with pattern matching."""
        query_lower = query.lower()
        
        # Enhanced keyword matching with weights
        category_scores = {}
        
        for category, rules in self.validation_rules.items():
            score = 0
            keywords = rules.get("keywords", [])
            
            for keyword in keywords:
                if keyword in query_lower:
                    # Exact match gets higher score
                    if f" {keyword} " in f" {query_lower} ":
                        score += 3
                    else:
                        score += 1
            
            category_scores[category] = score
        
        # Return category with highest score
        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]
        return "general"
    
    def _validate_response_components(self, query: str, response_data: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, float]:
        """Validate individual response components."""
        scores = {}
        
        # 1. Source Quality Validation
        sources = response_data.get("sources", [])
        scores["source_quality"] = self._validate_source_quality(sources, rules)
        
        # 2. Content Relevance Validation
        response_text = response_data.get("response", "")
        scores["content_relevance"] = self._validate_content_relevance(query, response_text, rules)
        
        # 3. Entity Extraction Validation
        scores["entity_extraction"] = self._validate_entity_extraction(response_text, rules)
        
        # 4. Citation Quality Validation
        citations = response_data.get("citations", [])
        scores["citation_quality"] = self._validate_citation_quality(citations, rules)
        
        # 5. Response Completeness Validation
        scores["response_completeness"] = self._validate_response_completeness(
            query, response_text, sources
        )
        
        # 6. Factual Consistency Validation
        scores["factual_consistency"] = self._validate_factual_consistency(
            response_text, sources
        )
        
        return scores
    
    def _validate_source_quality(self, sources: List[str], rules: Dict[str, Any]) -> float:
        """Validate quality and relevance of sources."""
        if not sources:
            return 0.0
        
        quality_score = 0.0
        
        # Check source diversity
        unique_sources = set(sources)
        diversity_bonus = min(len(unique_sources) / 3, 1.0) * 20  # Max 20 points
        
        # Check source relevance to category
        category_keywords = rules.get("keywords", [])
        relevance_score = 0
        
        for source in sources:
            source_lower = source.lower()
            for keyword in category_keywords:
                if keyword in source_lower:
                    relevance_score += 10
        
        relevance_score = min(relevance_score, 50)  # Max 50 points
        
        # Base quality score
        base_score = min(len(sources) * 10, 30)  # Max 30 points
        
        quality_score = diversity_bonus + relevance_score + base_score
        return min(quality_score, 100.0)
    
    def _validate_content_relevance(self, query: str, response: str, rules: Dict[str, Any]) -> float:
        """Validate content relevance to query."""
        if not response:
            return 0.0
        
        query_words = set(query.lower().split())
        response_words = set(response.lower().split())
        
        # Word overlap score
        overlap = len(query_words.intersection(response_words))
        overlap_score = (overlap / len(query_words)) * 40 if query_words else 0
        
        # Keyword presence score
        category_keywords = rules.get("keywords", [])
        keyword_score = 0
        for keyword in category_keywords:
            if keyword in response.lower():
                keyword_score += 15
        keyword_score = min(keyword_score, 45)  # Max 45 points
        
        # Response length appropriateness
        length_score = 15 if 100 <= len(response) <= 2000 else 5
        
        total_score = overlap_score + keyword_score + length_score
        return min(total_score, 100.0)
    
    def _validate_entity_extraction(self, response: str, rules: Dict[str, Any]) -> float:
        """Validate entity extraction quality."""
        required_entities = rules.get("required_entities", [])
        
        if not required_entities:
            return 100.0  # No requirements
        
        extracted_entities = {
            "numbers": len(re.findall(r'\b\d+(?:,\d{3})*(?:\.\d+)?\b', response)),
            "percentages": len(re.findall(r'\b\d+(?:\.\d+)?%\b', response)),
            "dates": len(re.findall(r'\b(?:Q[1-4]|January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b', response)),
            "currencies": len(re.findall(r'\$\d+(?:,\d{3})*(?:\.\d+)?[KMB]?\b', response))
        }
        
        entity_score = 0
        for entity_type in required_entities:
            if extracted_entities.get(entity_type, 0) > 0:
                entity_score += 100 / len(required_entities)
        
        return entity_score
    
    def _validate_citation_quality(self, citations: List[str], rules: Dict[str, Any]) -> float:
        """Validate citation quality and completeness."""
        citation_required = rules.get("citation_required", False)
        
        if not citation_required:
            return 100.0  # No requirements
        
        if not citations:
            return 0.0  # Required but missing
        
        quality_score = 0
        
        for citation in citations:
            # Check citation format
            if "(" in citation and ")" in citation:  # Has date
                quality_score += 25
            if any(word in citation.lower() for word in ["department", "finsolve"]):  # Has author
                quality_score += 25
            if "p." in citation or "pp." in citation:  # Has page numbers
                quality_score += 25
            if len(citation) > 50:  # Detailed citation
                quality_score += 25
        
        return min(quality_score / len(citations), 100.0)
    
    def _validate_response_completeness(self, query: str, response: str, sources: List[str]) -> float:
        """Validate response completeness."""
        completeness_score = 0
        
        # Check if response addresses the query
        query_words = query.lower().split()
        response_lower = response.lower()
        
        addressed_words = sum(1 for word in query_words if word in response_lower)
        address_score = (addressed_words / len(query_words)) * 40 if query_words else 0
        
        # Check response structure
        if "based on" in response_lower or "according to" in response_lower:
            completeness_score += 20  # Shows source attribution
        
        if len(response.split('\n')) > 3:  # Structured response
            completeness_score += 20
        
        if sources and len(sources) > 1:  # Multiple sources
            completeness_score += 20
        
        total_score = address_score + completeness_score
        return min(total_score, 100.0)
    
    def _validate_factual_consistency(self, response: str, sources: List[str]) -> float:
        """Validate factual consistency (basic checks)."""
        # This is a simplified version - in production, you'd want more sophisticated fact-checking
        consistency_score = 80.0  # Default assumption of consistency
        
        # Check for contradictory statements
        contradictory_patterns = [
            (r'increase.*decrease', -10),
            (r'profit.*loss', -5),
            (r'success.*fail', -5),
            (r'high.*low', -3)
        ]
        
        response_lower = response.lower()
        for pattern, penalty in contradictory_patterns:
            if re.search(pattern, response_lower):
                consistency_score += penalty
        
        # Bonus for specific numbers and facts
        if re.search(r'\d+%', response):
            consistency_score += 5
        if re.search(r'\$\d+', response):
            consistency_score += 5
        
        return max(consistency_score, 0.0)
    
    def _calculate_enhanced_accuracy(self, original_accuracy: float, component_scores: Dict[str, float], rules: Dict[str, Any]) -> float:
        """Calculate enhanced accuracy score."""
        # Weighted combination of original accuracy and validation scores
        weights = {
            "original": 0.3,
            "source_quality": 0.15,
            "content_relevance": 0.20,
            "entity_extraction": 0.10,
            "citation_quality": 0.10,
            "response_completeness": 0.10,
            "factual_consistency": 0.05
        }
        
        enhanced_score = original_accuracy * weights["original"]
        
        for component, score in component_scores.items():
            weight = weights.get(component, 0)
            enhanced_score += (score / 100.0) * 100 * weight
        
        # Apply minimum accuracy requirement
        min_accuracy = rules.get("min_accuracy", 80.0)
        if enhanced_score < min_accuracy:
            # Penalty for not meeting minimum requirements
            enhanced_score = enhanced_score * 0.9
        
        return min(enhanced_score, 96.0)  # Cap at 96%
    
    def _generate_improvement_suggestions(self, query: str, response_data: Dict[str, Any], component_scores: Dict[str, float], rules: Dict[str, Any]) -> List[str]:
        """Generate specific improvement suggestions."""
        suggestions = []
        
        # Source quality suggestions
        if component_scores.get("source_quality", 0) < 70:
            suggestions.append("Consider rephrasing your query to match more relevant documents.")
            if len(response_data.get("sources", [])) < 2:
                suggestions.append("Try using broader search terms to find more sources.")
        
        # Content relevance suggestions
        if component_scores.get("content_relevance", 0) < 70:
            suggestions.append("Your query might be too specific or use terms not found in our documents.")
            suggestions.append("Try using synonyms or more general terms related to your topic.")
        
        # Entity extraction suggestions
        if component_scores.get("entity_extraction", 0) < 70:
            required_entities = rules.get("required_entities", [])
            if required_entities:
                suggestions.append(f"For {rules.get('keywords', [''])[0]} queries, try asking for specific {', '.join(required_entities)}.")
        
        # Citation quality suggestions
        if component_scores.get("citation_quality", 0) < 70 and rules.get("citation_required"):
            suggestions.append("The response may lack proper citations. This could indicate limited source material.")
        
        # Response completeness suggestions
        if component_scores.get("response_completeness", 0) < 70:
            suggestions.append("Try asking more specific questions to get more complete answers.")
            suggestions.append("Consider breaking complex questions into smaller, focused queries.")
        
        # General suggestions based on accuracy
        original_accuracy = response_data.get("accuracy_score", 0)
        if original_accuracy < 80:
            suggestions.append("Low accuracy detected. Try rephrasing your question or using different keywords.")
            suggestions.append("Make sure your question relates to topics covered in company documents.")
        
        return suggestions[:3]  # Limit to top 3 suggestions
    
    def _calculate_confidence_level(self, accuracy: float, component_scores: Dict[str, float]) -> str:
        """Calculate confidence level based on accuracy and component scores."""
        avg_component_score = sum(component_scores.values()) / len(component_scores) if component_scores else 0
        
        combined_score = (accuracy + avg_component_score) / 2
        
        if combined_score >= 90:
            return "very_high"
        elif combined_score >= 80:
            return "high"
        elif combined_score >= 70:
            return "medium"
        elif combined_score >= 60:
            return "low"
        else:
            return "very_low"
    
    def _store_accuracy_data(self, query: str, validation_result: Dict[str, Any]):
        """Store accuracy data for learning and improvement."""
        accuracy_record = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "query_category": validation_result.get("query_category"),
            "original_accuracy": validation_result.get("original_accuracy"),
            "enhanced_accuracy": validation_result.get("enhanced_accuracy"),
            "confidence_level": validation_result.get("confidence_level"),
            "component_scores": validation_result.get("quality_metrics", {})
        }
        
        self.accuracy_history.append(accuracy_record)
        
        # Keep only last 100 records
        if len(self.accuracy_history) > 100:
            self.accuracy_history = self.accuracy_history[-100:]
    
    def get_accuracy_analytics(self) -> Dict[str, Any]:
        """Get accuracy analytics and trends."""
        if not self.accuracy_history:
            return {"message": "No accuracy data available yet."}
        
        recent_records = self.accuracy_history[-20:]  # Last 20 queries
        
        analytics = {
            "total_queries": len(self.accuracy_history),
            "recent_average_accuracy": sum(r["enhanced_accuracy"] for r in recent_records) / len(recent_records),
            "accuracy_trend": self._calculate_accuracy_trend(),
            "category_performance": self._analyze_category_performance(),
            "confidence_distribution": self._analyze_confidence_distribution(),
            "improvement_opportunities": self._identify_improvement_opportunities()
        }
        
        return analytics
    
    def _calculate_accuracy_trend(self) -> str:
        """Calculate accuracy trend over time."""
        if len(self.accuracy_history) < 10:
            return "insufficient_data"
        
        recent_10 = self.accuracy_history[-10:]
        previous_10 = self.accuracy_history[-20:-10] if len(self.accuracy_history) >= 20 else self.accuracy_history[:-10]
        
        recent_avg = sum(r["enhanced_accuracy"] for r in recent_10) / len(recent_10)
        previous_avg = sum(r["enhanced_accuracy"] for r in previous_10) / len(previous_10)
        
        if recent_avg > previous_avg + 2:
            return "improving"
        elif recent_avg < previous_avg - 2:
            return "declining"
        else:
            return "stable"
    
    def _analyze_category_performance(self) -> Dict[str, float]:
        """Analyze performance by query category."""
        category_scores = defaultdict(list)
        
        for record in self.accuracy_history:
            category = record.get("query_category", "unknown")
            accuracy = record.get("enhanced_accuracy", 0)
            category_scores[category].append(accuracy)
        
        return {
            category: sum(scores) / len(scores)
            for category, scores in category_scores.items()
        }
    
    def _analyze_confidence_distribution(self) -> Dict[str, int]:
        """Analyze confidence level distribution."""
        confidence_counts = Counter(
            record.get("confidence_level", "unknown")
            for record in self.accuracy_history
        )
        
        return dict(confidence_counts)
    
    def _identify_improvement_opportunities(self) -> List[str]:
        """Identify key improvement opportunities."""
        opportunities = []
        
        # Analyze component scores across all records
        component_averages = defaultdict(list)
        
        for record in self.accuracy_history:
            for component, score in record.get("component_scores", {}).items():
                component_averages[component].append(score)
        
        # Find components with low average scores
        for component, scores in component_averages.items():
            avg_score = sum(scores) / len(scores)
            if avg_score < 75:
                opportunities.append(f"Improve {component.replace('_', ' ')}: current average {avg_score:.1f}%")
        
        return opportunities[:3]  # Top 3 opportunities


# Global instance
accuracy_enhancer = AccuracyEnhancer()