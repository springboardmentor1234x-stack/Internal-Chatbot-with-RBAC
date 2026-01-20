from ingestion.loader import ingest_documents
from chunking.chunker import chunk_documents
from normalization.normalizer import normalize_chunks
from embeddings.embedder import SentenceTransformerEmbedder, embed_chunks
from vectorstore.chroma_store import ChromaVectorStore

print("Starting indexing...")

docs = ingest_documents("datasets/Fintech-data")
chunks = chunk_documents(docs)
normalized_chunks = normalize_chunks(chunks)

embedder = SentenceTransformerEmbedder()
embedded_chunks = embed_chunks(normalized_chunks, embedder)

store = ChromaVectorStore()
store.add_documents(embedded_chunks)

print("Indexing complete ✅")
