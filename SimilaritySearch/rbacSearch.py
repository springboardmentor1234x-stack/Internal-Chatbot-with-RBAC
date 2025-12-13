import json
import numpy as np
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

CHUNKS_FILE = r"D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC/Chunking/all_chunks.json"
METADATA_FILE = r"D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC/Chunking/all_metadata.json"
EMBEDDINGS_FILE = r"D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC/Embeddings/chunk_embeddings.npy"
VECTOR_DB_DIR = r"D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC/VectorDB"

def load_data():
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    embeddings = np.load(EMBEDDINGS_FILE)
    
    global embedding_lookup
    
    embedding_lookup = {
    chunk["chunk_id"]: embeddings[i]
    for i, chunk in enumerate(chunks)
    }

    # Convert list metadata to strings
    for meta in metadata:
        for key, value in meta.items():
            if isinstance(value, list):
                meta[key] = ", ".join(value)

    print(f"Loaded {len(chunks)} chunks.")
    return chunks, metadata, embeddings

def create_collections(chunks, metadata, embeddings):
    chroma_client = chromadb.Client(
        Settings(
            persist_directory=VECTOR_DB_DIR,
            anonymized_telemetry=False
        )
    )

    # Organize by department group
    dept_groups = {}

    for i, meta in enumerate(metadata):
        dept = meta["department"].lower().replace(" ", "_")

        if dept not in dept_groups:
            dept_groups[dept] = {
                "ids": [],
                "docs": [],
                "metas": [],
                "vectors": []
            }

        dept_groups[dept]["ids"].append(chunks[i]["chunk_id"])
        dept_groups[dept]["docs"].append(chunks[i]["content"])
        dept_groups[dept]["metas"].append(meta)
        dept_groups[dept]["vectors"].append(embeddings[i].tolist())

    # Create and insert each department collection
    for dept, data in dept_groups.items():
        print(f"\nCreating collection: {dept}")

        if dept == "hr":
            dept = "human_resource"

        collection = chroma_client.get_or_create_collection(name=dept)

        collection.add(
            ids=data["ids"],
            documents=data["docs"],
            metadatas=data["metas"],
            embeddings=data["vectors"]
        )

    print("\nAll department collections created successfully!")
    return chroma_client

def run_chroma_query(
    chroma_client,
    query,
    department,
    user_role,
    top_k=5,
    similarity_threshold=0.50
):
    model = SentenceTransformer("all-MiniLM-L6-v2")

    query_embedding = model.encode(
        query,
        convert_to_numpy=True,
        normalize_embeddings=True
    ).reshape(1, -1)

    collection = chroma_client.get_collection(name=department)

    ann_results = collection.query(
        query_embeddings=[query_embedding.tolist()[0]],
        n_results=top_k * 4 
    )

    filtered_results = []

    for i in range(len(ann_results["ids"][0])):
        meta = ann_results["metadatas"][0][i]

        allowed_roles = meta.get("allowed_roles", "")
        if isinstance(allowed_roles, list):
            allowed_roles = ", ".join(allowed_roles)

        # If user role NOT allowed then skip
        if user_role.lower() not in allowed_roles.lower():
            continue

        filtered_results.append({
            "id": ann_results["ids"][0][i],
            "document": ann_results["documents"][0][i],
            "metadata": meta,
            "distance": ann_results["distances"][0][i]
        })

    if not filtered_results:
        return "No RBAC-allowed matches found."

    reranked = []

    for item in filtered_results:
        doc_emb = embedding_lookup[item["id"]].reshape(1, -1)
        similarity = cosine_similarity(query_embedding, doc_emb)[0][0]

        if similarity >= similarity_threshold:
            reranked.append({
                "id": item["id"],
                "metadata": item["metadata"],
                "similarity": float(similarity)
            })

    if not reranked:
        return "No matches above similarity threshold."

    # Sort by similarity desc
    reranked = sorted(reranked, key=lambda x: x["similarity"], reverse=True)

    # Return top_k
    return reranked[:top_k]

def run_custom_knn_query(chunks, metadata, embeddings, query, department=None, top_k=5):
    model = SentenceTransformer("all-MiniLM-L6-v2")

    query_emb = model.encode(
        query, convert_to_numpy=True, normalize_embeddings=True
    )
    department = "hr" if department == "human_resource" else department

    # Filter by department (RBAC)
    dept_indices = []
    for i, meta in enumerate(metadata):
        if department is None or meta["department"].lower() == department.lower():
            dept_indices.append(i)

    filtered_embeddings = embeddings[dept_indices]
    filtered_meta = [metadata[i] for i in dept_indices]

    # Compute cosine similarity KNN
    sims = cosine_similarity([query_emb], filtered_embeddings)[0]

    # Sort and get top K
    top_idx = sims.argsort()[::-1][:top_k]

    # Similarity threshold
    threshold = 0.50
    reranked_results = []

    for idx in top_idx:
        if sims[idx] >= threshold:
            reranked_results.append({
                "similarity": float(sims[idx]),
                "metadata": filtered_meta[idx]
            })

    return reranked_results

if __name__ == "__main__":
    chunks, metadata, embeddings = load_data()
    chroma_client = create_collections(chunks, metadata, embeddings)

    user_query = input("\nAsk a Question: ")
    user_dept = input("Which Department to search in? (e.g. engineering, human_resource, etc): ").lower()

    print("\n======== METHOD 1: ChromaDB Search ========\n")
    chroma_results = run_chroma_query(chroma_client, user_query, user_dept, user_role="C-Level Executive")

    if isinstance(chroma_results, str):
        print(chroma_results)
    else:
        for i in range(len(chroma_results)):
            print(f"\nRank {i+1} | Similarity: {chroma_results[i]['similarity']:.4f}")
            print("Chunk ID:", chroma_results[i]["id"])
            print("Department:", chroma_results[i]["metadata"].get("department"))

    print("\n======== METHOD 2: Custom KNN + Reranking ========\n")

    knn_results = run_custom_knn_query(
        chunks, metadata, embeddings, user_query, department=user_dept, top_k=5
    )

    if not knn_results:
        print("No info found...")
    else:
        for i, r in enumerate(knn_results):
            print(f"\nRank {i+1} | Similarity: {r['score']:.4f}")
            print("Chunk ID:", r["metadata"].get("chunk_id"))
            print("Department:", r["metadata"].get("department"))

