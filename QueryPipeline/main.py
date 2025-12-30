from typing import Dict, List, Tuple

from QueryPipeline.normalize import QueryNormalizer
from roleBasedAccess.rbac_engine import RBACEngine
from chunking.chunk_filter import ChunkFilter
from VectorDB.vector_retrive import VectorRetriever
from QueryPipeline.ReRanker import ReRanker
from QueryPipeline.Deduplicator import Deduplicator
from QueryPipeline.ThresholdGate import ThresholdGate

class RAGPipeline:
    def __init__(
        self,
        abbreviations: Dict[str, str],
        chunk_to_doc_map: Dict[str, str]
    ):
        # Step 1: Query normalization
        self.normalizer = QueryNormalizer(abbreviations)

        # Step 2: Role expansion (RBAC)
        self.rbac = RBACEngine()

        # Step 3: Chunk filtering (security gate)
        self.chunk_filter = ChunkFilter()

        # Step 4: Vector retrieval
        self.retriever = VectorRetriever()

        # Step 5: Multi-query ranking
        self.reranker = ReRanker()

        # Step 6: Deduplication & diversity
        self.deduplicator = Deduplicator(chunk_to_doc_map)

        # Step 7: Thresholding
        self.threshold_gate = ThresholdGate()

    def process_query(
        self,
        user_query: str,
        user_role: str,
        embed_fn
    ) -> Dict:
        """
        Main pipeline entry point.
        """

        # -------- STEP 1: Normalize --------
        query_variants = self.normalizer.normalize(user_query)

        # -------- STEP 2: Expand Roles --------
        effective_roles = self.rbac.expand_roles(user_role)

        # -------- STEP 3: Filter Chunks --------
        allowed_chunks = self.chunk_filter.filter_allowed_chunks(effective_roles)

        if not allowed_chunks:
            return {
                "answerable": False,
                "reason": "No accessible data for this role"
            }

        # -------- STEP 4 + 5: Retrieve & Aggregate --------
        all_results: List[List[Tuple[str, float]]] = []

        for q in query_variants:
            q_embedding = embed_fn(q)
            results = self.retriever.retrieve(q_embedding, allowed_chunks)
            all_results.append(results)

        ranked_chunks = self.reranker.aggregate_scores(all_results)

        # -------- STEP 6: Deduplication --------
        deduped_chunks = self.deduplicator.deduplicate(ranked_chunks)

        # -------- STEP 7: Thresholding --------
        if not self.threshold_gate.is_confident(deduped_chunks):
            return {
                "answerable": False,
                "reason": "Low confidence retrieval"
            }

        # -------- STEP 8: Final Assembly --------
        return {
            "answerable": True,
            "chunks": deduped_chunks
        }
