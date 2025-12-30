from QueryPipeline.main import RAGPipeline

def fake_embed(text):
    return [0.1] * 384

abbreviations = {
    "hr": "human resources",
    "fin": "finance"
}

chunk_to_doc = {
    "FINANCE_CHUNK_12": "FIN_DOC_A",
    "FINANCE_CHUNK_14": "FIN_DOC_B"
}

pipeline = RAGPipeline(abbreviations, chunk_to_doc)

result = pipeline.process_query(
    user_query="HR leave policy for interns",
    user_role="intern",
    embed_fn=fake_embed
)

print(result)
