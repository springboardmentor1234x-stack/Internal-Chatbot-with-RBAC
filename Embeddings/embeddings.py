import json
import numpy as np
from sentence_transformers import SentenceTransformer

INPUT_FILE = "D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC/Chunking/all_chunks.json"

OUTPUT_EMBEDDINGS = "chunk_embeddings.npy"
OUTPUT_INDEX = "embedding_index.json"

model = SentenceTransformer("all-MiniLM-L6-v2")

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    chunks = json.load(f)

contents = [chunk["content"] for chunk in chunks]
chunk_ids = [chunk["chunk_id"] for chunk in chunks]

embeddings = model.encode(
    contents,
    batch_size=32,
    show_progress_bar=True,
    convert_to_numpy=True,
    normalize_embeddings=True
)

np.save(OUTPUT_EMBEDDINGS, embeddings)

with open(OUTPUT_INDEX, "w", encoding="utf-8") as f:
    json.dump(chunk_ids, f, indent=4)
