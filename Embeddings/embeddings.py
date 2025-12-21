import json
import numpy as np
from sentence_transformers import SentenceTransformer
import os

# ==========================================================
# 1. Paths
# ==========================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHUNKS_FILE = os.path.join(BASE_DIR, "chunking", "student_chunks.json")
EMBEDDINGS_FILE = os.path.join(BASE_DIR, "Embeddings", "chunk_embeddings.npy")
INDEX_FILE = os.path.join(BASE_DIR, "Embeddings", "embedding_index.json")

os.makedirs(os.path.join(BASE_DIR, "Embeddings"), exist_ok=True)

# ==========================================================
# 2. Load Model
# ==========================================================
print("Loading SentenceTransformer model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# ==========================================================
# 3. Load Chunks
# ==========================================================
with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
    chunks = json.load(f)

texts = [chunk["chunk_text"] for chunk in chunks]

print(f"Generating embeddings for {len(texts)} chunks...")

# ==========================================================
# 4. Generate Embeddings
# ==========================================================
embeddings = model.encode(texts, show_progress_bar=True)

# ==========================================================
# 5. Save Embeddings
# ==========================================================
np.save(EMBEDDINGS_FILE, embeddings)

# ==========================================================
# 6. Create Corrected Embedding Index
#    Ensures format like: ENGINEERING_CHUNK_1
# ==========================================================
index_list = []

for chunk in chunks:
    # If chunk_id already contains _CHUNK_, keep it
    if "_CHUNK_" in chunk["chunk_id"]:
        index_list.append(chunk["chunk_id"])
    else:
        department, number = chunk["chunk_id"].rsplit("_", 1)
        index_list.append(f"{department}_CHUNK_{number}")

# ==========================================================
# 7. Save Index
# ==========================================================
with open(INDEX_FILE, "w", encoding="utf-8") as f:
    json.dump(index_list, f, indent=4)

print("Embeddings saved →", EMBEDDINGS_FILE)
print("Index saved      →", INDEX_FILE)
print("Embedding generation completed successfully!")






