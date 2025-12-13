import json
import numpy as np
import chromadb
import os

# ----------------------------------------------------
# 1. File Paths
# ----------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))          
PROJECT_ROOT = os.path.dirname(BASE_DIR)                        

EMBEDDINGS_DIR = os.path.join(PROJECT_ROOT, "Embeddings")

EMBEDDINGS_PATH = os.path.join(EMBEDDINGS_DIR, "chunk_embeddings.npy")
IDS_PATH = os.path.join(EMBEDDINGS_DIR, "embedding_index.json")

CHUNKS_PATH = os.path.join(PROJECT_ROOT, "chunking", "student_chunks.json")
METADATA_PATH = os.path.join(PROJECT_ROOT, "chunking", "student_metadata.json")

# ----------------------------------------------------
# 2. Load Embeddings, IDs, Chunk Texts, Metadata
# ----------------------------------------------------
print("Loading embeddings...")
embeddings = np.load(EMBEDDINGS_PATH)

with open(IDS_PATH, "r") as f:
    ids = json.load(f)

with open(CHUNKS_PATH, "r") as f:
    chunk_list = json.load(f)

with open(METADATA_PATH, "r") as f:
    metadata_list = json.load(f)

# Convert list → dictionary { "ENGINEERING_CHUNK_1": "text..." }
chunk_texts = {}
for item in chunk_list:
    original_id = item["chunk_id"]              # ENGINEERING_1
    chunk_id = original_id + "_CHUNK"           # ENGINEERING_1_CHUNK (but your IDs are ENGINEERING_CHUNK_1)

    # Convert ENGINEERING_1 → ENGINEERING_CHUNK_1
    parts = original_id.split("_")              # ["ENGINEERING", "1"]
    new_id = parts[0] + "_CHUNK_" + parts[1]    # ENGINEERING_CHUNK_1

    chunk_texts[new_id] = item["chunk_text"]

# Convert metadata list → dictionary { "ENGINEERING_1": {...} }
metadata_map = {item["chunk_id"]: item for item in metadata_list}

print(f"Loaded {len(ids)} IDs.")
print(f"Loaded {embeddings.shape[0]} embeddings.")

# ----------------------------------------------------
# 3. Create Chroma Collection
# ----------------------------------------------------
client = chromadb.PersistentClient(
    path=os.path.join(PROJECT_ROOT, "chroma_db")
)


collection = client.get_or_create_collection(
    name="company_chunks",
    metadata={"hnsw:space": "cosine"}
)

# ----------------------------------------------------
# 4. Prepare Data for Insertion
# ----------------------------------------------------
documents = []
metadatas = []
final_ids = []

for eid in ids:
    # eid = ENGINEERING_CHUNK_1
    # Convert → ENGINEERING_1 for metadata lookup
    meta_key = eid.replace("_CHUNK_", "_")

    if meta_key not in metadata_map:
        print(f"Warning: Metadata missing for ID '{meta_key}'.")
        continue

    if eid not in chunk_texts:
        print(f"Warning: Chunk text missing for ID '{eid}'.")
        continue

    doc = chunk_texts[eid]
    meta = metadata_map[meta_key].copy()

    # Convert lists → comma-separated strings
    for key, value in meta.items():
        if isinstance(value, list):
            meta[key] = ", ".join(value)

    documents.append(doc)
    metadatas.append(meta)
    final_ids.append(eid)

# ----------------------------------------------------
# 5. Insert into Chroma
# ----------------------------------------------------
print("Inserting into Chroma...")

collection.add(
    ids=final_ids,
    documents=documents,
    metadatas=metadatas,
    embeddings=embeddings.tolist()
)

print("Insertion complete.")
print("Total documents stored:", collection.count())






