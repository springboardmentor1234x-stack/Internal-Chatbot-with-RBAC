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






# import os
# import json
# import re
# import numpy as np
# import chromadb
# from sentence_transformers import SentenceTransformer
# from typing import Dict, Set, List

# # =======================================================
# # DEBUG MODE
# # =======================================================
# DEBUG = False  # Set False for production

# def debug_print(*args):
#     if DEBUG:
#         print("[DEBUG]", *args)

# # =======================================================
# # 1. Load Sentence Transformer Model
# # =======================================================
# print("Loading SentenceTransformer model...")
# model = SentenceTransformer("all-MiniLM-L6-v2")

# # =======================================================
# # 2. Resolve Paths
# # =======================================================
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# PROJECT_ROOT = os.path.dirname(BASE_DIR)

# RBAC_FILE = os.path.join(PROJECT_ROOT, "RBAC", "rbac.json")
# CHROMA_DB_PATH = os.path.join(PROJECT_ROOT, "chroma_db")

# # =======================================================
# # 3. Load RBAC Configuration
# # =======================================================
# with open(RBAC_FILE, "r", encoding="utf-8") as f:
#     RBAC_RAW = json.load(f)

# ROLES = RBAC_RAW["roles"]
# ROLE_ALIASES = RBAC_RAW["role_aliases"]

# ROLE_ALIASES_NORM = {k.lower().strip(): v for k, v in ROLE_ALIASES.items()}

# # =======================================================
# # 4. Connect to Chroma DB
# # =======================================================
# client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
# collection = client.get_collection(name="company_chunks")

# # =======================================================
# # 5. Query Normalization
# # =======================================================
# def rewrite_query(query: str) -> str:
#     q = query.lower().strip()
#     q = re.sub(r"[^\w\s]", "", q)

#     abbreviations = {
#         "hr": "human resources",
#         "eng": "engineering",
#         "qa": "quality assurance",
#     }

#     tokens = q.split()
#     expanded = [abbreviations.get(t, t) for t in tokens]

#     stopwords = {
#         "what", "is", "the", "a", "an", "how",
#         "does", "do", "can", "please", "explain",
#         "tell", "me", "about"
#     }

#     return " ".join(t for t in expanded if t not in stopwords)

# # =======================================================
# # 5A. Query Variant Generation
# # =======================================================
# def generate_query_variants(original_query: str) -> List[str]:
#     base = rewrite_query(original_query)
#     variants = {base}

#     substitutions = {
#         "policy": ["rules", "guidelines", "procedure"],
#         "leave": ["time off", "absence"],
#         "handbook": ["manual", "documentation"],
#         "salary": ["pay", "compensation"],
#         "review": ["evaluation", "assessment"]
#     }

#     for word, repls in substitutions.items():
#         if word in base:
#             for r in repls:
#                 variants.add(base.replace(word, r))

#     return list(variants)

# # =======================================================
# # 6. RBAC Logic
# # =======================================================
# def resolve_role(user_role: str) -> str:
#     key = user_role.lower().strip()
#     return ROLE_ALIASES_NORM.get(key, key.replace(" ", "_"))

# def get_all_roles(role: str) -> Set[str]:
#     roles = {role}
#     for parent in ROLES.get(role, {}).get("inherits", []):
#         roles |= get_all_roles(parent)
#     return roles

# def get_all_permissions(role: str) -> Set[str]:
#     perms = set()
#     for r in get_all_roles(role):
#         perms |= set(ROLES.get(r, {}).get("permissions", []))
#     return perms

# # =======================================================
# # RBAC: Classification & Clearance (ADDED)
# # =======================================================

# CLASSIFICATION_LEVELS = {
#     "public": 0,
#     "internal": 1,
#     "confidential": 2,
#     "restricted": 3
# }

# ROLE_CLEARANCE = {
#     "intern": 0,
#     "employee": 1,
#     "engineering_employee": 1,
#     "finance_employee": 1,
#     "marketing_employee": 1,
#     "hr_employee": 1,

#     "engineering_manager": 2,
#     "finance_manager": 2,
#     "marketing_manager": 2,
#     "hr_manager": 2,

#     "c_level": 3,
#     "security_officer": 3,
#     "admin": 3
# }

# def normalize_roles(roles):
#     return {r.lower().strip() for r in roles}
# # def is_authorized(user_role: str, metadata: Dict) -> bool:
# #     # ---------------------------------------------------
# #     # 0. Resolve canonical role (from role_aliases)
# #     # ---------------------------------------------------
# #     canonical_role = resolve_role(user_role)

# #     # ---------------------------------------------------
# #     # 1. Department-level permission (RBAC.json)
# #     # ---------------------------------------------------
# #     permissions = get_all_permissions(canonical_role)

# #     dept = metadata.get("department", "").lower()
# #     dept_map = {
# #         "human resources": "hr",
# #         "hr": "hr",
# #         "engineering": "engineering",
# #         "finance": "finance",
# #         "marketing": "marketing",
# #         "general": "general"
# #     }
# #     normalized_dept = dept_map.get(dept, dept)

# #     if not (
# #         f"read:{normalized_dept}" in permissions or
# #         "read:*" in permissions or
# #         "*" in permissions
# #     ):
# #         return False  #  No department access

# #     # ---------------------------------------------------
# #     # 2. Document-level permitted_roles (METADATA)
# #     # ---------------------------------------------------
# #     permitted_roles_raw = metadata.get("permitted_roles", "")
# #     permitted_roles = {
# #         resolve_role(r.strip())
# #         for r in permitted_roles_raw.split(",")
# #         if r.strip()
# #     }

# #     if permitted_roles and canonical_role not in permitted_roles:
# #         return False  #  Role not allowed by document

# #     # ---------------------------------------------------
# #     # 3. Classification clearance (CONFIDENTIAL FIX)
# #     # ---------------------------------------------------
# #     classification = metadata.get("classification", "public").lower()

# #     user_clearance = ROLE_CLEARANCE.get(canonical_role, 0)
# #     doc_level = CLASSIFICATION_LEVELS.get(classification, 0)

# #     if user_clearance < doc_level:
# #         return False  #  Confidential data blocked

# #     return True  #  Fully authorized

