"""
Simple cache service for frequently accessed data
"""
import time
import logging
from typing import Optional, Any, Callable
from functools import wraps

logger = logging.getLogger(__name__)


class CacheService:
    """Simple in-memory cache service"""
    
    _cache = {}
    _default_ttl = 300  # 5 minutes default TTL
    
    @staticmethod
    def get(key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if expired/not found
        """
        if key not in CacheService._cache:
            return None
        
        entry = CacheService._cache[key]
        if time.time() > entry['expires_at']:
            # Expired, remove it
            del CacheService._cache[key]
            return None
        
        return entry['value']
    
    @staticmethod
    def set(key: str, value: Any, ttl: int = None) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 5 minutes)
        """
        if ttl is None:
            ttl = CacheService._default_ttl
        
        CacheService._cache[key] = {
            'value': value,
            'expires_at': time.time() + ttl,
            'created_at': time.time()
        }
    
    @staticmethod
    def delete(key: str) -> None:
        """Delete key from cache"""
        if key in CacheService._cache:
            del CacheService._cache[key]
    
    @staticmethod
    def clear() -> None:
        """Clear all cache"""
        CacheService._cache.clear()
    
    @staticmethod
    def cached(ttl: int = None, key_prefix: str = ""):
        """
        Decorator for caching function results.
        
        Args:
            ttl: Time to live in seconds
            key_prefix: Prefix for cache key
            
        Usage:
            @CacheService.cached(ttl=300)
            def get_user_data(user_id):
                ...
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key from function name and arguments
                cache_key = f"{key_prefix}{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
                
                # Try to get from cache
                cached_value = CacheService.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit: {cache_key}")
                    return cached_value
                
                # Cache miss, call function
                logger.debug(f"Cache miss: {cache_key}")
                result = func(*args, **kwargs)
                
                # Store in cache
                CacheService.set(cache_key, result, ttl)
                
                return result
            
            return wrapper
        return decorator
    
    @staticmethod
    def get_cache_stats() -> dict:
        """Get cache statistics"""
        now = time.time()
        total = len(CacheService._cache)
        expired = sum(1 for entry in CacheService._cache.values() if now > entry['expires_at'])
        active = total - expired
        
        return {
            'total_keys': total,
            'active_keys': active,
            'expired_keys': expired
        }
