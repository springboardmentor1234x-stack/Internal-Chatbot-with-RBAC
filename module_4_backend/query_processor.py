"""
Query Normalization and Processing
Implements query preprocessing pipeline for better retrieval
"""

import re
from typing import List


class QueryProcessor:
    """
    Query processor for normalizing and processing user queries
    """
    
    def __init__(self):
        """Initialize query processor"""
        pass
    
    def process_query(self, query: str) -> str:
        """
        Process query and return the best variant for embedding
        
        Args:
            query: Raw user query
        
        Returns:
            Processed query string suitable for embedding
        """
        # Use the full processing pipeline and return the expanded version
        result = process_query(query)
        # Return the expanded version which includes abbreviation expansion
        return result['expanded']


# Stop words for removal
STOP_WORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
    'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
    'to', 'was', 'will', 'with', 'what', 'when', 'where', 'who', 'how'
}

# Domain-specific abbreviations from dataset
ABBREVIATIONS = {
    'q1': 'quarter 1 first quarter',
    'q2': 'quarter 2 second quarter',
    'q3': 'quarter 3 third quarter',
    'q4': 'quarter 4 fourth quarter',
    'yr': 'year',
    'yoy': 'year over year',
    'roi': 'return on investment',
    'kpi': 'key performance indicator',
    'hr': 'human resources',
}


def normalize_query(query: str) -> str:
    """
    Normalize query text
    
    Steps:
    1. Lowercase
    2. Regex cleaning (remove special chars)
    3. Basic normalization
    """
    # Step 1: Lowercase
    query = query.lower()
    
    # Step 2: Remove special characters but keep spaces
    query = re.sub(r'[^a-z0-9\s-]', ' ', query)
    
    # Remove extra whitespace
    query = ' '.join(query.split())
    
    return query


def expand_abbreviations(text: str) -> str:
    """
    Expand domain-specific abbreviations
    
    Step 4: Abbreviation expansion
    """
    words = text.split()
    expanded = []
    
    for word in words:
        if word in ABBREVIATIONS:
            expanded.append(ABBREVIATIONS[word])
        else:
            expanded.append(word)
    
    return ' '.join(expanded)


def expand_quarter_ranges(text: str) -> str:
    """
    Expand quarter ranges (Q1-Q3 -> Q1 Q2 Q3)
    
    Step 4b: Quarter range expansion
    """
    # Match patterns like Q1-Q3, q1-q3
    pattern = r'q(\d)-q(\d)'
    
    def expand_range(match):
        start, end = int(match.group(1)), int(match.group(2))
        quarters = [f'q{i}' for i in range(start, end + 1)]
        return ' '.join(quarters)
    
    return re.sub(pattern, expand_range, text)


def remove_stopwords(text: str) -> str:
    """
    Remove common stop words
    
    Step 5: Stopword removal
    """
    words = text.split()
    filtered = [w for w in words if w not in STOP_WORDS]
    return ' '.join(filtered)


def generate_ngrams(text: str, n: int = 2) -> List[str]:
    """
    Generate n-grams from text
    
    Step 6: N-gram generation
    """
    words = text.split()
    ngrams = []
    
    for i in range(len(words) - n + 1):
        ngram = ' '.join(words[i:i+n])
        ngrams.append(ngram)
    
    return ngrams


def extract_key_terms(text: str) -> List[str]:
    """
    Extract important domain-specific terms
    
    Step 7: Extract domain-specific terms
    """
    domain_keywords = [
        'revenue', 'profit', 'loss', 'growth', 'performance',
        'sales', 'marketing', 'campaign', 'budget', 'cost',
        'employee', 'hiring', 'retention', 'training',
        'engineering', 'development', 'product', 'feature',
        'quarter', 'annual', 'monthly', 'report'
    ]
    
    words = text.split()
    key_terms = [w for w in words if w in domain_keywords]
    
    return key_terms


def process_query(query: str) -> dict:
    """
    Full query processing pipeline
    
    Returns:
    - normalized: normalized query
    - expanded: with abbreviations expanded
    - without_stopwords: stopwords removed
    - key_terms: domain-specific terms
    - bigrams: 2-grams
    """
    # Step 1-3: Basic normalization
    normalized = normalize_query(query)
    
    # Step 4: Abbreviation expansion
    expanded = expand_abbreviations(normalized)
    expanded = expand_quarter_ranges(expanded)
    
    # Step 5: Stopword removal
    without_stopwords = remove_stopwords(expanded)
    
    # Step 6: N-grams
    bigrams = generate_ngrams(without_stopwords, 2)
    
    # Step 7: Key terms
    key_terms = extract_key_terms(without_stopwords)
    
    return {
        'normalized': normalized,
        'expanded': expanded,
        'without_stopwords': without_stopwords,
        'key_terms': key_terms,
        'bigrams': bigrams
    }


def generate_query_variants(query: str) -> List[str]:
    """
    Generate multiple query variants for better retrieval
    
    Step 2: Generate query variants
    """
    processed = process_query(query)
    
    variants = [
        query,  # Original
        processed['normalized'],  # Normalized
        processed['expanded'],  # With abbreviations expanded
        processed['without_stopwords'],  # Without stopwords
    ]
    
    # Add key term combinations
    if processed['key_terms']:
        variants.append(' '.join(processed['key_terms']))
    
    # Remove duplicates while preserving order
    seen = set()
    unique_variants = []
    for v in variants:
        if v and v not in seen:
            seen.add(v)
            unique_variants.append(v)
    
    return unique_variants
