
#     ingest()
import os
from langchain_community.document_loaders import TextLoader, CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from  backend.core.config import DATA_DIR, CHROMA_DIR, embedding_model


def load_docs():
    documents = []

    for folder in os.listdir(DATA_DIR):
        folder_path = os.path.join(DATA_DIR, folder)

        if not os.path.isdir(folder_path):
            continue

        role = folder.lower().strip()   # ✅ role as STRING only

        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)

            try:
                if file.endswith(".md"):
                    loader = TextLoader(file_path, encoding="utf-8")
                elif file.endswith(".csv"):
                    loader = CSVLoader(file_path)
                else:
                    continue

                docs = loader.load()

                for doc in docs:
                    # ✅ VERY IMPORTANT: SIMPLE METADATA ONLY
                    doc.metadata = {
                        "role": role,      # string (NOT list)
                        "source": file     # string
                    }

                documents.extend(docs)

            except Exception as e:
                print(f"⚠️ Skipping {file_path}: {e}")

    return documents


def ingest():
    print("📥 Loading documents...")
    docs = load_docs()

    if not docs:
        print("❌ No documents found")
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(docs)

    print(f"✂️ Created {len(chunks)} chunks")

    # ✅ Chroma auto-persists (NO .persist() needed)
    Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=CHROMA_DIR
    )

    print("✅ Ingestion completed successfully")


if __name__ == "__main__":
    ingest()
