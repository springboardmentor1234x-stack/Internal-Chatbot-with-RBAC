from typing import List, Dict


def format_chunks_for_prompt(chunks: List[Dict]) -> str:
    formatted_sections = []

    for chunk in chunks:
        section = (
            f"[Document ID]: {chunk['metadata']['doc_id']}\n"
            f"[Chunk ID]: {chunk['chunk_id']}\n"
            f"[Content]:\n{chunk['text']}\n"
            f"---"
        )
        formatted_sections.append(section)

    return "\n".join(formatted_sections)
