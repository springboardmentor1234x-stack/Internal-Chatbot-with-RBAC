"""
Complete Application Initialization
Initializes Complete RAG Pipeline (Retrieval + LLM)
"""

import chromadb
import numpy as np
import json
from config import Config

# RAG Pipeline Components
from services.QueryNormalizer import QueryNormalizer
from rbac.RBACEngine import RBACEngine
from rbac.VectorRetriever import VectorRetriever
from services.ReRanker import ReRanker
from rag.llm_service import LLMService
from rag.prompt_builder import PromptBuilder
from rag.RAGPipeline import CompleteRAGPipeline


def create_complete_rag_pipeline(
    chroma_client,
    chunks,
    metadata,
    embeddings,
    rbac_config,
    abbreviations,
    audit_logger
):
    """
    Create and configure the complete RAG pipeline with LLM integration
    
    Args:
        chroma_client: ChromaDB client instance
        chunks: List of document chunks
        metadata: List of chunk metadata
        embeddings: Numpy array of embeddings
        rbac_config: RBAC configuration dictionary
        audit_logger: AuditLogger instance
        
    Returns:
        Initialized CompleteRAGPipeline instance
    """
    
    # Initialize query normalizer
    
    normalizer = QueryNormalizer(abbreviations)
    
    # Initialize RBAC with default admin role (will be overridden per request)
    rbac = RBACEngine(
        user_roles=[],
        rbac_config=rbac_config,
        audit_logger=audit_logger
    )
    
    # Initialize vector retriever
    retriever = VectorRetriever(
        chroma_client=chroma_client,
        chunks=chunks,
        metadata=metadata,
        embeddings=embeddings,
        model_name="all-MiniLM-L6-v2",
        audit_logger=audit_logger
    )
    
    # Initialize re-ranker
    ranker = ReRanker(
        similarity_threshold=0.3,
        audit_logger=audit_logger
    )
    
    # Initialize LLM service
    llm_service = LLMService(audit_logger=audit_logger)
    
    # Initialize prompt builder
    prompt_builder = PromptBuilder()
    
    # Create complete pipeline
    pipeline = CompleteRAGPipeline(
        normalizer=normalizer,
        retriever=retriever,
        rbac=rbac,
        ranker=ranker,
        llm_service=llm_service,
        prompt_builder=prompt_builder,
        audit_logger=audit_logger
    )
    
    assert pipeline.validate_pipeline(), "Pipeline validation failed"
    
    return pipeline

def load_real_data():
    """
    Load chunks, metadata, embeddings, and vector DB from disk
    """
    with open(Config.CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    with open(Config.METADATA_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    with open(Config.RBAC_PERMISSIONS_PATH, "r", encoding="utf-8") as f:
        rbac_config = json.load(f)

    with open(Config.ABBREVIATIONS_PATH, "r", encoding="utf-8") as f:
        abbreviations = json.load(f)

    embeddings = np.load(Config.EMBEDDINGS_PATH)

    chroma_client = chromadb.PersistentClient(
        path=Config.VECTOR_DB_PATH,
    )

    return chroma_client, chunks, metadata, embeddings, rbac_config, abbreviations

def bootstrap_application(audit_logger):

    audit_logger.log_info("Loading real document data...")
    chroma_client, chunks, metadata, embeddings, rbac_config, abbreviations  = load_real_data()

    audit_logger.log_info("Initializing RAG pipeline...")
    rag_pipeline = create_complete_rag_pipeline(
        chroma_client,
        chunks,
        metadata,
        embeddings,
        rbac_config,
        abbreviations,
        audit_logger
    )
    return rag_pipeline    
