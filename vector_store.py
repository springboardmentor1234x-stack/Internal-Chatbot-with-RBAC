import os
import chromadb
from chromadb.utils import embedding_functions

# Path to documents
DOCS_PATH = "documents"

# Embedding model
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# Chroma client
chroma_client = chromadb.Client()

collection = chroma_client.get_or_create_collection(
    name="company_docs",
    embedding_function=embedding_function
)


def ingest_documents():
    print("🔍 Starting document ingestion...")
    print("📁 Looking for documents in:", os.path.abspath(DOCS_PATH))

    documents = []
    metadatas = []
    ids = []

    doc_id = 0

    if not os.path.exists(DOCS_PATH):
        print("❌ documents folder not found")
        return

    for file_name in os.listdir(DOCS_PATH):
        print("📄 Found file:", file_name)

        if file_name.endswith(".txt"):
            file_path = os.path.join(DOCS_PATH, file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            documents.append(content)
            metadatas.append({"source": file_name})
            ids.append(str(doc_id))
            doc_id += 1

    if not documents:
        print("❌ No documents found to ingest")
        return

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    print(f"✅ Ingested {len(documents)} documents into ChromaDB")


def query_documents(query: str, top_k: int = 2):
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    return results["documents"][0]
