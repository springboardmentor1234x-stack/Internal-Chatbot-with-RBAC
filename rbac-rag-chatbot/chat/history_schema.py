from datetime import datetime
from typing import Dict, List, Optional


def current_timestamp() -> str:
    """
    Returns UTC timestamp in ISO format.
    Example: 2026-01-09T16:45:12Z
    """
    return datetime.utcnow().isoformat() + "Z"


def build_user_message(
    user_id: str,
    content: str,
    session_id: Optional[str] = None,
) -> Dict:
    """
    Build a user chat message payload.
    """
    return {
        "content": content,
        "metadata": {
            "user_id": user_id,
            "role": "USER",
            "timestamp": current_timestamp(),
            "session_id": session_id,
        },
    }


def build_assistant_message(
    user_id: str,
    content: str,
    sources: List[Dict],
    confidence: Optional[str] = None,
    session_id: Optional[str] = None,
) -> Dict:
    """
    Build an assistant chat message payload.
    """
    return {
        "content": content,
        "metadata": {
            "user_id": user_id,
            "role": "ASSISTANT",
            "timestamp": current_timestamp(),
            "session_id": session_id,
            "confidence": confidence,
        },
        "sources": sources,
    }
