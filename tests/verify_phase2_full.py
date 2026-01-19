# verify_phase2_full.py
import os
import sys

# -------------------------------
# Ensure project root is in sys.path
# -------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from data.database.db import SessionLocal
from sqlalchemy import text

# Import your orchestrator RAG pipeline
from backend.rag.orchestrator import run_rag_pipeline

# -------------------------------
# Start DB session
# -------------------------------
db = SessionLocal()

# -------------------------------
# 1️⃣ Verify tables exist
# -------------------------------
print("Checking database tables...")
tables = db.execute(
    text("SELECT name FROM sqlite_master WHERE type='table';")
).fetchall()
table_names = [t[0] for t in tables]
print("Tables found:", table_names)

# -------------------------------
# 2️⃣ Load citations from DB
# -------------------------------
citations = []
if "citations" in table_names:
    citations = db.execute(
        text("SELECT id, title, file_path FROM citations;")
    ).fetchall()
    if citations:
        print(f"\nFound {len(citations)} citations in DB:")
        for c in citations:
            print(f" - {c[1]} (ID: {c[0]}, Path: {c[2]})")
    else:
        print("❌ No citations found in DB!")
else:
    print("❌ Citations table missing!")

# -------------------------------
# 3️⃣ Verify files/URLs exist (DB)
# -------------------------------
if citations:
    print("\nVerifying linked files/URLs exist (DB citations)...")
    for c in citations:
        file_path = c[2]
        if file_path.startswith("http"):
            try:
                import requests
                r = requests.head(file_path, timeout=3)
                if r.status_code < 400:
                    print(f"✅ {file_path} exists (online)")
                else:
                    print(f"❌ {file_path} not reachable (status {r.status_code})")
            except Exception as e:
                print(f"❌ {file_path} not reachable ({e})")
        else:
            abs_path = os.path.join(PROJECT_ROOT, file_path)
            if os.path.exists(abs_path):
                print(f"✅ {abs_path} exists (local)")
            else:
                print(f"❌ {abs_path} missing (local)")

# -------------------------------
# 4️⃣ Role-based access simulation (DB)
# -------------------------------
if "users" in table_names and "permissions" in table_names:
    print("\nSimulating role-based access from RBAC table (DB)...")

    users = db.execute(
        text("SELECT id, username, role FROM users;")
    ).fetchall()

    for user in users:
        user_id, username, role = user
        print(f"\nUser: {username} (Role: {role})")

        accessible_citation_ids = db.execute(
            text("SELECT citation_id FROM permissions WHERE role = :role"),
            {"role": role}
        ).fetchall()
        accessible_ids = [r[0] for r in accessible_citation_ids]

        user_citations = [c for c in citations if c[0] in accessible_ids]

        if user_citations:
            print(f"Accessible citations ({len(user_citations)}):")
            for c in user_citations:
                print(f" - {c[1]} (ID: {c[0]}, Path: {c[2]})")
        else:
            print("No accessible citations! ❌")
else:
    print("❌ Users or Permissions table missing!")

# -------------------------------
# 5️⃣ Dynamic RAG pipeline verification
# -------------------------------
print("\n--- Verifying dynamic RAG pipeline ---")

# Convert DB users to dict format for RAG
rag_users = []
for u in users:
    _, username, role = u
    rag_users.append({"sub": username, "role": role})

# Test query
TEST_QUERY = "Explain the company leave policy in detail."

for user in rag_users:
    print(f"\nRunning RAG pipeline for user: {user['sub']} (role: {user['role']})")
    result = run_rag_pipeline(user=user, query=TEST_QUERY, top_k=5)

    citations_rag = result.get("citations", [])
    if citations_rag:
        print(f"✅ {len(citations_rag)} citations returned by RAG:")
        for c in citations_rag:
            print(f" - Chunk ID: {c['chunk_id']}, Doc: {c['document_id']}, File: {c['original_file']}, Score: {c['score']}")
            # Optional file check
            file_path = c.get("original_file")
            if file_path:
                abs_path = os.path.join(PROJECT_ROOT, file_path)
                if os.path.exists(abs_path):
                    print(f"   ✅ File exists at {abs_path}")
                else:
                    print(f"   ❌ File missing at {abs_path}")
    else:
        print("❌ No citations returned by RAG pipeline!")

    # Print answer and summaries
    print("\nAnswer:")
    print(result.get("answer", ""))
    print("\nSummaries:")
    for i, s in enumerate(result.get("chunk_summaries", []), 1):
        print(f" {i}. {s[:100]}...")  # first 100 chars

# -------------------------------
# Close DB session
# -------------------------------
db.close()
print("\n✅ Full Phase 2 verification completed!")


