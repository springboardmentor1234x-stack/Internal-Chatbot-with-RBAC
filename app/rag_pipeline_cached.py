"""
Cached RAG Pipeline for FinSolve
Integrates Redis caching with the existing RAG pipeline for improved performance.
"""

import os
import tiktoken
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from datetime import datetime
import hashlib

# LangChain Imports
from langchain_community.document_loaders import UnstructuredMarkdownLoader, CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

# Local imports
from redis_cache import get_search_cache, RedisSearchCache

load_dotenv()

# --- CONFIGURATION ---
RAW_DATA_PATH = "./data/raw"
PROCESSED_DATA_PATH = "./data/processed"
CHROMA_PATH = "./data/chroma"

EMBEDDING_MODEL = "text-embedding-ada-002"

DOCUMENT_MAP = {
    "quarterly_financial_report.md": ["Finance", "C-Level"],
    "marketing_report_2024.md": ["Marketing", "C-Level"],
    "marketing_report_q1_2024.md": ["Marketing", "C-Level"],
    "marketing_report_q2_2024.md": ["Marketing", "C-Level"],
    "marketing_report_q3_2024.md": ["Marketing", "C-Level"],
    "market_report_q4_2024.md": ["Marketing", "C-Level"],
    "hr_data.csv": ["HR", "C-Level"],
    "employee_handbook.md": [
        "HR",
        "Employee",
        "C-Level",
        "Finance",
        "Marketing",
        "Engineering",
    ],
    "engineering_master_doc.md": ["Engineering", "C-Level"],
}


