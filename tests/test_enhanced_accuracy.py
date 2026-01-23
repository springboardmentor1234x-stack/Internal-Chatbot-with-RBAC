#!/usr/bin/env python3
"""
Test script to validate accuracy improvements
Run this to test the enhanced system
"""

import sys
import os
sys.path.append('app')

from rag_pipeline_accuracy_enhanced import EnhancedFinSolveRAGPipeline
from accuracy_enhancer_v2 import enhanced_accuracy_validator

def test_enhanced_accuracy():
    """Test the enhanced accuracy system."""
    print("🧪 Testing Enhanced Accuracy System")
    print("=" * 50)
    
    # Test queries for different categories
    test_queries = [
        ("What was the quarterly revenue for Q4 2024?", "Finance"),
        ("What is the vacation policy for employees?", "HR"),
        ("What were the Q4 2024 marketing campaign results?", "Marketing"),
        ("What is the system architecture overview?", "Engineering"),
        ("What is FinSolve's company mission and values?", "Employee")
    ]
    
    total_accuracy = 0
    expectations_met = 0
    
    for query, role in test_queries:
        print(f"\n🔍 Testing: {query}")
        print(f"👤 Role: {role}")
        
        try:
            # Test enhanced RAG pipeline
            pipeline = EnhancedFinSolveRAGPipeline(role)
            result = pipeline.run_pipeline(query)
            
            if result.get("error"):
                print(f"❌ Error: {result['error']}")
                continue
            
            # Test enhanced accuracy validation
            validation = enhanced_accuracy_validator.validate_response_accuracy(query, result)
            
            accuracy = validation.get("enhanced_accuracy", 0)
            meets_expectations = validation.get("meets_expectations", False)
            confidence = validation.get("confidence_level", "unknown")
            
            total_accuracy += accuracy
            if meets_expectations:
                expectations_met += 1
            
            print(f"📊 Accuracy: {accuracy:.1f}%")
            print(f"🎯 Meets Expectations: {'✅' if meets_expectations else '❌'}")
            print(f"🔒 Confidence: {confidence}")
            
            # Show quality metrics
            quality_metrics = validation.get("quality_metrics", {})
            print("📈 Quality Metrics:")
            for metric, score in quality_metrics.items():
                print(f"   • {metric.replace('_', ' ').title()}: {score:.1f}%")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    # Calculate overall results
    avg_accuracy = total_accuracy / len(test_queries)
    expectations_rate = (expectations_met / len(test_queries)) * 100
    
    print("\n" + "=" * 50)
    print("📊 OVERALL RESULTS")
    print("=" * 50)
    print(f"Average Accuracy: {avg_accuracy:.1f}% (Target: 85%+)")
    print(f"Expectations Met Rate: {expectations_rate:.1f}% (Target: 70%+)")
    
    if avg_accuracy >= 85:
        print("🎉 SUCCESS: Accuracy target achieved!")
    else:
        print(f"⚠️  Need improvement: {85 - avg_accuracy:.1f}% to reach target")
    
    if expectations_rate >= 70:
        print("🎉 SUCCESS: Expectations target achieved!")
    else:
        print(f"⚠️  Need improvement: {70 - expectations_rate:.1f}% to reach target")

if __name__ == "__main__":
    test_enhanced_accuracy()
