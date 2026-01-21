# File: backend/core/vectorstore.py
# backend/core/vectorstore.py
# from langchain_community.vectorstores import Chroma
# from langchain_core.retrievers import BaseRetriever
# from backend.core.config import CHROMA_DIR, embedding_model


# def get_chroma_retriever(role: str) -> BaseRetriever:
#     """
#     Returns a role-filtered retriever from Chroma DB
#     """

#     vectordb = Chroma(
#         persist_directory=str(CHROMA_DIR),   # ✅ ensure string
#         embedding_function=embedding_model   # ✅ CRITICAL FIX
#     )

#     retriever = vectordb.as_retriever(
#         search_kwargs={
#             "k": 4,
#             "filter": {"role": role.lower()}
#         }
#     )

#     return retriever
from langchain_community.vectorstores import Chroma
from langchain_core.retrievers import BaseRetriever

# ✅ FIXED IMPORT (MOST IMPORTANT)
from backend.core.config import CHROMA_DIR, embedding_model


def get_chroma_retriever(role: str) -> BaseRetriever:
    """
    Returns a role-filtered retriever from Chroma DB
    """

    vectordb = Chroma(
        persist_directory=str(CHROMA_DIR),   # ✅ must be string
        embedding_function=embedding_model   # ✅ correct embeddings
    )

    retriever = vectordb.as_retriever(
        search_kwargs={
            "k": 4,
            "filter": {"role": role.lower()}
        }
    )

    return retriever

