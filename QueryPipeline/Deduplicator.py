from typing import List, Tuple, Dict, Set


class Deduplicator:
    """
    STEP 6: Deduplication & Diversity Control
    -----------------------------------------
    Ensures clean, diverse context for the LLM.
    """

    def __init__(self, chunk_to_doc_map: Dict[str, str]):
        """
        chunk_to_doc_map:
        {
          'FINANCE_CHUNK_12': 'FINANCE_DOC_A',
          'FINANCE_CHUNK_13': 'FINANCE_DOC_A',
          'FINANCE_CHUNK_20': 'FINANCE_DOC_B'
        }
        """
        self.chunk_to_doc_map = chunk_to_doc_map

    def deduplicate(
        self,
        ranked_chunks: List[Tuple[str, float]],
        max_chunks: int = 5
    ) -> List[Tuple[str, float]]:

        seen_chunks: Set[str] = set()
        seen_docs: Set[str] = set()
        output: List[Tuple[str, float]] = []

        for chunk_id, score in ranked_chunks:
            if chunk_id in seen_chunks:
                continue

            doc_id = self.chunk_to_doc_map.get(chunk_id)

            # Document-level diversity
            if doc_id and doc_id in seen_docs:
                continue

            seen_chunks.add(chunk_id)
            if doc_id:
                seen_docs.add(doc_id)

            output.append((chunk_id, score))

            if len(output) >= max_chunks:
                break

        return output
