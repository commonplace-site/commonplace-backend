import redis
from app.core.config import settings
import json
import logging
from typing import Any, Optional, Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)

class RedisService:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            ssl=settings.REDIS_SSL,
            decode_responses=True
        )
        
    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set a key-value pair in Redis"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            return self.redis_client.set(key, value, ex=expire)
        except Exception as e:
            logger.error(f"Redis set error: {str(e)}")
            return False
            
    async def get(self, key: str) -> Any:
        """Get a value from Redis"""
        try:
            value = self.redis_client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            logger.error(f"Redis get error: {str(e)}")
            return None
            
    async def delete(self, key: str) -> bool:
        """Delete a key from Redis"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Redis delete error: {str(e)}")
            return False
            
    async def exists(self, key: str) -> bool:
        """Check if a key exists in Redis"""
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Redis exists error: {str(e)}")
            return False
            
    async def set_hash(self, name: str, mapping: Dict[str, Any]) -> bool:
        """Set a hash in Redis"""
        try:
            return bool(self.redis_client.hset(name, mapping=mapping))
        except Exception as e:
            logger.error(f"Redis set_hash error: {str(e)}")
            return False
            
    async def get_hash(self, name: str) -> Dict[str, Any]:
        """Get a hash from Redis"""
        try:
            return self.redis_client.hgetall(name)
        except Exception as e:
            logger.error(f"Redis get_hash error: {str(e)}")
            return {}
            
    async def add_to_list(self, name: str, value: Any) -> bool:
        """Add a value to a Redis list"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            return bool(self.redis_client.rpush(name, value))
        except Exception as e:
            logger.error(f"Redis add_to_list error: {str(e)}")
            return False
            
    async def get_list(self, name: str, start: int = 0, end: int = -1) -> List[Any]:
        """Get a list from Redis"""
        try:
            values = self.redis_client.lrange(name, start, end)
            return [json.loads(v) if v.startswith('{') or v.startswith('[') else v for v in values]
        except Exception as e:
            logger.error(f"Redis get_list error: {str(e)}")
            return []
            
    async def log_audit(self, action: str, user_id: str, details: Dict[str, Any]) -> bool:
        """Log an audit event to Redis"""
        try:
            audit_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "action": action,
                "user_id": user_id,
                "details": details
            }
            return await self.add_to_list("audit_log", audit_entry)
        except Exception as e:
            logger.error(f"Redis audit log error: {str(e)}")
            return False
            
    async def get_audit_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent audit logs"""
        try:
            return await self.get_list("audit_log", start=-limit, end=-1)
        except Exception as e:
            logger.error(f"Redis get_audit_logs error: {str(e)}")
            return []

# Create a singleton instance
redis_service = RedisService() 