# def is_authorized(user_role: str, metadata: Dict) -> bool:
#     canonical_role = resolve_role(user_role)

#     # ---------------------------------------------------
#     # 0. ADMIN OVERRIDE
#     # ---------------------------------------------------
#     if canonical_role == "admin":
#         return True

#     # ---------------------------------------------------
#     # 1. Department-level RBAC (ORGANIZATIONAL ACCESS)
#     # ---------------------------------------------------
#     permissions = get_all_permissions(canonical_role)

#     dept = metadata.get("department", "").lower()
#     dept_map = {
#         "human resources": "hr",
#         "hr": "hr",
#         "engineering": "engineering",
#         "finance": "finance",
#         "marketing": "marketing",
#         "general": "general"
#     }

#     normalized_dept = dept_map.get(dept, dept)

#     if not (
#         f"read:{normalized_dept}" in permissions or
#         "read:*" in permissions or
#         "*" in permissions
#     ):
#         return False

#     # ---------------------------------------------------
#     # 2. METADATA permitted_roles (SOURCE OF TRUTH)
#     # ---------------------------------------------------
#     metadata_roles = normalize_roles(
#         metadata.get("permitted_roles", [])
#     )

#     # User may inherit multiple roles (RBAC hierarchy)
#     effective_roles = normalize_roles(
#         get_all_roles(canonical_role)
#     )

#     # If metadata defines roles, enforce them strictly
#     if metadata_roles and not (metadata_roles & effective_roles):
#         return False

#     # ---------------------------------------------------
#     # 3. Classification clearance
#     # ---------------------------------------------------
#     classification = metadata.get("classification", "public").lower()

#     user_clearance = ROLE_CLEARANCE.get(canonical_role, 0)
#     doc_level = CLASSIFICATION_LEVELS.get(classification, 0)

#     if user_clearance < doc_level:
#         return False

#     return True



# # =======================================================
# # 7. Similarity
# # =======================================================
# def cosine_similarity(a, b) -> float:
#     return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

# # =======================================================
# # 8. Deduplication
# # =======================================================
# def deduplicate_results(results, max_chunks_per_doc=2):
#     by_chunk = {}
#     for score, res in results:
#         cid = res["chunk_id"]
#         if cid not in by_chunk or score > by_chunk[cid][0]:
#             by_chunk[cid] = (score, res)

#     final, doc_counter = [], {}
#     for score, res in sorted(by_chunk.values(), key=lambda x: x[0], reverse=True):
#         doc_id = res["metadata"].get("document_id", "UNKNOWN")
#         doc_counter.setdefault(doc_id, 0)
#         if doc_counter[doc_id] < max_chunks_per_doc:
#             final.append((score, res))
#             doc_counter[doc_id] += 1
#     return final

# # =======================================================
# # 9. Semantic Search
# # =======================================================
# def semantic_search(query: str, user_role: str, final_k=3):

#     query_variants = generate_query_variants(query)
#     query_embeddings = model.encode(query_variants)

#     ann = collection.query(
#         query_embeddings=[qe.tolist() for qe in query_embeddings],
#         n_results=final_k * 10,
#         include=["documents", "metadatas", "embeddings"]
#     )

#     authorized = []

#     for docs, metas, embs, ids in zip(
#         ann["documents"], ann["metadatas"], ann["embeddings"], ann["ids"]
#     ):
#         for d, m, e, cid in zip(docs, metas, embs, ids):
#             if is_authorized(user_role, m):
#                 authorized.append({
#                     "chunk_id": cid,
#                     "document": d,          # ✅ chunk text added
#                     "metadata": m,
#                     "embedding": np.array(e)
#               })


#     aggregated = {}
#     MIN_SCORE = 0.3

#     for q_emb in query_embeddings:
#         for item in authorized:
#             score = cosine_similarity(q_emb, item["embedding"])
#             cid = item["chunk_id"]

#             if score < MIN_SCORE:
#                 continue

#             if cid not in aggregated or score > aggregated[cid][0]:
#                 aggregated[cid] = (score, item)

#     final_results = deduplicate_results(list(aggregated.values()))[:final_k]

#     return {
#         "results": final_results,
#         "query_variants": query_variants,
#         "authorized_count": len(authorized)
#     }

# # =======================================================
# # 10. CLI Output (FORMAT ONLY)
# # =======================================================
# def run_query(role, query):
#     canonical = resolve_role(role)
#     effective_roles = get_all_roles(canonical)

#     output = semantic_search(query, role)

#     print("\n================ QUERY SUMMARY ================")
#     print(f"User Role           : {role}")
#     print(f"Resolved Role       : {canonical}")
#     print(f"Effective Roles     : {', '.join(sorted(effective_roles))}")

#     print("\nQuery Variants:")
#     for v in output["query_variants"]:
#         print(f"  - {v}")

#     print(f"\nAuthorized Chunks After RBAC : {output['authorized_count']}")

#     if not output["results"]:
#         print("\n>> No authorized or relevant results found.")
#         print("================================================")
#         return

#     print("\n================ TOP K RESULTS ================")
    
#     for i, (score, res) in enumerate(output["results"], 1):
#         meta = res["metadata"]
#         print(f"{i}. Chunk ID : {res['chunk_id']}")
#         print(f"   Doc ID   : {meta.get('document_id')}")
#         print(f"   Score    : {round(score, 4)}")
#         print("   Chunk Text:")
#         print(f"   {res['document']}")
#         print()

#     print("================================================")

# # =======================================================
# # 11. Entry Point
# # =======================================================
# if __name__ == "__main__":
#     print("\nCompany Internal Chatbot (RBAC)")
#     user_role = input("Enter your role: ").strip()

#     while True:
#         q = input("\nAsk your question: ").strip()
#         if q.lower() in {"exit", "quit"}:
#             break
#         run_query(user_role, q)

# import os
# import json
# import re
# import numpy as np
# import chromadb
# from sentence_transformers import SentenceTransformer
# from typing import Dict, Set, List

# # =======================================================
# # DEBUG MODE
# # =======================================================
# DEBUG = False  # Set False for production

# def debug_print(*args):
#     if DEBUG:
#         print("[DEBUG]", *args)

