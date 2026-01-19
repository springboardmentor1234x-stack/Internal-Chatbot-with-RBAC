import chromadb
import os
from collections import Counter, defaultdict

# ================================
# 1. Connect to Chroma
# ================================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHROMA_DB_PATH = os.path.join(PROJECT_ROOT, "chroma_db")

print("🔍 Inspecting Chroma DB at:", CHROMA_DB_PATH)

client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = client.get_collection(name="company_chunks")

# ================================
# 2. Fetch ALL data (metadata only)
# ================================
data = collection.get(
    include=["metadatas", "documents"]
)

metadatas = data["metadatas"]
documents = data["documents"]

total_chunks = len(metadatas)

print("\n================ SUMMARY ================")
print("Total chunks stored :", total_chunks)

# ================================
# 3. Analyze chunk_id duplicates
# ================================
chunk_ids = [m.get("chunk_id") for m in metadatas if m.get("chunk_id")]
chunk_counter = Counter(chunk_ids)

duplicates = {cid: c for cid, c in chunk_counter.items() if c > 1}

print("\n================ DUPLICATE CHECK ================")
print("Unique chunk_ids :", len(chunk_counter))
print("Duplicate chunk_ids :", len(duplicates))

if duplicates:
    print("\n⚠️ Duplicate chunk_ids found:")
    for cid, count in list(duplicates.items())[:10]:
        print(f" - {cid}: {count} times")
else:
    print("✅ No duplicate chunk_ids detected")

# ================================
# 4. Department consistency check
# ================================
departments = [m.get("department") for m in metadatas if m.get("department")]
dept_counter = Counter(departments)

print("\n================ DEPARTMENT DISTRIBUTION ================")
for dept, count in dept_counter.items():
    print(f"{repr(dept):15} -> {count}")

print("\n⚠️ Normalized department view:")
norm_counter = Counter(d.lower().strip() for d in departments)
for dept, count in norm_counter.items():
    print(f"{dept:15} -> {count}")

# ================================
# 5. Document → chunk distribution
# ================================
doc_chunks = defaultdict(int)
for m in metadatas:
    doc_id = m.get("document_id", "UNKNOWN")
    doc_chunks[doc_id] += 1

print("\n================ DOCUMENT DISTRIBUTION ================")
print("Total documents :", len(doc_chunks))

for doc, count in list(doc_chunks.items())[:10]:
    print(f"{doc} -> {count} chunks")

# ================================
# 6. Exact duplicate content check (optional)
# ================================
doc_counter = Counter(documents)
exact_dupes = {d: c for d, c in doc_counter.items() if c > 1}

print("\n================ EXACT TEXT DUPLICATES ================")
print("Exact duplicate texts :", len(exact_dupes))

if exact_dupes:
    for txt, c in list(exact_dupes.items())[:3]:
        print(f"\n🔁 Appears {c} times:\n{txt[:200]}...")
else:
    print("✅ No exact text duplicates")
