import chromadb
import os
import json
import numpy as np

def sanitize_metadata(meta: dict):
    clean_meta = {}

    for key, value in meta.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            clean_meta[key] = value
        elif isinstance(value, list):
            clean_meta[key] = ", ".join(map(str, value))
        elif isinstance(value, dict):
            clean_meta[key] = json.dumps(value)
        else:
            clean_meta[key] = str(value)

    return clean_meta


def create_collections(chunks, metadata, embeddings, VECTOR_DB_DIR):
    os.makedirs(VECTOR_DB_DIR, exist_ok=True)

    chroma_client = chromadb.PersistentClient(
        path=VECTOR_DB_DIR
    )

    dept_groups = {}

    # -------- Group by department --------
    for i, meta in enumerate(metadata):
        dept = meta.get("department", "").lower().strip()

        if dept == "hr":
            dept = "human_resource"
        else:
            dept = dept.replace(" ", "_")

        if dept not in dept_groups:
            dept_groups[dept] = {
                "ids": [],
                "docs": [],
                "metas": [],
                "vectors": []
            }

        dept_groups[dept]["ids"].append(chunks[i]["chunk_id"])
        dept_groups[dept]["docs"].append(chunks[i]["content"])
        dept_groups[dept]["metas"].append(sanitize_metadata(meta))
        dept_groups[dept]["vectors"].append(embeddings[i].tolist())

    # -------- Create collections --------
    for dept, data in dept_groups.items():
        print(f"Creating / Updating collection: {dept}")

        collection = chroma_client.get_or_create_collection(name=dept)

        collection.add(
            ids=data["ids"],
            documents=data["docs"],
            metadatas=data["metas"],
            embeddings=data["vectors"]
        )

    print(f"\n✅ Vector DB automatically persisted at: {VECTOR_DB_DIR}")
    return chroma_client


if __name__ == "__main__":

    VECTOR_DB_DIR = r"D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC/VectorDB"

    CHUNKS_FILE = r"D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC/Chunking/all_chunks.json"
    METADATA_FILE = r"D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC/Chunking/all_metadata.json"
    EMBEDDINGS_FILE = r"D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC/Embeddings/chunk_embeddings.npy"

    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    embeddings = np.load(EMBEDDINGS_FILE)

    create_collections(chunks, metadata, embeddings, VECTOR_DB_DIR)