import os
from langchain_community.document_loaders import PyPDFLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

DATA_PATH = "data/"
DB_PATH = "vector_db/"

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def process_files():
    if not os.path.exists(DB_PATH):
        os.makedirs(DB_PATH)

    for root, dirs, files in os.walk(DATA_PATH):
        for file in files:
            file_path = os.path.join(root, file)
            
            if file.lower().endswith(".pdf"):
                loader = PyPDFLoader(file_path)
            elif file.lower().endswith((".md", ".txt")):
                loader = UnstructuredMarkdownLoader(file_path)
            else:
                continue

            documents = loader.load()
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, 
                chunk_overlap=200,
                separators=["\n\n", "\n", " ", ""]
            )
            chunks = text_splitter.split_documents(documents)
            
            if "salary" in file.lower() or "hr" in file.lower():
                collection_name = "hr_data"
            elif "marketing" in file.lower():
                collection_name = "marketing_data"
            else:
                collection_name = "general_data"
            
            Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                collection_name=collection_name,
                persist_directory=DB_PATH
            )

if __name__ == "__main__":
    process_files()