# # =======================================================
# # 1. Load Sentence Transformer Model
# # =======================================================
# print("Loading SentenceTransformer model...")
# model = SentenceTransformer("all-MiniLM-L6-v2")

# # =======================================================
# # 2. Resolve Paths
# # =======================================================
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# PROJECT_ROOT = os.path.dirname(BASE_DIR)

# RBAC_FILE = os.path.join(PROJECT_ROOT, "RBAC", "rbac.json")
# CHROMA_DB_PATH = os.path.join(PROJECT_ROOT, "chroma_db")

# # =======================================================
# # 3. Load RBAC Configuration
# # =======================================================
# with open(RBAC_FILE, "r", encoding="utf-8") as f:
#     RBAC_RAW = json.load(f)

# ROLES = RBAC_RAW["roles"]
# ROLE_ALIASES = RBAC_RAW["role_aliases"]

# # ✅ FIX: normalize BOTH key and value
# ROLE_ALIASES_NORM = {
#     k.lower().strip(): v.lower().strip()
#     for k, v in ROLE_ALIASES.items()
# }

# # =======================================================
# # 4. Connect to Chroma DB
# # =======================================================
# client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
# collection = client.get_collection(name="company_chunks")

# # =======================================================
# # 5. Query Normalization
# # =======================================================
# def rewrite_query(query: str) -> str:
#     q = query.lower().strip()
#     q = re.sub(r"[^\w\s]", "", q)

#     abbreviations = {
#         "hr": "human resources",
#         "eng": "engineering",
#         "qa": "quality assurance",
#     }

#     tokens = q.split()
#     expanded = [abbreviations.get(t, t) for t in tokens]

#     stopwords = {
#         "what", "is", "the", "a", "an", "how",
#         "does", "do", "can", "please",
#         "explain", "tell", "me", "about"
#     }

#     return " ".join(t for t in expanded if t not in stopwords)

# # =======================================================
# # 5A. Query Variant Generation
# # =======================================================
# def generate_query_variants(original_query: str) -> List[str]:
#     base = rewrite_query(original_query)
#     variants = {base}

#     substitutions = {
#         "policy": ["rules", "guidelines", "procedure"],
#         "leave": ["time off", "absence"],
#         "handbook": ["manual", "documentation"],
#         "salary": ["pay", "compensation"],
#         "review": ["evaluation", "assessment"]
#     }

#     for word, repls in substitutions.items():
#         if word in base:
#             for r in repls:
#                 variants.add(base.replace(word, r))

#     return list(variants)

# # =======================================================
# # 6. RBAC CORE LOGIC
# # =======================================================
# def resolve_role(user_role: str) -> str:
#     key = user_role.lower().strip()
#     return ROLE_ALIASES_NORM.get(key, key.replace(" ", "_"))

# # ✅ FIX: recursion-safe inheritance resolution
# def get_all_roles(role: str, visited=None) -> Set[str]:
#     if visited is None:
#         visited = set()

#     if role in visited:
#         return set()

#     visited.add(role)

#     roles = {role}
#     for parent in ROLES.get(role, {}).get("inherits", []):
#         roles |= get_all_roles(parent, visited)

#     return roles

# def get_all_permissions(role: str) -> Set[str]:
#     perms = set()
#     for r in get_all_roles(role):
#         perms |= set(ROLES.get(r, {}).get("permissions", []))
#     return perms

# # =======================================================
# # 7. CLASSIFICATION & CLEARANCE
# # =======================================================
# CLASSIFICATION_LEVELS = {
#     "public": 0,
#     "internal": 1,
#     "confidential": 2,
#     "restricted": 3
# }

# ROLE_CLEARANCE = {
#     "intern": 1,
#     "employee": 1,

#     "engineering_employee": 1,
#     "finance_employee": 1,
#     "marketing_employee": 1,
#     "hr_employee": 1,

#     "engineering_manager": 2,
#     "finance_manager": 2,
#     "marketing_manager": 2,
#     "hr_manager": 2,

#     "c_level": 3,
#     "security_officer": 3,
#     "admin": 3
# }

# # ✅ FIX: robust normalization
# def normalize_roles(roles):
#     if not roles:
#         return set()
#     if isinstance(roles, str):
#         return {roles.lower().strip()}
#     return {r.lower().strip() for r in roles}

# # =======================================================
# # 8. FINAL AUTHORIZATION LOGIC
# # =======================================================
# def is_authorized(user_role: str, metadata: Dict) -> bool:
#     canonical_role = resolve_role(user_role)

#     # -----------------------------
#     # ADMIN OVERRIDE
#     # -----------------------------
#     if canonical_role == "admin":
#         return True

#     # -----------------------------
#     # 1. Department-level RBAC
#     # -----------------------------
#     permissions = get_all_permissions(canonical_role)

#     dept = metadata.get("department", "").lower()
#     dept_map = {
#         "human resources": "hr",
#         "hr": "hr",
#         "engineering": "engineering",
#         "finance": "finance",
#         "marketing": "marketing",
#         "general": "general"
#     }

#     normalized_dept = dept_map.get(dept, dept)

#     if not (
#         f"read:{normalized_dept}" in permissions or
#         "read:*" in permissions or
#         "*" in permissions
#     ):
#         return False

#     # -----------------------------
#     # 2. METADATA permitted_roles
#     # -----------------------------
#     metadata_roles = normalize_roles(
#         metadata.get("permitted_roles", [])
#     )

#     effective_roles = normalize_roles(
#         get_all_roles(canonical_role)
#     )

#     if metadata_roles and not (metadata_roles & effective_roles):
#         return False

#     # -----------------------------
#     # 3. Classification clearance
#     # -----------------------------
#     classification = metadata.get("classification", "public").lower()

#     user_clearance = ROLE_CLEARANCE.get(canonical_role, 0)
#     doc_level = CLASSIFICATION_LEVELS.get(classification, 0)

#     if user_clearance < doc_level:
#         return False

#     return True

# # =======================================================
# # 9. Similarity
# # =======================================================
# def cosine_similarity(a, b) -> float:
#     return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

# # =======================================================
# # 10. Deduplication
# # =======================================================
# def deduplicate_results(results, max_chunks_per_doc=2):
#     by_chunk = {}
#     for score, res in results:
#         cid = res["chunk_id"]
#         if cid not in by_chunk or score > by_chunk[cid][0]:
#             by_chunk[cid] = (score, res)

