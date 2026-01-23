#!/usr/bin/env python3
"""
Simple Accuracy Checker for FinSolve Internal Chatbot
Run this anytime to check your chatbot's accuracy
"""

import sys
import os
import time

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def quick_accuracy_check():
    """Quick accuracy check with 5 test queries"""
    print("🎯 FinSolve Chatbot - Quick Accuracy Check")
    print("=" * 50)
    
    try:
        from app.rag_pipeline_enhanced import rag_pipeline
        
        # Quick test cases
        test_queries = [
            ("What are our quarterly financial results?", "Finance", "Financial Query"),
            ("How did our Q4 marketing campaigns perform?", "Marketing", "Marketing Query"),
            ("What are the employee vacation policies?", "HR", "HR Policy Query"),
            ("What technologies do we use?", "Engineering", "Technical Query"),
            ("What is the company mission?", "Employee", "General Query")
        ]
        
        total_accuracy = 0
        successful_tests = 0
        
        print(f"Testing {len(test_queries)} queries...\n")
        
        for i, (query, role, description) in enumerate(test_queries, 1):
            print(f"{i}. {description} ({role})")
            print(f"   Query: {query}")
            
            start_time = time.time()
            result = rag_pipeline.run_pipeline(query, role)
            end_time = time.time()
            
            if result.get("error"):
                print(f"   ❌ Error: {result['error']}")
            else:
                accuracy = result.get("accuracy_score", 0)
                total_accuracy += accuracy
                successful_tests += 1
                
                # Color coding for accuracy
                if accuracy >= 90:
                    status = "🎯 EXCELLENT"
                    color = "GREEN"
                elif accuracy >= 80:
                    status = "✅ GOOD"
                    color = "YELLOW"
                elif accuracy >= 70:
                    status = "⚠️  FAIR"
                    color = "ORANGE"
                else:
                    status = "❌ POOR"
                    color = "RED"
                
                print(f"   {status} - Accuracy: {accuracy:.1f}%")
                print(f"   Sources: {len(result.get('sources', []))} documents")
                print(f"   Response Time: {(end_time - start_time):.3f}s")
            
            print()
        
        # Calculate overall results
        if successful_tests > 0:
            avg_accuracy = total_accuracy / successful_tests
            
            print("=" * 50)
            print("📊 QUICK ACCURACY RESULTS")
            print("=" * 50)
            print(f"Tests Completed: {successful_tests}/{len(test_queries)}")
            print(f"Average Accuracy: {avg_accuracy:.1f}%")
            
            if avg_accuracy >= 90:
                print("🎉 EXCELLENT: Your chatbot is performing at target level!")
            elif avg_accuracy >= 80:
                print("✅ GOOD: Your chatbot is performing well!")
            elif avg_accuracy >= 70:
                print("⚠️  FAIR: Consider optimizing for better accuracy")
            else:
                print("❌ NEEDS WORK: Significant improvements needed")
            
            # Recommendations
            print(f"\n💡 RECOMMENDATIONS:")
            if avg_accuracy < 90:
                print("   • Add more detailed content to your documents")
                print("   • Improve keyword matching in queries")
                print("   • Consider using more specific questions")
            
            print(f"\n🎯 TARGET: 90-96% accuracy")
            print(f"📈 CURRENT: {avg_accuracy:.1f}% accuracy")
            
            if avg_accuracy >= 90:
                print("✅ TARGET ACHIEVED!")
            else:
                gap = 90 - avg_accuracy
                print(f"📊 GAP: {gap:.1f}% improvement needed")
        
    except Exception as e:
        print(f"❌ Error running accuracy check: {e}")
        print("Make sure your FinSolve chatbot is properly set up.")

