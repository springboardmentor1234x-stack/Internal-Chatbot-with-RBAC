import os
import json
import re
import numpy as np
import chromadb
from sentence_transformers import SentenceTransformer
from typing import Dict, Set, List

# =======================================================
# DEBUG MODE
# =======================================================
DEBUG = False  # Set False for production

def debug_print(*args):
    if DEBUG:
        print("[DEBUG]", *args)

# =======================================================
# 1. Load Sentence Transformer Model
# =======================================================
print("Loading SentenceTransformer model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# =======================================================
# 2. Resolve Paths
# =======================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
RBAC_FILE = os.path.join(PROJECT_ROOT, "RBAC", "rbac.json")
CHROMA_DB_PATH = os.path.join(PROJECT_ROOT, "chroma_db")

# =======================================================
# 3. Load RBAC Configuration
# =======================================================
with open(RBAC_FILE, "r", encoding="utf-8") as f:
    RBAC_RAW = json.load(f)

ROLES = RBAC_RAW["roles"]
ROLE_ALIASES = RBAC_RAW["role_aliases"]
ROLE_ALIASES_NORM = {k.lower().strip(): v for k, v in ROLE_ALIASES.items()}

# =======================================================
# 4. Connect to Chroma DB
# =======================================================
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = client.get_collection(name="company_chunks")

# =======================================================
# 5. Query Normalization
# =======================================================
def rewrite_query(query: str) -> str:
    q = query.lower().strip()
    q = re.sub(r"[^\w\s]", "", q)
    abbreviations = {
        "hr": "human resources",
        "eng": "engineering",
        "qa": "quality assurance",
    }
    tokens = q.split()
    expanded = [abbreviations.get(t, t) for t in tokens]
    stopwords = {
        "what", "is", "the", "a", "an", "how", "does", "do", "can",
        "please", "explain", "tell", "me", "about"
    }
    return " ".join(t for t in expanded if t not in stopwords)

# =======================================================
# 5A. Query Variant Generation
# =======================================================
def generate_query_variants(original_query: str) -> List[str]:
    base = rewrite_query(original_query)
    variants = {base}
    substitutions = {
        "policy": ["rules", "guidelines", "procedure"],
        "leave": ["time off", "absence"],
        "handbook": ["manual", "documentation"],
        "salary": ["pay", "compensation"],
        "review": ["evaluation", "assessment"]
    }
    for word, repls in substitutions.items():
        if word in base:
            for r in repls:
                variants.add(base.replace(word, r))
    return list(variants)

# =======================================================
# 6. RBAC Logic
# =======================================================
def resolve_role(user_role: str) -> str:
    key = user_role.lower().strip()
    return ROLE_ALIASES_NORM.get(key, key.replace(" ", "_"))

def get_all_roles(role: str) -> Set[str]:
    roles = {role}
    for parent in ROLES.get(role, {}).get("inherits", []):
        roles |= get_all_roles(parent)
    return roles

def get_all_permissions(role: str) -> Set[str]:
    perms = set()
    for r in get_all_roles(role):
        perms |= set(ROLES.get(r, {}).get("permissions", []))
    return perms

def is_authorized(user_role: str, metadata: Dict) -> bool:
    canonical = resolve_role(user_role)
    permissions = get_all_permissions(canonical)
    dept = metadata.get("department", "").lower()
    dept_map = {
        "human resources": "hr",
        "hr": "hr",
        "engineering": "engineering",
        "finance": "finance",
        "marketing": "marketing",
        "general": "general"
    }
    normalized = dept_map.get(dept, dept)
    return (
        f"read:{normalized}" in permissions
        or "read:*" in permissions
        or "*" in permissions
    )

# =======================================================
# 7. Similarity
# =======================================================
def cosine_similarity(a, b) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

# =======================================================
# 8. Deduplication
# =======================================================
def deduplicate_results(results, max_chunks_per_doc=2):
    by_chunk = {}
    for score, res in results:
        cid = res["chunk_id"]
        if cid not in by_chunk or score > by_chunk[cid][0]:
            by_chunk[cid] = (score, res)

    final, doc_counter = [], {}
    for score, res in sorted(by_chunk.values(), key=lambda x: x[0], reverse=True):
        doc_id = res["metadata"].get("document_id", "UNKNOWN")
        doc_counter.setdefault(doc_id, 0)
        if doc_counter[doc_id] < max_chunks_per_doc:
            final.append((score, res))
            doc_counter[doc_id] += 1
    return final

# =======================================================
# 9. Semantic Search
# =======================================================
def semantic_search(query: str, user_role: str, final_k=3):
    query_variants = generate_query_variants(query)
    query_embeddings = model.encode(query_variants)
    ann = collection.query(
        query_embeddings=[qe.tolist() for qe in query_embeddings],
        n_results=final_k * 10,
        include=["documents", "metadatas", "embeddings"]
    )

    authorized = []
    for docs, metas, embs, ids in zip(ann["documents"], ann["metadatas"], ann["embeddings"], ann["ids"]):
        for d, m, e, cid in zip(docs, metas, embs, ids):
            if is_authorized(user_role, m):
                authorized.append({
                    "chunk_id": cid,
                    "document": d,  # ✅ chunk text added
                    "metadata": m,
                    "embedding": np.array(e)
                })

    aggregated = {}
    MIN_SCORE = 0.3
    for q_emb in query_embeddings:
        for item in authorized:
            score = cosine_similarity(q_emb, item["embedding"])
            cid = item["chunk_id"]
            if score < MIN_SCORE:
                continue
            if cid not in aggregated or score > aggregated[cid][0]:
                aggregated[cid] = (score, item)

    final_results = deduplicate_results(list(aggregated.values()))[:final_k]

    return {
        "results": final_results,
        "query_variants": query_variants,
        "authorized_count": len(authorized)
    }

# =======================================================
# 10. CLI Output (FORMAT ONLY)
# =======================================================
def run_query(role, query):
    canonical = resolve_role(role)
    effective_roles = get_all_roles(canonical)
    output = semantic_search(query, role)

    print("\n================ QUERY SUMMARY ================")
    print(f"User Role           : {role}")
    print(f"Resolved Role       : {canonical}")
    print(f"Effective Roles     : {', '.join(sorted(effective_roles))}")

    print("\nQuery Variants:")
    for v in output["query_variants"]:
        print(f" - {v}")

    print(f"\nAuthorized Chunks After RBAC : {output['authorized_count']}")

    if not output["results"]:
        print("\n>> No authorized or relevant results found.")
        print("================================================")
        return

    print("\n================ TOP K RESULTS ================")
    for i, (score, res) in enumerate(output["results"], 1):
        meta = res["metadata"]
        print(f"{i}. Chunk ID : {res['chunk_id']}")
        print(f"   Doc ID   : {meta.get('document_id')}")
        print(f"   Score    : {round(score, 4)}")
        print("   Chunk Text:")
        print(f"   {res['document']}\n")
    print("================================================")

# =======================================================
# 11. Entry Point
# =======================================================
if __name__ == "__main__":
    print("\nCompany Internal Chatbot (RBAC)")
    user_role = input("Enter your role: ").strip()
    while True:
        q = input("\nAsk your question: ").strip()
        if q.lower() in {"exit", "quit"}:
            break
        run_query(user_role, q)








