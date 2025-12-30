import re
from typing import List, Dict


class QueryNormalizer:
    def __init__(self, abbreviations: Dict[str, str]):
        self.abbreviations = abbreviations

        self.abbr_patterns = {
            abbr: re.compile(rf"\b{re.escape(abbr)}\b", re.IGNORECASE)
            for abbr in abbreviations
        }

        self.stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on",
            "at", "to", "for", "of", "is", "are", "was", "were"
        }

        self.important_terms = {
            "revenue", "profit", "expense", "cost", "margin", "growth",
            "employee", "salary", "intern", "leave", "policy",
            "finance", "hr", "engineering", "marketing",
            "quarter", "annual", "monthly", "year",
            "performance", "compliance", "procedure", "guideline"
        }

        self.synonym_map = {
            "revenue": "revenue income earnings",
            "profit": "profit earnings margin",
            "cost": "cost expense expenditure",
            "employee": "employee staff personnel",
            "intern": "intern trainee apprentice",
            "customer": "customer client user",
            "growth": "growth increase expansion"
        }

    # -----------------------------
    # Core normalization
    # -----------------------------

    def clean_text(self, query: str) -> str:
        query = query.lower()
        query = query.replace("&", " and ").replace("%", " percent ")
        query = query.replace("/", " or ").replace("vs.", " versus ").replace("vs", " versus ")
        query = re.sub(r"q(\d)\s*-\s*q(\d)", r"q\1 to q\2", query)
        query = re.sub(r"[^\w\s]", " ", query)
        query = re.sub(r"\s+", " ", query).strip()
        return query

    def expand_abbreviations(self, query: str) -> str:
        for abbr, pattern in self.abbr_patterns.items():
            query = pattern.sub(self.abbreviations[abbr], query)
        return query

    def expand_ranges(self, query: str) -> str:
        query = re.sub(
            r"q(\d)\s*(?:to|-)\s*q(\d)",
            lambda m: " ".join(f"q{i}" for i in range(int(m.group(1)), int(m.group(2)) + 1)),
            query,
            flags=re.IGNORECASE
        )
        return query

    # -----------------------------
    # Variants
    # -----------------------------

    def remove_stopwords(self, query: str) -> str:
        return " ".join(w for w in query.split() if w not in self.stop_words)

    def extract_key_terms(self, query: str) -> str:
        words = query.split()
        return " ".join(w for w in words if w in self.important_terms)

    def expand_synonyms(self, query: str) -> str:
        words = []
        for w in query.split():
            words.append(self.synonym_map.get(w, w))
        expanded = " ".join(words)
        return expanded if expanded != query else query

    # -----------------------------
    # Public API
    # -----------------------------

    def normalize(self, raw_query: str) -> List[str]:
        q = self.clean_text(raw_query)
        q = self.expand_abbreviations(q)
        q = self.expand_ranges(q)

        variants = [
            q,
            self.remove_stopwords(q),
            self.extract_key_terms(q),
            self.expand_synonyms(q)
        ]

        seen = set()
        return [v for v in variants if v and not (v in seen or seen.add(v))]
