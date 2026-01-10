"""
Non-interactive accuracy test runner
"""

from test_accuracy_enhanced import AccuracyTester
import json
from datetime import datetime

def run_accuracy_test():
    """Run accuracy test without user interaction."""
    print("🧪 Running Enhanced RAG Accuracy Testing Suite...")
    
    tester = AccuracyTester()
    
    try:
        results = tester.run_comprehensive_test()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"accuracy_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📁 Results saved to: {filename}")
        
        # Return summary for immediate viewing
        return results.get("summary", {})
        
    except Exception as e:
        print(f"❌ Testing failed: {e}")
        return None

if __name__ == "__main__":
    summary = run_accuracy_test()
    if summary:
        print("\n🎯 QUICK SUMMARY:")
        overall = summary.get("overall", {})
        print(f"Average Accuracy: {overall.get('average_accuracy', 0):.1f}%")
        print(f"Success Rate: {overall.get('success_rate', 0):.1f}%")
        print(f"Expectations Met: {overall.get('expectations_met_rate', 0):.1f}%")