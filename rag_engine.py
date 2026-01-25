# rag_engine.py

import os
from typing import List, Tuple

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain_core.documents import Document
from functools import lru_cache

# ----------------------------
# CONFIG
# ----------------------------

FAISS_INDEX_PATH = "faiss_index"

ROLE_ACCESS = {
    "Employee": ["employee_handbook"],
    "HR": ["hr_data"],
    "Engineering": ["engineering_docs"],
    "Finance": ["quarterly_financial_report"],
    "Marketing": ["marketing_report"],
    "Admin": ["employee_handbook", "hr_data", "engineering_docs",
              "quarterly_financial_report", "marketing_report"],
}

# ----------------------------
# EMBEDDINGS
# ----------------------------
from langchain_huggingface import HuggingFaceEmbeddings

@lru_cache(maxsize=1)
def load_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": False}
    )



# ----------------------------
# LLM
# ----------------------------

@lru_cache(maxsize=1)
def load_llm():
    return Ollama(
        model="mistral",
        temperature=0.0
    )


# ----------------------------
# VECTOR STORE
# ----------------------------

@lru_cache(maxsize=1)
def load_vectorstore():
    if not os.path.exists(FAISS_INDEX_PATH):
        raise RuntimeError("FAISS index not found. Run data_ingest.py first.")

    embeddings = load_embeddings()
    return FAISS.load_local(
        FAISS_INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )


# ----------------------------
# RBAC
# ----------------------------

def is_authorized(role: str, docs: List[Document]) -> bool:
    # Full access roles
    if role == "C-Level":
        return True

    allowed_sources = ROLE_ACCESS.get(role, [])
    if not allowed_sources:
        return False

    for doc in docs:
        source = str(doc.metadata.get("source", "")).lower()
        if not any(allowed in source for allowed in allowed_sources):
            return False  # even ONE violation blocks access

    return True

# ----------------------------
# QUERY SUGGESTIONS
# ----------------------------

ROLE_SUGGESTIONS = {
    "HR": [
        "What is the leave policy?",
        "Explain the hiring process",
        "What benefits are provided to employees?",
        "HR rules and guidelines"
    ],
    "Finance": [
        "Summarize the quarterly financial report",
        "What is the revenue growth?",
        "Explain financial performance"
    ],
    "Engineering": [
        "Explain engineering guidelines",
        "What are the development standards?",
        "Describe system architecture"
    ],
    "Employee": [
        "What is the employee handbook?",
        "Explain company policies",
        "Leave and attendance rules"
    ],
    "C-Level": [
        "Give an overview of financial performance",
        "Summarize HR and employee status",
        "Overall company performance"
    ]
}

def get_query_suggestions(role: str) -> List[str]:
    return ROLE_SUGGESTIONS.get(role, [])


# ----------------------------
# PROMPT
# ----------------------------

def build_prompt(context: str, question: str) -> str:
    return f"""
You are a secure internal enterprise assistant.

RULES:
- Answer ONLY from the context.
- Do NOT guess or calculate.
- If information is missing, say:
  "Information not found in the authorized documents."

Context:
{context}

Question:
{question}

Answer:
""".strip()

# ----------------------------
# MAIN SEARCH FUNCTION
# ----------------------------

def search(question: str, role: str, messages: list, k: int = 2) -> Tuple[str, List[Document]]:
    """
    Secure RAG search with RBAC.
    Returns (answer, documents)
    """

    vectorstore = load_vectorstore()
    llm = load_llm()

    docs = vectorstore.similarity_search(question, k=k)

    if not docs:
        return "Information not found in the authorized documents.", []

    # ---- ROLE-AWARE FILTERING ----
    if role != "C-Level":
        allowed_sources = ROLE_ACCESS.get(role, [])
        docs = [
            d for d in docs
            if any(a in str(d.metadata.get("source", "")).lower()
                for a in allowed_sources)
    ]
    if not docs:
        return "Information not found in the authorized documents.", []
    context = "\n\n".join(
    f"[Source: {doc.metadata.get('source')}]\n{doc.page_content[:800]}"
    for doc in docs
)



    prompt = build_prompt(context, question)

    response = llm.invoke(prompt)

    return response.strip(), docs