#     final, doc_counter = [], {}
#     for score, res in sorted(by_chunk.values(), key=lambda x: x[0], reverse=True):
#         doc_id = res["metadata"].get("document_id", "UNKNOWN")
#         doc_counter.setdefault(doc_id, 0)
#         if doc_counter[doc_id] < max_chunks_per_doc:
#             final.append((score, res))
#             doc_counter[doc_id] += 1
#     return final

# # =======================================================
# # 11. SEMANTIC SEARCH (FASTAPI USE)
# # =======================================================
# def semantic_search(query: str, user_role: str, final_k=3):
#     query_variants = generate_query_variants(query)
#     query_embeddings = model.encode(query_variants)

#     ann = collection.query(
#         query_embeddings=[qe.tolist() for qe in query_embeddings],
#         n_results=final_k * 10,
#         include=["documents", "metadatas", "embeddings"]
#     )

#     authorized = []

#     for docs, metas, embs, ids in zip(
#         ann["documents"], ann["metadatas"], ann["embeddings"], ann["ids"]
#     ):
#         for d, m, e, cid in zip(docs, metas, embs, ids):
#             if is_authorized(user_role, m):
#                 authorized.append({
#                     "chunk_id": cid,
#                     "document": d,
#                     "metadata": m,
#                     "embedding": np.array(e)
#                 })

#     aggregated = {}
#     MIN_SCORE = 0.3

#     for q_emb in query_embeddings:
#         for item in authorized:
#             score = cosine_similarity(q_emb, item["embedding"])
#             cid = item["chunk_id"]

#             if score < MIN_SCORE:
#                 continue

#             if cid not in aggregated or score > aggregated[cid][0]:
#                 aggregated[cid] = (score, item)

#     final_results = deduplicate_results(
#         list(aggregated.values())
#     )[:final_k]

#     return {
#         "results": final_results,
#         "query_variants": query_variants,
#         "authorized_count": len(authorized)
#     }

# import os
# import json
# import re
# import numpy as np
# import chromadb
# from sentence_transformers import SentenceTransformer
# from typing import Dict, Set, List

# # =======================================================
# # DEBUG MODE
# # =======================================================
# DEBUG = False  # Set False for production

# def debug_print(*args):
#     if DEBUG:
#         print("[DEBUG]", *args)

# # =======================================================
# # 1. Load Sentence Transformer Model
# # =======================================================
# print("Loading SentenceTransformer model...")
# model = SentenceTransformer("all-MiniLM-L6-v2")

# # =======================================================
# # 2. Resolve Paths
# # =======================================================
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# PROJECT_ROOT = os.path.dirname(BASE_DIR)

# RBAC_FILE = os.path.join(PROJECT_ROOT, "RBAC", "rbac.json")
# CHROMA_DB_PATH = os.path.join(PROJECT_ROOT, "chroma_db")

# # =======================================================
# # 3. Load RBAC Configuration
# # =======================================================
# with open(RBAC_FILE, "r", encoding="utf-8") as f:
#     RBAC_RAW = json.load(f)

# ROLES = RBAC_RAW["roles"]
# ROLE_ALIASES = RBAC_RAW["role_aliases"]

# ROLE_ALIASES_NORM = {
#     k.lower().strip(): v.lower().strip()
#     for k, v in ROLE_ALIASES.items()
# }

# # =======================================================
# # 🔧 FIX 1: PERMITTED ROLE → CANONICAL ROLE MAPPING
# # =======================================================
# PERMITTED_ROLE_ALIASES = {
#     "intern": "intern",
#     "employees": "employee",
#     "employee": "employee",
#     "department heads": "manager",

#     "backend developer": "engineering_employee",
#     "frontend developer": "engineering_employee",
#     "engineering lead": "engineering_manager",

#     "c-level executive": "c_level",
#     "c level executive": "c_level",
#     "c_level": "c_level"
# }

# # =======================================================
# # 4. Connect to Chroma DB
# # =======================================================
# client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
# collection = client.get_collection(name="company_chunks")

# # =======================================================
# # 5. Query Normalization
# # =======================================================
# def rewrite_query(query: str) -> str:
#     q = query.lower().strip()
#     q = re.sub(r"[^\w\s]", "", q)

#     abbreviations = {
#         "hr": "human resources",
#         "eng": "engineering",
#         "qa": "quality assurance",
#     }

#     tokens = q.split()
#     expanded = [abbreviations.get(t, t) for t in tokens]

#     stopwords = {
#         "what", "is", "the", "a", "an", "how",
#         "does", "do", "can", "please",
#         "explain", "tell", "me", "about"
#     }

#     return " ".join(t for t in expanded if t not in stopwords)

# # =======================================================
# # 5A. Query Variant Generation
# # =======================================================
# def generate_query_variants(original_query: str) -> List[str]:
#     base = rewrite_query(original_query)
#     variants = {base}

#     substitutions = {
#         "policy": ["rules", "guidelines", "procedure"],
#         "leave": ["time off", "absence"],
#         "handbook": ["manual", "documentation"],
#         "salary": ["pay", "compensation"],
#         "review": ["evaluation", "assessment"]
#     }

#     for word, repls in substitutions.items():
#         if word in base:
#             for r in repls:
#                 variants.add(base.replace(word, r))

#     return list(variants)

# # =======================================================
# # 6. RBAC CORE LOGIC
# # =======================================================
# def resolve_role(user_role: str) -> str:
#     key = user_role.lower().strip()
#     return ROLE_ALIASES_NORM.get(key, key.replace(" ", "_"))

# def get_all_roles(role: str, visited=None) -> Set[str]:
#     if visited is None:
#         visited = set()

#     if role in visited:
#         return set()

#     visited.add(role)

#     roles = {role}
#     for parent in ROLES.get(role, {}).get("inherits", []):
#         roles |= get_all_roles(parent, visited)

#     return roles

# def get_all_permissions(role: str) -> Set[str]:
#     perms = set()
#     for r in get_all_roles(role):
#         perms |= set(ROLES.get(r, {}).get("permissions", []))
#     return perms

