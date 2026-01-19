# backend/rag/orchestrator.py

import logging
from collections import defaultdict
from pathlib import Path
from typing import Dict

from backend.rag.action_rbac import enforce_action_rbac
from backend.rag.retrieval import retrieve_authorized_chunks
from backend.rag.role_normaliser import normalize_role
from backend.rag.llm import summarize_chunk, generate_answer_from_summaries
from data.database.audit import log_action

# -------------------------------------------------
# LOGGER CONFIGURATION
# -------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# -------------------------------------------------
# FALLBACK ANSWERS (SINGLE SOURCE OF TRUTH)
# -------------------------------------------------
FALLBACK_ANSWERS = {
    "Information not available in authorized documents.",
    "Information not available at the moment.",
    "Unable to generate answer at this time."
}


# ============================================================
# Helper: resolve normalized file safely from filesystem
# ============================================================
def resolve_normalised_file(document_id: str, department: str) -> str | None:
    try:
        if not document_id or not department:
            return None

        project_root = Path(__file__).resolve().parents[2]
        department_folder = department.strip().lower()
        base_dir = project_root / "normalized_datasets" / department_folder

        if not base_dir.exists() or not base_dir.is_dir():
            return None

        expected_filename = f"{document_id}_cleaned.txt"
        file_path = base_dir / expected_filename

        if file_path.exists() and file_path.is_file():
            return expected_filename

        matches = [
            f.name
            for f in base_dir.iterdir()
            if f.is_file()
            and f.suffix == ".txt"
            and document_id.lower() in f.stem.lower()
        ]

        if len(matches) == 1:
            return matches[0]

    except Exception as e:
        logger.error(
            "Normalized file resolution failed | doc=%s | error=%s",
            document_id,
            str(e),
            exc_info=True
        )

    return None


# ============================================================
# Main RAG Orchestrator (CORRECTED & HARDENED)
# ============================================================
def run_rag_pipeline(user: Dict, query: str, top_k: int = 5) -> Dict:
    username = user.get("sub") or user.get("username") or "unknown"
    raw_role = user.get("role")
    user_id = user.get("user_id")

    logger.info(
        "RAG pipeline started | user=%s | role=%s | query='%s'",
        username,
        raw_role,
        query
    )

    # ----------------------------------------------------
    # 1️⃣ Normalize role & enforce ACTION-level RBAC
    # ----------------------------------------------------
    try:
        normalized_role = normalize_role(raw_role)
        enforce_action_rbac(user, action="RAG_QUERY")

    except Exception:
        logger.warning(
            "RAG RBAC denied | user=%s | role=%s",
            username,
            raw_role
        )

        log_action(
            username=username,
            role=raw_role,
            user_id=user_id,
            action="RAG_RBAC_DENIED",
            query=query,
            documents=[]
        )

        return {
            "user": username,
            "role": raw_role,
            "query": query,
            "answer": "You are not authorized to perform this action.",
            "citations": []
        }

    # --------------------------------------------------------
    # 2️⃣ Retrieval (RBAC-aware)
    # --------------------------------------------------------
    try:
        chunks = retrieve_authorized_chunks(
            query=query,
            role=normalized_role,
            username=username,
            user_id=user_id,
            top_k=top_k
        )

    except Exception as e:
        logger.error(
            "Retrieval layer crashed | error=%s",
            str(e),
            exc_info=True
        )

        log_action(
            username=username,
            role=raw_role,
            user_id=user_id,
            action="RAG_RETRIEVAL_CRASH",
            query=query,
            documents=[]
        )

        return {
            "user": username,
            "role": raw_role,
            "query": query,
            "answer": "Information not available at the moment.",
            "citations": []
        }

    if not chunks:
        return {
            "user": username,
            "role": raw_role,
            "query": query,
            "answer": "Information not available in authorized documents.",
            "citations": []
        }

    # --------------------------------------------------------
    # 3️⃣ Chunk summarization (NO AUTH DECISION HERE)
    # --------------------------------------------------------
    chunk_summaries = []
    grouped_sources = defaultdict(lambda: {
        "doc_name": None,
        "download_link": None,
        "chunks": []
    })

    for chunk in chunks:
        try:
            text = chunk.get("text", "").strip()
            if not text:
                continue

            summary = summarize_chunk(text, query)
            if not summary:
                continue

            chunk_summaries.append(summary)

            metadata = chunk.get("metadata", {})
            document_id = metadata.get("document_id", "unknown_document")
            department = metadata.get("department", "general")
            chunk_id = metadata.get("chunk_id", "unknown")

            doc_name = metadata.get("original_file") or document_id
            normalized_file = resolve_normalised_file(document_id, department)

            download_link = None
            if normalized_file:
                download_link = (
                    f"/downloads/normalized_datasets/"
                    f"{department.strip().lower()}/{normalized_file}"
                )

            grouped_sources[document_id]["doc_name"] = doc_name
            grouped_sources[document_id]["download_link"] = download_link
            grouped_sources[document_id]["chunks"].append({
                "chunk_id": chunk_id,
                "relevance_score": round(chunk.get("score", 0.0), 4)
            })

        except Exception as e:
            logger.warning(
                "Chunk processing failed | error=%s",
                str(e),
                exc_info=True
            )
            continue

    # --------------------------------------------------------
    # 4️⃣ Final LLM answer generation
    # --------------------------------------------------------
    try:
        answer_text = generate_answer_from_summaries(
            summaries=chunk_summaries,
            user_query=query
        )
    except Exception as e:
        logger.error(
            "LLM generation failed | error=%s",
            str(e),
            exc_info=True
        )
        answer_text = "Unable to generate answer at this time."

    # --------------------------------------------------------
    # 🔐 FINAL ENFORCEMENT (THE MISSING PIECE)
    # --------------------------------------------------------
    if not chunk_summaries or answer_text.strip() in FALLBACK_ANSWERS:
        log_action(
            username=username,
            role=raw_role,
            user_id=user_id,
            action="RAG_NO_AUTHORIZED_FINAL_CONTENT",
            query=query,
            documents=[]
        )

        return {
            "user": username,
            "role": raw_role,
            "query": query,
            "answer": "Information not available in authorized documents.",
            "citations": []   # 🚫 HARD BLOCK
        }

    # --------------------------------------------------------
    # 5️⃣ AUDIT SUCCESS
    # --------------------------------------------------------
    log_action(
        username=username,
        role=raw_role,
        user_id=user_id,
        action="RAG_QUERY_SUCCESS",
        query=query,
        documents=list(grouped_sources.keys())
    )

    logger.info(
        "RAG pipeline completed | user=%s | docs=%d",
        username,
        len(grouped_sources)
    )

    return {
        "user": username,
        "role": raw_role,
        "query": query,
        "answer": answer_text,
        "citations": list(grouped_sources.values())
    }
