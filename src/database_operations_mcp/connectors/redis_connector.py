"""Redis database connector."""

from typing import Any, Dict, List, Optional

try:
    import redis.asyncio as aioredis
except ImportError:
    aioredis = None


class RedisConnector:
    """Redis database connector.

    Provides async connection to Redis with key-value operations,
    pub/sub, and data structure support.
    """

    def __init__(self):
        """Initialize Redis connector."""
        self.client: Optional[Any] = None

    async def connect(
        self,
        host: str = "localhost",
        port: int = 6379,
        password: Optional[str] = None,
        db: int = 0,
    ) -> Any:
        """Connect to Redis database.

        Args:
            host: Redis host address
            port: Redis port (default: 6379)
            password: Redis password
            db: Database number (0-15)

        Returns:
            Redis client object

        Raises:
            RuntimeError: If aioredis not installed
        """
        if aioredis is None:
            raise RuntimeError("redis not installed. Install with: pip install redis")

        self.client = aioredis.from_url(
            f"redis://:{password}@{host}:{port}/{db}"
            if password
            else f"redis://{host}:{port}/{db}",
            decode_responses=True,
        )

        return self.client

    async def get_value(self, key: str) -> Any:
        """Get value by key.

        Args:
            key: Redis key

        Returns:
            Value stored at key
        """
        if not self.client:
            raise RuntimeError("Not connected to Redis")

        return await self.client.get(key)

    async def set_value(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set key-value pair.

        Args:
            key: Redis key
            value: Value to store
            ttl: Time to live in seconds

        Returns:
            True if successful
        """
        if not self.client:
            raise RuntimeError("Not connected to Redis")

        result = await self.client.set(key, value, ex=ttl)
        return result

    async def delete_key(self, key: str) -> int:
        """Delete key.

        Args:
            key: Redis key to delete

        Returns:
            Number of keys deleted
        """
        if not self.client:
            raise RuntimeError("Not connected to Redis")

        return await self.client.delete(key)

    async def get_keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern.

        Args:
            pattern: Key pattern (supports wildcards)

        Returns:
            List of matching keys
        """
        if not self.client:
            raise RuntimeError("Not connected to Redis")

        return await self.client.keys(pattern)

    async def get_info(self) -> Dict[str, Any]:
        """Get Redis server information.

        Returns:
            Dictionary of server information
        """
        if not self.client:
            raise RuntimeError("Not connected to Redis")

        info = await self.client.info()
        return dict(info)

    async def close(self):
        """Close Redis connection."""
        if self.client:
            await self.client.close()
