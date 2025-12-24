import os
import pandas as pd
from langchain_text_splitters import RecursiveCharacterTextSplitter # Updated
from langchain_community.vectorstores import FAISS               # Updated
from langchain_core.documents import Document                   # Updated
from langchain_huggingface import HuggingFaceEmbeddings


# Initialize Embeddings
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Mapping must match roles used in streamlit_app.py
FILE_ROLE_MAP = {
    "employee_handbook.md": "Employee",      # General access
    "hr_data.csv": "HR",
    "engineering_master_doc.md": "Engineering",
    "financial_summary.md": "Finance",
    "quarterly_financial_report.md": "Finance",
    "market_report_q4_2024.md": "Marketing",
    "marketing_report_2024.md": "Marketing",
}

def load_docs():
    docs = []
    for filename, access in FILE_ROLE_MAP.items():
        if not os.path.exists(filename):
            print(f"⚠️ Missing file: {filename}")
            continue
        
        text = ""
        if filename.endswith(".md"):
            with open(filename, encoding="utf-8") as f:
                text = f.read()
        elif filename.endswith(".csv"):
            df = pd.read_csv(filename)
            text = df.to_string(index=False)
        
        if text:
            docs.append(
                Document(
                    page_content=text,
                    metadata={"source": filename, "role": access}
                )
            )
    return docs

def ingest():
    docs = load_docs()
    if not docs:
        print("❌ No documents found to index!")
        return

    print(f"Loaded {len(docs)} documents")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    print(f"Split into {len(chunks)} chunks")

    # Create FAISS vector store and save to folder
    vectorstore = FAISS.from_documents(chunks, embedding)
    vectorstore.save_local("faiss_index")
    print("✅ Indexed into FAISS successfully and saved to 'faiss_index' folder")

if __name__ == "__main__":
    ingest()