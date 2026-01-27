import re
from typing import List, Dict

class QueryNormalizer:
    """Normalize and expand search queries"""
    
    def __init__(self, abbreviations: Dict[str, str]):
        self.abbreviations = abbreviations
        
        # Compile regex patterns for better performance
        self.abbr_patterns = {}

        for abbr in abbreviations.keys():
            if abbr.lower() == "q":
                # Match q followed by a digit (q1, q2, ...)
                self.abbr_patterns[abbr] = re.compile(
                    r"\bq(\d)\b",
                    re.IGNORECASE
                )
            else:
                # Normal word abbreviations
                self.abbr_patterns[abbr] = re.compile(
                    rf"\b{re.escape(abbr)}\b",
                    re.IGNORECASE
                )
    
    def expand_abbreviations(self, query: str) -> str:
        """Expand abbreviations in query"""
        result = query

        for abbr, pattern in self.abbr_patterns.items():
            full_term = self.abbreviations[abbr]
            result = pattern.sub(full_term, result)

        return result
    
    def expand_ranges(self, query: str) -> str:
        """Expand quarter ranges (Q1-Q3 -> Q1 Q2 Q3)"""
        # Handle Q1-Q3 format
        def expand_quarter_range(match):
            start = int(match.group(1))
            end = int(match.group(2))
            return " ".join(f"quarter {i}" for i in range(start, end + 1))
        
        result = re.sub(
            r"quarter\s*(\d)\s*(?:-|\bto\b)\s*quarter\s*(\d)",
            expand_quarter_range,
            query,
            flags=re.IGNORECASE
        )
        
        # Handle abbreviated format: q1-q3
        result = re.sub(
            r"q(\d)\s*(?:-|\bto\b)\s*q(\d)",
            lambda m: " ".join(f"q{i}" for i in range(int(m.group(1)), int(m.group(2)) + 1)),
            result,
            flags=re.IGNORECASE
        )
        
        return result
    
    def clean_text(self, query: str) -> str:
        """Clean and normalize query text"""
        # Convert to lowercase
        query = query.lower()
        
        # Replace common symbols
        query = query.replace("&", " and ")
        query = query.replace("%", " percent ")
        query = query.replace("/", " or ")
        query = query.replace("vs", " versus ")
        query = query.replace("vs.", " versus ")
        
        query = re.sub(r"q(\d)[-]q(\d)", r"q\1 to q\2", query)

        # Remove special characters but keep periods for decimals
        query = re.sub(r"[^\w\s\.]", " ", query)
        
        # Normalize whitespace
        query = re.sub(r"\s+", " ", query).strip()

        return query
    
    def normalize(self, query: str) -> str:
        """Complete normalization pipeline"""
        # Step 1: Clean text
        query = self.clean_text(query)
        
        # Step 2: Expand abbreviations
        query = self.expand_abbreviations(query)

        # Step 3: Expand ranges
        query = self.expand_ranges(query)
        
        # Step 4: Final cleanup
        query = re.sub(r"\s+", " ", query).strip()
        
        return query
    
    def generate_variants(self, query: str) -> List[str]:
        """Generate query variants for better retrieval"""
        variants = [query]  # Original query
        
        # Variant 1: Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        words = query.split()
        filtered_words = [w for w in words if w not in stop_words]
        if len(filtered_words) != len(words):
            variants.append(" ".join(filtered_words))
        
        # Variant 2: Extract key terms
        key_terms = self._extract_key_terms(query)
        if key_terms and key_terms != query:
            variants.append(key_terms)

        # Remove duplicates while preserving order
        seen = set()
        unique_variants = []
        for v in variants:
            if v not in seen and v.strip():
                seen.add(v)
                unique_variants.append(v)
        
        return unique_variants
    
    def _extract_key_terms(self, query: str) -> str:
        """Extract important domain-specific terms"""
        important_terms = {
            'revenue', 'profit', 'expense', 'cost', 'margin', 'growth',
            'customer', 'acquisition', 'retention', 'lifetime', 'value',
            'employee', 'salary', 'attrition', 'hiring', 'performance',
            'marketing', 'campaign', 'conversion', 'engagement',
            'engineering', 'architecture', 'security', 'api', 'system',
            'quarter', 'annual', 'monthly', 'financial', 'year',
            'policy', 'compliance', 'procedure', 'guideline'
        }
        
        words = query.split()
        key_words = []
        skip_next = False

        for i, w in enumerate(words):
            if skip_next:
                skip_next = False
                continue

            if w == "quarter" and i + 1 < len(words) and words[i + 1].isdigit():
                key_words.append(f"quarter {words[i + 1]}")
                skip_next = True
            elif w in important_terms:
                key_words.append(w)
        
        return " ".join(key_words) if key_words else query
    