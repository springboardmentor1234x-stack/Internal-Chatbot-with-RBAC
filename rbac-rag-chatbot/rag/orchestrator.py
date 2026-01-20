# rag/orchestrator.py
from rbac.action_rbac import is_action_allowed
from rag.report_builder import build_final_report
from api.hf_client import call_hf_model

def run_rag(
    user_context,
    action,
    user_query,
    embedder,
    vector_store,
    llm_client
):
    # 1️⃣ RBAC CHECK
    if not is_action_allowed(user_context, action):
        return {
            "answer": "You are not authorized to perform this action.",
            "sources": [],
            "confidence": "low"
        }

    # 2️⃣ Embed query
    query_vector = embedder.embed([user_query])[0]

    # 3️⃣ Retrieve chunks
    retrieved_chunks = vector_store.search(
        query_vector=query_vector,
        user_context=user_context,
        top_k=5,
        threshold=0.3
    )

    # 4️⃣ If nothing retrieved
    if not retrieved_chunks:
        return {
            "answer": "No relevant documents found to answer this question.",
            "sources": [],
            "confidence": "low"
        }

    # ================================
    # ✅ SAFE TEXT EXTRACTION
    # ================================
    texts = []

    for chunk in retrieved_chunks:
        if isinstance(chunk, dict):
            if "content" in chunk:
                texts.append(chunk["content"])
            elif "text" in chunk:
                texts.append(chunk["text"])
            elif "page_content" in chunk:
                texts.append(chunk["page_content"])
            else:
                texts.append(str(chunk))
        else:
            texts.append(str(chunk))

    context = "\n\n".join(texts)

    # ================================
    # ✅ PROPER RAG PROMPT
    # ================================
    prompt = f"""
You are a helpful RAG assistant.
Answer ONLY based on the provided context.
Be clear, structured, and human-readable.

-----------------
CONTEXT:
{context}
-----------------

QUESTION:
{user_query}

ANSWER:
"""

    # ================================
    # 7️⃣ CALL HUGGING FACE
    # ================================
    try:
        answer = call_hf_model(prompt)
    except Exception as e:
        answer = f"I encountered an LLM error: {str(e)}"

    # ================================
    # 8️⃣ CONFIDENCE HEURISTIC
    # ================================
    confidence = "high" if len(retrieved_chunks) >= 3 else "medium"

    # ================================
    # 9️⃣ FINAL REPORT
    # ================================
    return build_final_report(
        answer=answer,
        retrieved_chunks=retrieved_chunks,
        confidence=confidence
    )
