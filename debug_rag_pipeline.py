#!/usr/bin/env python3
"""
Debug RAG pipeline directly to see what's happening with chunks
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.rag_pipeline_enhanced import rag_pipeline

def debug_rag_pipeline():
    """Debug the RAG pipeline directly"""
    print("🔍 Debugging RAG Pipeline Directly...")
    
    query = "What is our company policy?"
    user_role = "C-Level"
    
    print(f"📝 Query: {query}")
    print(f"👤 User Role: {user_role}")
    
    # Call RAG pipeline directly
    result = rag_pipeline.run_pipeline(query, user_role)
    
    print(f"\n📊 RAG Pipeline Result:")
    print(f"✅ Response length: {len(result.get('response', ''))}")
    print(f"📄 Sources: {len(result.get('sources', []))}")
    print(f"📈 Accuracy: {result.get('accuracy_score', 0):.1f}%")
    print(f"🔍 Total chunks analyzed: {result.get('total_chunks_analyzed', 0)}")
    
    # Check chunk details
    chunk_details = result.get("chunk_details", [])
    print(f"🧩 Chunk Details: {len(chunk_details)} documents")
    
    if chunk_details:
        for i, chunk_info in enumerate(chunk_details, 1):
            doc_name = chunk_info.get("document_name", "Unknown")
            source_file = chunk_info.get("source_file", "Unknown")
            chunks = chunk_info.get("chunks", [])
            print(f"   📋 Document {i}: {doc_name}")
            print(f"      📁 Source: {source_file}")
            print(f"      🔢 Chunks: {len(chunks)}")
            
            if chunks:
                for j, chunk in enumerate(chunks[:2], 1):  # Show first 2 chunks
                    chunk_id = chunk.get("chunk_id", "N/A")
                    chunk_type = chunk.get("type", "N/A")
                    score = chunk.get("score", 0)
                    word_count = chunk.get("word_count", 0)
                    content_preview = chunk.get("content", "")[:100] + "..." if len(chunk.get("content", "")) > 100 else chunk.get("content", "")
                    print(f"         🧩 Chunk {j}: {chunk_id}")
                    print(f"            Type: {chunk_type}, Score: {score:.3f}, Words: {word_count}")
                    print(f"            Preview: {content_preview}")
            else:
                print(f"      ⚠️  No chunks found for this document")
    else:
        print("⚠️  No chunk details found")
        
        # Let's debug the search results
        print("\n🔍 Debugging search results...")
        search_results = rag_pipeline.enhanced_search(query, user_role)
        print(f"Search results count: {len(search_results)}")
        
        for i, result in enumerate(search_results, 1):
            print(f"\nResult {i}:")
            print(f"  Source: {result.get('source', 'N/A')}")
            print(f"  Score: {result.get('score', 0):.3f}")
            print(f"  All chunks: {len(result.get('all_chunks', []))}")
            
            all_chunks = result.get('all_chunks', [])
            if all_chunks:
                print(f"  First chunk ID: {all_chunks[0].get('chunk_id', 'N/A')}")
                print(f"  First chunk type: {all_chunks[0].get('type', 'N/A')}")
                print(f"  First chunk score: {all_chunks[0].get('score', 0):.3f}")
            else:
                print("  ⚠️  No all_chunks found")
    
    print(f"\n🔑 All result keys: {list(result.keys())}")

if __name__ == "__main__":
    debug_rag_pipeline()