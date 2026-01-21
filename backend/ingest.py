import os
import pandas as pd
from backend.vector_store import collection, fit_vectorizer, persist_db

DATA_DIR = "data"

ALLOWED_EXTENSIONS = [".md", ".txt", ".csv"]

ROLE_MAP = {
    "finance": ["finance"],
    "marketing": ["marketing"],
    "hr": ["hr"],
    "engineering": ["engineering"],
    "intern": ["general"],
    "admin": ["admin"]
}

def detect_role_from_path(path):
    lower = path.lower()
    for role, keys in ROLE_MAP.items():
        for k in keys:
            if k in lower:
                return role
    return "intern"

def read_file(path):
    try:
        if path.endswith(".csv"):
            df = pd.read_csv(path)
            return df.to_string()
        else:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
    except Exception as e:
        print(f"⚠️ Could not read {path}: {e}")
        return ""

def ingest_docs():
    print("🚀 Ingest script started")

    documents = []
    metadatas = []
    ids = []

    for root, dirs, files in os.walk(DATA_DIR):
        # Skip .git directories
        dirs[:] = [d for d in dirs if d != ".git"]

        for file in files:
            if not any(file.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
                continue

            filepath = os.path.join(root, file)
            text = read_file(filepath)

            if not text or len(text.strip()) < 50:
                print(f"⏭️ Skipped empty/short file: {file}")
                continue

            role = detect_role_from_path(filepath)
            source_name = os.path.relpath(filepath, DATA_DIR)

            print(f"📄 {source_name} → ROLE = {role} | chars={len(text)}")

            documents.append(text)
            metadatas.append({
                "role": role,
                "source": source_name
            })
            ids.append(source_name)

    if not documents:
        print("❌ No valid documents found in data folder.")
        return

    print("🔄 Fitting embedding model...")
    fit_vectorizer(documents)

    print("📥 Indexing into Vector DB...")
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    persist_db()
    print("✅ Dataset fully ingested into Vector DB")

if __name__ == "__main__":
    ingest_docs()
