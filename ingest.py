import os
import shutil
import re
from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Absolute paths ensure stability on Windows
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(BASE_DIR, "chroma_db")

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def clean_text(text):
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'Page \d+ of \d+', '', text)
    return text.strip()

def process_files():
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
        print(f"📁 Folder created at {DATA_PATH}. Place your dept folders here.")
        return

    # Fresh Start: Clears old data to prevent "WinError 32" locking issues
    if os.path.exists(DB_PATH):
        try:
            shutil.rmtree(DB_PATH)
        except PermissionError:
            print("🛑 Error: Database is locked. Close all other terminals first!")
            return

    all_docs = []
    # walk into subfolders: data/hr, data/finance, etc.
    for root, dirs, files in os.walk(DATA_PATH):
        # The department name is the folder name
        dept = os.path.basename(root).lower()
        if dept == "data" or not dept:
            dept = "general"
            
        for file in files:
            file_path = os.path.join(root, file)
            try:
                # Select loader based on extension
                if file.lower().endswith(".pdf"):
                    loader = PyPDFLoader(file_path)
                elif file.lower().endswith(".csv"):
                    loader = CSVLoader(file_path, encoding='utf-8')
                elif file.lower().endswith((".txt", ".md")):
                    loader = TextLoader(file_path, encoding='utf-8')
                else:
                    continue
                
                documents = loader.load()
                for doc in documents:
                    doc.page_content = clean_text(doc.page_content)
                    # Metadata Tagging: This is where RBAC is enforced
                    doc.metadata.update({"dept": dept, "source": file})
                all_docs.extend(documents)
                print(f"✅ Assigned {file} -> Department: {dept}")
            except Exception as e:
                print(f"❌ Error loading {file}: {e}")

    if all_docs:
        # Smaller chunks (350) for high-precision retrieval
        splitter = RecursiveCharacterTextSplitter(chunk_size=350, chunk_overlap=50)
        chunks = splitter.split_documents(all_docs)
        
        Chroma.from_documents(
            documents=chunks, 
            embedding=embeddings, 
            persist_directory=DB_PATH
        )
        print(f"🎉 Success! Vector database built with {len(chunks)} chunks.")
    else:
        print("🛑 No documents found! Ensure your files are inside subfolders in 'data/'.")

if __name__ == "__main__":
    process_files()