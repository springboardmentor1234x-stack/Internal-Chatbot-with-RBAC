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
DEBUG = True

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
def resolve_paths():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(base_dir)
    project_root = os.path.dirname(backend_dir)

    rbac_file = os.path.join(backend_dir, "RBAC", "rbac.json")
    chroma_db_path = os.path.join(project_root, "chroma_db")

    return rbac_file, chroma_db_path

RBAC_FILE, CHROMA_DB_PATH = resolve_paths()

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
print("🔍 Chroma DB path used by API:", CHROMA_DB_PATH)
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
        "policy": ["guidelines"],
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
# 6. RBAC LOGIC
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

def get_allowed_departments(user_role: str) -> List[str]:
    canonical = resolve_role(user_role)
    permissions = get_all_permissions(canonical)

    debug_print("Canonical role:", canonical)
    debug_print("Permissions:", permissions)

    allowed = set()
    for p in permissions:
        if p in {"*", "read:*"}:
            return ["general", "engineering", "finance", "hr", "marketing"]
        if p.startswith("read:"):
            allowed.add(p.split(":")[1])

    debug_print("Allowed departments:", allowed)
    return list(allowed)

# =======================================================
# 7. Similarity
# =======================================================
def cosine_similarity(a, b) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

# =======================================================
# 7A. Reranking
# =======================================================
def rerank_results(query_variants: List[str], results: List, top_k: int):
    reranked = []
    query_embs = [model.encode(qv) for qv in query_variants]

    for score, item in results:
        chunk_emb = model.encode(item["document"])
        semantic_score = max(cosine_similarity(qe, chunk_emb) for qe in query_embs)
        final_score = (0.6 * score) + (0.4 * semantic_score)
        reranked.append((final_score, item))

    reranked.sort(key=lambda x: x[0], reverse=True)
    return reranked[:top_k]

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
# 9. 🔐 SECURE SEMANTIC SEARCH (RBAC → SEARCH)
# =======================================================
def semantic_search(query: str, user_role: str, final_k=3):
    query_variants = generate_query_variants(query)
    query_embeddings = model.encode(query_variants)

    # ===================================================
    # STEP 1: RBAC FIRST (HARD GATE)
    # ===================================================
    allowed_departments = get_allowed_departments(user_role)

    if not allowed_departments:
        return {
            "results": [],
            "authorized_count": 0,
            "query_variants": query_variants,
            "rbac_status": "NO_ACCESS"
        }

    allowed_departments_mapped = [d.capitalize() for d in allowed_departments]
    debug_print("RBAC allowlist:", allowed_departments_mapped)

    # ===================================================
    # STEP 2: RETRIEVE ONLY AUTHORIZED CHUNKS
    # ===================================================
    ann = collection.query(
        query_embeddings=[qe.tolist() for qe in query_embeddings],
        n_results=final_k * 10,
        where={"department": {"$in": allowed_departments_mapped}},
        include=["documents", "metadatas", "embeddings"]
    )

    authorized_chunks = []
    for docs, metas, embs in zip(ann["documents"], ann["metadatas"], ann["embeddings"]):
        for d, m, e in zip(docs, metas, embs):
            authorized_chunks.append({
                "chunk_id": m.get("chunk_id") or f"chunk_{hash(d) % 1_000_000}",
                "document": d,
                "metadata": m,
                "embedding": np.array(e)
            })

    debug_print("Authorized chunks retrieved:", len(authorized_chunks))

    # ===================================================
    # STEP 3: SEMANTIC SCORING (AUTHORIZED ONLY)
    # ===================================================
    aggregated = {}

    for q_emb in query_embeddings:
        for item in authorized_chunks:
            score = cosine_similarity(q_emb, item["embedding"])
            cid = item["chunk_id"]

            if cid not in aggregated or score > aggregated[cid][0]:
                aggregated[cid] = (score, item)

    # ===================================================
    # STEP 4: DEDUPLICATION
    # ===================================================
    deduped = deduplicate_results(list(aggregated.values()))

    # ===================================================
    # STEP 5: THRESHOLDING (FINAL)
    # ===================================================
    FINAL_MIN_SCORE = 0.3
    thresholded = [(s, r) for s, r in deduped if s >= FINAL_MIN_SCORE]

    # ===================================================
    # STEP 6: RERANKING
    # ===================================================
    final_results = rerank_results(query_variants, thresholded, final_k)

    return {
        "results": final_results,
        "authorized_count": len(authorized_chunks),
        "authorized_departments": allowed_departments_mapped,
        "query_variants": query_variants,
        "rbac_status": "AUTHORIZED"
    }

# =======================================================
# 10. CLI TEST HARNESS
# =======================================================
def run_query(role, query):
    canonical = resolve_role(role)
    effective_roles = get_all_roles(canonical)
    output = semantic_search(query, role)

    print("\n================ QUERY SUMMARY ================")
    print(f"User Role       : {role}")
    print(f"Resolved Role   : {canonical}")
    print(f"Effective Roles : {', '.join(sorted(effective_roles))}")

    print("\nQuery Variants:")
    for v in output["query_variants"]:
        print(f" - {v}")

    print(f"\nAuthorized Chunks : {output['authorized_count']}")

    if not output["results"]:
        print("\n>> ACCESS DENIED OR NO AUTHORIZED DATA")
        print("================================================")
        return

    print("\n================ TOP RESULTS ================")
    for i, (score, res) in enumerate(output["results"], 1):
        meta = res["metadata"]
        print(f"{i}. Chunk ID : {res['chunk_id']}")
        print(f"   Doc ID   : {meta.get('document_id')}")
        print(f"   Score    : {round(score, 4)}")
        print(f"   Text     : {res['document']}\n")

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
