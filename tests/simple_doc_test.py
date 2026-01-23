#!/usr/bin/env python3
"""
Simple test for document access
"""
import sys
import os
sys.path.append('app')

from rag_pipeline_enhanced_real import run_pipeline

def test_document_reading():
    print("🧪 Testing Enhanced RAG Pipeline with Real Documents")
    print("=" * 60)
    
    # Test different roles and queries
    test_cases = [
        {"role": "HR", "query": "What are the employee benefits?"},
        {"role": "Finance", "query": "What is our financial performance?"},
        {"role": "Marketing", "query": "What are our marketing results?"},
        {"role": "Engineering", "query": "What are the technical guidelines?"},
        {"role": "Intern", "query": "What company policies should I know?"},
    ]
    
    for test_case in test_cases:
        print(f"\n🔍 Testing {test_case['role']} role")
        print(f"Query: {test_case['query']}")
        print("-" * 40)
        
        try:
            result = run_pipeline(test_case['query'], test_case['role'])
            
            print(f"✅ Pipeline executed successfully")
            print(f"   Sources: {result.get('sources', [])}")
            print(f"   Accuracy: {result.get('accuracy_score', 0)}")
            print(f"   Document-based: {result.get('quality_metrics', {}).get('document_based', False)}")
            print(f"   Response length: {len(result.get('response', ''))} characters")
            
            # Show first 200 characters of response
            response_preview = result.get('response', '')[:200] + "..."
            print(f"   Preview: {response_preview}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_document_reading()