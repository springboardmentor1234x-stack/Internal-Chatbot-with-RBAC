# #chatbot.py

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama
from backend.core.vectorstore import get_chroma_retriever


# ================= APPLICATION-LEVEL CACHE =================
# key   -> (role, query)
# value -> {"answer": str, "sources": dict}
QA_CACHE = {}


# ---------- PROMPT ----------
prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are FinBot, a professional internal company assistant.

STRICT RULES:
- Answer ONLY using the provided context.
- DO NOT return JSON, lists, bullet points, or key-value pairs.
- DO NOT expose raw database fields or objects.
- Always respond in clear, natural English sentences.
- If information is not found, say exactly:
  "Sorry, information not available."
- If the user's role does not have access, say exactly:
  "Access denied for your role."

Context:
{context}

Question:
{question}

Answer (plain text only):
"""
)

# ---------- LLM ----------
llm = Ollama(
    model="phi3",
    temperature=0
)


def get_answer(query: str, role: str):
    """
    Returns chatbot answer using application-level cache
    """

    # ---------- CACHE KEY ----------
    cache_key = (role.lower().strip(), query.strip().lower())

    # ---------- CACHE HIT ----------
    if cache_key in QA_CACHE:
        return QA_CACHE[cache_key]

    # ---------- CACHE MISS ----------
    retriever = get_chroma_retriever(role)

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True
    )

    result = qa.invoke({"query": query})

    # ---------- FORMAT SOURCES ----------
    sources = {}

    for doc in result.get("source_documents", []):
        doc_name = doc.metadata.get("source", "Unknown document")

        if doc_name not in sources:
            sources[doc_name] = []

        clean_text = doc.page_content.replace("\n", " ").strip()
        sources[doc_name].append(clean_text[:250] + "...")

    # ---------- FINAL ANSWER ----------
    answer = result.get("result", "").strip()

    if not answer:
        answer = "Sorry, information not available."

    response = {
        "answer": answer,
        "sources": sources
    }

    # ---------- STORE IN CACHE ----------
    QA_CACHE[cache_key] = response

    return response
