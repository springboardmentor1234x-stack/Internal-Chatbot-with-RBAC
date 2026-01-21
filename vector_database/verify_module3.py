#!/usr/bin/env python3
"""
Module 3 Verification Script
Validates embeddings, vector database, and search functionality
"""

import json
from pathlib import Path
import sys


def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"{title:^70}")
    print("=" * 70)


def print_success(message):
    """Print success message"""
    print(f"✅ {message}")


def print_error(message):
    """Print error message"""
    print(f"❌ {message}")


def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")


def verify_files():
    """Verify all required files exist"""
    print_header("FILE EXISTENCE CHECK")
    
    required_files = [
        "chunks_with_embeddings.json",
        "module3_summary.json",
        "embedding_generator.py",
        "vector_db_manager.py",
        "module3_pipeline.py"
    ]
    
    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print_success(f"{file} exists")
        else:
            print_error(f"{file} not found")
            all_exist = False
    
    # Check ChromaDB directory
    if Path("chroma_db").exists() and Path("chroma_db").is_dir():
        print_success("chroma_db/ directory exists")
        # Check for key files
        if Path("chroma_db/chroma.sqlite3").exists():
            print_success("ChromaDB database file found")
    else:
        print_error("chroma_db/ directory not found")
        all_exist = False
    
    return all_exist


def verify_embeddings():
    """Verify embedding quality and structure"""
    print_header("EMBEDDING VALIDATION")
    
    try:
        with open('chunks_with_embeddings.json', 'r') as f:
            chunks = json.load(f)
        
        print_success(f"Loaded {len(chunks)} chunks")
        
        # Check first chunk structure
        if chunks:
            chunk = chunks[0]
            required_keys = ['chunk_id', 'text', 'embedding', 'metadata']
            
            for key in required_keys:
                if key in chunk:
                    print_success(f"Chunk has '{key}' field")
                else:
                    print_error(f"Chunk missing '{key}' field")
                    return False
            
            # Check embedding dimensions
            embedding_dim = len(chunk['embedding'])
            if embedding_dim == 384:
                print_success(f"Embedding dimension correct: {embedding_dim}")
            else:
                print_error(f"Unexpected embedding dimension: {embedding_dim}")
                return False
            
            # Check metadata structure
            metadata = chunk['metadata']
            required_metadata = ['department', 'source_file', 'accessible_roles']
            for key in required_metadata:
                if key in metadata:
                    print_success(f"Metadata has '{key}' field")
                else:
                    print_error(f"Metadata missing '{key}' field")
                    return False
            
            # Verify all chunks have embeddings
            chunks_with_embeddings = sum(1 for c in chunks if 'embedding' in c and len(c['embedding']) == 384)
            print_info(f"{chunks_with_embeddings}/{len(chunks)} chunks have valid embeddings")
            
            if chunks_with_embeddings == len(chunks):
                print_success("All chunks have valid embeddings")
                return True
            else:
                print_error("Some chunks missing embeddings")
                return False
        
    except Exception as e:
        print_error(f"Error validating embeddings: {e}")
        return False


def verify_summary():
    """Verify summary file"""
    print_header("SUMMARY VALIDATION")
    
    try:
        with open('module3_summary.json', 'r') as f:
            summary = json.load(f)
        
        print_success("Summary file loaded")
        
        # Check required fields
        required_fields = ['total_chunks', 'embedding_dimension', 'vector_db_stats', 'model_used', 'status']
        for field in required_fields:
            if field in summary:
                print_success(f"Summary has '{field}' field: {summary[field]}")
            else:
                print_error(f"Summary missing '{field}' field")
                return False
        
        # Verify stats
        stats = summary['vector_db_stats']
        print_info(f"Total documents in DB: {stats['total_documents']}")
        print_info("Documents by department:")
        for dept, count in sorted(stats['by_department'].items()):
            print(f"   • {dept}: {count} chunks")
        
        return True
        
    except Exception as e:
        print_error(f"Error validating summary: {e}")
        return False


