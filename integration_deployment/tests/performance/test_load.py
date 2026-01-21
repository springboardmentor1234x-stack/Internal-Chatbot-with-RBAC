#!/usr/bin/env python3
"""
Load Testing - Stress and Scalability Tests
Tests system behavior under various load conditions
"""

import requests
import time
import concurrent.futures
from typing import List, Dict, Tuple
from datetime import datetime
import statistics

API_BASE_URL = "http://localhost:8000"


class LoadTestMetrics:
    """Track load testing metrics"""
    
    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.response_times: List[float] = []
        self.errors: List[str] = []
    
    def add_success(self, duration: float):
        self.total_requests += 1
        self.successful_requests += 1
        self.response_times.append(duration)
    
    def add_failure(self, error: str):
        self.total_requests += 1
        self.failed_requests += 1
        self.errors.append(error)
    
    @property
    def success_rate(self) -> float:
        return (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0
    
    @property
    def avg_response_time(self) -> float:
        return statistics.mean(self.response_times) if self.response_times else 0
    
    @property
    def median_response_time(self) -> float:
        return statistics.median(self.response_times) if self.response_times else 0
    
    @property
    def throughput(self) -> float:
        """Requests per second"""
        if not self.response_times:
            return 0
        total_time = sum(self.response_times)
        return len(self.response_times) / total_time if total_time > 0 else 0


class TestLoadConditions:
    """Load testing suite"""
    
    @classmethod
    def setup_class(cls):
        """Setup test users for load testing"""
        cls.test_users = []
        
        # Create multiple test users
        for i in range(5):
            user = {
                "username": f"load_test_user_{int(time.time())}_{i}",
                "password": "LoadTest123!",
                "email": f"loadtest_{int(time.time())}_{i}@example.com",
                "full_name": f"Load Test User {i}",
                "role": "finance_employee"
            }
            
            # Register
            response = requests.post(f"{API_BASE_URL}/auth/register", json=user)
            
            # Login
            login_response = requests.post(
                f"{API_BASE_URL}/auth/login",
                json={"username": user["username"], "password": user["password"]}
            )
            
            if login_response.status_code == 200:
                token = login_response.json()['access_token']
                cls.test_users.append({
                    "username": user["username"],
                    "token": token,
                    "headers": {"Authorization": f"Bearer {token}"}
                })
        
        print(f"✅ Created {len(cls.test_users)} test users for load testing")
    
    def test_01_baseline_load(self):
        """Test baseline load - 50 requests"""
        print("\n" + "="*70)
        print("📊 Test: Baseline Load (50 requests)")
        print("="*70)
        
        metrics = LoadTestMetrics()
        
        def make_request():
            user = self.test_users[0]
            try:
                start = time.time()
                response = requests.get(f"{API_BASE_URL}/stats", headers=user["headers"])
                duration = time.time() - start
                
                if response.status_code == 200:
                    metrics.add_success(duration)
                else:
                    metrics.add_failure(f"Status {response.status_code}")
            except Exception as e:
                metrics.add_failure(str(e))
        
        # Execute requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            concurrent.futures.wait(futures)
        
        self._print_metrics(metrics)
        
        assert metrics.success_rate >= 95, f"Success rate too low: {metrics.success_rate}%"
        assert metrics.avg_response_time < 1.0, f"Avg response time too high: {metrics.avg_response_time}s"
        
        print("✅ Baseline load test passed")
    
    def test_02_moderate_load(self):
        """Test moderate load - 100 requests with 10 concurrent workers"""
        print("\n" + "="*70)
        print("📊 Test: Moderate Load (100 requests, 10 workers)")
        print("="*70)
        
        metrics = LoadTestMetrics()
        
        def make_request(user_idx: int):
            user = self.test_users[user_idx % len(self.test_users)]
            try:
                start = time.time()
                response = requests.get(f"{API_BASE_URL}/health")
                duration = time.time() - start
                
                if response.status_code == 200:
                    metrics.add_success(duration)
                else:
                    metrics.add_failure(f"Status {response.status_code}")
            except Exception as e:
                metrics.add_failure(str(e))
        
        # Execute requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, i) for i in range(100)]
            concurrent.futures.wait(futures)
        
        self._print_metrics(metrics)
        
        assert metrics.success_rate >= 90, f"Success rate too low: {metrics.success_rate}%"
        assert metrics.avg_response_time < 2.0, f"Avg response time too high: {metrics.avg_response_time}s"
        
        print("✅ Moderate load test passed")
    
    def test_03_heavy_load(self):
        """Test heavy load - 200 requests with 20 concurrent workers"""
        print("\n" + "="*70)
        print("📊 Test: Heavy Load (200 requests, 20 workers)")
        print("="*70)
        
        metrics = LoadTestMetrics()
        
        def make_authenticated_request(user_idx: int):
            user = self.test_users[user_idx % len(self.test_users)]
            try:
                start = time.time()
                response = requests.get(f"{API_BASE_URL}/stats", headers=user["headers"])
                duration = time.time() - start
                
                if response.status_code == 200:
                    metrics.add_success(duration)
                else:
                    metrics.add_failure(f"Status {response.status_code}")
            except Exception as e:
                metrics.add_failure(str(e))
        
        # Execute requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_authenticated_request, i) for i in range(200)]
            concurrent.futures.wait(futures)
        
        self._print_metrics(metrics)
        
        assert metrics.success_rate >= 85, f"Success rate too low: {metrics.success_rate}%"
        assert metrics.avg_response_time < 3.0, f"Avg response time too high: {metrics.avg_response_time}s"
        
        print("✅ Heavy load test passed")
    
    def test_04_burst_load(self):
        """Test burst load - sudden spike in requests"""
        print("\n" + "="*70)
        print("📊 Test: Burst Load (50 simultaneous requests)")
        print("="*70)
        
        metrics = LoadTestMetrics()
        
        def make_burst_request(user_idx: int):
            user = self.test_users[user_idx % len(self.test_users)]
            try:
                start = time.time()
                response = requests.get(f"{API_BASE_URL}/health")
                duration = time.time() - start
                
                if response.status_code == 200:
                    metrics.add_success(duration)
                else:
                    metrics.add_failure(f"Status {response.status_code}")
            except Exception as e:
                metrics.add_failure(str(e))
        
        # Execute all requests simultaneously
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(make_burst_request, i) for i in range(50)]
            concurrent.futures.wait(futures)
        
        self._print_metrics(metrics)
        
        assert metrics.success_rate >= 80, f"Success rate too low under burst: {metrics.success_rate}%"
        
        print("✅ Burst load test passed")
    
    def test_05_sustained_load(self):
        """Test sustained load - continuous requests over time"""
        print("\n" + "="*70)
        print("📊 Test: Sustained Load (100 requests over 30 seconds)")
        print("="*70)
        
        metrics = LoadTestMetrics()
        duration_seconds = 30
        request_interval = duration_seconds / 100  # Evenly distribute 100 requests
        
        def make_sustained_request(user_idx: int):
            user = self.test_users[user_idx % len(self.test_users)]
            try:
                start = time.time()
                response = requests.get(f"{API_BASE_URL}/stats", headers=user["headers"])
                duration = time.time() - start
                
                if response.status_code == 200:
                    metrics.add_success(duration)
                else:
                    metrics.add_failure(f"Status {response.status_code}")
            except Exception as e:
                metrics.add_failure(str(e))
        
        # Execute requests with interval
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for i in range(100):
                futures.append(executor.submit(make_sustained_request, i))
                time.sleep(request_interval)
            
            concurrent.futures.wait(futures)
        
        elapsed_time = time.time() - start_time
        
        self._print_metrics(metrics)
        print(f"Elapsed time: {elapsed_time:.2f}s")
        print(f"Throughput: {metrics.successful_requests/elapsed_time:.2f} req/s")
        
        assert metrics.success_rate >= 90, f"Success rate too low: {metrics.success_rate}%"
        assert elapsed_time <= duration_seconds + 5, "Test took too long to complete"
        
        print("✅ Sustained load test passed")
    
    def _print_metrics(self, metrics: LoadTestMetrics):
        """Print load test metrics"""
        print(f"\nTotal Requests: {metrics.total_requests}")
        print(f"Successful: {metrics.successful_requests}")
        print(f"Failed: {metrics.failed_requests}")
        print(f"Success Rate: {metrics.success_rate:.2f}%")
        print(f"Avg Response Time: {metrics.avg_response_time*1000:.2f}ms")
        print(f"Median Response Time: {metrics.median_response_time*1000:.2f}ms")
        
        if metrics.errors:
            print(f"\nErrors encountered: {len(set(metrics.errors))} unique")
            for error in set(metrics.errors[:5]):  # Show first 5 unique errors
                print(f"  - {error}")


def run_load_tests():
    """Run all load tests"""
    print("="*70)
    print("💪 RUNNING LOAD TESTS")
    print("="*70)
    
    test_suite = TestLoadConditions()
    test_suite.setup_class()
    
    tests = [
        ("Baseline Load (50 requests)", test_suite.test_01_baseline_load),
        ("Moderate Load (100 requests)", test_suite.test_02_moderate_load),
        ("Heavy Load (200 requests)", test_suite.test_03_heavy_load),
        ("Burst Load (50 simultaneous)", test_suite.test_04_burst_load),
        ("Sustained Load (100 over 30s)", test_suite.test_05_sustained_load),
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
    print("📊 LOAD TEST SUMMARY")
    print("="*70)
    
    for test_name, status in results:
        print(f"{status.split(':')[0]:15} {test_name}")
    
    passed = sum(1 for _, status in results if "✅" in status)
    total = len(results)
    
    print(f"\nTotal: {total} | Passed: {passed} | Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    print("="*70)


if __name__ == "__main__":
    run_load_tests()
