"""
rag/report_builder.py

Responsible for assembling the FINAL RAG response.
This is the ONLY place where:
- Sources are constructed
- Evidence is deduplicated
- Audit-ready output is created

UI MUST NOT modify this output.
"""

from typing import List, Dict


# -----------------------------
# SOURCE BUILDER
# -----------------------------

DOCUMENT_REGISTRY = {
    "engineering_engineering_master_doc_md": "engineering_master_doc.pdf",
    "general_employee_handbook_md": "employee_handbook.pdf",
    "finance_financial_summary_md": "financial_summary.pdf",
    "finance_quarterly_financial_report_md": "quarterly_financial_report.pdf",
    "marketing_market_report_q1_2024_md": "marketing_report_q1_2024.pdf",
    "marketing_market_report_q2_2024_md": "marketing_report_q2_2024.pdf",
    "marketing_market_report_q3_2024_md": "marketing_report_q3_2024.pdf",
    "marketing_market_report_q4_2024_md": "market_report_q4_2024.pdf",
}


def build_sources(retrieved_chunks: List[Dict]) -> List[Dict]:
    """
    Build structured, auditable sources from retrieved chunks.

    Each source corresponds to ONE chunk.
    Deduplication happens at (doc_id, chunk_id) level.
    """

    sources = []
    seen = set()

    for chunk in retrieved_chunks:
        metadata = chunk.get("metadata", {})
        score = chunk.get("score")

        doc_id = metadata.get("doc_id")
        chunk_index = metadata.get("chunk_index")

        # Safety guard — do not invent sources
        if not doc_id:
            continue

        dedup_key = (doc_id, chunk_index)
        if dedup_key in seen:
            continue
        seen.add(dedup_key)

        sources.append({
            "document_id": doc_id,
            "document_title": humanize_doc_title(doc_id),
            "chunk_id": f"chunk_{chunk_index}" if chunk_index is not None else None,
            "score": score,   # similarity score from retriever
            "url": build_document_url(doc_id)
        })

    return sources


# -----------------------------
# REPORT ASSEMBLER
# -----------------------------

def build_final_report(
    answer: str,
    retrieved_chunks: List[Dict],
    confidence: str
) -> Dict:
    """
    Assemble the final response returned to the API layer.
    """

    sources = build_sources(retrieved_chunks)

    return {
        "answer": answer,
        "sources": sources,
        "confidence": confidence
    }


# -----------------------------
# HELPERS
# -----------------------------

def humanize_doc_title(doc_id: str) -> str:
    """
    Convert internal doc_id to readable title.
    Example:
        engineering_engineering_master_doc_md
        → Engineering Engineering Master Doc
    """
    return doc_id.replace("_", " ").replace(" md", "").title()


def build_document_url(doc_id: str) -> str | None:
    """
    Map internal doc_id to a real PDF file served by FastAPI.
    """
    filename = DOCUMENT_REGISTRY.get(doc_id)

    if not filename:
        return None  # UI will handle gracefully

    return f"http://127.0.0.1:8000/docs/{filename}"