# # =======================================================
# # 🔧 FIX 2: NORMALIZE METADATA ROLES CORRECTLY
# # =======================================================
# def normalize_roles(roles):
#     if not roles:
#         return set()

#     if isinstance(roles, str):
#         roles = [roles]

#     normalized = set()
#     for r in roles:
#         key = r.lower().strip()
#         normalized.add(PERMITTED_ROLE_ALIASES.get(key, key))
#     return normalized

# # =======================================================
# # 🔧 FIX 3: TEMPORARY CLASSIFICATION TOGGLE
# # =======================================================
# ENABLE_CLASSIFICATION_RBAC = False

# CLASSIFICATION_LEVELS = {
#     "public": 0,
#     "internal": 1,
#     "confidential": 2,
#     "restricted": 3
# }

# ROLE_CLEARANCE = {
#     "intern": 1,
#     "employee": 1,
#     "engineering_employee": 1,
#     "finance_employee": 1,
#     "marketing_employee": 1,
#     "hr_employee": 1,
#     "engineering_manager": 2,
#     "finance_manager": 2,
#     "marketing_manager": 2,
#     "hr_manager": 2,
#     "c_level": 3,
#     "security_officer": 3,
#     "admin": 3
# }

# # =======================================================
# # 8. FINAL AUTHORIZATION LOGIC
# # =======================================================
# def is_authorized(user_role: str, metadata: Dict) -> bool:
#     canonical_role = resolve_role(user_role)

#     if canonical_role == "admin":
#         return True

#     permissions = get_all_permissions(canonical_role)

#     dept = metadata.get("department", "").lower()
#     dept_map = {
#         "human resources": "hr",
#         "hr": "hr",
#         "engineering": "engineering",
#         "finance": "finance",
#         "marketing": "marketing",
#         "general": "general"
#     }

#     normalized_dept = dept_map.get(dept, dept)

#     if not (
#         f"read:{normalized_dept}" in permissions or
#         "read:*" in permissions or
#         "*" in permissions
#     ):
#         return False

#     metadata_roles = normalize_roles(metadata.get("permitted_roles", []))
#     effective_roles = normalize_roles(get_all_roles(canonical_role))

#     if metadata_roles and not (metadata_roles & effective_roles):
#         return False

#     # 🔧 FIX: classification check disabled for now
#     if ENABLE_CLASSIFICATION_RBAC:
#         classification = metadata.get("classification", "public").lower()
#         if ROLE_CLEARANCE.get(canonical_role, 0) < CLASSIFICATION_LEVELS.get(classification, 0):
#             return False

#     return True

# # =======================================================
# # 9. Similarity
# # =======================================================
# def cosine_similarity(a, b) -> float:
#     return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

# # =======================================================
# # 10. Deduplication
# # =======================================================
# def deduplicate_results(results, max_chunks_per_doc=2):
#     by_chunk = {}
#     for score, res in results:
#         cid = res["chunk_id"]
#         if cid not in by_chunk or score > by_chunk[cid][0]:
#             by_chunk[cid] = (score, res)

#     final, doc_counter = [], {}
#     for score, res in sorted(by_chunk.values(), key=lambda x: x[0], reverse=True):
#         doc_id = res["metadata"].get("document_id", "UNKNOWN")
#         doc_counter.setdefault(doc_id, 0)
#         if doc_counter[doc_id] < max_chunks_per_doc:
#             final.append((score, res))
#             doc_counter[doc_id] += 1
#     return final

# # =======================================================
# # 11. SEMANTIC SEARCH
# # =======================================================
# def semantic_search(query: str, user_role: str, final_k=3):
#     query_variants = generate_query_variants(query)
#     query_embeddings = model.encode(query_variants)

#     ann = collection.query(
#         query_embeddings=[qe.tolist() for qe in query_embeddings],
#         n_results=final_k * 10,
#         include=["documents", "metadatas", "embeddings"]
#     )

#     authorized = []

#     for docs, metas, embs, ids in zip(
#         ann["documents"], ann["metadatas"], ann["embeddings"], ann["ids"]
#     ):
#         for d, m, e, cid in zip(docs, metas, embs, ids):
#             if is_authorized(user_role, m):
#                 authorized.append({
#                     "chunk_id": cid,
#                     "document": d,
#                     "metadata": m,
#                     "embedding": np.array(e)
#                 })

#     aggregated = {}
#     MIN_SCORE = 0.3

#     for q_emb in query_embeddings:
#         for item in authorized:
#             score = cosine_similarity(q_emb, item["embedding"])
#             cid = item["chunk_id"]
#             if score >= MIN_SCORE and (cid not in aggregated or score > aggregated[cid][0]):
#                 aggregated[cid] = (score, item)

#     final_results = deduplicate_results(list(aggregated.values()))[:final_k]

#     return {
#         "results": final_results,
#         "query_variants": query_variants,
#         "authorized_count": len(authorized)
#     }


# import os
# import json
# import re
# import numpy as np
# import chromadb
# from sentence_transformers import SentenceTransformer
# from typing import Dict, Set, List

# # =======================================================
# # DEBUG MODE
# # =======================================================
# DEBUG = False  # Set True to see role normalization logs

# def debug_print(*args):
#     if DEBUG:
#         print("[DEBUG]", *args)

# # =======================================================
# # 1. Load Sentence Transformer Model
# # =======================================================
# print("Loading SentenceTransformer model...")
# model = SentenceTransformer("all-MiniLM-L6-v2")

# # =======================================================
# # 2. Resolve Paths
# # =======================================================
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# PROJECT_ROOT = os.path.dirname(BASE_DIR)

# RBAC_FILE = os.path.join(PROJECT_ROOT, "RBAC", "rbac.json")
# CHROMA_DB_PATH = os.path.join(PROJECT_ROOT, "chroma_db")

# # =======================================================
# # 3. Load RBAC Configuration
# # =======================================================
# with open(RBAC_FILE, "r", encoding="utf-8") as f:
#     RBAC_RAW = json.load(f)

# ROLES = RBAC_RAW["roles"]
# ROLE_ALIASES = RBAC_RAW["role_aliases"]

# ROLE_ALIASES_NORM = {
#     k.lower().strip(): v.lower().strip()
#     for k, v in ROLE_ALIASES.items()
# }

