import json
from sentence_transformers import SentenceTransformer

# Paths
CHUNKS_FILE = "../chunking/chunks.json"
OUTPUT_FILE = "embedding.json"

# Load model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Load chunks (LIST)
with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
    chunks = json.load(f)

chunk_ids = []
chunk_texts = []

for item in chunks:
    chunk_ids.append(item["chunk_id"])
    chunk_texts.append(item["content"])

# Generate embeddings
embeddings = model.encode(chunk_texts, show_progress_bar=True)

# Store as chunk_id -> embedding
embedding_data = {
    chunk_id: embedding.tolist()
    for chunk_id, embedding in zip(chunk_ids, embeddings)
}

# Save embeddings
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(embedding_data, f, indent=2)

print(f"✅ Successfully saved {len(embedding_data)} embeddings to {OUTPUT_FILE}")
