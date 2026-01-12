import os
from fastapi import FastAPI, HTTPException
from langchain_groq import ChatGroq # Swapped from OpenAI
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_classic.chains import RetrievalQA

# 1. SET YOUR FREE GROQ KEY HERE
os.environ["GROQ_API_KEY"] = "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"

app = FastAPI(title="FinSolve Free Secure Backend")

# 2. RBAC ACCESS MATRIX
ACCESS_MATRIX = {
    "C-Level": ["engineering", "finance", "hr", "marketing", "general"],
    "Finance_Manager": ["finance", "general"],
    "HR_Manager": ["hr", "general"],
    "Engineering_Lead": ["engineering", "general"],
    "Marketing_Manager": ["marketing", "general"],
    "Intern": ["general"] 
}

# 3. INITIALIZE VECTOR DB
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "chroma_db")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

@app.get("/ask")
async def secure_query(role: str, query: str):
    if role not in ACCESS_MATRIX:
        raise HTTPException(status_code=403, detail="Unauthorized: Role not recognized.")

    # Negative Test: Interns are restricted from sensitive keywords
    sensitive_keywords = ["salary", "revenue", "architecture", "profit", "payroll"]
    if role == "Intern" and any(word in query.lower() for word in sensitive_keywords):
        raise HTTPException(
            status_code=403, 
            detail="Forbidden: Interns do not have permission to access restricted data."
        )

    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=500, detail="Database not found. Run ingest.py first.")

    try:
        vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
        
        # Apply Metadata Filter
        allowed_depts = ACCESS_MATRIX[role]
        search_filter = {"dept": {"$in": allowed_depts}}
        
        retriever = vector_db.as_retriever(
            search_kwargs={"filter": search_filter, "k": 3}
        )
        
        # 4. INITIALIZE GROQ MODEL (FREE)
        # We use Llama-3 for high-speed, grounded performance
        llm = ChatGroq(
            temperature=0, 
            model_name="llama3-8b-8192"
        )
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True
        )
        
        result = qa_chain.invoke({"query": query})
        
        if not result['source_documents']:
            return {
                "answer": "I am sorry, the expected information is not available in your authorized documents.",
                "sources": []
            }

        sources = list(set([os.path.basename(d.metadata.get('source', 'Unknown')) for d in result['source_documents']]))
        
        return {"answer": result['result'], "sources": sources}
        
    except Exception as e:
        print(f"!!! BACKEND ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)