def detailed_accuracy_check():
    """Detailed accuracy check with comprehensive testing"""
    print("🔬 FinSolve Chatbot - Detailed Accuracy Analysis")
    print("=" * 60)
    
    try:
        from app.rag_pipeline_enhanced import rag_pipeline
        
        # Comprehensive test cases
        detailed_tests = [
            # Financial queries
            ("What were our Q4 revenue and profit margins?", "Finance", "financial", "Detailed Financial"),
            ("Show me quarterly expense breakdowns", "C-Level", "financial", "Executive Financial"),
            
            # Marketing queries  
            ("How did our digital campaigns perform in Q4?", "Marketing", "marketing", "Campaign Performance"),
            ("What are our customer engagement metrics?", "C-Level", "marketing", "Executive Marketing"),
            
            # HR queries
            ("What are the remote work policies?", "HR", "hr", "HR Policy Detail"),
            ("Tell me about employee development programs", "Employee", "hr", "Employee Benefits"),
            
            # Engineering queries
            ("What is our technical stack and architecture?", "Engineering", "engineering", "Technical Architecture"),
            ("How do we handle deployment and scaling?", "C-Level", "engineering", "Executive Technical"),
            
            # Cross-role tests (should have limited access)
            ("Show me financial data", "Employee", "financial", "Access Control Test"),
            ("Tell me about technical infrastructure", "Marketing", "engineering", "Cross-Department Access")
        ]
        
        category_scores = {}
        role_scores = {}
        
        for i, (query, role, category, description) in enumerate(detailed_tests, 1):
            print(f"\n{i:2d}. {description}")
            print(f"    Role: {role} | Category: {category}")
            print(f"    Query: {query}")
            
            result = rag_pipeline.run_pipeline(query, role)
            
            if result.get("error"):
                accuracy = 0
                print(f"    ❌ Access Denied: {result['error'][:50]}...")
            else:
                accuracy = result.get("accuracy_score", 0)
                sources = result.get("sources", [])
                
                status = ("🎯" if accuracy >= 90 else "✅" if accuracy >= 80 else 
                         "⚠️" if accuracy >= 70 else "❌")
                
                print(f"    {status} Accuracy: {accuracy:.1f}% | Sources: {len(sources)}")
            
            # Track by category and role
            if category not in category_scores:
                category_scores[category] = []
            category_scores[category].append(accuracy)
            
            if role not in role_scores:
                role_scores[role] = []
            role_scores[role].append(accuracy)
        
        # Analysis by category
        print(f"\n{'='*60}")
        print("📊 DETAILED ACCURACY ANALYSIS")
        print(f"{'='*60}")
        
        print("\n🏷️  BY CATEGORY:")
        for category, scores in category_scores.items():
            avg_score = sum(scores) / len(scores)
            max_score = max(scores)
            min_score = min(scores)
            print(f"   {category.title():12} | Avg: {avg_score:5.1f}% | Range: {min_score:.1f}%-{max_score:.1f}%")
        
        print("\n👤 BY ROLE:")
        for role, scores in role_scores.items():
            avg_score = sum(scores) / len(scores)
            max_score = max(scores)
            min_score = min(scores)
            print(f"   {role:12} | Avg: {avg_score:5.1f}% | Range: {min_score:.1f}%-{max_score:.1f}%")
        
        # Overall statistics
        all_scores = [score for scores in category_scores.values() for score in scores if score > 0]
        if all_scores:
            overall_avg = sum(all_scores) / len(all_scores)
            high_accuracy = len([s for s in all_scores if s >= 90])
            good_accuracy = len([s for s in all_scores if 80 <= s < 90])
            
            print(f"\n🎯 OVERALL PERFORMANCE:")
            print(f"   Average Accuracy: {overall_avg:.1f}%")
            print(f"   High Accuracy (90%+): {high_accuracy}/{len(all_scores)} ({high_accuracy/len(all_scores)*100:.1f}%)")
            print(f"   Good Accuracy (80%+): {good_accuracy}/{len(all_scores)} ({good_accuracy/len(all_scores)*100:.1f}%)")
            
            target_achievement = high_accuracy / len(all_scores) * 100
            print(f"\n🏆 TARGET ACHIEVEMENT: {target_achievement:.1f}% of responses in 90%+ range")
            
            if target_achievement >= 70:
                print("🎉 EXCELLENT: Exceeding target performance!")
            elif target_achievement >= 50:
                print("✅ GOOD: Meeting performance expectations")
            else:
                print("⚠️  IMPROVEMENT NEEDED: Below target performance")
    
    except Exception as e:
        print(f"❌ Error in detailed analysis: {e}")

if __name__ == "__main__":
    print("Choose accuracy check type:")
    print("1. Quick Check (5 queries)")
    print("2. Detailed Analysis (10+ queries)")
    print("3. Both")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        quick_accuracy_check()
    elif choice == "2":
        detailed_accuracy_check()
    elif choice == "3":
        quick_accuracy_check()
        print("\n" + "="*60)
        detailed_accuracy_check()
    else:
        print("Invalid choice. Running quick check...")
        quick_accuracy_check()