"""
Test script for Redis cache implementation in FinSolve RAG Pipeline
"""

import os
import sys
import time
from datetime import datetime

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app.redis_cache import RedisSearchCache, CacheConfig
    from app.rag_pipeline_cached import CachedFinSolveRAGPipeline, get_cached_pipeline
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)


def test_redis_connection():
    """Test Redis connection and basic operations"""
    print("🔍 Testing Redis Connection...")
    
    cache = RedisSearchCache()
    health = cache.health_check()
    
    print(f"Redis Status: {health['status']}")
    print(f"Connected: {health['redis_connected']}")
    
    if health['redis_connected']:
        print(f"Response Time: {health['response_time_ms']:.2f}ms")
        print("✅ Redis connection successful!")
    else:
        print("⚠️  Redis not connected, using fallback cache")
        for error in health.get('errors', []):
            print(f"   Error: {error}")
    
    return health['redis_connected']


def test_cache_operations():
    """Test basic cache operations"""
    print("\n🧪 Testing Cache Operations...")
    
    cache = RedisSearchCache()
    
    # Test data
    test_query = "What are our quarterly financial results?"
    test_role = "C-Level"
    test_data = {
        "response": "Based on Q3 2024 results, revenue increased by 15%...",
        "sources": ["quarterly_financial_report.md"],
        "accuracy_score": 85.5,
        "timestamp": datetime.now().isoformat()
    }
    
    # Test cache set
    print("📝 Testing cache set...")
    success = cache.cache_search_results(test_query, test_role, test_data)
    print(f"Cache set success: {success}")
    
    # Test cache get
    print("📖 Testing cache get...")
    cached_result = cache.get_search_results(test_query, test_role)
    
    if cached_result:
        print("✅ Cache retrieval successful!")
        print(f"   Cached response length: {len(cached_result.get('response', ''))}")
        print(f"   Cache info: {cached_result.get('cache_info', {})}")
    else:
        print("❌ Cache retrieval failed")
    
    # Test cache stats
    print("\n📊 Cache Statistics:")
    stats = cache.get_cache_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    return cached_result is not None


def test_cached_pipeline():
    """Test the cached RAG pipeline"""
    print("\n🚀 Testing Cached RAG Pipeline...")
    
    # Test queries
    test_queries = [
        "What are our marketing performance metrics?",
        "Tell me about HR policies",
        "What are the engineering team's recent achievements?"
    ]
    
    roles = ["Marketing", "HR", "Engineering"]
    
    for role in roles:
        print(f"\n👤 Testing role: {role}")
        pipeline = get_cached_pipeline(role)
        
        for i, query in enumerate(test_queries):
            print(f"\n   Query {i+1}: {query[:50]}...")
            
            # First run (should be cache miss)
            start_time = time.time()
            result1 = pipeline.run_pipeline(query, use_cache=True)
            time1 = time.time() - start_time
            
            # Second run (should be cache hit)
            start_time = time.time()
            result2 = pipeline.run_pipeline(query, use_cache=True)
            time2 = time.time() - start_time
            
            print(f"   First run: {time1*1000:.1f}ms (cache: {result1.get('performance', {}).get('cache_hit', False)})")
            print(f"   Second run: {time2*1000:.1f}ms (cache: {result2.get('performance', {}).get('cache_hit', False)})")
            
            if result2.get('performance', {}).get('cache_hit'):
                speedup = time1 / time2 if time2 > 0 else 0
                print(f"   ⚡ Speedup: {speedup:.1f}x faster")
            
            # Check for errors
            if result1.get('error'):
                print(f"   ⚠️  Error: {result1['error']}")
        
        # Show pipeline stats
        stats = pipeline.get_cache_statistics()
        print(f"\n   📈 Pipeline Stats for {role}:")
        print(f"      Total queries: {stats['pipeline_stats']['total_queries']}")
        print(f"      Cache hits: {stats['pipeline_stats']['cache_hits']}")
        print(f"      Hit rate: {stats['cache_efficiency']['hit_rate']:.1f}%")


def test_cache_management():
    """Test cache management operations"""
    print("\n🛠️  Testing Cache Management...")
    
    cache = RedisSearchCache()
    
    # Test cache clear for specific role
    print("🗑️  Testing role-specific cache clear...")
    deleted = cache.invalidate_user_cache("Marketing")
    print(f"Deleted {deleted} entries for Marketing role")
    
    # Test query-specific cache clear
    print("🗑️  Testing query-specific cache clear...")
    test_query = "What are our marketing performance metrics?"
    deleted = cache.invalidate_query_cache(test_query)
    print(f"Deleted {deleted} entries for query: {test_query[:50]}...")
    
    # Test cache warmup
    print("🔥 Testing cache warmup...")
    pipeline = get_cached_pipeline("C-Level")
    warmup_queries = [
        "What are our quarterly results?",
        "Show me the latest financial data",
        "What is our current market position?"
    ]
    
    warmup_result = pipeline.warm_cache(warmup_queries)
    print(f"Warmed {warmup_result['warmed_queries']} queries")
    if warmup_result['failed_queries'] > 0:
        print(f"Failed to warm {warmup_result['failed_queries']} queries")
        for error in warmup_result['errors']:
            print(f"   Error: {error}")


def main():
    """Run all tests"""
    print("🚀 FinSolve Redis Cache Test Suite")
    print("=" * 50)
    
    # Test Redis connection
    redis_connected = test_redis_connection()
    
    # Test basic cache operations
    cache_working = test_cache_operations()
    
    if cache_working:
        # Test cached pipeline
        test_cached_pipeline()
        
        # Test cache management
        test_cache_management()
    else:
        print("\n❌ Cache operations failed, skipping pipeline tests")
    
    print("\n" + "=" * 50)
    print("🏁 Test suite completed!")
    
    if redis_connected and cache_working:
        print("✅ All tests passed! Redis cache is working correctly.")
        print("\n💡 Next steps:")
        print("   1. Install Redis server if not already running")
        print("   2. Update your .env file with Redis connection details")
        print("   3. Start using the cached endpoints in your application")
        print("   4. Monitor cache performance with /api/v1/cache/stats")
    else:
        print("⚠️  Some tests failed. Check Redis installation and configuration.")
        print("\n🔧 Troubleshooting:")
        print("   1. Install Redis: https://redis.io/download")
        print("   2. Start Redis server: redis-server")
        print("   3. Check Redis connection: redis-cli ping")
        print("   4. Verify .env configuration")


if __name__ == "__main__":
    main()