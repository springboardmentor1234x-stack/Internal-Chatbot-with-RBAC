import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np
import os

# -------------------------------------------------------
# 1. Load embedding model
# -------------------------------------------------------
print("Loading SentenceTransformer model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# -------------------------------------------------------
# 2. Connect to Chroma and load collection
# -------------------------------------------------------
print("Connecting to Chroma...")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

client = chromadb.PersistentClient(
    path=os.path.join(PROJECT_ROOT, "chroma_db")
)

collection = client.get_collection(
    name="company_chunks"
)

print("Collection loaded successfully.")

# -------------------------------------------------------
# 3. Function: Perform semantic search
# -------------------------------------------------------
def semantic_search(query_text, top_k=3):
    """
    Performs semantic search on the Chroma database.
    Returns top_k most relevant documents with metadata.
    """

    # Convert query into embedding
    query_embedding = model.encode([query_text])
    query_embedding = np.array(query_embedding).tolist()

    # Query Chroma
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )

    return results

# -------------------------------------------------------
# 4. MAIN PROGRAM FLOW
# -------------------------------------------------------
if __name__ == "__main__":
    print("\n===== Semantic Search System Ready =====")

    while True:
        query = input("\nEnter your query (or type 'exit'): ")

        if query.lower() == "exit":
            print("Exiting search system. Goodbye.")
            break

        top_k = 3  # default
        results = semantic_search(query, top_k)

        print("\n===== Search Results =====")

        for idx in range(len(results["ids"][0])):
            print(f"\nResult {idx+1}")
            print("-" * 40)
            print("ID:", results["ids"][0][idx])
            print("Score:", results["distances"][0][idx])
            print("Chunk Text Preview:", results["documents"][0][idx][:200], "...")
            print("Metadata:", results["metadatas"][0][idx])

        print("\n========================================")
