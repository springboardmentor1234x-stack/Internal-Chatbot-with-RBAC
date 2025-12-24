{
    "chunks_file": "D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC-Project/Chunking/all_chunks.json",
    "metadata_file": "D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC-Project/Chunking/all_metadata.json",
    "embeddings_file": "D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC-Project/Embeddings/chunk_embeddings.npy",
    "abbreviations_file": "D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC-Project/RAGPipeline/ABBREVATIONS.json",
    "rbac_permissions_file": "D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC-Project/RAGPipeline/rbac_permissions.json",
    "vector_db": "D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC-Project/VectorDB",
    
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "similarity_threshold": 0.30,
    "top_k": 3,
    
    "retrieval": {
        "use_chroma": True,
        "use_custom_knn": True,
        "top_k_initial": 10
    },
    
    "reranking": {
        "enable_deduplication": True,
        "enable_semantic_dedup": True,
        "semantic_threshold": 0.95,
        "max_per_source": 3
    },
    
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    }
}