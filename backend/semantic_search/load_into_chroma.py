import json
import numpy as np
import chromadb
import os

# ----------------------------------------------------
# 1. Resolve Paths (CORRECT)
# ----------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))      # backend/semantic_search
BACKEND_DIR = os.path.dirname(BASE_DIR)                    # backend
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)                # project root

EMBEDDINGS_DIR = os.path.join(PROJECT_ROOT, "Embeddings")

EMBEDDINGS_PATH = os.path.join(EMBEDDINGS_DIR, "chunk_embeddings.npy")
IDS_PATH = os.path.join(EMBEDDINGS_DIR, "embedding_index.json")

CHUNKS_PATH = os.path.join(PROJECT_ROOT, "chunking", "student_chunks.json")
METADATA_PATH = os.path.join(PROJECT_ROOT, "chunking", "student_metadata.json")


# ----------------------------------------------------
# 2. Load Embeddings, IDs, Chunks, Metadata
# ----------------------------------------------------
print("Loading embeddings...")
embeddings = np.load(EMBEDDINGS_PATH)

with open(IDS_PATH, "r", encoding="utf-8") as f:
    ids = json.load(f)

with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
    chunk_list = json.load(f)

with open(METADATA_PATH, "r", encoding="utf-8") as f:
    metadata_list = json.load(f)

# ----------------------------------------------------
# 3. Prepare Dictionaries (match IDs exactly)
# ----------------------------------------------------
# Chunk IDs are already in the correct format: ENGINEERING_CHUNK_1, FINANCE_CHUNK_13, etc.
chunk_texts = {item["chunk_id"]: item["chunk_text"] for item in chunk_list}
metadata_map = {item["chunk_id"]: item for item in metadata_list}

print(f"Loaded {len(ids)} IDs.")
print(f"Loaded {embeddings.shape[0]} embeddings.")

# ----------------------------------------------------
# 4. Create Chroma Collection
# ----------------------------------------------------
client = chromadb.PersistentClient(
    path=os.path.join(PROJECT_ROOT, "chroma_db")
)

# Delete old collection if exists
if "company_chunks" in [col.name for col in client.list_collections()]:
    client.delete_collection("company_chunks")
    print("Old Chroma collection deleted successfully.")

collection = client.get_or_create_collection(
    name="company_chunks",
    metadata={"hnsw:space": "cosine"}
)

# ----------------------------------------------------
# 5. Prepare Data for Insertion
# ----------------------------------------------------
documents = []
metadatas = []
final_ids = []

for eid in ids:
    if eid not in chunk_texts:
        print(f"Warning: Chunk text missing for ID '{eid}'. Skipping...")
        continue
    if eid not in metadata_map:
        print(f"Warning: Metadata missing for ID '{eid}'. Skipping...")
        continue

    doc = chunk_texts[eid]
    meta = metadata_map[eid].copy()

    # Convert list fields in metadata to comma-separated strings
    for key, value in meta.items():
        if isinstance(value, list):
            meta[key] = ", ".join(value)

    documents.append(doc)
    metadatas.append(meta)
    final_ids.append(eid)

# ----------------------------------------------------
# 6. Insert into Chroma
# ----------------------------------------------------
if documents and metadatas and final_ids:
    print("Inserting into Chroma...")
    # Make sure embeddings match the filtered final_ids
    filtered_embeddings = [embeddings[ids.index(eid)].tolist() for eid in final_ids]

    collection.add(
        ids=final_ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=filtered_embeddings
    )
    print("Insertion complete.")
    print("Total documents stored:", collection.count())
else:
    print("No data to insert. Check chunk IDs and embeddings.")