# # =======================================================
# # 🔥 METADATA ROLE NORMALIZATION (Aligned with rbac.json)
# # =======================================================
# METADATA_ROLE_ALIASES = {
#     "intern": "intern",
#     "employees": "employee",
#     "employee": "employee",

#     "department heads": "manager",
#     "engineering lead": "engineering_manager",
#     "system architect": "engineering_manager",
#     "backend developer": "engineering_employee",
#     "frontend developer": "engineering_employee",
#     "devops engineer": "engineering_employee",

#     "finance manager": "finance_manager",
#     "accounts team": "finance_employee",
#     "risk analyst": "finance_employee",
#     "auditor": "security_officer",

#     "marketing manager": "marketing_manager",
#     "seo team": "marketing_employee",
#     "content strategist": "marketing_employee",
#     "growth lead": "marketing_manager",

#     "hr manager": "hr_manager",
#     "talent acquisition": "hr_employee",
#     "payroll team": "hr_employee",

#     "security team": "security_officer",

#     "cto": "c_level",
#     "cfo": "c_level",
#     "cmo": "c_level",
#     "c-level executive": "c_level"
# }

# # =======================================================
# # 4. Connect to Chroma DB
# # =======================================================
# client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
# collection = client.get_collection(name="company_chunks")

# # =======================================================
# # 5. Query Normalization
# # =======================================================
# def rewrite_query(query: str) -> str:
#     q = query.lower().strip()
#     q = re.sub(r"[^\w\s]", "", q)

#     abbreviations = {
#         "hr": "human resources",
#         "eng": "engineering",
#         "qa": "quality assurance",
#     }

#     tokens = q.split()
#     expanded = [abbreviations.get(t, t) for t in tokens]

#     stopwords = {
#         "what", "is", "the", "a", "an", "how",
#         "does", "do", "can", "please",
#         "explain", "tell", "me", "about"
#     }

#     return " ".join(t for t in expanded if t not in stopwords)

# # =======================================================
# # 5A. Query Variant Generation
# # =======================================================
# def generate_query_variants(original_query: str) -> List[str]:
#     base = rewrite_query(original_query)
#     variants = {base}

#     substitutions = {
#         "policy": ["rules", "guidelines", "procedure"],
#         "leave": ["time off", "absence"],
#         "handbook": ["manual", "documentation"],
#         "salary": ["pay", "compensation"],
#         "review": ["evaluation", "assessment"]
#     }

#     for word, repls in substitutions.items():
#         if word in base:
#             for r in repls:
#                 variants.add(base.replace(word, r))

#     return list(variants)

# # =======================================================
# # 6. RBAC CORE LOGIC
# # =======================================================
# def resolve_role(user_role: str) -> str:
#     key = user_role.lower().strip()
#     return ROLE_ALIASES_NORM.get(key, key.replace(" ", "_"))

# def get_all_roles(role: str, visited=None) -> Set[str]:
#     if visited is None:
#         visited = set()

#     if role in visited:
#         return set()

#     visited.add(role)

#     roles = {role}
#     for parent in ROLES.get(role, {}).get("inherits", []):
#         roles |= get_all_roles(parent, visited)

#     return roles

# def get_all_permissions(role: str) -> Set[str]:
#     perms = set()
#     for r in get_all_roles(role):
#         perms |= set(ROLES.get(r, {}).get("permissions", []))
#     return perms

# # =======================================================
# # 🔧 FIX: NORMALIZE METADATA ROLES USING COMPLETE ALIASES
# # =======================================================
# def normalize_roles(roles):
#     if not roles:
#         return set()

#     if isinstance(roles, str):
#         roles = [roles]

#     normalized = set()
#     for r in roles:
#         key = r.lower().strip()
#         normalized.add(METADATA_ROLE_ALIASES.get(key, key))
#     return normalized

# # =======================================================
# # 7. CLASSIFICATION (Optional)
# # =======================================================
# ENABLE_CLASSIFICATION_RBAC = False

# CLASSIFICATION_LEVELS = {
#     "public": 0,
#     "internal": 1,
#     "confidential": 2,
#     "restricted": 3
# }

# ROLE_CLEARANCE = {
#     "intern": 1,
#     "employee": 1,
#     "engineering_employee": 1,
#     "finance_employee": 1,
#     "marketing_employee": 1,
#     "hr_employee": 1,
#     "engineering_manager": 2,
#     "finance_manager": 2,
#     "marketing_manager": 2,
#     "hr_manager": 2,
#     "c_level": 3,
#     "security_officer": 3,
#     "admin": 3
# }

# # =======================================================
# # 8. FINAL AUTHORIZATION LOGIC
# # =======================================================
# def is_authorized(user_role: str, metadata: Dict) -> bool:
#     canonical_role = resolve_role(user_role)

#     if canonical_role == "admin":
#         return True

#     permissions = get_all_permissions(canonical_role)

#     dept = metadata.get("department", "").lower()
#     dept_map = {
#         "human resources": "hr",
#         "hr": "hr",
#         "engineering": "engineering",
#         "finance": "finance",
#         "marketing": "marketing",
#         "general": "general"
#     }

#     normalized_dept = dept_map.get(dept, dept)

#     if not (
#         f"read:{normalized_dept}" in permissions or
#         "read:*" in permissions or
#         "*" in permissions
#     ):
#         return False

#     metadata_roles = normalize_roles(metadata.get("permitted_roles", []))
#     effective_roles = normalize_roles(get_all_roles(canonical_role))

#     debug_print("metadata_roles:", metadata_roles)
#     debug_print("effective_roles:", effective_roles)

#     if metadata_roles and not (metadata_roles & effective_roles):
#         return False

#     # Classification check disabled for now
#     if ENABLE_CLASSIFICATION_RBAC:
#         classification = metadata.get("classification", "public").lower()
#         if ROLE_CLEARANCE.get(canonical_role, 0) < CLASSIFICATION_LEVELS.get(classification, 0):
#             return False

#     return True

# # =======================================================
# # 9. Similarity
# # =======================================================
# def cosine_similarity(a, b) -> float:
#     return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

