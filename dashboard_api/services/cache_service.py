from typing import Optional, Any, Dict
import json
import hashlib
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class CacheService:
    """Simple in-memory cache service for Phase 1"""
    
    def __init__(self):
        # Cache storage with TTL
        self._cache: Dict[str, Dict[str, Any]] = {}
        
        # Cache TTL settings (in seconds)
        self.ttl_settings = {
            "user_profile": 900,     # 15 minutes
            "user_scores": 180,      # 3 minutes
            "health_check": 60,      # 1 minute
            "user_list": 300,        # 5 minutes
            "analysis_data": 3600,   # 1 hour (for Phase 2)
        }
        
        # Statistics
        self.hit_count = 0
        self.miss_count = 0
        
        logger.info("CacheService initialized")
    
    def _generate_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key from parameters"""
        key_data = f"{prefix}:{json.dumps(kwargs, sort_keys=True, default=str)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _is_expired(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is expired"""
        expiry_time = cache_entry.get("expiry")
        if not expiry_time:
            return True
        return datetime.now() > expiry_time
    
    def _set_cache(self, key: str, value: Any, cache_type: str) -> None:
        """Set cache entry with TTL"""
        ttl = self.ttl_settings.get(cache_type, 300)  # Default 5 minutes
        expiry = datetime.now() + timedelta(seconds=ttl)
        
        self._cache[key] = {
            "value": value,
            "expiry": expiry,
            "cache_type": cache_type,
            "created": datetime.now()
        }
        
        logger.debug(f"Cached {cache_type} with key {key[:8]}... for {ttl} seconds")
    
    def _get_cache(self, key: str) -> Optional[Any]:
        """Get cache entry if not expired"""
        if key not in self._cache:
            self.miss_count += 1
            return None
        
        cache_entry = self._cache[key]
        
        if self._is_expired(cache_entry):
            del self._cache[key]
            self.miss_count += 1
            logger.debug(f"Cache expired for key {key[:8]}...")
            return None
        
        self.hit_count += 1
        logger.debug(f"Cache hit for key {key[:8]}...")
        return cache_entry["value"]
    
    async def get_user_profile(self, profile_id: str) -> Optional[Any]:
        """Get cached user profile data"""
        key = self._generate_key("user_profile", profile_id=profile_id)
        return self._get_cache(key)
    
    async def set_user_profile(self, profile_id: str, data: Any) -> None:
        """Cache user profile data"""
        key = self._generate_key("user_profile", profile_id=profile_id)
        self._set_cache(key, data, "user_profile")
    
    async def get_user_scores(self, profile_id: str) -> Optional[Any]:
        """Get cached user health scores"""
        key = self._generate_key("user_scores", profile_id=profile_id)
        return self._get_cache(key)
    
    async def set_user_scores(self, profile_id: str, data: Any) -> None:
        """Cache user health scores"""
        key = self._generate_key("user_scores", profile_id=profile_id)
        self._set_cache(key, data, "user_scores")
    
    async def get_user_list(self, limit: int, offset: int) -> Optional[Any]:
        """Get cached user list"""
        key = self._generate_key("user_list", limit=limit, offset=offset)
        return self._get_cache(key)
    
    async def set_user_list(self, limit: int, offset: int, data: Any) -> None:
        """Cache user list"""
        key = self._generate_key("user_list", limit=limit, offset=offset)
        self._set_cache(key, data, "user_list")
    
    async def get_health_check(self) -> Optional[Any]:
        """Get cached health check result"""
        key = self._generate_key("health_check")
        return self._get_cache(key)
    
    async def set_health_check(self, data: Any) -> None:
        """Cache health check result"""
        key = self._generate_key("health_check")
        self._set_cache(key, data, "health_check")
    
    # Generic cache methods for Phase 2
    async def get(self, cache_key: str) -> Optional[Any]:
        """Generic get method for custom cache keys"""
        return self._get_cache(cache_key)
    
    async def set(self, cache_key: str, data: Any, ttl: int = None) -> None:
        """Generic set method for custom cache keys with optional TTL"""
        if ttl:
            # Use custom TTL
            expiry = datetime.now() + timedelta(seconds=ttl)
            self._cache[cache_key] = {
                "value": data,
                "expiry": expiry,
                "cache_type": "custom",
                "created": datetime.now()
            }
            logger.debug(f"Cached custom entry with key {cache_key[:8]}... for {ttl} seconds")
        else:
            # Use default analysis_data TTL
            self._set_cache(cache_key, data, "analysis_data")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0
        
        # Clean up expired entries for accurate count
        expired_keys = []
        for key, entry in self._cache.items():
            if self._is_expired(entry):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
        
        return {
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate_percent": round(hit_rate, 2),
            "total_requests": total_requests,
            "cached_entries": len(self._cache),
            "cache_types": {
                cache_type: len([k for k, v in self._cache.items() if v.get("cache_type") == cache_type])
                for cache_type in list(self.ttl_settings.keys()) + ["custom"]
            }
        }
    
    def clear_cache(self, cache_type: Optional[str] = None) -> None:
        """Clear cache entries"""
        if cache_type:
            keys_to_remove = [k for k, v in self._cache.items() if v.get("cache_type") == cache_type]
            for key in keys_to_remove:
                del self._cache[key]
            logger.info(f"Cleared {len(keys_to_remove)} entries for cache type: {cache_type}")
        else:
            self._cache.clear()
            logger.info("Cleared all cache entries")
    
    def cleanup_expired(self) -> int:
        """Remove expired cache entries"""
        expired_keys = []
        for key, entry in self._cache.items():
            if self._is_expired(entry):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)