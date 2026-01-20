import os
import csv
from typing import List, Dict


def load_markdown(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def load_csv(file_path: str) -> str:
    rows = []
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(" | ".join(row))
    return "\n".join(rows)


def generate_doc_id(department: str, filename: str) -> str:
    name = filename.replace(".", "_").lower()
    return f"{department}_{name}"


def ingest_documents(dataset_root: str) -> List[Dict]:
    documents = []

    for department in os.listdir(dataset_root):
        dept_path = os.path.join(dataset_root, department)

        if not os.path.isdir(dept_path):
            continue

        for filename in os.listdir(dept_path):
            file_path = os.path.join(dept_path, filename)

            if filename.endswith(".md"):
                text = load_markdown(file_path)
                file_type = "md"

            elif filename.endswith(".csv"):
                text = load_csv(file_path)
                file_type = "csv"

            else:
                continue  # skip unsupported files

            document = {
                "doc_id": generate_doc_id(department, filename),
                "text": text,
                "metadata": {
                    "department": department.lower(),
                    "source_file": filename,
                    "file_type": file_type,
                },
            }

            documents.append(document)

    return documents
