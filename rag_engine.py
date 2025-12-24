import os
from groq import Groq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Initialize Embeddings
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# --- SECURE CONFIGURATION ---
MY_GROQ_KEY = "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"
MODEL_NAME = "llama-3.1-8b-instant"
client = Groq(api_key=MY_GROQ_KEY)

def search(query, user_role, chat_history):
    if not os.path.exists("faiss_index"):
        return "System Error: Vector database not found. Please run ingest first.", []

    # 1. PRE-CHECK: Targeted Departmental Keyword Blocking
    # Including 'General' in the logic to ensure we handle it as a public domain
    all_depts = {"Finance", "Marketing", "HR", "Engineering", "General"}
    
    # If the user is NOT C-Level, check if they are asking for a specific other department
    if user_role != "C-Level":
        query_lower = query.lower()
        # Find if any restricted department name is mentioned in the query
        # We exclude the user's own role and 'General' from the forbidden list
        forbidden_depts = all_depts - {user_role, "General", "Employee"}
        
        if any(dept.lower() in query_lower for dept in forbidden_depts):
            return "Permission is restricted for this data. You are strictly prohibited from accessing data outside your department.", []

    # 2. LOAD DB
    db = FAISS.load_local("faiss_index", embedding, allow_dangerous_deserialization=True)
    
    # 3. RETRIEVE: Get top matches
    results = db.similarity_search(query, k=10)
    
    # 4. HARD FILTER: Programmatic Security Gate
    # Documents are allowed if their metadata 'role' matches the user, General, or Employee
    allowed_roles = {"Employee", "General", user_role}
    
    context_docs = []
    if user_role == "C-Level":
        context_docs = results
    else:
        # Programmatically remove any doc that is not authorized
        context_docs = [d for d in results if d.metadata.get("role") in allowed_roles]

    # 5. SECURITY GATE: Block if no authorized records are found
    if not context_docs:
        return f"Permission is restricted for this data. No authorized records were found for role: {user_role}.", []

    # 6. CONSTRUCT CONTEXT
    context_text = "\n\n".join([f"Source: {d.metadata['source']}\n{d.page_content}" for d in context_docs])
    
    # 7. GENERATE: Strict System Instructions for LLM
    messages = [
        {
            "role": "system", 
            "content": (
                f"STRICT SECURITY PROTOCOL: You are the {user_role} Department Assistant. "
                f"1. You can ONLY discuss {user_role}, General, or Employee data. "
                "2. If the user asks for info not in context, or from another department, "
                "reply exactly: 'Permission is restricted for this data.' "
                "3. No explanations or apologies. Cite filenames for every answer."
            )
        }
    ]
    
    for msg in chat_history[-5:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    
    messages.append({
        "role": "user", 
        "content": f"### AUTHORIZED CONTEXT\n{context_text}\n\n### USER QUESTION\n{query}"
    })

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.0  # Maximum strictness
        )
        return completion.choices[0].message.content, context_docs
    except Exception as e:
        return f"System Connection Error: {str(e)}", context_docs