# Redis Cache Implementation for FinSolve RAG Pipeline

## Overview

This implementation adds intelligent Redis caching to your FinSolve RAG pipeline, providing significant performance improvements by caching search results, embeddings, and complete responses.

## Features

### 🚀 Performance Benefits
- **Search Result Caching**: Cache vector database queries to avoid repeated expensive operations
- **Response Caching**: Cache complete responses including accuracy metrics
- **Role-Based Caching**: Separate cache entries for different user roles
- **Intelligent TTL**: Different expiration times for different data types
- **Fallback Support**: Automatic fallback to in-memory cache if Redis is unavailable

### 🔧 Cache Management
- **Cache Statistics**: Monitor hit rates, performance metrics, and Redis health
- **Cache Warmup**: Pre-populate cache with common queries
- **Selective Clearing**: Clear cache by user role or specific queries
- **Admin Controls**: Full cache management for administrators

### 🛡️ Security & Reliability
- **Role-Based Access**: Cache respects user role permissions
- **Error Handling**: Graceful degradation when Redis is unavailable
- **Health Monitoring**: Comprehensive health checks and diagnostics
- **Connection Pooling**: Efficient Redis connection management

## Installation & Setup

### 1. Install Redis

#### Windows (using Chocolatey)
```bash
choco install redis-64
```

#### Windows (using WSL)
```bash
sudo apt update
sudo apt install redis-server
```

#### macOS (using Homebrew)
```bash
brew install redis
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install redis-server
```

### 2. Start Redis Server

```bash
# Start Redis server
redis-server

# Test Redis connection
redis-cli ping
# Should return: PONG
```

### 3. Install Python Dependencies

The Redis dependencies are already added to your `requirements.txt`:

```bash
pip install redis==5.0.1 hiredis==2.2.3
```

### 4. Configure Environment Variables

Update your `.env` file with Redis configuration (already added):

```env
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
```

### 5. Test the Implementation

Run the test script to verify everything is working:

```bash
python test_redis_cache.py
```

## Usage

### Basic Usage in Your Application

The cache is automatically integrated into your existing chat endpoint. No code changes needed for basic functionality!

```python
# Your existing chat endpoint now uses caching automatically
POST /api/v1/chat
{
    "query": "What are our quarterly financial results?"
}
```

### Cache Management Endpoints

#### Get Cache Statistics
```bash
GET /api/v1/cache/stats
```

Response includes:
- Hit/miss rates
- Performance metrics
- Redis health status
- Cache efficiency data

#### Clear User Cache
```bash
POST /api/v1/cache/clear
```

Clears all cache entries for the current user's role.

#### Clear Query-Specific Cache
```bash
POST /api/v1/cache/clear/query
{
    "query": "specific query to clear"
}
```

#### Warm Up Cache
```bash
POST /api/v1/cache/warmup
{
    "queries": [
        "What are our quarterly results?",
        "Show me marketing performance",
        "What are the HR policies?"
    ],
    "force_refresh": false
}
```

#### Cache Health Check
```bash
GET /api/v1/cache/health
```

### Advanced Usage

#### Using Cached Pipeline Directly

```python
from app.rag_pipeline_cached import get_cached_pipeline

# Get cached pipeline for specific role
pipeline = get_cached_pipeline("C-Level")

# Run query with caching
result = pipeline.run_pipeline("What are our financial results?", use_cache=True)

# Run query without caching (force fresh data)
result = pipeline.run_pipeline("What are our financial results?", use_cache=False)

# Get performance statistics
stats = pipeline.get_cache_statistics()
print(f"Cache hit rate: {stats['cache_efficiency']['hit_rate']:.1f}%")
```

#### Custom Cache Configuration

```python
from app.redis_cache import RedisSearchCache, CacheConfig

# Custom cache configuration
config = CacheConfig(
    host="your-redis-host",
    port=6379,
    search_results_ttl=7200,  # 2 hours
    responses_ttl=3600,       # 1 hour
)

cache = RedisSearchCache(config)
```

## Cache Configuration

### TTL (Time To Live) Settings

| Cache Type | Default TTL | Description |
|------------|-------------|-------------|
| Search Results | 1 hour | Vector database query results |
| Responses | 30 minutes | Complete chat responses |
| Embeddings | 24 hours | Document embeddings |
| User Sessions | 2 hours | User session data |

### Cache Key Structure

```
search:{hash}     - Search results
response:{hash}   - Complete responses  
embed:{hash}      - Embeddings
session:{hash}    - Session data
analytics:{hash}  - Analytics data
```

## Performance Monitoring

### Key Metrics to Monitor

