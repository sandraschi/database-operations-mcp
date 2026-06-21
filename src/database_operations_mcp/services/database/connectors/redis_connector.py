"""
Redis database connector implementation.

Provides async access to Redis with key-value operations.
"""

import logging
from datetime import datetime
from typing import Any

try:
    import redis.asyncio as aioredis
except ImportError:
    aioredis = None

from ....database_manager import (
    BaseDatabaseConnector,
    ConnectionStatus,
    DatabaseType,
    QueryResult,
)

logger = logging.getLogger(__name__)


class RedisConnector(BaseDatabaseConnector):
    """Redis database connector."""

    @property
    def database_type(self) -> DatabaseType:
        """Return the database type."""
        return DatabaseType.REDIS

    def __init__(self, connection_config: dict[str, Any]):
        """Initialize Redis connector.

        Args:
            connection_config: Must contain connection parameters
                - host: Redis server host
                - port: Redis server port (default: 6379)
                - password: Password (optional)
                - db: Database number (default: 0)
        """
        super().__init__(connection_config)
        self.host = connection_config.get("host", "localhost")
        self.port = connection_config.get("port", 6379)
        self.password = connection_config.get("password")
        self.db = connection_config.get("db", 0)
        self.client = None

    async def connect(self) -> bool:
        """Establish Redis connection."""
        if aioredis is None:
            self.status = ConnectionStatus.ERROR
            self.last_error = "redis is not installed"
            logger.error(self.last_error)
            return False

        try:
            if self.client:
                await self.client.close()

            # Construct URL
            if self.password:
                url = f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
            else:
                url = f"redis://{self.host}:{self.port}/{self.db}"

            self.client = aioredis.from_url(url, decode_responses=True)
            # Test connection
            await self.client.ping()

            self.status = ConnectionStatus.CONNECTED
            self.last_error = None
            logger.info(f"Connected to Redis: {self.host}:{self.port}/{self.db}")
            return True
        except Exception as e:
            self.status = ConnectionStatus.ERROR
            self.last_error = str(e)
            logger.error(f"Failed to connect to Redis: {e}")
            return False

    async def disconnect(self) -> bool:
        """Close Redis connection."""
        try:
            if self.client:
                await self.client.close()
                self.client = None
            self.status = ConnectionStatus.DISCONNECTED
            self.last_error = None
            return True
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error disconnecting from Redis: {e}")
            return False

    async def execute_query(
        self, query: str, parameters: dict[str, Any] | None = None, **kwargs: Any
    ) -> QueryResult:
        """
        Execute a pseudo-query on Redis.
        Redis doesn't use SQL, so 'query' is interpreted as a Redis command
        or it can be a specific operation name.
        """
        if not self.client:
            if not await self.connect():
                return QueryResult(success=False, data=[], message="Not connected to Redis")

        try:
            start_time = datetime.now()

            # Simple command parsing for basic string commands
            # This is a very basic implementation, ideally we'd have
            # dedicated methods for Redis operations in the tool layer
            parts = query.split()
            cmd = parts[0].upper()

            # Use getattr to call the command on the client
            method = getattr(self.client, cmd.lower(), None)
            if not method:
                return QueryResult(success=False, data=[], message=f"Unknown Redis command: {cmd}")

            # Call method with remaining parts as arguments
            result = await method(*parts[1:])

            execution_time = (datetime.now() - start_time).total_seconds()

            # Wrap result in a list of dicts for consistency
            data = [{"result": result}]
            if isinstance(result, list):
                data = [{"item": i} for i in result]
            elif isinstance(result, dict):
                data = [result]

            return QueryResult(
                success=True,
                data=data,
                rowcount=1 if not isinstance(result, list) else len(result),
                execution_time=execution_time,
            )
        except Exception as e:
            logger.error(f"Redis operation error: {e}")
            return QueryResult(success=False, data=[], message=f"Operation failed: {e!s}")

    async def get_schema(self, **kwargs: Any) -> dict[str, Any]:
        """Get Redis info as schema."""
        if not self.client:
            await self.connect()

        info = await self.client.info()
        keys_count = await self.client.dbsize()

        return {"type": "redis", "keys_count": keys_count, "info": info}

    async def health_check(self) -> dict[str, Any]:
        """Check Redis health."""
        if not self.client:
            connected = await self.connect()
        else:
            try:
                await self.client.ping()
                connected = True
            except Exception:
                connected = False

        return {
            "status": "connected" if connected else "error",
            "database_type": "redis",
            "host": self.host,
            "db": self.db,
            "timestamp": datetime.now().isoformat(),
        }
