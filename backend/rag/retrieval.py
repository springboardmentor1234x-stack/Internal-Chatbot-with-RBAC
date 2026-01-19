import logging
from typing import List

from backend.semantic_search.semantic_search import semantic_search
from data.database.audit import log_action

# -------------------------------------------------
# LOGGER CONFIGURATION (TECHNICAL LOGS)
# -------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def retrieve_authorized_chunks(
    query: str,
    role: str,
    username: str = "unknown",
    user_id: int = None,
    top_k: int = 5,
    debug: bool = False
) -> List[dict]:
    """
    Retrieval pipeline (RBAC-safe & audit-safe)

    Guarantees:
    - Never raises HTTPException
    - Never crashes
    - Never hallucinates (empty => [])
    - Always audit-logs access attempt
    """

    logger.info(
        "Retrieval started | user=%s | role=%s | query='%s'",
        username,
        role,
        query
    )

    try:
        # 1️⃣ Semantic search (RBAC-aware)
        output = semantic_search(
            query=query,
            user_role=role,
            final_k=top_k * 5
        )

    except Exception as e:
        logger.error(
            "Semantic search failure | role=%s | error=%s",
            role,
            str(e),
            exc_info=True
        )

        # ✅ AUDIT: retrieval attempted but failed
        log_action(
            username=username,
            role=role,
            user_id=user_id,
            action="RETRIEVAL_FAILED",
            query=query,
            documents=[]
        )

        return []

    # Defensive check
    if not isinstance(output, dict):
        logger.error(
            "Invalid semantic_search output | type=%s",
            type(output)
        )

        log_action(
            username=username,
            role=role,
            user_id=user_id,
            action="RETRIEVAL_INVALID_OUTPUT",
            query=query,
            documents=[]
        )

        return []

    results = output.get("results")
    if not results:
        logger.warning(
            "No authorized chunks | role=%s | query='%s'",
            role,
            query
        )

        # ✅ AUDIT: empty retrieval (important for hallucination prevention proof)
        log_action(
            username=username,
            role=role,
            user_id=user_id,
            action="RETRIEVAL_EMPTY",
            query=query,
            documents=[]
        )

        return []

    seen_chunk_ids = set()
    authorized_chunks = []

    try:
        # 2️⃣ Parse & deduplicate
        for score, res in results:
            chunk_id = (
                res.get("chunk_id")
                or f"chunk_{hash(res.get('document', '')) % 1_000_000}"
            )

            if chunk_id in seen_chunk_ids:
                continue

            seen_chunk_ids.add(chunk_id)

            authorized_chunks.append({
                "chunk_id": chunk_id,
                "text": res.get("document", ""),
                "score": score,
                "metadata": res.get("metadata", {})
            })

    except Exception as e:
        logger.error(
            "Retrieval parsing failed | role=%s | error=%s",
            role,
            str(e),
            exc_info=True
        )

        log_action(
            username=username,
            role=role,
            user_id=user_id,
            action="RETRIEVAL_PARSE_ERROR",
            query=query,
            documents=[]
        )

        return []

    # 3️⃣ Sort by relevance
    authorized_chunks.sort(key=lambda x: x["score"], reverse=True)

    # 4️⃣ Limit strictly
    authorized_chunks = authorized_chunks[:top_k]

    # 5️⃣ AUDIT: successful retrieval
    log_action(
        username=username,
        role=role,
        user_id=user_id,
        action="RETRIEVAL_SUCCESS",
        query=query,
        documents=[
            ch["chunk_id"] for ch in authorized_chunks
        ]
    )

    logger.info(
        "Retrieval successful | role=%s | chunks=%d",
        role,
        len(authorized_chunks)
    )

    # 6️⃣ Optional debug (developer-only)
    if debug:
        print("\nDEBUG: AUTHORIZED CHUNKS\n")
        for ch in authorized_chunks:
            print({
                "chunk_id": ch["chunk_id"],
                "score": round(ch["score"], 4),
                "preview": ch["text"][:120] + "...",
                "metadata": ch["metadata"]
            })

    return authorized_chunks

