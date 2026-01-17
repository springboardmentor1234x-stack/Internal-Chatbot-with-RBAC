"""
Redis Cache Manager for FinSolve RAG Pipeline
Provides intelligent caching for search results, embeddings, and responses.
"""

import redis
import json
import hashlib
import pickle
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class CacheConfig:
    """Configuration for Redis cache settings"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    decode_responses: bool = True
    
    # Cache TTL settings (in seconds)
    search_results_ttl: int = 3600  # 1 hour
    embeddings_ttl: int = 86400     # 24 hours
    responses_ttl: int = 1800       # 30 minutes
    user_sessions_ttl: int = 7200   # 2 hours
    
    # Cache key prefixes
    search_prefix: str = "search:"
    embedding_prefix: str = "embed:"
    response_prefix: str = "response:"
    session_prefix: str = "session:"
    analytics_prefix: str = "analytics:"


class RedisSearchCache:
    """
    Redis-based cache manager for RAG pipeline search results.
    Provides intelligent caching with role-based access control.
    """
    
    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self._setup_redis_connection()
        self._cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
    
    def _setup_redis_connection(self):
        """Initialize Redis connection with error handling"""
        try:
            # Get Redis config from environment variables
            redis_host = os.getenv("REDIS_HOST", self.config.host)
            redis_port = int(os.getenv("REDIS_PORT", self.config.port))
            redis_password = os.getenv("REDIS_PASSWORD", self.config.password)
            redis_db = int(os.getenv("REDIS_DB", self.config.db))
            
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                password=redis_password,
                decode_responses=self.config.decode_responses,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            self.redis_client.ping()
            print(f"✅ Redis connected: {redis_host}:{redis_port}")
            
        except redis.ConnectionError as e:
            print(f"❌ Redis connection failed: {e}")
            print("🔄 Falling back to in-memory cache")
            self.redis_client = None
            self._fallback_cache = {}
        except Exception as e:
            print(f"❌ Redis setup error: {e}")
            self.redis_client = None
            self._fallback_cache = {}
    
    def _generate_cache_key(self, query: str, user_role: str, cache_type: str = "search") -> str:
        """Generate a unique cache key based on query, role, and type"""
        # Create a hash of the query and role for consistent keys
        content = f"{query.lower().strip()}:{user_role}:{cache_type}"
        hash_key = hashlib.md5(content.encode()).hexdigest()
        
        prefix_map = {
            "search": self.config.search_prefix,
            "embedding": self.config.embedding_prefix,
            "response": self.config.response_prefix,
            "session": self.config.session_prefix,
            "analytics": self.config.analytics_prefix
        }
        
        prefix = prefix_map.get(cache_type, "cache:")
        return f"{prefix}{hash_key}"
    
    def _serialize_data(self, data: Any) -> str:
        """Serialize data for Redis storage"""
        try:
            if isinstance(data, (dict, list)):
                return json.dumps(data, default=str)
            else:
                return pickle.dumps(data).hex()
        except Exception as e:
            print(f"Serialization error: {e}")
            return json.dumps({"error": "serialization_failed"})
    
    def _deserialize_data(self, data: str) -> Any:
        """Deserialize data from Redis storage"""
        try:
            # Try JSON first
            return json.loads(data)
        except json.JSONDecodeError:
            try:
                # Try pickle if JSON fails
                return pickle.loads(bytes.fromhex(data))
            except Exception as e:
                print(f"Deserialization error: {e}")
                return None
    
    def get_search_results(self, query: str, user_role: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached search results for a query and role"""
        if not self.redis_client:
            return self._fallback_cache.get(self._generate_cache_key(query, user_role))
        
        try:
            cache_key = self._generate_cache_key(query, user_role, "search")
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                self._cache_stats["hits"] += 1
                result = self._deserialize_data(cached_data)
                
                # Add cache metadata
                if isinstance(result, dict):
                    result["cache_info"] = {
                        "cached": True,
                        "cache_key": cache_key,
                        "retrieved_at": datetime.now().isoformat()
                    }
                
                return result
            else:
                self._cache_stats["misses"] += 1
                return None
                
        except Exception as e:
            print(f"Cache retrieval error: {e}")
            self._cache_stats["misses"] += 1
            return None
    
    def cache_search_results(self, query: str, user_role: str, results: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Cache search results with optional TTL"""
        if not self.redis_client:
            self._fallback_cache[self._generate_cache_key(query, user_role)] = results
            return True
        
        try:
            cache_key = self._generate_cache_key(query, user_role, "search")
            ttl = ttl or self.config.search_results_ttl
            
            # Add cache metadata to results
            cached_results = results.copy()
            cached_results["cache_info"] = {
                "cached_at": datetime.now().isoformat(),
                "ttl": ttl,
                "cache_key": cache_key,
                "query_hash": hashlib.md5(query.encode()).hexdigest()
            }
            
            serialized_data = self._serialize_data(cached_results)
            success = self.redis_client.setex(cache_key, ttl, serialized_data)
            
            if success:
                self._cache_stats["sets"] += 1
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Cache storage error: {e}")
            return False
    
    def cache_response(self, query: str, user_role: str, response: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Cache complete response including accuracy metrics"""
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._generate_cache_key(query, user_role, "response")
            ttl = ttl or self.config.responses_ttl
            
            # Add response cache metadata
            cached_response = response.copy()
            cached_response["response_cache_info"] = {
                "cached_at": datetime.now().isoformat(),
                "ttl": ttl,
                "response_cache_key": cache_key
            }
            
            serialized_data = self._serialize_data(cached_response)
            success = self.redis_client.setex(cache_key, ttl, serialized_data)
            
            if success:
                self._cache_stats["sets"] += 1
            
            return success
            
        except Exception as e:
            print(f"Response cache error: {e}")
            return False
    
    def get_cached_response(self, query: str, user_role: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached complete response"""
        if not self.redis_client:
            return None
        
        try:
            cache_key = self._generate_cache_key(query, user_role, "response")
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                self._cache_stats["hits"] += 1
                result = self._deserialize_data(cached_data)
                
                if isinstance(result, dict):
                    result["response_cache_info"]["retrieved_at"] = datetime.now().isoformat()
                
                return result
            else:
                self._cache_stats["misses"] += 1
                return None
                
        except Exception as e:
            print(f"Response cache retrieval error: {e}")
            return None
    
    def invalidate_user_cache(self, user_role: str) -> int:
        """Invalidate all cache entries for a specific user role"""
        if not self.redis_client:
            return 0
        
        try:
            # Find all keys for this role
            pattern = f"*:{user_role}:*"
            keys = self.redis_client.keys(pattern)
            
            if keys:
                deleted = self.redis_client.delete(*keys)
                self._cache_stats["deletes"] += deleted
                return deleted
            
            return 0
            
        except Exception as e:
            print(f"Cache invalidation error: {e}")
            return 0
    
    def invalidate_query_cache(self, query: str) -> int:
        """Invalidate cache entries for a specific query across all roles"""
        if not self.redis_client:
            return 0
        
        try:
            query_hash = hashlib.md5(query.lower().strip().encode()).hexdigest()
            pattern = f"*{query_hash}*"
            keys = self.redis_client.keys(pattern)
            
            if keys:
                deleted = self.redis_client.delete(*keys)
                self._cache_stats["deletes"] += deleted
                return deleted
            
            return 0
            
        except Exception as e:
            print(f"Query cache invalidation error: {e}")
            return 0
    
    def clear_all_cache(self) -> bool:
        """Clear all cache entries (use with caution)"""
        if not self.redis_client:
            self._fallback_cache.clear()
            return True
        
        try:
            self.redis_client.flushdb()
            self._cache_stats = {"hits": 0, "misses": 0, "sets": 0, "deletes": 0}
            return True
        except Exception as e:
            print(f"Cache clear error: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        stats = self._cache_stats.copy()
        
        if self.redis_client:
            try:
                info = self.redis_client.info()
                stats.update({
                    "redis_connected": True,
                    "redis_memory_used": info.get("used_memory_human", "unknown"),
                    "redis_keys": self.redis_client.dbsize(),
                    "redis_uptime": info.get("uptime_in_seconds", 0)
                })
            except Exception as e:
                stats["redis_error"] = str(e)
        else:
            stats.update({
                "redis_connected": False,
                "fallback_cache_size": len(getattr(self, '_fallback_cache', {}))
            })
        
        # Calculate hit rate
        total_requests = stats["hits"] + stats["misses"]
        stats["hit_rate"] = (stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return stats
    
    def health_check(self) -> Dict[str, Any]:
        """Perform cache health check"""
        health = {
            "status": "healthy",
            "redis_connected": False,
            "response_time_ms": None,
            "errors": []
        }
        
        if self.redis_client:
            try:
                start_time = datetime.now()
                self.redis_client.ping()
                end_time = datetime.now()
                
                health["redis_connected"] = True
                health["response_time_ms"] = (end_time - start_time).total_seconds() * 1000
                
            except Exception as e:
                health["status"] = "degraded"
                health["errors"].append(f"Redis ping failed: {e}")
        else:
            health["status"] = "degraded"
            health["errors"].append("Redis not connected, using fallback cache")
        
        return health


# Global cache instance
cache_config = CacheConfig()
search_cache = RedisSearchCache(cache_config)


def get_search_cache() -> RedisSearchCache:
    """Get the global search cache instance"""
    return search_cache