class CachedFinSolveRAGPipeline:
    """
    Enhanced RAG Pipeline with Redis caching for improved performance.
    Caches search results, embeddings, and responses based on query and user role.
    """
    
    def __init__(self, role: str):
        self.user_role = role
        self.embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        self.cache: RedisSearchCache = get_search_cache()
        
        # Performance tracking
        self.performance_stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "vector_searches": 0,
            "total_queries": 0
        }

    def load_documents(self) -> List:
        """Load documents with caching support"""
        # Check if documents are cached
        cache_key = f"documents:{self.user_role}"
        
        # For document loading, we'll cache the processed documents
        # This is especially useful for large document sets
        all_documents = []

        # Initialize Tokenizer for more accurate splitting
        tokenizer = tiktoken.get_encoding("cl100k_base")

        def tiktoken_len(text):
            tokens = tokenizer.encode(text, disallowed_special=())
            return len(tokens)

        for filename, roles in DOCUMENT_MAP.items():
            # Only load documents the user role can access
            if self.user_role not in roles:
                continue
                
            folder = RAW_DATA_PATH if filename.endswith(".csv") else PROCESSED_DATA_PATH
            file_path = os.path.join(folder, filename)

            if not os.path.exists(file_path):
                print(f"Warning: {filename} not found in {folder}")
                continue

            loader = (
                CSVLoader(file_path, encoding="utf-8")
                if filename.endswith(".csv")
                else UnstructuredMarkdownLoader(file_path)
            )
            docs = loader.load()

            # Using tiktoken for splitting logic
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,  # 500 tokens is a sweet spot for RAG
                chunk_overlap=50,
                length_function=tiktoken_len,
                separators=["\n\n", "\n", " ", ""],
            )

            chunks = text_splitter.split_documents(docs)

            for chunk in chunks:
                chunk.metadata["allowed_roles"] = roles
                chunk.metadata["source"] = filename
                all_documents.append(chunk)

        return all_documents

    def create_vector_store(self):
        """Create vector store (same as original, no caching needed here)"""
        documents = self.load_documents()
        if not documents:
            print("No documents found to index.")
            return

        if os.path.exists(CHROMA_PATH):
            import shutil
            shutil.rmtree(CHROMA_PATH)

        db = Chroma.from_documents(
            documents, self.embeddings, persist_directory=CHROMA_PATH
        )
        print(f"Vector store created at {CHROMA_PATH}")

    def _generate_query_signature(self, question: str) -> str:
        """Generate a unique signature for the query"""
        return hashlib.md5(f"{question.lower().strip()}:{self.user_role}".encode()).hexdigest()

    def run_pipeline(self, question: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Run the RAG pipeline with intelligent caching.
        
        Args:
            question: The user's query
            use_cache: Whether to use caching (default: True)
            
        Returns:
            Dict containing response, sources, and performance metrics
        """
        self.performance_stats["total_queries"] += 1
        start_time = datetime.now()
        
        # Check cache first if enabled
        if use_cache:
            cached_result = self.cache.get_cached_response(question, self.user_role)
            if cached_result:
                self.performance_stats["cache_hits"] += 1
                
                # Add performance info
                cached_result["performance"] = {
                    "cache_hit": True,
                    "response_time_ms": (datetime.now() - start_time).total_seconds() * 1000,
                    "source": "redis_cache"
                }
                
                return cached_result
        
        # Cache miss - perform actual search
        self.performance_stats["cache_misses"] += 1
        
        if not os.path.exists(CHROMA_PATH):
            error_result = {
                "error": "Vector store not found. Please run create_vector_store() first.",
                "sources": [],
                "response": "I apologize, but the knowledge base is not available. Please contact your administrator.",
                "performance": {
                    "cache_hit": False,
                    "response_time_ms": (datetime.now() - start_time).total_seconds() * 1000,
                    "source": "error"
                }
            }
            return error_result

        try:
            # Check if search results are cached
            search_cache_key = f"search_results:{self._generate_query_signature(question)}"
            cached_search = self.cache.get_search_results(question, self.user_role) if use_cache else None
            
            if cached_search and use_cache:
                docs_data = cached_search.get("docs", [])
                print(f"📋 Using cached search results for query: {question[:50]}...")
            else:
                # Perform vector search
                self.performance_stats["vector_searches"] += 1
                
                db = Chroma(persist_directory=CHROMA_PATH, embedding_function=self.embeddings)
                
                # Role-based access control filter
                chroma_filter = {"allowed_roles": {"$in": [self.user_role]}}
                retriever = db.as_retriever(search_kwargs={"k": 5, "filter": chroma_filter})
                
                docs = retriever.invoke(question)
                
                # Convert to serializable format
                docs_data = [
                    {
                        "doc_id": d.metadata.get("source"),
                        "content": d.page_content,
                        "metadata": d.metadata,
                        "relevance_score": getattr(d, 'relevance_score', 0.0)
                    }
                    for d in docs
                ]
                
                # Cache search results if enabled
                if use_cache and docs_data:
                    search_results = {
                        "docs": docs_data,
                        "query": question,
                        "user_role": self.user_role,
                        "search_timestamp": datetime.now().isoformat(),
                        "total_docs": len(docs_data)
                    }
                    self.cache.cache_search_results(question, self.user_role, search_results)
                    print(f"💾 Cached search results for future use")

            # Check if no documents found
            if not docs_data:
                no_docs_result = {
                    "error": "No accessible documents found for your role and query.",
                    "sources": [],
                    "response": f"I couldn't find any information that you have access to regarding '{question}'. Your role ({self.user_role}) may not have permission to view documents related to this query.",
                    "performance": {
                        "cache_hit": False,
                        "response_time_ms": (datetime.now() - start_time).total_seconds() * 1000,
                        "source": "no_documents",
                        "docs_found": 0
                    }
                }
                return no_docs_result

            # Generate response (this could also be cached separately)
            response_text = self._generate_response(question, docs_data)
            
            # Prepare final result
            result = {
                "response": response_text,
                "sources": list(set([doc["doc_id"] for doc in docs_data if doc["doc_id"]])),
                "query": question,
                "user_role": self.user_role,
                "total_chunks_analyzed": len(docs_data),
                "chunk_details": [
                    {
                        "source": doc["doc_id"],
                        "content_preview": doc["content"][:100] + "..." if len(doc["content"]) > 100 else doc["content"],
                        "relevance_score": doc.get("relevance_score", 0.0)
                    }
                    for doc in docs_data
                ],
                "accuracy_score": self._calculate_accuracy_score(docs_data),
                "timestamp": datetime.now().isoformat(),
                "performance": {
                    "cache_hit": False,
                    "response_time_ms": (datetime.now() - start_time).total_seconds() * 1000,
                    "source": "vector_search",
                    "docs_analyzed": len(docs_data),
                    "vector_search_performed": True
                }
            }
            
            # Cache the complete response if enabled
            if use_cache:
                self.cache.cache_response(question, self.user_role, result)
                print(f"💾 Cached complete response for future use")
            
            return result
            
        except Exception as e:
            error_result = {
                "error": f"Pipeline error: {str(e)}",
                "sources": [],
                "response": "I apologize, but I encountered an error while processing your request. Please try again or contact support.",
                "performance": {
                    "cache_hit": False,
                    "response_time_ms": (datetime.now() - start_time).total_seconds() * 1000,
                    "source": "error",
                    "error_details": str(e)
                }
            }
            return error_result

    def _generate_response(self, question: str, docs_data: List[Dict]) -> str:
        """
        Generate response from retrieved documents.
        This is a simplified version - in production you'd use an LLM here.
        """
        if not docs_data:
            return "No relevant information found."
        
        # Simple response generation based on document content
        relevant_content = []
        for doc in docs_data[:3]:  # Use top 3 most relevant docs
            content = doc["content"]
            if len(content) > 200:
                content = content[:200] + "..."
            relevant_content.append(f"From {doc['doc_id']}: {content}")
        
        response = f"Based on the available information:\n\n" + "\n\n".join(relevant_content)
        
        if len(docs_data) > 3:
            response += f"\n\n(Additional information available from {len(docs_data) - 3} more sources)"
        
        return response

    def _calculate_accuracy_score(self, docs_data: List[Dict]) -> float:
        """Calculate a simple accuracy score based on document relevance"""
        if not docs_data:
            return 0.0
        
        # Simple scoring based on number of relevant documents and content length
        base_score = min(len(docs_data) * 15, 70)  # Up to 70 points for document count
        
        # Add points for content quality (length as a proxy)
        content_score = 0
        for doc in docs_data:
            content_length = len(doc["content"])
            if content_length > 100:
                content_score += min(content_length / 50, 10)  # Up to 10 points per doc
        
        total_score = min(base_score + content_score, 100.0)
        return round(total_score, 2)

    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache and performance statistics"""
        cache_stats = self.cache.get_cache_stats()
        
        return {
            "pipeline_stats": self.performance_stats,
            "cache_stats": cache_stats,
            "cache_efficiency": {
                "hit_rate": cache_stats.get("hit_rate", 0),
                "total_queries": self.performance_stats["total_queries"],
                "cache_saves": self.performance_stats["cache_hits"],
                "vector_searches_avoided": self.performance_stats["cache_hits"]
            }
        }

    def clear_user_cache(self) -> Dict[str, Any]:
        """Clear cache entries for the current user role"""
        deleted_count = self.cache.invalidate_user_cache(self.user_role)
        
        return {
            "success": True,
            "deleted_entries": deleted_count,
            "user_role": self.user_role,
            "timestamp": datetime.now().isoformat()
        }

    def warm_cache(self, common_queries: List[str]) -> Dict[str, Any]:
        """Pre-populate cache with common queries for better performance"""
        results = {
            "warmed_queries": 0,
            "failed_queries": 0,
            "errors": []
        }
        
        for query in common_queries:
            try:
                # Run pipeline to populate cache
                self.run_pipeline(query, use_cache=False)  # Don't use cache for warming
                results["warmed_queries"] += 1
                print(f"🔥 Warmed cache for: {query[:50]}...")
            except Exception as e:
                results["failed_queries"] += 1
                results["errors"].append(f"Failed to warm '{query[:30]}...': {str(e)}")
        
        return results


# Global cached pipeline instances for different roles
_cached_pipelines = {}

def get_cached_pipeline(role: str) -> CachedFinSolveRAGPipeline:
    """Get or create a cached pipeline instance for a specific role"""
    if role not in _cached_pipelines:
        _cached_pipelines[role] = CachedFinSolveRAGPipeline(role)
    return _cached_pipelines[role]


# For backward compatibility
cached_rag_pipeline = get_cached_pipeline("Employee")  # Default instance


if __name__ == "__main__":
    # Example usage and testing
    pipeline = CachedFinSolveRAGPipeline(role="C-Level")
    
    # Create vector store if needed
    if not os.path.exists(CHROMA_PATH):
        print("Creating vector store...")
        pipeline.create_vector_store()
    
    # Test queries
    test_queries = [
        "What are our quarterly financial results?",
        "Tell me about our marketing performance",
        "What are the HR policies for remote work?"
    ]
    
    print("\n🧪 Testing cached pipeline...")
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        result = pipeline.run_pipeline(query)
        print(f"✅ Response length: {len(result.get('response', ''))}")
        print(f"📊 Performance: {result.get('performance', {})}")
    
    # Show cache statistics
    print("\n📈 Cache Statistics:")
    stats = pipeline.get_cache_statistics()
    print(f"Cache hit rate: {stats['cache_efficiency']['hit_rate']:.1f}%")
    print(f"Total queries: {stats['pipeline_stats']['total_queries']}")
    print(f"Vector searches: {stats['pipeline_stats']['vector_searches']}")