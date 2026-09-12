"""Redis database connector."""

from typing import Any

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
        self.client: Any | None = None

    async def connect(
        self,
        host: str = "localhost",
        port: int = 6379,
        password: str | None = None,
        db: int = 0,
    ) -> Any:
        """Connect to Redis database.

        ## Return Format
        Returns the Redis client object.

        ## Examples
        Connect locally:
            client = await connector.connect()
        """
        if aioredis is None:
            raise RuntimeError("redis not installed. Install with: pip install redis")

        self.client = aioredis.from_url(
            f"redis://:{password}@{host}:{port}/{db}" if password else f"redis://{host}:{port}/{db}",
            decode_responses=True,
        )

        return self.client

    async def get_value(self, key: str) -> Any:
        """Get value by key.

        ## Return Format
        Returns the stored value (or None).

        ## Examples
        Read a key:
            value = await connector.get_value("session:1")
        """
        if not self.client:
            raise RuntimeError("Not connected to Redis")

        return await self.client.get(key)

    async def set_value(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """Set key-value pair.

        ## Return Format
        Returns True on success.

        ## Examples
        Store a key:
            ok = await connector.set_value("session:1", "abc", ttl=3600)
        """
        if not self.client:
            raise RuntimeError("Not connected to Redis")

        result = await self.client.set(key, value, ex=ttl)
        return result

    async def delete_key(self, key: str) -> int:
        """Delete key.

        ## Return Format
        Returns the number of keys deleted.

        ## Examples
        Delete a key:
            n = await connector.delete_key("session:1")
        """
        if not self.client:
            raise RuntimeError("Not connected to Redis")

        return await self.client.delete(key)

    async def get_keys(self, pattern: str = "*") -> list[str]:
        """Get keys matching pattern.

        ## Return Format
        Returns the list of matching keys.

        ## Examples
        List session keys:
            keys = await connector.get_keys("session:*")
        """
        if not self.client:
            raise RuntimeError("Not connected to Redis")

        return await self.client.keys(pattern)

    async def get_info(self) -> dict[str, Any]:
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
