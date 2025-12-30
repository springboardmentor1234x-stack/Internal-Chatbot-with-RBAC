from QueryPipeline.main import RAGPipeline

def fake_embed(text):
    text = text.lower()

    if "hr" in text or "leave" in text:
        return [0.9] * 384     # strong match
    if "finance" in text or "profit" in text:
        return [0.85] * 384

    return [0.1] * 384



if __name__ == "__main__":
    print("\n🚀 RBAC RAG PIPELINE STARTED\n")

    abbreviations = {
        "hr": "human resources",
        "fin": "finance"
    }

    chunk_to_doc_map = {
        "ENGINEERING_CHUNK_10": "ENG_DOC",
        "FINANCE_CHUNK_12": "FIN_DOC_A",
        "FINANCE_CHUNK_14": "FIN_DOC_B"
    }

    pipeline = RAGPipeline(
        abbreviations=abbreviations,
        chunk_to_doc_map=chunk_to_doc_map
    )

    # 🔹 CHANGE THESE TO TEST DIFFERENT CASES
    user_query = "HR leave policy for interns"  
    user_role = "manager"     # try: intern, employee, admin

    result = pipeline.process_query(
        user_query=user_query,
        user_role=user_role,
        embed_fn=fake_embed
    )

    print("🔎 USER QUERY:", user_query)
    print("👤 USER ROLE :", user_role)
    print("\n📤 PIPELINE OUTPUT:")
    print(result)
    print("\n✅ PIPELINE EXECUTION FINISHED\n")
