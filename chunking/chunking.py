import os
import json

INPUT_ROOT = "D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC/Fintech-data-normalized"
OUTPUT_CHUNKS_FILE = "all_chunks.json"
OUTPUT_METADATA_FILE = "all_metadata.json"

CHUNK_SIZE = 350
OVERLAP = 50

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

def restore_original_filename(cleaned_name):
    if cleaned_name.endswith("_cleaned.txt"):
        base = cleaned_name.replace("_cleaned.txt", "")
        # Assume original was md unless HR (csv)
        if "hr" in base.lower():
            return base + ".csv"
        return base + ".md"
    return cleaned_name

all_chunks = []
all_metadata = []
global_chunk_counter = 1

for root, dirs, files in os.walk(INPUT_ROOT):
    for file in files:
        if not file.endswith("_cleaned.txt"):
            continue

        file_path = os.path.join(root, file)

        # Extract department from folder name
        department = os.path.basename(root).lower()

        # Restore original source filename
        source_document = restore_original_filename(file)

        print(f"Processing: {department}/{file}")

        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        tokens = text.split()
        total_tokens = len(tokens)

        start = 0
        chunk_index = 1

        while start < total_tokens:
            end = start + CHUNK_SIZE
            chunk_tokens = tokens[start:end]
            chunk_text = " ".join(chunk_tokens)

            chunk_id = f"{department.upper()}_CHUNK_{global_chunk_counter}"

            all_chunks.append({
                "chunk_id": chunk_id,
                "content": chunk_text
            })

            all_metadata.append({
                "chunk_id": chunk_id,
                "source_document": source_document,
                "department": department.capitalize(),
                "chunk_index": chunk_index,
                "approx_token_count": len(chunk_tokens),
                "security_level": "Confidential",
                "allowed_roles": ROLE_MAP.get(department, ["C-Level Executive"])
            })

            global_chunk_counter += 1
            chunk_index += 1
            start = end - OVERLAP

with open(OUTPUT_CHUNKS_FILE, "w", encoding="utf-8") as f:
    json.dump(all_chunks, f, indent=4)

with open(OUTPUT_METADATA_FILE, "w", encoding="utf-8") as f:
    json.dump(all_metadata, f, indent=4)

print("\nALL FILES CHUNKED SUCCESSFULLY")
print("Chunks Saved as ", OUTPUT_CHUNKS_FILE)
print("Metadata Saved as ", OUTPUT_METADATA_FILE)
print("Total Chunks Created:", len(all_chunks))
