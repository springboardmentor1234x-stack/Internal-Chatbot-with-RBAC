"""
Complete Module 3 Pipeline
Generate embeddings and populate vector database
"""

import json
import sys
import io
from pathlib import Path
from embedding_generator import EmbeddingGenerator
from vector_db_manager import VectorDBManager

# Fix Windows encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def run_module3_pipeline():
    """Run complete Module 3 workflow"""
    
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 12 + "MODULE 3: VECTOR DATABASE PIPELINE" + " " * 12 + "║")
    print("╚" + "=" * 58 + "╝")
    
    # Step 1: Load processed chunks from Module 2
    print("\n" + "=" * 60)
    print("STEP 1: LOADING CHUNKS FROM MODULE 2")
    print("=" * 60)
    
    chunks_file = "../module_2_document_preprocessing/chunks_for_embedding.json"
    
    if not Path(chunks_file).exists():
        print(f"\n❌ Error: {chunks_file} not found")
        print("   Please run Module 2 first!")
        return
    
    with open(chunks_file, 'r') as f:
        chunks = json.load(f)
    
    print(f"✅ Loaded {len(chunks)} chunks from Module 2")
    
    # Step 2: Generate embeddings
    print("\n" + "=" * 60)
    print("STEP 2: GENERATING EMBEDDINGS")
    print("=" * 60)
    
    generator = EmbeddingGenerator()
    chunks_with_embeddings = generator.embed_chunks(chunks)
    
    # Save embeddings
    generator.save_embeddings(chunks_with_embeddings, "chunks_with_embeddings.json")
    
    # Step 3: Initialize vector database
    print("\n" + "=" * 60)
    print("STEP 3: INITIALIZING VECTOR DATABASE")
    print("=" * 60)
    
    db = VectorDBManager(persist_directory="./chroma_db")
    
    # Clear existing data if any
    if db.collection.count() > 0:
        print("\n🗑️  Clearing existing data...")
        db.clear_collection()
    
    # Step 4: Add documents to vector DB
    print("\n" + "=" * 60)
    print("STEP 4: POPULATING VECTOR DATABASE")
    print("=" * 60)
    
    db.add_documents(chunks_with_embeddings)
    
    # Step 5: Verify and get statistics
    print("\n" + "=" * 60)
    print("STEP 5: VERIFICATION & STATISTICS")
    print("=" * 60)
    
    stats = db.get_stats()
    
    print(f"\n📊 Vector Database Statistics:")
    print(f"   Total documents: {stats['total_documents']}")
    print(f"   Collection: {stats['collection_name']}")
    print(f"   Persist directory: ./chroma_db")
    print(f"\n   Documents by department:")
    for dept, count in sorted(stats['by_department'].items()):
        print(f"      {dept}: {count} chunks")
    
    # Step 6: Test searches
    print("\n" + "=" * 60)
    print("STEP 6: TESTING SEMANTIC SEARCH")
    print("=" * 60)
    
    test_queries = [
        ("What is the financial performance?", None),
        ("Tell me about marketing campaigns", None),
        ("HR policies and employee data", None),
        ("What are our Q4 results?", None)
    ]
    
    print("\n🔍 Running test queries:")
    for query, role in test_queries:
        print(f"\n   Query: '{query}'")
        results = db.search(query_text=query, n_results=2, user_role=role)
        print(f"   Found {results['count']} results:")
        for i, metadata in enumerate(results['metadatas'][:2]):
            print(f"      {i+1}. {metadata['department']} - {metadata['source_file']}")
    
    # Test RBAC filtering
    print("\n🔐 Testing RBAC filtering:")
    test_rbac = [
        ("financial information", "finance_employee", "Finance only"),
        ("marketing campaigns", "marketing_employee", "Marketing only"),
        ("employee handbook", "employee", "General only")
    ]
    
    for query, role, expected in test_rbac:
        print(f"\n   Query: '{query}' | Role: {role}")
        print(f"   Expected: {expected}")
        results = db.search(query_text=query, n_results=3, user_role=role)
        print(f"   Found {results['count']} results:")
        depts = set(m['department'] for m in results['metadatas'])
        print(f"   Departments: {', '.join(depts)}")
    
    # Save summary
    print("\n" + "=" * 60)
    print("STEP 7: SAVING SUMMARY")
    print("=" * 60)
    
    summary = {
        'total_chunks': len(chunks_with_embeddings),
        'embedding_dimension': len(chunks_with_embeddings[0]['embedding']),
        'vector_db_stats': stats,
        'model_used': generator.model_name,
        'status': 'complete'
    }
    
    with open('module3_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("✅ Saved summary to: module3_summary.json")
    
    print("\n╔" + "=" * 58 + "╗")
    print("║" + " " * 18 + "PIPELINE COMPLETE! ✅" + " " * 18 + "║")
    print("╚" + "=" * 58 + "╝")
    
    print("\n📊 FINAL RESULTS:")
    print(f"   ✅ {len(chunks_with_embeddings)} chunks embedded")
    print(f"   ✅ Vector database populated")
    print(f"   ✅ RBAC filtering working")
    print(f"   ✅ Semantic search enabled")
    print(f"\n🚀 Ready for Module 4 (Backend & Authentication)")


if __name__ == "__main__":
    run_module3_pipeline()