# # =======================================================
# # 10. Deduplication
# # =======================================================
# def deduplicate_results(results, max_chunks_per_doc=2):
#     by_chunk = {}
#     for score, res in results:
#         cid = res["chunk_id"]
#         if cid not in by_chunk or score > by_chunk[cid][0]:
#             by_chunk[cid] = (score, res)

#     final, doc_counter = [], {}
#     for score, res in sorted(by_chunk.values(), key=lambda x: x[0], reverse=True):
#         doc_id = res["metadata"].get("document_id", "UNKNOWN")
#         doc_counter.setdefault(doc_id, 0)
#         if doc_counter[doc_id] < max_chunks_per_doc:
#             final.append((score, res))
#             doc_counter[doc_id] += 1
#     return final

# # =======================================================
# # 11. SEMANTIC SEARCH
# # =======================================================
# def semantic_search(query: str, user_role: str, final_k=3):
#     query_variants = generate_query_variants(query)
#     query_embeddings = model.encode(query_variants)

#     ann = collection.query(
#         query_embeddings=[qe.tolist() for qe in query_embeddings],
#         n_results=final_k * 10,
#         include=["documents", "metadatas", "embeddings"]
#     )

#     authorized = []

#     for docs, metas, embs, ids in zip(
#         ann["documents"], ann["metadatas"], ann["embeddings"], ann["ids"]
#     ):
#         for d, m, e, cid in zip(docs, metas, embs, ids):
#             if is_authorized(user_role, m):
#                 authorized.append({
#                     "chunk_id": cid,
#                     "document": d,
#                     "metadata": m,
#                     "embedding": np.array(e)
#                 })

#     aggregated = {}
#     MIN_SCORE = 0.3

#     for q_emb in query_embeddings:
#         for item in authorized:
#             score = cosine_similarity(q_emb, item["embedding"])
#             cid = item["chunk_id"]
#             if score >= MIN_SCORE and (cid not in aggregated or score > aggregated[cid][0]):
#                 aggregated[cid] = (score, item)

#     final_results = deduplicate_results(list(aggregated.values()))[:final_k]

#     return {
#         "results": final_results,
#         "query_variants": query_variants,
#         "authorized_count": len(authorized)
#     }


# import os
# import json
# import re
# import numpy as np
# import chromadb
# from sentence_transformers import SentenceTransformer
# from typing import Dict, Set, List

# # =======================================================
# # DEBUG MODE
# # =======================================================
# DEBUG = True  # Set False for production

# def debug_print(*args):
#     if DEBUG:
#         print("[DEBUG]", *args)

# # =======================================================
# # 1. Load Sentence Transformer Model
# # =======================================================
# print("Loading SentenceTransformer model...")
# model = SentenceTransformer("all-MiniLM-L6-v2")

# # =======================================================
# # 2. Resolve Paths
# # =======================================================
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# PROJECT_ROOT = os.path.dirname(BASE_DIR)

# RBAC_FILE = os.path.join(PROJECT_ROOT, "RBAC", "rbac.json")
# CHROMA_DB_PATH = os.path.join(PROJECT_ROOT, "chroma_db")

# # =======================================================
# # 3. Load RBAC Configuration
# # =======================================================
# with open(RBAC_FILE, "r", encoding="utf-8") as f:
#     RBAC_RAW = json.load(f)

# ROLES = RBAC_RAW["roles"]
# ROLE_ALIASES = RBAC_RAW["role_aliases"]

# ROLE_ALIASES_NORM = {
#     k.lower().strip(): v.lower().strip()
#     for k, v in ROLE_ALIASES.items()
# }

# # =======================================================
# # 🔥 METADATA ROLE NORMALIZATION (Full Alignment)
# # =======================================================
# METADATA_ROLE_ALIASES = {
#     "intern": "intern",
#     "employees": "employee",
#     "employee": "employee",

#     "department heads": "manager",
#     "engineering lead": "engineering_manager",
#     "system architect": "engineering_manager",
#     "backend developer": "engineering_employee",
#     "frontend developer": "engineering_employee",
#     "devops engineer": "engineering_employee",

#     "finance manager": "finance_manager",
#     "accounts team": "finance_employee",
#     "risk analyst": "finance_employee",
#     "auditor": "security_officer",

#     "marketing manager": "marketing_manager",
#     "seo team": "marketing_employee",
#     "content strategist": "marketing_employee",
#     "growth lead": "marketing_manager",

#     "hr manager": "hr_manager",
#     "talent acquisition": "hr_employee",
#     "payroll team": "hr_employee",

#     "security team": "security_officer",

#     "cto": "c_level",
#     "cfo": "c_level",
#     "cmo": "c_level",
#     "c-level executive": "c_level"
# }

# # =======================================================
# # 4. Connect to Chroma DB
# # =======================================================
# client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
# collection = client.get_collection(name="company_chunks")

# # =======================================================
# # 5. Query Normalization
# # =======================================================
# def rewrite_query(query: str) -> str:
#     q = query.lower().strip()
#     q = re.sub(r"[^\w\s]", "", q)

#     abbreviations = {
#         "hr": "human resources",
#         "eng": "engineering",
#         "qa": "quality assurance",
#     }

#     tokens = q.split()
#     expanded = [abbreviations.get(t, t) for t in tokens]

#     stopwords = {
#         "what", "is", "the", "a", "an", "how",
#         "does", "do", "can", "please",
#         "explain", "tell", "me", "about"
#     }

#     return " ".join(t for t in expanded if t not in stopwords)

# # =======================================================
# # 5A. Query Variant Generation
# # =======================================================
# def generate_query_variants(original_query: str) -> List[str]:
#     base = rewrite_query(original_query)
#     variants = {base}

#     substitutions = {
#         "policy": ["rules", "guidelines", "procedure"],
#         "leave": ["time off", "absence"],
#         "handbook": ["manual", "documentation"],
#         "salary": ["pay", "compensation"],
#         "review": ["evaluation", "assessment"]
#     }

#     for word, repls in substitutions.items():
#         if word in base:
#             for r in repls:
#                 variants.add(base.replace(word, r))

#     return list(variants)

# # =======================================================
# # 6. RBAC CORE LOGIC
# # =======================================================
# def resolve_role(user_role: str) -> str:
#     key = user_role.lower().strip()
#     return ROLE_ALIASES_NORM.get(key, key.replace(" ", "_"))

