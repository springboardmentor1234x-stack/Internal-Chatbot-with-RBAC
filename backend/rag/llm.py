# backend/rag/llm.py

import os
import logging
from typing import List, Tuple
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from data.database.audit import log_action

# --------------------------------------------------
# LOGGER CONFIGURATION
# --------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# --------------------------------------------------
# Environment (SAFE LOAD)
# --------------------------------------------------
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    logger.critical("GROQ_API_KEY is missing")
    raise RuntimeError("LLM configuration error")

# --------------------------------------------------
# LLM Configuration
# --------------------------------------------------
llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0,
    groq_api_key=groq_api_key,
    timeout=15  # ✅ HARD TIMEOUT
)

output_parser = StrOutputParser()

# --------------------------------------------------
# Prompts (ANTI-HALLUCINATION)
# --------------------------------------------------
SUMMARY_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You summarize internal company documents. "
        "STRICTLY use ONLY the provided text. "
        "Do NOT add or infer any information."
    ),
    (
        "human",
        "Query: {query}\n\nText:\n{chunk}\n\n"
        "Summarize ONLY facts present in the text."
    )
])

ANSWER_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "Answer STRICTLY using ONLY the provided summaries. "
        "If the answer is missing, respond exactly:\n"
        "'Information not available in authorized documents.'"
    ),
    (
        "human",
        "User question: {question}\n\nSummaries:\n{summaries}"
    )
])

# --------------------------------------------------
# Chains
# --------------------------------------------------
summary_chain = SUMMARY_PROMPT | llm | output_parser
answer_chain = ANSWER_PROMPT | llm | output_parser

# --------------------------------------------------
# Public API
# --------------------------------------------------
def summarize_chunk(chunk_text: str, query: str) -> str:
    """
    Safely summarize a retrieved chunk.
    NEVER raises.
    """
    try:
        summary = summary_chain.invoke({
            "chunk": chunk_text,
            "query": query
        })

        if not summary or not summary.strip():
            return chunk_text[:300] + "..."

        return summary.strip()

    except Exception as e:
        logger.warning(
            "LLM summarize_chunk failed | error=%s",
            str(e),
            exc_info=True
        )

        log_action(
            username="system",
            action="LLM_SUMMARY_FAILURE",
            query=query,
            documents=[]
        )

        return chunk_text[:300] + "..."


def generate_answer_from_summaries(
    summaries: List[str],
    user_query: str
) -> str:
    """
    Generate final answer strictly from summaries.
    NEVER raises.
    """

    if not summaries:
        return "Information not available in authorized documents."

    # Limit prompt size defensively
    summaries = summaries[:10]

    joined_summaries = "\n".join(f"- {s}" for s in summaries)

    try:
        answer = answer_chain.invoke({
            "question": user_query,
            "summaries": joined_summaries
        })

        if not answer or not answer.strip():
            return "Information not available in authorized documents."

        return answer.strip()

    except Exception as e:
        logger.error(
            "LLM answer generation failed | error=%s",
            str(e),
            exc_info=True
        )

        log_action(
            username="system",
            action="LLM_ANSWER_FAILURE",
            query=user_query,
            documents=[]
        )

        return "Information not available in authorized documents."


def summarize_large_text(
    text: str,
    query: str,
    chunk_size: int = 2000,
    hierarchical: bool = True
) -> Tuple[List[str], str]:
    """
    Large document summarization with failure isolation.
    """
    try:
        chunks = [
            text[i:i + chunk_size]
            for i in range(0, len(text), chunk_size)
        ]

        chunk_summaries = [
            summarize_chunk(c, query)
            for c in chunks
        ]

        if hierarchical and len(chunk_summaries) > 1:
            combined = "\n".join(chunk_summaries)
            final_summary = summarize_chunk(combined, query)
        else:
            final_summary = "\n".join(chunk_summaries)

        return chunk_summaries, final_summary

    except Exception as e:
        logger.error(
            "Hierarchical summarization failed | error=%s",
            str(e),
            exc_info=True
        )

        return [], "Information not available in authorized documents."
