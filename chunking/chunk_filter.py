import json
from typing import Set, List


class ChunkFilter:
    def __init__(self, chunks_path="chunking/chunks.json"):
        with open(chunks_path, "r") as f:
            self.chunks = json.load(f)  # THIS IS A LIST

    def filter_allowed_chunks(self, roles: Set[str]) -> List[str]:
        """
        Filters chunks based on role keywords in chunk_id
        """
        allowed_chunks = []

        for chunk in self.chunks:
            chunk_id = chunk["chunk_id"]

            # Role-based visibility logic
            if "finance" in chunk_id.lower() and "finance_manager" not in roles:
                continue

            if "engineering" in chunk_id.lower() and "admin" not in roles:
                continue

            # Allowed
            allowed_chunks.append(chunk_id)

        return allowed_chunks
