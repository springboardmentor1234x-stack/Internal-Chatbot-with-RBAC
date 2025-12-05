from pathlib import Path
from typing import List, Dict

def tokenize_text(text: str) -> List[str]:
    return text.split()

def chunk_by_token_limit(tokens: List[str], max_tokens: int = 350, max_chunks: int = 3) -> List[str]:
    chunks = []

    for i in range(0, min(len(tokens), max_tokens * max_chunks), max_tokens):
        chunk_tokens = tokens[i:i + max_tokens]
        chunk_text = " ".join(chunk_tokens)
        chunks.append(chunk_text)

        if len(chunks) == max_chunks:
            break

    return chunks

def generate_metadata(chunk: str, file_name: str, department: str, role: str, chunk_id: int) -> Dict:
    return {
        "chunk_id": chunk_id,
        "file_name": file_name,
        "department": department,
        "role": role,
        "source_type": "md",
        "token_count": len(chunk.split()),
        "text_preview": chunk[:120] + "..."
    }

def process_document(file_path: str, department: str, role: str):
    text = Path(file_path).read_text(encoding="utf-8")

    tokens = tokenize_text(text)
    chunks = chunk_by_token_limit(tokens, max_tokens=350, max_chunks=3)

    metadata_records = []
    for i, chunk in enumerate(chunks, start=1):
        meta = generate_metadata(
            chunk=chunk,
            file_name=Path(file_path).name,
            department=department,
            role=role,
            chunk_id=i
        )
        metadata_records.append(meta)

    return chunks, metadata_records

if __name__ == "__main__":

    base_path = Path(__file__).parent
    doc = base_path / "quarterly_financial_report.md"

    chunks, metadata = process_document(
        file_path=doc,
        department="finance",
        role="c-level"
    )

    print("\n TOTAL CHUNKS CREATED (LIMITED TO 3):", len(chunks))

    for i, c in enumerate(chunks, start=1):
        print(f"\n--- CHUNK {i} | Tokens: {len(c.split())} ---\n")
        print(c[:600], "...\n") 

    print("\n\n ---- GENERATED METADATA ----\n")
    for m in metadata:
        print(m)
