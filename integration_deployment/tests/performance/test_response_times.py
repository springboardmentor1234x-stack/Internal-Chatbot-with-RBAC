#!/usr/bin/env python3
"""
Performance Testing - Response Time Benchmarks
Tests response times for all critical endpoints
"""

import requests
import time
import statistics
from typing import List, Dict
from datetime import datetime

API_BASE_URL = "http://localhost:8000"

class PerformanceMetrics:
    """Track and calculate performance metrics"""
    
    def __init__(self):
        self.measurements: List[float] = []
    
    def add(self, duration: float):
        self.measurements.append(duration)
    
    @property
    def avg(self) -> float:
        return statistics.mean(self.measurements) if self.measurements else 0
    
    @property
    def median(self) -> float:
        return statistics.median(self.measurements) if self.measurements else 0
    
    @property
    def min(self) -> float:
        return min(self.measurements) if self.measurements else 0
    
    @property
    def max(self) -> float:
        return max(self.measurements) if self.measurements else 0
    
    @property
    def p95(self) -> float:
        """95th percentile"""
        if not self.measurements:
            return 0
        sorted_vals = sorted(self.measurements)
        idx = int(len(sorted_vals) * 0.95)
        return sorted_vals[idx] if idx < len(sorted_vals) else sorted_vals[-1]
    
    @property
    def p99(self) -> float:
        """99th percentile"""
        if not self.measurements:
            return 0
        sorted_vals = sorted(self.measurements)
        idx = int(len(sorted_vals) * 0.99)
        return sorted_vals[idx] if idx < len(sorted_vals) else sorted_vals[-1]


