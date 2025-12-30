import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

app = FastAPI()

llm = ChatGroq(
    model_name="llama-3.3-70b-versatile", 
    temperature=0,
    groq_api_key=api_key  
)

PERMISSION_MAP = {
    "admin": ["hr_data", "marketing_data", "general_data"],
    "hr_manager": ["hr_data", "general_data"],
    "marketing_manager": ["marketing_data", "general_data"],
    "intern": ["marketing_data", "general_data"]
}

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

RAG_PROMPT = ChatPromptTemplate.from_template("""
You are an expert Fintech Analyst. Use the provided context to answer the user's question accurately.

Context:
{context}

Question: {question}

Instructions:
1. If the answer is in the context, provide a detailed response.
2. If the context is related but doesn't have the specific answer, summarize what is available.
3. Only if the context is completely irrelevant, say "I don't have enough information for your role."

Answer:""")

@app.get("/ask")
async def ask_bot(role: str, question: str):
    try:
        role = role.lower()
        if role not in PERMISSION_MAP:
            raise HTTPException(status_code=403, detail="Invalid role")

        allowed_collections = PERMISSION_MAP[role]
        context_docs = []
        
        for collection in allowed_collections:
            try:
                vector_db = Chroma(
                    persist_directory="vector_db/", 
                    embedding_function=embeddings, 
                    collection_name=collection
                )
                docs = vector_db.similarity_search(question, k=2)
                context_docs.extend(docs)
            except Exception:
                continue

        if not context_docs:
            return {"answer": "I don't have enough information for your role.", "sources": []}

        combined_context = "\n".join([doc.page_content for doc in context_docs])
        sources = list(set([doc.metadata.get("source", "Unknown") for doc in context_docs]))

        formatted_prompt = RAG_PROMPT.format(context=combined_context, question=question)
        response = llm.invoke(formatted_prompt)

        return {
            "question": question, 
            "role": role, 
            "answer": response.content,
            "sources": sources
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)