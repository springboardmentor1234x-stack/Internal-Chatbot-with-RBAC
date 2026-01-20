from typing import List, Dict


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap

        if start < 0:
            start = 0

    return chunks


def chunk_documents(documents: List[Dict]) -> List[Dict]:
    all_chunks = []

    for doc in documents:
        text_chunks = chunk_text(doc["text"])

        for idx, chunk_text_content in enumerate(text_chunks):
            chunk = {
                "chunk_id": f"{doc['doc_id']}__chunk_{idx}",
                "text": chunk_text_content,
                "metadata": {
                    "doc_id": doc["doc_id"],
                    "department": doc["metadata"]["department"],
                    "chunk_index": idx,
                },
            }

            all_chunks.append(chunk)

    return all_chunks
