from vectorstore.chroma_store import ChromaVectorStore
from embeddings.embedder import SentenceTransformerEmbedder

store = ChromaVectorStore()
embedder = SentenceTransformerEmbedder()

query = "system architecture"
query_vector = embedder.embed([query])[0]

results = store.search(
    query_vector=query_vector,
    user_context={"role": "ENGINEERING"},
    top_k=3,
    threshold=0.35
)


print("Results found:", len(results))
for r in results:
    print(r["metadata"]["doc_id"])
