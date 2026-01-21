import os
import requests


OLLAMA_API = "http://localhost:11434/api/generate"
MODEL = "tinyllama"

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "raw_docs"
)

ROLE_FOLDERS = {
    "finance": ["Finance"],
    "hr": ["HR"],
    "marketing": ["marketing"],
    "engineering": ["engineering"],
    "intern": ["general"],
    "admin": ["Finance", "HR", "marketing", "engineering", "general"]
}
FORBIDDEN_KEYWORDS = {
    "intern": ["finance", "salary", "revenue", "marketing", "engineering", "hr"],
    "hr": ["finance", "revenue", "profit", "quarterly", "financial"],
    "finance": ["hr", "employee", "leave", "salary", "attendance"],
    "marketing": ["finance", "salary", "hr", "engineering"],
    "engineering": ["finance", "salary", "hr", "marketing"]
}

MAX_CHARS = 1500
def get_authorized_files(role):
    allowed = ROLE_FOLDERS.get(role, [])
    files = []

    for folder in allowed:
        folder_path = os.path.join(DATA_DIR, folder)

        if not os.path.exists(folder_path):
            continue

        for root, dirs, filenames in os.walk(folder_path):
            for f in filenames:
                if f.lower().endswith((".md", ".csv", ".txt")):
                    files.append(os.path.join(root, f))

    return files



def read_file(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except:
        return ""

def simple_search(query, texts):
    # Very simple keyword scoring
    scores = []
    for path, text in texts:
        score = sum(1 for word in query.lower().split() if word in text.lower())
        scores.append((score, path, text))

    scores.sort(reverse=True, key=lambda x: x[0])
    return scores[:1]  # return best match


def generate_answer(query, role):
    query_lower = query.lower()

    # Block forbidden queries by role
    blocked = FORBIDDEN_KEYWORDS.get(role, [])
    for word in blocked:
        if word in query_lower:
            return "You are not authorized to access this type of information.", []

    # Get authorized files for this role
    files = get_authorized_files(role)

    if not files:
        return "No authorized documents found for your role.", []

    texts = [(f, read_file(f)) for f in files]
    best = simple_search(query, texts)

    if not best or best[0][0] == 0:
        return "No relevant documents found for your role.", []

    _, path, content = best[0]
    context = content[:MAX_CHARS]

    prompt = f"""
You are a company internal assistant.
Summarize clearly using ONLY this document.

Document:
{context}

Question: {query}
Answer:
"""

    try:
        res = requests.post(
            OLLAMA_API,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        data = res.json()
        return data.get("response", "Summary unavailable."), [
            {"source": os.path.relpath(path, DATA_DIR)}
        ]

    except Exception:
        return context[:500] + "...", [
            {"source": os.path.relpath(path, DATA_DIR)}
        ]
