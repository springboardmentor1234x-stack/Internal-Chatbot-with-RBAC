import os
from groq import Groq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Initialize Embeddings
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

MY_GROQ_KEY = os.getenv("GROQ_API_KEY") 
MODEL_NAME = "llama-3.1-8b-instant"

if not MY_GROQ_KEY:
    # This helps you debug if the secret isn't set correctly
    raise ValueError("System Error: GROQ_API_KEY secret not found in Hugging Face Settings.")

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
    results_with_scores = db.similarity_search_with_score(query, k=10)
    
   # --- 4. FILTER & RANKING LOG ---
    allowed_roles = {"Employee", "General", user_role}
    context_docs = []
    ranking_log = []

    for doc, score in results_with_scores:
        # SECURITY CHECK: Only allow C-Level or matching departmental roles
        if user_role == "C-Level" or doc.metadata.get("role") in allowed_roles:
            context_docs.append(doc)
            
            match_pct = round(max(0, 100 - (score * 100)), 2)
            
            # If the score is still very low but relevant, we ensure it shows as at least 0.01
            if match_pct == 0 and score < 2.0:
                 match_pct = round(max(0, 100 - (score * 10)), 2)

            ranking_log.append(f"{doc.metadata.get('source')} ({match_pct}%)")

    print(f"--- LIVE RANKING SCORES: {ranking_log} ---")

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
        
        for i in range(len(context_docs)):
            if i < len(ranking_log):
                context_docs[i].metadata['source'] = ranking_log[i]

        return completion.choices[0].message.content, context_docs
    except Exception as e:
        return f"System Connection Error: {str(e)}", context_docs
