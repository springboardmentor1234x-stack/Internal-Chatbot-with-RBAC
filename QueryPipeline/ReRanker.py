from collections import defaultdict
from typing import List, Dict


class ReRanker:
    """
    Aggregates scores across multiple query variants
    """

    def aggregate_scores(
        self,
        multi_query_results: List[List[tuple]]
    ) -> List[tuple]:
        """
        Input:
        [
          [('CHUNK1', 0.82), ('CHUNK2', 0.79)],
          [('CHUNK2', 0.85), ('CHUNK3', 0.77)]
        ]

        Output:
        [('CHUNK2', 1.64), ('CHUNK1', 0.82), ('CHUNK3', 0.77)]
        """

        score_map = defaultdict(float)

        for query_result in multi_query_results:
            for chunk_id, score in query_result:
                score_map[chunk_id] += score

        return sorted(score_map.items(), key=lambda x: x[1], reverse=True)
