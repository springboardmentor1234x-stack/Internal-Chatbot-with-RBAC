import json
from datetime import datetime

INPUT_FILE = "D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC/normalization/engineering_master_doc_cleaned.txt"
CHUNK_SIZE = 350
OVERLAP = 50
OUTPUT_CHUNKS_FILE = "engineering_chunks.json"
OUTPUT_METADATA_FILE = "engineering_metadata.json"

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    text = file.read()

tokens = text.split()

total_tokens = len(tokens)
print(f"Total Tokens in Document: {total_tokens}")

chunks = []
start = 0

for i in range(3):
    end = start + CHUNK_SIZE
    chunk_tokens = tokens[start:end]
    chunk_text = " ".join(chunk_tokens)
    chunks.append(chunk_text)
    start = end - OVERLAP

chunk_data = []

for i, chunk in enumerate(chunks, start=1):
    chunk_data.append({
        "chunk_id": f"ENG_CHUNK_{i}",
        "content": chunk
    })

with open(OUTPUT_CHUNKS_FILE, "w", encoding="utf-8") as f:
    json.dump(chunk_data, f, indent=4)

print("Chunks saved to:", OUTPUT_CHUNKS_FILE)

metadata = []

for i, chunk in enumerate(chunks, start=1):
    meta = {
        "chunk_id": f"ENG_CHUNK_{i}",
        "source_document": "engineering_master_doc.md",
        "department": "Engineering",
        "chunk_index": i,
        "total_chunks": 3,
        "approx_token_count": len(chunk.split()),
        "security_level": "Confidential",
        "allowed_roles": [
            "Engineering Lead",
            "Backend Developer",
            "Frontend Developer",
            "DevOps Engineer",
            "System Architect",
            "Security Team",
            "C-Level Executive"
        ],
        "created_at": datetime.now().isoformat()
    }

    metadata.append(meta)

with open(OUTPUT_METADATA_FILE, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=4)

print("Metadata saved to:", OUTPUT_METADATA_FILE)
