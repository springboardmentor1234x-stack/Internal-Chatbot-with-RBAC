import os
import tiktoken
from typing import List
from dotenv import load_dotenv

# LangChain Imports
from langchain_community.document_loaders import UnstructuredMarkdownLoader, CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

# --- CONFIGURATION ---
RAW_DATA_PATH = "./data/raw"
PROCESSED_DATA_PATH = "./data/processed"
CHROMA_PATH = "./data/chroma"

EMBEDDING_MODEL = "text-embedding-ada-002"

DOCUMENT_MAP = {
    "quarterly_financial_report.md": ["Finance", "C-Level"],
    "marketing_report_2024.md": ["Marketing", "C-Level"],
    "marketing_report_q1_2024.md": ["Marketing", "C-Level"],
    "marketing_report_q2_2024.md": ["Marketing", "C-Level"],
    "marketing_report_q3_2024.md": ["Marketing", "C-Level"],
    "market_report_q4_2024.md": ["Marketing", "C-Level"],
    "hr_data.csv": ["HR", "C-Level"],
    "employee_handbook.md": [
        "HR",
        "Employee",
        "C-Level",
        "Finance",
        "Marketing",
        "Engineering",
    ],
    "engineering_master_doc.md": ["Engineering", "C-Level"],
}


class FinSolveRAGPipeline:
    def __init__(self, role: str):  # Renamed to 'role' to match your routes.py call
        self.user_role = role
        self.embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    def load_documents(self) -> List:
        all_documents = []

        # Initialize Tokenizer for more accurate splitting
        tokenizer = tiktoken.get_encoding("cl100k_base")

        def tiktoken_len(text):
            tokens = tokenizer.encode(text, disallowed_special=())
            return len(tokens)

        for filename, roles in DOCUMENT_MAP.items():
            folder = RAW_DATA_PATH if filename.endswith(".csv") else PROCESSED_DATA_PATH
            file_path = os.path.join(folder, filename)

            if not os.path.exists(file_path):
                print(f"Warning: {filename} not found in {folder}")
                continue

            loader = (
                CSVLoader(file_path, encoding="utf-8")
                if filename.endswith(".csv")
                else UnstructuredMarkdownLoader(file_path)
            )
            docs = loader.load()

            # Using tiktoken for splitting logic
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,  # 500 tokens is a sweet spot for RAG
                chunk_overlap=50,
                length_function=tiktoken_len,
                separators=["\n\n", "\n", " ", ""],
            )

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

        db = Chroma.from_documents(
            documents, self.embeddings, persist_directory=CHROMA_PATH
        )
        print(f"Vector store created at {CHROMA_PATH}")

    def run_pipeline(self, question: str):
        if not os.path.exists(CHROMA_PATH):
            print(f"Vector store not found at {CHROMA_PATH}")
            return []

        db = Chroma(persist_directory=CHROMA_PATH, embedding_function=self.embeddings)

        # Get all documents first, then filter by role
        retriever = db.as_retriever(search_kwargs={"k": 20})  # Get more docs to filter
        all_docs = retriever.invoke(question)
        
        # Filter documents based on user role
        filtered_docs = []
        for doc in all_docs:
            allowed_roles = doc.metadata.get("allowed_roles", [])
            if self.user_role in allowed_roles:
                filtered_docs.append(doc)
        
        # Limit to top 5 results after filtering
        filtered_docs = filtered_docs[:5]
        
        print(f"User role: {self.user_role}")
        print(f"Found {len(all_docs)} total documents, {len(filtered_docs)} accessible to user")
        
        if not filtered_docs:
            print(f"No documents accessible to role: {self.user_role}")
            return []

        # Return structured data for routes.py
        return [
            {
                "doc_id": d.metadata.get("source"), 
                "content": d.page_content,
                "allowed_roles": d.metadata.get("allowed_roles", [])
            }
            for d in filtered_docs
        ]


if __name__ == "__main__":
    # To build the database initially, run: python app/rag_pipeline.py
    pipeline = FinSolveRAGPipeline(role="C-Level")
    pipeline.create_vector_store()
