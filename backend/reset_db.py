import chromadb

client = chromadb.PersistentClient(path="chroma_db")

print("🧹 Deleting collection: company_docs")
client.delete_collection("company_docs")

print("✅ Collection deleted. You can now re-ingest safely.")
