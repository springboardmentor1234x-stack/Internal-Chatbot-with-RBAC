from typing import List, Tuple


class ThresholdGate:
    """
    STEP 7: Thresholding (Hallucination Guard)
    -----------------------------------------
    Decides whether retrieved content is strong enough
    to be sent to the LLM.
    """

    def __init__(
        self,
        min_top_score: float = 0.2,
        min_chunks: int = 1
    ):
        self.min_top_score = min_top_score
        self.min_chunks = min_chunks

    def is_confident(
        self,
        chunks: List[Tuple[str, float]]
    ) -> bool:
        """
        Returns True if the retrieval quality is acceptable.
        """

        if not chunks:
            return False

        top_score = chunks[0][1]

        if top_score < self.min_top_score:
            return False

        if len(chunks) < self.min_chunks:
            return False

        return True
