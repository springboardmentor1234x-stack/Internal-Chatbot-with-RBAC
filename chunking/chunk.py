import os
import json
from datetime import datetime

INPUT_ROOT = r"C:\Users\91707\OneDrive\Desktop\RBAC-Chatbot\Internal-Chatbot-with-RBAC\datasets\Fintech-data"
OUTPUT_CHUNKS_FILE = "chunks.json"
OUTPUT_METADATA_FILE = "metadata.json"

CHUNK_SIZE = 350
OVERLAP = 50

ALLOWED_EXTS = {".md", ".csv", ".txt"}

ROLE_MAP = {
    "engineering": [
        "Engineering Lead", "Backend Developer", "Frontend Developer",
        "DevOps Engineer", "System Architect", "Security Team", "C-Level Executive"
    ],
    "finance": [
        "Finance Manager", "Accounts Team", "Auditor",
        "Risk Analyst", "CFO", "C-Level Executive"
    ],
    "marketing": [
        "Marketing Manager", "SEO Team", "Content Strategist",
        "Growth Lead", "CMO", "C-Level Executive"
    ],
    "hr": [
        "HR Manager", "Talent Acquisition", "Compliance Officer",
        "Payroll Team", "C-Level Executive"
    ],
    "general": [
        "Employees", "Department Heads", "C-Level Executive"
    ]
}


def normalize_text(text: str) -> str:
    """Collapse whitespace & newlines to single spaces and strip ends."""
    return " ".join(text.split())

def guess_department_from_path(path: str) -> str:
    """Use the nearest folder name under INPUT_ROOT as department (lowercased)."""
    rel = os.path.relpath(path, INPUT_ROOT)
    parts = rel.split(os.sep)
    if parts and parts[0] not in (".", ""):
        return parts[0].lower()
    return "general"

def get_allowed_roles_for_dept(dept: str):
    return ROLE_MAP.get(dept.lower(), ROLE_MAP["general"])

def file_extension_ok(filename: str) -> bool:
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTS

def restore_source_name(file_path: str) -> str:
    """Return a reasonable source document name (filename with original extension)."""
    return os.path.basename(file_path)

def chunk_file_text(text: str, chunk_size: int, overlap: int):
    tokens = text.split()
    n = len(tokens)
    if n == 0:
        return []
    chunks = []
    start = 0
    while start < n:
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunks.append(" ".join(chunk_tokens))
        # advance with overlap
        start = max(end - overlap, end) if overlap >= chunk_size else end - overlap
        # ensure progress
        if start <= end and end >= n:
            break
    return chunks

def main():
    if not os.path.exists(INPUT_ROOT):
        print(f"ERROR: INPUT_ROOT does not exist: {INPUT_ROOT!r}")
        return

    all_chunks = []
    all_metadata = []
    global_counter = 1

    candidate_files = 0
    matched_files = 0
    processed_files = 0

    for root, dirs, files in os.walk(INPUT_ROOT):
        for fname in files:
            candidate_files += 1
            if not file_extension_ok(fname):
                # skip files like 'er', 'se' (no extension) or other non-text files
                continue

            matched_files += 1
            file_path = os.path.join(root, fname)
            dept = guess_department_from_path(root)
            source_doc = restore_source_name(file_path)
            allowed_roles = get_allowed_roles_for_dept(dept)

            print(f"Processing [{dept}] {source_doc} ...", end=" ")

            try:
                # open with utf-8 and fallback to latin-1 if needed
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        raw = f.read()
                except UnicodeDecodeError:
                    with open(file_path, "r", encoding="latin-1") as f:
                        raw = f.read()
            except Exception as e:
                print(f"FAILED to read ({e})")
                continue

            text = normalize_text(raw)
            if not text:
                print("SKIPPED (empty)")
                continue

            chunks = chunk_file_text(text, CHUNK_SIZE, OVERLAP)
            if not chunks:
                print("SKIPPED (no chunks produced)")
                continue

            for idx, chunk_text in enumerate(chunks, start=1):
                chunk_id = f"{dept.upper()}_CHUNK_{global_counter}"
                all_chunks.append({
                    "chunk_id": chunk_id,
                    "content": chunk_text
                })
                all_metadata.append({
                    "chunk_id": chunk_id,
                    "source_document": source_doc,
                    "department": dept.capitalize(),
                    "chunk_index": idx,
                    "approx_token_count": len(chunk_text.split()),
                    "security_level": "Confidential",
                    "allowed_roles": allowed_roles,
                    "created_at": datetime.utcnow().isoformat() + "Z"
                })
                global_counter += 1

            processed_files += 1
            print(f"DONE ({len(chunks)} chunks)")

    # write outputs
    print("\nWriting output files...")
    with open(OUTPUT_CHUNKS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    with open(OUTPUT_METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(all_metadata, f, indent=2, ensure_ascii=False)

    print("SUMMARY:")
    print("  Candidate files scanned:", candidate_files)
    print("  Files matching extensions:", matched_files)
    print("  Files actually processed:", processed_files)
    print("  Total chunks created:", len(all_chunks))
    print("  Chunks saved to:", OUTPUT_CHUNKS_FILE)
    print("  Metadata saved to:", OUTPUT_METADATA_FILE)

if __name__ == "__main__":
    main()
