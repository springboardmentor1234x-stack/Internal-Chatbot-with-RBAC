from typing import Dict


SYSTEM_INSTRUCTIONS = """You are an internal company assistant.
You must answer questions using ONLY the information provided in the context below.
Do NOT use prior knowledge.
If the answer cannot be found in the context, say:
"I do not have enough authorized information to answer this question."
"""


def build_prompt(formatted_context: str, user_query: str) -> str:
    prompt = f"""
{SYSTEM_INSTRUCTIONS}

====================
CONTEXT:
====================
{formatted_context}

====================
USER QUESTION:
====================
{user_query}

====================
ANSWER:
====================
"""
    return prompt.strip()
