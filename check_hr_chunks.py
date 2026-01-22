from chromadb import PersistentClient

client = PersistentClient(path="ingestion/chroma_db")
collection = client.get_or_create_collection("fintech_documents")

hr_docs = collection.get(where={"department": "hr"})

print("HR chunks count:", len(hr_docs["documents"]))
print("HR docs:")
for doc in hr_docs["documents"]:
    print("-", doc)
