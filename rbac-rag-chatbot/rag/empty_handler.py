from typing import Dict


def handle_empty_retrieval(user_query: str) -> Dict:
    return {
        "answer": (
            "I couldn’t find any authorized information to answer your question. "
            "This may be because the information does not exist or you do not have "
            "permission to access it."
        ),
        "sources": [],
        "confidence": "low",
        "query": user_query,
    }
