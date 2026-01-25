import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag_engine import load_embeddings
embedding = load_embeddings()


FILE_ROLE_MAP = {
    "data/employee_handbook.md": "Employee",
    "data/hr_data.csv": "HR",
    "data/engineering_master_doc.md": "Engineering",
    "data/quarterly_financial_report.md": "Finance",
    "data/marketing_report_2024.md": "Marketing"
}

docs = []

for file, role in FILE_ROLE_MAP.items():
    if os.path.exists(file):
        with open(file, encoding="utf-8") as f:
            docs.append(Document(
                page_content=f.read(),
                metadata={"source": file, "role": role}
            ))

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)

db = FAISS.from_documents(chunks, embedding)
db.save_local("faiss_index")
print("✅ FAISS index created")
