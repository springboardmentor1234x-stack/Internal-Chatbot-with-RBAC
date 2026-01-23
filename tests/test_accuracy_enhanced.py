"""
Enhanced Accuracy Testing Suite for RAG Pipeline
Tests the accuracy improvements and validates the enhanced system performance.
"""

import requests
import json
import time
from typing import Dict, List, Any
from datetime import datetime


class AccuracyTester:
    """
    Comprehensive accuracy testing system for the enhanced RAG pipeline.
    """
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.test_results = []
        
        # Enhanced test queries with expected accuracy ranges
        self.test_queries = {
            "financial": [
                {
                    "query": "What was the quarterly revenue for Q4 2024?",
                    "expected_accuracy_min": 85.0,
                    "expected_entities": ["numbers", "percentages", "currencies"],
                    "expected_sources": ["quarterly_financial_report.md"]
                },
                {
                    "query": "Show me the profit margins and expense breakdown",
                    "expected_accuracy_min": 80.0,
                    "expected_entities": ["numbers", "percentages"],
                    "expected_sources": ["quarterly_financial_report.md"]
                },
                {
                    "query": "What are the budget allocations for different departments?",
                    "expected_accuracy_min": 75.0,
                    "expected_entities": ["numbers", "currencies"],
                    "expected_sources": ["quarterly_financial_report.md"]
                }
            ],
            "hr": [
                {
                    "query": "What is the vacation policy for employees?",
                    "expected_accuracy_min": 90.0,
                    "expected_entities": ["dates"],
                    "expected_sources": ["employee_handbook.md"]
                },
                {
                    "query": "Explain the employee benefits package",
                    "expected_accuracy_min": 85.0,
                    "expected_entities": [],
                    "expected_sources": ["employee_handbook.md"]
                },
                {
                    "query": "What are the training and development opportunities?",
                    "expected_accuracy_min": 80.0,
                    "expected_entities": [],
                    "expected_sources": ["employee_handbook.md"]
                }
            ],
            "marketing": [
                {
                    "query": "What were the Q4 2024 marketing campaign results?",
                    "expected_accuracy_min": 85.0,
                    "expected_entities": ["numbers", "percentages"],
                    "expected_sources": ["market_report_q4_2024.md"]
                },
                {
                    "query": "Show me customer engagement metrics and conversion rates",
                    "expected_accuracy_min": 80.0,
                    "expected_entities": ["percentages"],
                    "expected_sources": ["market_report_q4_2024.md"]
                }
            ],
            "engineering": [
                {
                    "query": "What is the system architecture overview?",
                    "expected_accuracy_min": 85.0,
                    "expected_entities": [],
                    "expected_sources": ["engineering_master_doc.md"]
                },
                {
                    "query": "Explain the development process and deployment procedures",
                    "expected_accuracy_min": 80.0,
                    "expected_entities": [],
                    "expected_sources": ["engineering_master_doc.md"]
                }
            ],
            "general": [
                {
                    "query": "What is FinSolve's company mission and values?",
                    "expected_accuracy_min": 75.0,
                    "expected_entities": [],
                    "expected_sources": ["employee_handbook.md"]
                },
                {
                    "query": "Give me an overview of the company structure",
                    "expected_accuracy_min": 70.0,
                    "expected_entities": [],
                    "expected_sources": ["employee_handbook.md"]
                }
            ]
        }
        
        # Test user credentials for different roles
        self.test_users = {
            "finance": {"username": "finance_user", "password": "password123"},
            "hr": {"username": "hr_user", "password": "password123"},
            "marketing": {"username": "marketing_user", "password": "password123"},
            "engineering": {"username": "engineering_user", "password": "password123"},
            "admin": {"username": "admin", "password": "password123"},
            "employee": {"username": "employee", "password": "password123"}
        }
    
    def login_user(self, role: str) -> str:
        """Login and get access token for a specific role."""
        if role not in self.test_users:
            raise ValueError(f"Unknown role: {role}")
        
        credentials = self.test_users[role]
        
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                data=credentials,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()["access_token"]
            else:
                print(f"Login failed for {role}: {response.status_code}")
                return None
        except Exception as e:
            print(f"Login error for {role}: {e}")
            return None
    
    def test_query_accuracy(self, query: str, token: str, expected_result: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single query and validate accuracy."""
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/api/v1/chat",
                json={"query": query},
                headers=headers,
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code != 200:
                return {
                    "query": query,
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "response_time": response_time
                }
            
            data = response.json()
            
            # Extract accuracy metrics
            accuracy_score = data.get("accuracy_score", 0.0)
            original_accuracy = data.get("original_accuracy", 0.0)
            validation_score = data.get("validation_score", 0.0)
            confidence_level = data.get("confidence_level", "unknown")
            sources = data.get("sources", [])
            citations = data.get("citations", [])
            quality_metrics = data.get("quality_metrics", {})
            improvement_suggestions = data.get("improvement_suggestions", [])
            query_optimization = data.get("query_optimization", {})
            
            # Validate results
            validation_results = self._validate_response(data, expected_result)
            
            return {
                "query": query,
                "success": True,
                "accuracy_score": accuracy_score,
                "original_accuracy": original_accuracy,
                "validation_score": validation_score,
                "confidence_level": confidence_level,
                "response_time": response_time,
                "sources_count": len(sources),
                "citations_count": len(citations),
                "quality_metrics": quality_metrics,
                "improvement_suggestions_count": len(improvement_suggestions),
                "query_optimization_score": query_optimization.get("optimization_score", 0.0),
                "validation_results": validation_results,
                "meets_expectations": validation_results["accuracy_meets_min"] and validation_results["has_expected_sources"],
                "response_length": len(data.get("response", "")),
                "error": None
            }
            
        except Exception as e:
            return {
                "query": query,
                "success": False,
                "error": str(e),
                "response_time": 0
            }
    
    def _validate_response(self, response_data: Dict[str, Any], expected: Dict[str, Any]) -> Dict[str, Any]:
        """Validate response against expected results."""
        validation = {
            "accuracy_meets_min": False,
            "has_expected_sources": False,
            "has_expected_entities": False,
            "has_citations": False,
            "response_complete": False
        }
        
        # Check accuracy
        accuracy = response_data.get("accuracy_score", 0.0)
        min_expected = expected.get("expected_accuracy_min", 70.0)
        validation["accuracy_meets_min"] = accuracy >= min_expected
        
        # Check sources
        sources = response_data.get("sources", [])
        expected_sources = expected.get("expected_sources", [])
        if expected_sources:
            validation["has_expected_sources"] = any(
                any(exp_source in source for exp_source in expected_sources)
                for source in sources
            )
        else:
            validation["has_expected_sources"] = len(sources) > 0
        
        # Check entities (simplified check)
        response_text = response_data.get("response", "")
        expected_entities = expected.get("expected_entities", [])
        if expected_entities:
            entity_found = False
            if "numbers" in expected_entities and any(char.isdigit() for char in response_text):
                entity_found = True
            if "percentages" in expected_entities and "%" in response_text:
                entity_found = True
            if "currencies" in expected_entities and "$" in response_text:
                entity_found = True
            if "dates" in expected_entities and any(month in response_text.lower() for month in ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december", "q1", "q2", "q3", "q4"]):
                entity_found = True
            validation["has_expected_entities"] = entity_found
        else:
            validation["has_expected_entities"] = True
        
        # Check citations
        citations = response_data.get("citations", [])
        validation["has_citations"] = len(citations) > 0
        
        # Check response completeness
        validation["response_complete"] = len(response_text) > 50
        
        return validation
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive accuracy tests across all categories and roles."""
        print("🚀 Starting Enhanced Accuracy Testing Suite...")
        print("=" * 60)
        
        all_results = []
        category_results = {}
        role_results = {}
        
        # Test each category with appropriate roles
        role_mapping = {
            "financial": ["finance", "admin"],
            "hr": ["hr", "admin", "employee"],
            "marketing": ["marketing", "admin"],
            "engineering": ["engineering", "admin"],
            "general": ["employee", "admin"]
        }
        
        for category, queries in self.test_queries.items():
            print(f"\n📊 Testing {category.upper()} queries...")
            category_results[category] = []
            
            for role in role_mapping.get(category, ["employee"]):
                print(f"  👤 Testing as {role} user...")
                
                # Login
                token = self.login_user(role)
                if not token:
                    print(f"    ❌ Failed to login as {role}")
                    continue
                
                role_category_results = []
                
                for query_data in queries:
                    query = query_data["query"]
                    print(f"    🔍 Testing: {query[:50]}...")
                    
                    result = self.test_query_accuracy(query, token, query_data)
                    result["role"] = role
                    result["category"] = category
                    
                    all_results.append(result)
                    category_results[category].append(result)
                    role_category_results.append(result)
                    
                    # Print result summary
                    if result["success"]:
                        accuracy = result["accuracy_score"]
                        meets_exp = "✅" if result["meets_expectations"] else "⚠️"
                        print(f"      {meets_exp} Accuracy: {accuracy:.1f}% | Response: {result['response_time']:.2f}s")
                    else:
                        print(f"      ❌ Failed: {result['error']}")
                    
                    time.sleep(1)  # Rate limiting
                
                # Store role results
                if role not in role_results:
                    role_results[role] = []
                role_results[role].extend(role_category_results)
        
        # Calculate summary statistics
        summary = self._calculate_summary_stats(all_results, category_results, role_results)
        
        # Print summary
        self._print_test_summary(summary)
        
        # Store results
        self.test_results = all_results
        
        return {
            "summary": summary,
            "detailed_results": all_results,
            "category_results": category_results,
            "role_results": role_results,
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_summary_stats(self, all_results: List[Dict], category_results: Dict, role_results: Dict) -> Dict[str, Any]:
        """Calculate comprehensive summary statistics."""
        successful_results = [r for r in all_results if r["success"]]
        
        if not successful_results:
            return {"error": "No successful test results"}
        
        # Overall statistics
        accuracies = [r["accuracy_score"] for r in successful_results]
        response_times = [r["response_time"] for r in successful_results]
        meets_expectations = [r["meets_expectations"] for r in successful_results]
        
        overall_stats = {
            "total_tests": len(all_results),
            "successful_tests": len(successful_results),
            "success_rate": len(successful_results) / len(all_results) * 100,
            "average_accuracy": sum(accuracies) / len(accuracies),
            "min_accuracy": min(accuracies),
            "max_accuracy": max(accuracies),
            "average_response_time": sum(response_times) / len(response_times),
            "expectations_met_rate": sum(meets_expectations) / len(meets_expectations) * 100
        }
        
        # Category statistics
        category_stats = {}
        for category, results in category_results.items():
            successful = [r for r in results if r["success"]]
            if successful:
                cat_accuracies = [r["accuracy_score"] for r in successful]
                category_stats[category] = {
                    "tests": len(results),
                    "successful": len(successful),
                    "average_accuracy": sum(cat_accuracies) / len(cat_accuracies),
                    "min_accuracy": min(cat_accuracies),
                    "max_accuracy": max(cat_accuracies),
                    "expectations_met": sum(r["meets_expectations"] for r in successful) / len(successful) * 100
                }
        
        # Role statistics
        role_stats = {}
        for role, results in role_results.items():
            successful = [r for r in results if r["success"]]
            if successful:
                role_accuracies = [r["accuracy_score"] for r in successful]
                role_stats[role] = {
                    "tests": len(results),
                    "successful": len(successful),
                    "average_accuracy": sum(role_accuracies) / len(role_accuracies),
                    "expectations_met": sum(r["meets_expectations"] for r in successful) / len(successful) * 100
                }
        
        # Quality metrics analysis
        quality_analysis = self._analyze_quality_metrics(successful_results)
        
        return {
            "overall": overall_stats,
            "by_category": category_stats,
            "by_role": role_stats,
            "quality_analysis": quality_analysis
        }
    
    def _analyze_quality_metrics(self, results: List[Dict]) -> Dict[str, Any]:
        """Analyze quality metrics across all results."""
        all_quality_metrics = []
        
        for result in results:
            quality_metrics = result.get("quality_metrics", {})
            if quality_metrics:
                all_quality_metrics.append(quality_metrics)
        
        if not all_quality_metrics:
            return {"error": "No quality metrics available"}
        
        # Calculate averages for each metric
        metric_averages = {}
        metric_names = set()
        for metrics in all_quality_metrics:
            metric_names.update(metrics.keys())
        
        for metric_name in metric_names:
            values = [metrics.get(metric_name, 0) for metrics in all_quality_metrics]
            metric_averages[metric_name] = {
                "average": sum(values) / len(values),
                "min": min(values),
                "max": max(values)
            }
        
        return metric_averages
    
    def _print_test_summary(self, summary: Dict[str, Any]):
        """Print comprehensive test summary."""
        print("\n" + "=" * 60)
        print("📊 ENHANCED ACCURACY TEST RESULTS SUMMARY")
        print("=" * 60)
        
        overall = summary.get("overall", {})
        print(f"\n🎯 OVERALL PERFORMANCE:")
        print(f"   Total Tests: {overall.get('total_tests', 0)}")
        print(f"   Success Rate: {overall.get('success_rate', 0):.1f}%")
        print(f"   Average Accuracy: {overall.get('average_accuracy', 0):.1f}%")
        print(f"   Accuracy Range: {overall.get('min_accuracy', 0):.1f}% - {overall.get('max_accuracy', 0):.1f}%")
        print(f"   Expectations Met: {overall.get('expectations_met_rate', 0):.1f}%")
        print(f"   Avg Response Time: {overall.get('average_response_time', 0):.2f}s")
        
        # Category performance
        category_stats = summary.get("by_category", {})
        if category_stats:
            print(f"\n📈 CATEGORY PERFORMANCE:")
            for category, stats in category_stats.items():
                print(f"   {category.upper()}:")
                print(f"     Accuracy: {stats.get('average_accuracy', 0):.1f}% (Range: {stats.get('min_accuracy', 0):.1f}%-{stats.get('max_accuracy', 0):.1f}%)")
                print(f"     Expectations Met: {stats.get('expectations_met', 0):.1f}%")
        
        # Role performance
        role_stats = summary.get("by_role", {})
        if role_stats:
            print(f"\n👥 ROLE PERFORMANCE:")
            for role, stats in role_stats.items():
                print(f"   {role.upper()}:")
                print(f"     Accuracy: {stats.get('average_accuracy', 0):.1f}%")
                print(f"     Expectations Met: {stats.get('expectations_met', 0):.1f}%")
        
        # Quality metrics
        quality_analysis = summary.get("quality_analysis", {})
        if quality_analysis and "error" not in quality_analysis:
            print(f"\n🔍 QUALITY METRICS ANALYSIS:")
            for metric, stats in quality_analysis.items():
                metric_name = metric.replace("_", " ").title()
                print(f"   {metric_name}: {stats.get('average', 0):.1f}% (Range: {stats.get('min', 0):.1f}%-{stats.get('max', 0):.1f}%)")
        
        print("\n" + "=" * 60)
    
    def save_results(self, filename: str = None):
        """Save test results to JSON file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"accuracy_test_results_{timestamp}.json"
        
        if self.test_results:
            with open(filename, 'w') as f:
                json.dump({
                    "test_results": self.test_results,
                    "timestamp": datetime.now().isoformat(),
                    "total_tests": len(self.test_results)
                }, f, indent=2)
            print(f"📁 Results saved to: {filename}")
        else:
            print("❌ No results to save")


def main():
    """Run the enhanced accuracy testing suite."""
    tester = AccuracyTester()
    
    print("🧪 Enhanced RAG Accuracy Testing Suite")
    print("This will test the accuracy improvements across all categories and roles.")
    print("\nMake sure your FastAPI server is running on http://127.0.0.1:8000")
    
    input("\nPress Enter to start testing...")
    
    try:
        results = tester.run_comprehensive_test()
        
        # Save results
        tester.save_results()
        
        print("\n✅ Testing completed successfully!")
        print("Check the generated JSON file for detailed results.")
        
    except KeyboardInterrupt:
        print("\n⏹️ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing failed: {e}")


if __name__ == "__main__":
    main()