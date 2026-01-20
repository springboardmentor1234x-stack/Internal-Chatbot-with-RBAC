import unicodedata
import re
from typing import List, Dict


def normalize_text(text: str) -> str:
    # Unicode normalization
    text = unicodedata.normalize("NFKC", text)

    # Replace multiple spaces with single space
    text = re.sub(r"[ \t]+", " ", text)

    # Replace multiple newlines with single newline
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    # Trim leading/trailing whitespace
    return text.strip()


def normalize_chunks(chunks: List[Dict]) -> List[Dict]:
    normalized = []

    for chunk in chunks:
        normalized_chunk = {
            "chunk_id": chunk["chunk_id"],
            "text": normalize_text(chunk["text"]),
            "metadata": chunk["metadata"],
        }
        normalized.append(normalized_chunk)

    return normalized