class TestResponseTimes:
    """Performance tests for response times"""
    
    @classmethod
    def setup_class(cls):
        """Setup test user"""
        cls.test_user = {
            "username": f"perf_test_user_{int(time.time())}",
            "password": "TestPass123!",
            "email": f"perftest_{int(time.time())}@example.com",
            "full_name": "Performance Test User",
            "role": "finance_employee"
        }
        
        # Register user
        response = requests.post(f"{API_BASE_URL}/auth/register", json=cls.test_user)
        if response.status_code != 200:
            # User might exist, try login
            pass
        
        # Login
        login_response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"username": cls.test_user["username"], "password": cls.test_user["password"]}
        )
        cls.token = login_response.json()['access_token']
        cls.headers = {"Authorization": f"Bearer {cls.token}"}
    
    def measure_endpoint(self, method: str, endpoint: str, runs: int = 10, **kwargs) -> PerformanceMetrics:
        """Measure response time for an endpoint"""
        metrics = PerformanceMetrics()
        
        for _ in range(runs):
            start = time.time()
            
            if method.upper() == "GET":
                response = requests.get(f"{API_BASE_URL}{endpoint}", **kwargs)
            elif method.upper() == "POST":
                response = requests.post(f"{API_BASE_URL}{endpoint}", **kwargs)
            
            duration = (time.time() - start) * 1000  # Convert to milliseconds
            
            if response.status_code == 200:
                metrics.add(duration)
        
        return metrics
    
    def test_01_health_check_performance(self):
        """Test /health endpoint performance"""
        print("\n" + "="*70)
        print("🔬 Testing: /health endpoint performance")
        print("="*70)
        
        metrics = self.measure_endpoint("GET", "/health", runs=50)
        
        print(f"Runs: 50")
        print(f"Average: {metrics.avg:.2f}ms")
        print(f"Median: {metrics.median:.2f}ms")
        print(f"Min: {metrics.min:.2f}ms")
        print(f"Max: {metrics.max:.2f}ms")
        print(f"P95: {metrics.p95:.2f}ms")
        print(f"P99: {metrics.p99:.2f}ms")
        
        # Assert performance thresholds
        assert metrics.avg < 100, f"Average response time too high: {metrics.avg}ms"
        assert metrics.p95 < 150, f"P95 response time too high: {metrics.p95}ms"
        
        print("✅ Health check performance acceptable")
    
    def test_02_authentication_performance(self):
        """Test authentication endpoint performance"""
        print("\n" + "="*70)
        print("🔬 Testing: /auth/login endpoint performance")
        print("="*70)
        
        login_data = {
            "username": self.test_user["username"],
            "password": self.test_user["password"]
        }
        
        metrics = self.measure_endpoint("POST", "/auth/login", runs=20, json=login_data)
        
        print(f"Runs: 20")
        print(f"Average: {metrics.avg:.2f}ms")
        print(f"Median: {metrics.median:.2f}ms")
        print(f"Min: {metrics.min:.2f}ms")
        print(f"Max: {metrics.max:.2f}ms")
        print(f"P95: {metrics.p95:.2f}ms")
        
        # Authentication should complete within reasonable time
        assert metrics.avg < 500, f"Average login time too high: {metrics.avg}ms"
        assert metrics.p95 < 1000, f"P95 login time too high: {metrics.p95}ms"
        
        print("✅ Authentication performance acceptable")
    
    def test_03_stats_endpoint_performance(self):
        """Test /stats endpoint performance"""
        print("\n" + "="*70)
        print("🔬 Testing: /stats endpoint performance")
        print("="*70)
        
        metrics = self.measure_endpoint("GET", "/stats", runs=30, headers=self.headers)
        
        print(f"Runs: 30")
        print(f"Average: {metrics.avg:.2f}ms")
        print(f"Median: {metrics.median:.2f}ms")
        print(f"Min: {metrics.min:.2f}ms")
        print(f"Max: {metrics.max:.2f}ms")
        print(f"P95: {metrics.p95:.2f}ms")
        
        assert metrics.avg < 200, f"Average stats response time too high: {metrics.avg}ms"
        assert metrics.p95 < 300, f"P95 stats response time too high: {metrics.p95}ms"
        
        print("✅ Stats endpoint performance acceptable")
    
    def test_04_query_endpoint_performance(self):
        """Test /query/advanced endpoint performance"""
        print("\n" + "="*70)
        print("🔬 Testing: /query/advanced endpoint performance")
        print("="*70)
        
        query_data = {
            "query": "What is the company revenue?",
            "top_k": 5
        }
        
        metrics = self.measure_endpoint(
            "POST",
            "/query/advanced",
            runs=10,  # Fewer runs for complex queries
            json=query_data,
            headers=self.headers
        )
        
        print(f"Runs: 10")
        print(f"Average: {metrics.avg:.2f}ms")
        print(f"Median: {metrics.median:.2f}ms")
        print(f"Min: {metrics.min:.2f}ms")
        print(f"Max: {metrics.max:.2f}ms")
        print(f"P95: {metrics.p95:.2f}ms")
        
        # RAG queries are more complex, allow more time
        assert metrics.avg < 5000, f"Average query time too high: {metrics.avg}ms"
        assert metrics.p95 < 8000, f"P95 query time too high: {metrics.p95}ms"
        
        print("✅ Query endpoint performance acceptable")
    
    def test_05_concurrent_requests(self):
        """Test handling multiple concurrent requests"""
        print("\n" + "="*70)
        print("🔬 Testing: Concurrent request handling")
        print("="*70)
        
        import concurrent.futures
        
        def make_stats_request():
            start = time.time()
            response = requests.get(f"{API_BASE_URL}/stats", headers=self.headers)
            duration = (time.time() - start) * 1000
            return duration if response.status_code == 200 else None
        
        # Execute 20 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_stats_request) for _ in range(20)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # Filter out failed requests
        results = [r for r in results if r is not None]
        
        metrics = PerformanceMetrics()
        for duration in results:
            metrics.add(duration)
        
        print(f"Concurrent requests: 20")
        print(f"Successful: {len(results)}")
        print(f"Average: {metrics.avg:.2f}ms")
        print(f"Median: {metrics.median:.2f}ms")
        print(f"Max: {metrics.max:.2f}ms")
        
        assert len(results) >= 18, "Too many concurrent requests failed"
        assert metrics.avg < 500, f"Concurrent request average too high: {metrics.avg}ms"
        
        print("✅ Concurrent request handling acceptable")


def run_performance_tests():
    """Run all performance tests"""
    print("="*70)
    print("⚡ RUNNING PERFORMANCE TESTS")
    print("="*70)
    
    test_suite = TestResponseTimes()
    test_suite.setup_class()
    
    tests = [
        ("Health Check Performance", test_suite.test_01_health_check_performance),
        ("Authentication Performance", test_suite.test_02_authentication_performance),
        ("Stats Endpoint Performance", test_suite.test_03_stats_endpoint_performance),
        ("Query Endpoint Performance", test_suite.test_04_query_endpoint_performance),
        ("Concurrent Requests", test_suite.test_05_concurrent_requests),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            test_func()
            results.append((test_name, "✅ PASSED"))
        except AssertionError as e:
            results.append((test_name, f"❌ FAILED: {str(e)}"))
        except Exception as e:
            results.append((test_name, f"💥 ERROR: {str(e)}"))
    
    print("\n" + "="*70)
    print("📊 PERFORMANCE TEST SUMMARY")
    print("="*70)
    
    for test_name, status in results:
        print(f"{status.split(':')[0]:15} {test_name}")
    
    passed = sum(1 for _, status in results if "✅" in status)
    total = len(results)
    
    print(f"\nTotal: {total} | Passed: {passed} | Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    print("="*70)


if __name__ == "__main__":
    run_performance_tests()