1. **Hit Rate**: Percentage of requests served from cache
2. **Response Time**: Average response time improvement
3. **Memory Usage**: Redis memory consumption
4. **Cache Size**: Number of cached entries

### Monitoring Endpoints

```bash
# Get comprehensive statistics
GET /api/v1/cache/stats

# Check Redis health
GET /api/v1/cache/health

# List cache keys (admin only)
GET /api/v1/cache/keys?pattern=search:*&limit=50
```

## Troubleshooting

### Common Issues

#### 1. Redis Connection Failed
```
❌ Redis connection failed: [Errno 111] Connection refused
```

**Solution**: 
- Ensure Redis server is running: `redis-server`
- Check Redis is listening on correct port: `redis-cli ping`
- Verify firewall settings

#### 2. Cache Not Working
```
⚠️ Redis not connected, using fallback cache
```

**Solution**:
- Check Redis configuration in `.env`
- Verify Redis server is accessible
- Check network connectivity

#### 3. Permission Denied
```
❌ Redis setup error: NOAUTH Authentication required
```

**Solution**:
- Set `REDIS_PASSWORD` in `.env` if Redis requires authentication
- Check Redis ACL settings

### Performance Optimization

#### 1. Optimize TTL Settings
```python
# Adjust TTL based on your data update frequency
config = CacheConfig(
    search_results_ttl=3600,  # Increase for stable data
    responses_ttl=1800,       # Decrease for dynamic data
)
```

#### 2. Monitor Memory Usage
```bash
# Check Redis memory usage
redis-cli info memory

# Set memory limit if needed
redis-cli config set maxmemory 256mb
redis-cli config set maxmemory-policy allkeys-lru
```

#### 3. Use Cache Warmup
```python
# Pre-populate cache with common queries
common_queries = [
    "What are our quarterly results?",
    "Show me marketing performance",
    "What are the latest financial metrics?"
]

pipeline = get_cached_pipeline("C-Level")
pipeline.warm_cache(common_queries)
```

## Production Considerations

### 1. Redis Configuration
```bash
# /etc/redis/redis.conf
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### 2. Monitoring & Alerting
- Monitor Redis memory usage
- Set up alerts for cache hit rate drops
- Monitor Redis connection health
- Track response time improvements

### 3. Backup & Recovery
```bash
# Enable Redis persistence
save 900 1
appendonly yes
appendfsync everysec
```

### 4. Security
```bash
# Set Redis password
requirepass your_secure_password

# Bind to specific interface
bind 127.0.0.1

# Disable dangerous commands
rename-command FLUSHDB ""
rename-command FLUSHALL ""
```

## API Reference

### Cache Management Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/cache/stats` | GET | Get cache statistics |
| `/cache/clear` | POST | Clear user role cache |
| `/cache/clear/query` | POST | Clear specific query cache |
| `/cache/warmup` | POST | Pre-populate cache |
| `/cache/health` | GET | Check cache health |
| `/cache/keys` | GET | List cache keys (admin) |
| `/cache/admin/clear-all` | POST | Clear all cache (admin) |

### Response Format

```json
{
    "cache_statistics": {
        "pipeline_stats": {
            "cache_hits": 45,
            "cache_misses": 12,
            "total_queries": 57,
            "vector_searches": 12
        },
        "cache_stats": {
            "hits": 45,
            "misses": 12,
            "hit_rate": 78.9,
            "redis_connected": true,
            "redis_memory_used": "2.1M",
            "redis_keys": 23
        }
    },
    "cache_health": {
        "status": "healthy",
        "redis_connected": true,
        "response_time_ms": 1.2
    }
}
```

## Benefits Summary

### Performance Improvements
- **50-90% faster response times** for cached queries
- **Reduced OpenAI API calls** through response caching
- **Lower database load** through search result caching
- **Improved user experience** with faster responses

### Cost Savings
- **Reduced API costs** by avoiding duplicate OpenAI calls
- **Lower infrastructure costs** through reduced compute load
- **Improved scalability** with better resource utilization

### Operational Benefits
- **Better monitoring** with comprehensive cache metrics
- **Flexible management** with role-based cache control
- **Graceful degradation** when Redis is unavailable
- **Easy maintenance** with built-in cache management tools

## Next Steps

1. **Install and configure Redis** following the setup guide
2. **Run the test script** to verify functionality
3. **Monitor cache performance** using the statistics endpoints
4. **Optimize TTL settings** based on your usage patterns
5. **Set up monitoring** for production deployment
6. **Configure cache warmup** for common queries

For questions or issues, check the troubleshooting section or review the test script output for diagnostic information.