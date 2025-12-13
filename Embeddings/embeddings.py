import json
import numpy as np
from sentence_transformers import SentenceTransformer
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, "chunking", "student_chunks.json")
OUTPUT_EMBEDDINGS = os.path.join(BASE_DIR, "Embeddings", "chunk_embeddings.npy")
OUTPUT_INDEX = os.path.join(BASE_DIR, "Embeddings", "embedding_index.json")

model = SentenceTransformer("all-MiniLM-L6-v2")

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    chunks = json.load(f)

contents = [chunk["chunk_text"] for chunk in chunks]

embeddings = model.encode(contents, show_progress_bar=True)

np.save(OUTPUT_EMBEDDINGS, embeddings)

index_list = [f"{chunk['chunk_id'].split('_')[0]}_CHUNK_{i+1}" for i, chunk in enumerate(chunks)]

with open(OUTPUT_INDEX, "w", encoding="utf-8") as f:
    json.dump(index_list, f, ensure_ascii=False, indent=4)

print("Embeddings and index saved successfully!")




