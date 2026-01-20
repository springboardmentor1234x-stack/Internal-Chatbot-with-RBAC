from vectorstore.chroma_store import ChromaVectorStore

store = ChromaVectorStore()

print("Collection name:", store.collection.name)
print("Document count:", store.collection.count())