# def get_all_roles(role: str, visited=None) -> Set[str]:
#     if visited is None:
#         visited = set()

#     if role in visited:
#         return set()

#     visited.add(role)

#     roles = {role}
#     for parent in ROLES.get(role, {}).get("inherits", []):
#         roles |= get_all_roles(parent, visited)

#     return roles

# def get_all_permissions(role: str) -> Set[str]:
#     perms = set()
#     for r in get_all_roles(role):
#         perms |= set(ROLES.get(r, {}).get("permissions", []))
#     return perms

# # =======================================================
# # 🔧 FIX: NORMALIZE METADATA ROLES + DEPARTMENT CASE
# # =======================================================
# def normalize_roles(roles):
#     if not roles:
#         return set()

#     if isinstance(roles, str):
#         roles = [roles]

#     normalized = set()
#     for r in roles:
#         key = r.lower().strip()
#         normalized.add(METADATA_ROLE_ALIASES.get(key, key))
#     return normalized

# def normalize_department(dept: str) -> str:
#     return dept.lower().strip() if dept else "general"

# # =======================================================
# # 7. CLASSIFICATION (Optional)
# # =======================================================
# ENABLE_CLASSIFICATION_RBAC = False

# CLASSIFICATION_LEVELS = {
#     "public": 0,
#     "internal": 1,
#     "confidential": 2,
#     "restricted": 3
# }

# ROLE_CLEARANCE = {
#     "intern": 1,
#     "employee": 1,
#     "engineering_employee": 1,
#     "finance_employee": 1,
#     "marketing_employee": 1,
#     "hr_employee": 1,
#     "engineering_manager": 2,
#     "finance_manager": 2,
#     "marketing_manager": 2,
#     "hr_manager": 2,
#     "c_level": 3,
#     "security_officer": 3,
#     "admin": 3
# }

# # =======================================================
# # 8. FINAL AUTHORIZATION LOGIC
# # =======================================================
# def is_authorized(user_role: str, metadata: Dict) -> bool:
#     canonical_role = resolve_role(user_role)

#     if canonical_role == "admin":
#         return True

#     permissions = get_all_permissions(canonical_role)

#     dept = normalize_department(metadata.get("department", "general"))

#     metadata_roles = normalize_roles(metadata.get("permitted_roles", []))
#     effective_roles = normalize_roles(get_all_roles(canonical_role))

#     debug_print("User role:", user_role, "Canonical:", canonical_role)
#     debug_print("Effective roles:", effective_roles)
#     debug_print("Metadata roles:", metadata_roles)
#     debug_print("Permissions:", permissions)
#     debug_print("Normalized dept:", dept)

#     if metadata_roles and not (metadata_roles & effective_roles):
#         return False

#     if not (
#         f"read:{dept}" in permissions or
#         "read:*" in permissions or
#         "*" in permissions
#     ):
#         return False

#     # Classification check disabled
#     if ENABLE_CLASSIFICATION_RBAC:
#         classification = metadata.get("classification", "public").lower()
#         if ROLE_CLEARANCE.get(canonical_role, 0) < CLASSIFICATION_LEVELS.get(classification, 0):
#             return False

#     return True

# # =======================================================
# # 9. Similarity
# # =======================================================
# def cosine_similarity(a, b) -> float:
#     return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

# # =======================================================
# # 10. Deduplication
# # =======================================================
# def deduplicate_results(results, max_chunks_per_doc=2):
#     by_chunk = {}
#     for score, res in results:
#         cid = res["chunk_id"]
#         if cid not in by_chunk or score > by_chunk[cid][0]:
#             by_chunk[cid] = (score, res)

#     final, doc_counter = [], {}
#     for score, res in sorted(by_chunk.values(), key=lambda x: x[0], reverse=True):
#         doc_id = res["metadata"].get("document_id", "UNKNOWN")
#         doc_counter.setdefault(doc_id, 0)
#         if doc_counter[doc_id] < max_chunks_per_doc:
#             final.append((score, res))
#             doc_counter[doc_id] += 1
#     return final

# # =======================================================
# # 11. SEMANTIC SEARCH
# # =======================================================
# def semantic_search(query: str, user_role: str, final_k=3):
#     query_variants = generate_query_variants(query)
#     query_embeddings = model.encode(query_variants)

#     ann = collection.query(
#         query_embeddings=[qe.tolist() for qe in query_embeddings],
#         n_results=final_k * 10,
#         include=["documents", "metadatas", "embeddings"]  # "ids" removed
#     )

#     authorized = []

#     for docs, metas, embs in zip(
#         ann["documents"], ann["metadatas"], ann["embeddings"]
#     ):
#         for d, m, e in zip(docs, metas, embs):
#             if is_authorized(user_role, m):
#                 authorized.append({
#                     "chunk_id": m.get("chunk_id", "UNKNOWN"),  # from metadata
#                     "document": d,
#                     "metadata": m,
#                     "embedding": np.array(e)
#                 })

#     aggregated = {}
#     MIN_SCORE = 0.3

#     for q_emb in query_embeddings:
#         for item in authorized:
#             score = cosine_similarity(q_emb, item["embedding"])
#             cid = item["chunk_id"]
#             if score >= MIN_SCORE and (cid not in aggregated or score > aggregated[cid][0]):
#                 aggregated[cid] = (score, item)

#     final_results = deduplicate_results(list(aggregated.values()))[:final_k]

#     return {
#         "results": final_results,
#         "query_variants": query_variants,
#         "authorized_count": len(authorized)
#     }

# # =======================================================
# # MAIN BLOCK FOR TESTING
# # =======================================================
# if __name__ == "__main__":
#     DEBUG = True

#     # Test users
#     test_users = ["intern", "finance_employee", "c_level"]
#     test_queries = [
#         "Explain employee handbook",
#         "Explain financial reporting process"
#     ]

#     for user in test_users:
#         print(f"\n--- Testing as user: {user} ---")
#         for q in test_queries:
#             print(f"\nQuery: {q}")
#             result = semantic_search(q, user_role=user, final_k=3)
#             print("Authorized chunks:", result["authorized_count"])
#             for r in result["results"]:
#                 print("-", r["metadata"].get("permitted_roles"), "->", r["document"])

