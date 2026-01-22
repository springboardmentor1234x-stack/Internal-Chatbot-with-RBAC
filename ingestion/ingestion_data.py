import os
import re
import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb

# =========================
# CONFIG
# =========================

BASE_DATA_PATH = "../Fintech-data"
CHROMA_PERSIST_DIR = "../ingestion/chroma_db"
COLLECTION_NAME = "fintech_documents"

ROLE_MAPPING = {
    "finance": ["Finance", "Manager", "Admin"],
    "hr": ["HR", "Manager", "Admin"],
    "engineering": ["Engineering", "Manager", "Admin"],
    "marketing": ["Marketing", "Manager", "Admin"],
    "general": ["Intern", "Employee", "Manager", "Admin"],
}

# =========================
# FILE READERS
# =========================

def read_markdown(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def read_csv(path):
    df = pd.read_csv(path)

    rows = []
    for _, row in df.iterrows():
        sentence = " ".join(
            [f"{col}: {str(row[col])}" for col in df.columns if pd.notna(row[col])]
        )
        if len(sentence.split()) > 5:
            rows.append(sentence)

    return "\n".join(rows)

# =========================
# CLEANING + CHUNKING
# =========================

def clean_text(text: str) -> str:
    text = re.sub(r"#+", "", text)
    text = re.sub(r"-{2,}", "", text)
    text = re.sub(r"\n{2,}", "\n", text)

    lines = []
    for line in text.split("\n"):
        line = line.strip()
        if len(line.split()) > 2:
            lines.append(line)

    return "\n".join(lines)

def section_chunk_text(text, min_words=15, max_words=180):
    text = clean_text(text)
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]

    chunks = []
    current = ""

    for para in paragraphs:
        current += " " + para
        wc = len(current.split())

        if min_words <= wc <= max_words:
            chunks.append(current.strip())
            current = ""
        elif wc > max_words:
            chunks.append(current.strip())
            current = ""

    if len(current.split()) >= min_words:
        chunks.append(current.strip())

    return chunks

# =========================
# INGESTION
# =========================

def ingest_documents():
    chunks = []

    for folder in os.listdir(BASE_DATA_PATH):
        folder_path = os.path.join(BASE_DATA_PATH, folder)
        if not os.path.isdir(folder_path):
            continue

        dept = folder.lower()
        roles_allowed = ROLE_MAPPING.get(dept, [])

        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)

            if file.endswith(".md"):
                content = read_markdown(file_path)
            elif file.endswith(".csv"):
                content = read_csv(file_path)
            else:
                continue  # ✅ skip unsupported files

            for i, chunk in enumerate(section_chunk_text(content)):
                chunks.append({
                    "id": f"{dept}_{file}_{i}",
                    "text": chunk,
                    "department": dept,
                    "roles_allowed": "|".join(roles_allowed),
                    "source": file
                })

    return chunks

# =========================
# STORE IN CHROMA
# =========================

def store_in_chromadb(chunks):
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

    # Reset collection safely
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.get_or_create_collection(COLLECTION_NAME)

    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True).tolist()

    collection.add(
        ids=[c["id"] for c in chunks],
        documents=texts,
        embeddings=embeddings,
        metadatas=[
            {
                "department": c["department"],
                "roles_allowed": c["roles_allowed"],
                "source": c["source"]
            } for c in chunks
        ]
    )

    print(f"✅ Stored {len(chunks)} chunks in ChromaDB")

# =========================
# MAIN
# =========================

if __name__ == "__main__":
    print("🚀 Starting ingestion")
    chunks = ingest_documents()
    store_in_chromadb(chunks)
    print("✅ Ingestion complete")
