from typing import List
import chromadb
from chromadb.config import Settings

from chat.history_schema import (
    build_user_message,
    build_assistant_message,
)


class ChatHistoryStore:
    """
    Persistent chat history storage using ChromaDB.
    """

    def __init__(self, persist_dir: str = "vector_db"):
        self.client = chromadb.Client(
            Settings(
                persist_directory=persist_dir,
                anonymized_telemetry=False,
            )
        )

        self.collection = self.client.get_or_create_collection(
            name="chat_history"
        )

    # -------------------------
    # HELPER FUNCTIONS
    # -------------------------

    @staticmethod
    def _sanitize_metadata(metadata: dict) -> dict:
        """
        Ensure all metadata values are valid types for ChromaDB.
        Replace None with empty string.
        """
        sanitized = {}
        for k, v in metadata.items():
            if v is None:
                sanitized[k] = ""
            elif isinstance(v, (str, int, float, bool)):
                sanitized[k] = v
            else:
                # fallback: convert to string
                sanitized[k] = str(v)
        return sanitized

    def _generate_id(self, message: dict) -> str:
        meta = message.get("metadata", {})
        user_id = meta.get("user_id", "unknown_user")
        timestamp = meta.get("timestamp", "unknown_time")
        return f"{user_id}::{timestamp}"

    # -------------------------
    # WRITE OPERATIONS
    # -------------------------

    def add_message(self, message: dict):
        """
        Append a chat message (user or assistant).
        """
        metadata = self._sanitize_metadata(message.get("metadata", {}))

        self.collection.add(
            documents=[message["content"]],
            metadatas=[metadata],
            ids=[self._generate_id(message)],
        )

        # Removed self.client.persist() since it's no longer needed

    def add_user_message(self, user_id: str, content: str, session_id: str = None):
        message = build_user_message(user_id, content, session_id)
        self.add_message(message)

    def add_assistant_message(
        self,
        user_id: str,
        content: str,
        sources: List[dict],
        confidence: str,
        session_id: str = None,
    ):
        message = build_assistant_message(
            user_id=user_id,
            content=content,
            sources=sources,
            confidence=confidence,
            session_id=session_id,
        )
        self.add_message(message)

    # -------------------------
    # READ OPERATIONS
    # -------------------------

    def get_user_history(self, user_id: str, limit: int = 50) -> List[dict]:
        """
        Retrieve chat history for a given user.
        """
        results = self.collection.get(
            where={"user_id": user_id},
            limit=limit,
        )

        messages = []

        for doc, meta in zip(results["documents"], results["metadatas"]):
            messages.append(
                {
                    "content": doc,
                    "metadata": meta,
                }
            )

        return messages

    # -------------------------
    # DELETE OPERATIONS
    # -------------------------

    def clear_user_history(self, user_id: str):
        """
        Delete all chat messages for a given user.
        """
        self.collection.delete(where={"user_id": user_id})
        # Removed self.client.persist() here too
