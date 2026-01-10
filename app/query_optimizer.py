"""
Query Optimization System for Enhanced RAG Accuracy
Preprocesses and optimizes user queries for better retrieval and response accuracy.
"""

import re
from typing import Dict, List, Tuple, Any
from datetime import datetime


class QueryOptimizer:
    """
    Advanced query optimization system to improve RAG accuracy.
    Handles query expansion, normalization, and intent detection.
    """
    
    def __init__(self):
        self.synonyms = self._load_synonyms()
        self.query_patterns = self._load_query_patterns()
        self.stopwords = self._load_stopwords()
        
    def _load_synonyms(self) -> Dict[str, List[str]]:
        """Load domain-specific synonyms for query expansion."""
        return {
            # Financial terms
            "revenue": ["income", "earnings", "sales", "turnover"],
            "profit": ["earnings", "income", "margin", "return"],
            "expense": ["cost", "expenditure", "spending", "outlay"],
            "budget": ["allocation", "funding", "financial plan"],
            "quarterly": ["q1", "q2", "q3", "q4", "quarter"],
            
            # HR terms
            "employee": ["staff", "worker", "personnel", "team member"],
            "policy": ["rule", "guideline", "procedure", "regulation"],
            "benefit": ["perk", "advantage", "compensation", "package"],
            "vacation": ["leave", "time off", "holiday", "pto"],
            "training": ["development", "education", "learning", "skill building"],
            
            # Marketing terms
            "campaign": ["initiative", "program", "promotion", "effort"],
            "customer": ["client", "consumer", "user", "buyer"],
            "market": ["industry", "sector", "segment", "audience"],
            "engagement": ["interaction", "participation", "involvement"],
            "conversion": ["sale", "acquisition", "signup", "purchase"],
            
            # Engineering terms
            "system": ["platform", "infrastructure", "architecture", "framework"],
            "development": ["coding", "programming", "building", "creation"],
            "deployment": ["release", "launch", "rollout", "implementation"],
            "performance": ["speed", "efficiency", "optimization", "throughput"],
            "security": ["protection", "safety", "privacy", "encryption"],
            
            # General business terms
            "company": ["organization", "business", "firm", "corporation"],
            "team": ["group", "department", "unit", "division"],
            "process": ["procedure", "workflow", "method", "approach"],
            "goal": ["objective", "target", "aim", "purpose"],
            "strategy": ["plan", "approach", "method", "tactic"]
        }
    
    def _load_query_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load query patterns for intent detection and optimization."""
        return {
            "definition": {
                "patterns": [r"what is", r"define", r"explain", r"meaning of"],
                "optimization": "add_context_keywords",
                "expected_entities": []
            },
            "comparison": {
                "patterns": [r"difference between", r"compare", r"vs", r"versus"],
                "optimization": "expand_comparison_terms",
                "expected_entities": []
            },
            "quantitative": {
                "patterns": [r"how much", r"how many", r"what percentage", r"cost of"],
                "optimization": "add_numeric_context",
                "expected_entities": ["numbers", "percentages", "currencies"]
            },
            "temporal": {
                "patterns": [r"when", r"what time", r"schedule", r"deadline"],
                "optimization": "add_time_context",
                "expected_entities": ["dates"]
            },
            "procedural": {
                "patterns": [r"how to", r"steps", r"process", r"procedure"],
                "optimization": "add_process_keywords",
                "expected_entities": []
            },
            "location": {
                "patterns": [r"where", r"location", r"office", r"address"],
                "optimization": "add_location_context",
                "expected_entities": []
            }
        }
    
    def _load_stopwords(self) -> List[str]:
        """Load stopwords to filter out during optimization."""
        return [
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "is", "are", "was", "were", "be", "been", "have",
            "has", "had", "do", "does", "did", "will", "would", "could", "should",
            "may", "might", "can", "this", "that", "these", "those", "i", "you",
            "he", "she", "it", "we", "they", "me", "him", "her", "us", "them"
        ]
    
    def optimize_query(self, query: str, user_role: str = "Employee") -> Dict[str, Any]:
        """
        Comprehensive query optimization for enhanced accuracy.
        """
        optimization_result = {
            "original_query": query,
            "optimized_query": query,
            "query_intent": "general",
            "expanded_terms": [],
            "suggested_alternatives": [],
            "optimization_score": 0.0,
            "role_specific_hints": []
        }
        
        try:
            # 1. Clean and normalize query
            cleaned_query = self._clean_query(query)
            
            # 2. Detect query intent
            intent = self._detect_query_intent(cleaned_query)
            
            # 3. Expand query with synonyms
            expanded_query, expanded_terms = self._expand_query_synonyms(cleaned_query)
            
            # 4. Apply intent-specific optimizations
            optimized_query = self._apply_intent_optimization(expanded_query, intent)
            
            # 5. Add role-specific context
            role_optimized_query, role_hints = self._add_role_context(optimized_query, user_role)
            
            # 6. Generate alternative queries
            alternatives = self._generate_query_alternatives(role_optimized_query, intent)
            
            # 7. Calculate optimization score
            optimization_score = self._calculate_optimization_score(
                query, role_optimized_query, expanded_terms, intent
            )
            
            optimization_result.update({
                "optimized_query": role_optimized_query,
                "query_intent": intent,
                "expanded_terms": expanded_terms,
                "suggested_alternatives": alternatives,
                "optimization_score": optimization_score,
                "role_specific_hints": role_hints
            })
            
        except Exception as e:
            optimization_result["error"] = str(e)
            optimization_result["optimized_query"] = query  # Fallback to original
        
        return optimization_result
    
    def _clean_query(self, query: str) -> str:
        """Clean and normalize the query."""
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', query.strip())
        
        # Fix common typos and variations
        typo_fixes = {
            r'\bfinsolve\b': 'FinSolve',
            r'\bq(\d)\b': r'Q\1',
            r'\b(\d+)%\b': r'\1 percent',
            r'\$(\d+)': r'\1 dollars'
        }
        
        for pattern, replacement in typo_fixes.items():
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
        
        return cleaned
    
    def _detect_query_intent(self, query: str) -> str:
        """Detect the intent of the query."""
        query_lower = query.lower()
        
        intent_scores = {}
        for intent, config in self.query_patterns.items():
            score = 0
            for pattern in config["patterns"]:
                if re.search(pattern, query_lower):
                    score += 1
            intent_scores[intent] = score
        
        # Return intent with highest score, or "general" if no matches
        if intent_scores and max(intent_scores.values()) > 0:
            return max(intent_scores.items(), key=lambda x: x[1])[0]
        return "general"
    
    def _expand_query_synonyms(self, query: str) -> Tuple[str, List[str]]:
        """Expand query with relevant synonyms."""
        words = query.lower().split()
        expanded_terms = []
        expanded_words = []
        
        for word in words:
            expanded_words.append(word)
            
            # Check if word has synonyms
            if word in self.synonyms:
                # Add the most relevant synonym (first one)
                synonym = self.synonyms[word][0]
                expanded_words.append(synonym)
                expanded_terms.append(f"{word} -> {synonym}")
        
        expanded_query = " ".join(expanded_words)
        return expanded_query, expanded_terms
    
    def _apply_intent_optimization(self, query: str, intent: str) -> str:
        """Apply intent-specific optimizations."""
        if intent not in self.query_patterns:
            return query
        
        optimization_type = self.query_patterns[intent].get("optimization")
        
        if optimization_type == "add_context_keywords":
            return f"{query} definition explanation overview"
        
        elif optimization_type == "expand_comparison_terms":
            return f"{query} comparison analysis difference"
        
        elif optimization_type == "add_numeric_context":
            return f"{query} amount number percentage cost value"
        
        elif optimization_type == "add_time_context":
            return f"{query} date time schedule when deadline"
        
        elif optimization_type == "add_process_keywords":
            return f"{query} steps procedure process how method"
        
        elif optimization_type == "add_location_context":
            return f"{query} location where office address place"
        
        return query
    
    def _add_role_context(self, query: str, user_role: str) -> Tuple[str, List[str]]:
        """Add role-specific context to improve accuracy."""
        role_keywords = {
            "Finance": ["financial", "budget", "revenue", "cost", "profit"],
            "Marketing": ["marketing", "campaign", "customer", "market", "engagement"],
            "HR": ["employee", "policy", "benefit", "training", "handbook"],
            "Engineering": ["technical", "system", "development", "architecture"],
            "C-Level": ["strategic", "executive", "leadership", "overview", "performance"],
            "Employee": ["general", "company", "policy", "information"]
        }
        
        hints = []
        role_context = ""
        
        if user_role in role_keywords:
            keywords = role_keywords[user_role]
            
            # Add role-specific keywords if not already present
            query_lower = query.lower()
            missing_keywords = [kw for kw in keywords if kw not in query_lower]
            
            if missing_keywords:
                # Add the most relevant keyword
                role_context = f" {missing_keywords[0]}"
                hints.append(f"Added '{missing_keywords[0]}' context for {user_role} role")
        
        optimized_query = query + role_context
        return optimized_query, hints
    
    def _generate_query_alternatives(self, query: str, intent: str) -> List[str]:
        """Generate alternative query formulations."""
        alternatives = []
        
        # Intent-based alternatives
        if intent == "definition":
            alternatives.extend([
                f"What does {query.replace('what is', '').strip()} mean?",
                f"Explain {query.replace('what is', '').strip()}",
                f"Define {query.replace('what is', '').strip()}"
            ])
        
        elif intent == "quantitative":
            base_query = query.replace("how much", "").replace("how many", "").strip()
            alternatives.extend([
                f"What is the cost of {base_query}?",
                f"What percentage {base_query}?",
                f"Show me numbers for {base_query}"
            ])
        
        elif intent == "procedural":
            base_query = query.replace("how to", "").strip()
            alternatives.extend([
                f"What are the steps for {base_query}?",
                f"Process for {base_query}",
                f"Procedure to {base_query}"
            ])
        
        # General alternatives using synonyms
        words = query.split()
        if len(words) > 1:
            # Try replacing key terms with synonyms
            for i, word in enumerate(words):
                if word.lower() in self.synonyms:
                    synonym = self.synonyms[word.lower()][0]
                    alt_words = words.copy()
                    alt_words[i] = synonym
                    alternatives.append(" ".join(alt_words))
        
        # Remove duplicates and limit to 3 alternatives
        unique_alternatives = list(set(alternatives))[:3]
        return [alt for alt in unique_alternatives if alt != query]
    
    def _calculate_optimization_score(self, original: str, optimized: str, expanded_terms: List[str], intent: str) -> float:
        """Calculate optimization effectiveness score."""
        score = 0.0
        
        # Base score for successful processing
        score += 20.0
        
        # Score for query expansion
        if expanded_terms:
            score += min(len(expanded_terms) * 10, 30)  # Max 30 points
        
        # Score for intent detection
        if intent != "general":
            score += 20.0
        
        # Score for query enhancement
        original_words = set(original.lower().split())
        optimized_words = set(optimized.lower().split())
        new_words = optimized_words - original_words
        
        if new_words:
            score += min(len(new_words) * 5, 20)  # Max 20 points
        
        # Score for query length appropriateness
        word_count = len(optimized.split())
        if 3 <= word_count <= 15:  # Optimal range
            score += 10.0
        
        return min(score, 100.0)
    
    def suggest_query_improvements(self, query: str, accuracy_score: float) -> List[str]:
        """Suggest specific query improvements based on accuracy."""
        suggestions = []
        
        if accuracy_score < 70:
            suggestions.extend([
                "Try using more specific terms related to your topic",
                "Include relevant keywords from your department or role",
                "Break complex questions into simpler, focused queries"
            ])
        
        if len(query.split()) < 3:
            suggestions.append("Add more descriptive words to your query")
        
        if len(query.split()) > 20:
            suggestions.append("Try shortening your query and focus on key terms")
        
        # Check for common issues
        if not re.search(r'[?.]$', query):
            suggestions.append("Consider phrasing your query as a clear question")
        
        if query.isupper():
            suggestions.append("Use normal capitalization for better results")
        
        # Domain-specific suggestions
        query_lower = query.lower()
        if any(word in query_lower for word in ["cost", "price", "budget", "money"]):
            suggestions.append("For financial queries, specify time periods (Q1, Q2, etc.) or fiscal year")
        
        if any(word in query_lower for word in ["policy", "rule", "procedure"]):
            suggestions.append("For policy questions, mention specific departments or employee types")
        
        return suggestions[:3]  # Limit to top 3 suggestions


# Global instance
query_optimizer = QueryOptimizer()