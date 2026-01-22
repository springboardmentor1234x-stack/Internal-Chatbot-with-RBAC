import chromadb
from sentence_transformers import SentenceTransformer

# =====================================================
# CONFIG
# =====================================================

CHROMA_PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "fintech_documents"
TOP_K = 3

# =====================================================
# INPUT (MANUAL FOR PHASE 1)
# =====================================================

user_role = "Marketing"
query = "employee salary"


# =====================================================
# LOAD CHROMADB
# =====================================================

client = chromadb.PersistentClient(
    path=CHROMA_PERSIST_DIR
)

collection = client.get_collection(name=COLLECTION_NAME)

print("✅ ChromaDB loaded successfully")

# =====================================================
# EMBEDDING MODEL
# =====================================================

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
query_embedding = model.encode(query).tolist()

# =====================================================
# RBAC CHECK FUNCTION
# =====================================================

def is_allowed(metadata, role):
    roles_allowed = metadata["roles_allowed"].split("|")
    return role in roles_allowed

# =====================================================
# QUERY CHROMADB
# =====================================================

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=10,  # get more, then RBAC-filter
    include=["documents", "metadatas", "distances"]
)

print("\n🔍 Query :", query)
print("👤 Role  :", user_role)

# =====================================================
# APPLY RBAC FILTER
# =====================================================

authorized_results = []

for doc, meta, dist in zip(
    results["documents"][0],
    results["metadatas"][0],
    results["distances"][0]
):
    if is_allowed(meta, user_role):
        authorized_results.append((doc, meta, dist))

# =====================================================
# DISPLAY RESULTS
# =====================================================

print(f"\n✅ Authorized Results (Top {TOP_K})\n")

if not authorized_results:
    print("❌ No documents allowed for this role")
else:
    for i, (doc, meta, dist) in enumerate(authorized_results[:TOP_K], 1):
        print(f"Result {i}")
        print("Department :", meta["department"])
        print("Roles      :", meta["roles_allowed"])
        print("Source     :", meta["source"])
        print("Distance   :", dist)
        print("Content    :", doc[:300])
        print("-" * 60)
