def build_prompt(context_chunks, question, role):
    """
    Builds a secure, role-aware prompt for RAG.
    """

    return f"""
You are an internal company AI assistant.

User Role: {role}

Instructions:
- Answer strictly based on the provided context.
- Do NOT hallucinate or add external information.
- If information is not present, say "Information not available."

Context:
{context_chunks}

User Question:
{question}

Answer:
"""

