import redis.asyncio as redis
from app.config import get_settings
import json

settings = get_settings()

class RedisService:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def close(self):
        await self.redis.close()

    async def push_to_queue(self, queue_name: str, message: dict):
        """Push a message to a Redis list (queue)."""
        await self.redis.rpush(queue_name, json.dumps(message))

    async def pop_from_queue(self, queue_name: str):
        """Pop a message from a Redis list (queue)."""
        # blpop returns a tuple (queue_name, data) or None
        item = await self.redis.blpop(queue_name, timeout=1)
        if item:
            return json.loads(item[1])
        return None

    async def set_value(self, key: str, value: str, ttl: int = None):
        """Set a value in Redis with optional TTL."""
        await self.redis.set(key, value, ex=ttl)

    async def get_value(self, key: str):
        """Get a value from Redis."""
        return await self.redis.get(key)

    async def publish(self, channel: str, message: dict):
        """Publish a message to a Redis channel."""
        await self.redis.publish(channel, json.dumps(message))

    async def subscribe(self, channel: str):
        """Subscribe to a Redis channel."""
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel)
        return pubsub

redis_client = RedisService()