def verify_vector_db():
    """Verify vector database functionality"""
    print_header("VECTOR DATABASE TEST")
    
    try:
        from vector_db_manager import VectorDBManager
        
        db = VectorDBManager(persist_directory="./chroma_db")
        print_success("Vector database loaded")
        
        # Get stats
        stats = db.get_stats()
        total_docs = stats['total_documents']
        
        if total_docs > 0:
            print_success(f"Database contains {total_docs} documents")
        else:
            print_error("Database is empty")
            return False
        
        # Test search without RBAC
        print_info("Testing semantic search...")
        results = db.search(query_text="financial performance", n_results=3)
        
        if results['count'] > 0:
            print_success(f"Search returned {results['count']} results")
            print_info("Top result:")
            print(f"   • Department: {results['metadatas'][0]['department']}")
            print(f"   • Source: {results['metadatas'][0]['source_file']}")
        else:
            print_error("Search returned no results")
            return False
        
        # Test RBAC filtering
        print_info("Testing RBAC filtering...")
        rbac_results = db.search(
            query_text="financial information",
            user_role="finance_employee",
            n_results=3
        )
        
        if rbac_results['count'] > 0:
            print_success(f"RBAC search returned {rbac_results['count']} results")
            departments = set(m['department'] for m in rbac_results['metadatas'])
            print_info(f"Departments: {', '.join(departments)}")
            
            # Verify Finance employee only gets Finance and General
            allowed_depts = {'Finance', 'General'}
            if departments.issubset(allowed_depts):
                print_success("RBAC filtering working correctly")
            else:
                print_error(f"RBAC filtering issue: Got {departments}, expected subset of {allowed_depts}")
                return False
        else:
            print_error("RBAC search returned no results")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Error testing vector database: {e}")
        return False


def verify_rbac_compliance():
    """Verify RBAC compliance across all roles"""
    print_header("RBAC COMPLIANCE TEST")
    
    try:
        from vector_db_manager import VectorDBManager
        
        db = VectorDBManager(persist_directory="./chroma_db")
        
        # Test different roles
        rbac_tests = [
            ("admin", None, "Should access all departments"),
            ("finance_employee", {'Finance', 'General'}, "Finance + General only"),
            ("marketing_employee", {'Marketing', 'General'}, "Marketing + General only"),
            ("hr_employee", {'HR', 'General'}, "HR + General only"),
            ("engineering_employee", {'Engineering', 'General'}, "Engineering + General only"),
            ("employee", {'General'}, "General only")
        ]
        
        all_passed = True
        
        for role, expected_depts, description in rbac_tests:
            print(f"\n🔐 Testing role: {role}")
            print(f"   Expected: {description}")
            
            results = db.search(
                query_text="company information",
                user_role=role,
                n_results=10
            )
            
            departments = set(m['department'] for m in results['metadatas'])
            print(f"   Got departments: {departments}")
            
            if expected_depts is None:  # Admin - should get all
                if len(departments) > 1:
                    print_success(f"Admin has access to multiple departments ✓")
                else:
                    print_error(f"Admin should have access to all departments")
                    all_passed = False
            else:
                if departments.issubset(expected_depts):
                    print_success(f"Access control correct ✓")
                else:
                    print_error(f"Access control violation! Expected subset of {expected_depts}")
                    all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_error(f"Error in RBAC compliance test: {e}")
        return False


def main():
    """Run all verification tests"""
    print("\n" + "╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "MODULE 3 COMPREHENSIVE VERIFICATION" + " " * 18 + "║")
    print("╚" + "=" * 68 + "╝")
    
    tests = [
        ("File Existence", verify_files),
        ("Embedding Validation", verify_embeddings),
        ("Summary Validation", verify_summary),
        ("Vector Database Test", verify_vector_db),
        ("RBAC Compliance", verify_rbac_compliance)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Print final results
    print_header("VERIFICATION SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} | {test_name}")
    
    print("\n" + "=" * 70)
    print(f"FINAL SCORE: {passed}/{total} tests passed")
    print("=" * 70)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Module 3 is fully validated and ready.")
        print("🚀 You can proceed to Module 4: Backend & Authentication")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
