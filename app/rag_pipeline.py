import os
from typing import List
from operator import itemgetter
from dotenv import load_dotenv

# LangChain Imports
from langchain_community.document_loaders import UnstructuredMarkdownLoader, CSVLoader 
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# --- NEW CONFIGURATION (Matching your new folders) ---
# We point to the specific subfolders created in the previous steps
RAW_DATA_PATH = "./data/raw"
PROCESSED_DATA_PATH = "./data/processed"
CHROMA_PATH = "./data/chroma" 

EMBEDDING_MODEL = "text-embedding-ada-002"
LLM_MODEL = "gpt-3.5-turbo"
LLM_TEMPERATURE = 0.1

DOCUMENT_MAP = {
    "quarterly_financial_report.md": ["Finance", "C-Level"],
    "marketing_report_2024.md": ["Marketing", "C-Level"],
    "marketing_report_q1_2024.md": ["Marketing", "C-Level"],
    "marketing_report_q2_2024.md": ["Marketing", "C-Level"],
    "marketing_report_q3_2024.md": ["Marketing", "C-Level"],
    "market_report_q4_2024.md": ["Marketing", "C-Level"],
    "hr_data.csv": ["HR", "C-Level"],
    "employee_handbook.md": ["HR", "Employee", "C-Level", "Finance", "Marketing", "Engineering"], 
    "engineering_master_doc.md": ["Engineering", "C-Level"],
}

class FinSolveRAGPipeline:
    def __init__(self, user_role: str):
        self.user_role = user_role
        self.embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    def load_documents(self) -> List:
        all_documents = []
        for filename, roles in DOCUMENT_MAP.items():
            # Determine if it's in raw (csv) or processed (md)
            folder = RAW_DATA_PATH if filename.endswith(".csv") else PROCESSED_DATA_PATH
            file_path = os.path.join(folder, filename)
            
            if not os.path.exists(file_path):
                print(f"Warning: {filename} not found in {folder}")
                continue

            loader = CSVLoader(file_path, encoding="utf-8") if filename.endswith(".csv") else UnstructuredMarkdownLoader(file_path)
            docs = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = text_splitter.split_documents(docs)

            for chunk in chunks:
                chunk.metadata["allowed_roles"] = roles
                chunk.metadata["source"] = filename
                all_documents.append(chunk)
                
        return all_documents

    def create_vector_store(self):
        documents = self.load_documents()
        if not documents:
            print("No documents found to index.")
            return
        
        if os.path.exists(CHROMA_PATH):
            import shutil
            shutil.rmtree(CHROMA_PATH)

        db = Chroma.from_documents(documents, self.embeddings, persist_directory=CHROMA_PATH)
        print(f"Vector store created at {CHROMA_PATH}")

    def run_pipeline(self, question: str):
        """The main entry point used by routes.py"""
        if not os.path.exists(CHROMA_PATH):
            return [{"doc_id": "Error", "content": "Vector database not found."}]
        
        db = Chroma(persist_directory=CHROMA_PATH, embedding_function=self.embeddings)
        
        # RBAC Filter
        chroma_filter = {"allowed_roles": {"$in": [self.user_role]}}
        retriever = db.as_retriever(search_kwargs={"k": 5, "filter": chroma_filter})
        
        # Get relevant docs
        docs = retriever.invoke(question)
        
        # Format for routes.py (returning a list of dicts as your route expects)
        return [{"doc_id": d.metadata.get("source"), "content": d.page_content} for d in docs]

# For manual setup
if __name__ == "__main__":
    pipeline = FinSolveRAGPipeline(user_role="C-Level")
    pipeline.create_vector_store()