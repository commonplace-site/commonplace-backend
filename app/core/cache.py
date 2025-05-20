from typing import Any, Optional
import json
import redis
from app.core.config import settings

class Cache:
    def __init__(self):
        self.redis = redis.Redis.from_url(settings.REDIS_URL)
        self.default_expire = 300  # 5 minutes

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        value = self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ):
        """Set value in cache with optional expiration"""
        self.redis.setex(
            key,
            expire or self.default_expire,
            json.dumps(value)
        )

    async def delete(self, key: str):
        """Delete value from cache"""
        self.redis.delete(key)

    async def invalidate_memory_cache(self, business_id: str):
        """Invalidate all memory-related caches for a business"""
        pattern = f"memory:*:{business_id}:*"
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)

    async def invalidate_user_cache(self, user_id: str):
        """Invalidate all user-related caches"""
        pattern = f"user:*:{user_id}:*"
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)

    async def get_or_set(
        self,
        key: str,
        getter_func,
        expire: Optional[int] = None
    ) -> Any:
        """Get value from cache or set it using the getter function"""
        value = await self.get(key)
        if value is None:
            value = await getter_func()
            await self.set(key, value, expire)
        return value 