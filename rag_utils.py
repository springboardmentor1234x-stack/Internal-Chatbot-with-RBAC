def format_chunks(docs):
    formatted = []
    for i, doc in enumerate(docs):
        formatted.append(f"Chunk {i+1}: {doc}")
    return formatted
