"""
MySQL database connector implementation.

Handles MySQL and MariaDB databases with connection pooling.
"""

import logging
from datetime import datetime
from typing import Any

try:
    import aiomysql
except ImportError:
    aiomysql = None

from ....database_manager import (
    BaseDatabaseConnector,
    ConnectionStatus,
    DatabaseType,
    QueryError,
    QueryResult,
)

logger = logging.getLogger(__name__)


class MySQLConnector(BaseDatabaseConnector):
    """MySQL database connector."""

    @property
    def database_type(self) -> DatabaseType:
        """Return the database type."""
        return DatabaseType.MYSQL

    def __init__(self, connection_config: dict[str, Any]):
        """Initialize MySQL connector.

        Args:
            connection_config: Must contain connection parameters
                - host: MySQL server host
                - port: MySQL server port (default: 3306)
                - database: Database name
                - user: Username
                - password: Password
        """
        super().__init__(connection_config)
        self.host = connection_config.get("host", "localhost")
        self.port = connection_config.get("port", 3306)
        self.database = connection_config.get("database")
        self.user = connection_config.get("user")
        self.password = connection_config.get("password")
        self.pool = None

    async def connect(self) -> bool:
        """Establish MySQL database connection pool."""
        if aiomysql is None:
            self.status = ConnectionStatus.ERROR
            self.last_error = "aiomysql is not installed"
            logger.error(self.last_error)
            return False

        try:
            if self.pool:
                self.pool.close()
                await self.pool.wait_closed()

            self.pool = await aiomysql.create_pool(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                db=self.database,
                autocommit=True,
            )
            self.status = ConnectionStatus.CONNECTED
            self.last_error = None
            logger.info(f"Connected to MySQL database: {self.host}:{self.port}/{self.database}")
            return True
        except Exception as e:
            self.status = ConnectionStatus.ERROR
            self.last_error = str(e)
            logger.error(f"Failed to connect to MySQL database: {e}")
            return False

    async def disconnect(self) -> bool:
        """Close MySQL database connection pool."""
        try:
            if self.pool:
                self.pool.close()
                await self.pool.wait_closed()
                self.pool = None
            self.status = ConnectionStatus.DISCONNECTED
            self.last_error = None
            return True
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error disconnecting from MySQL: {e}")
            return False

    async def execute_query(
        self, query: str, parameters: dict[str, Any] | None = None, **kwargs: Any
    ) -> QueryResult:
        """Execute query and return results."""
        if not self.pool:
            if not await self.connect():
                return QueryResult(success=False, data=[], message="Not connected to MySQL")

        try:
            start_time = datetime.now()
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    await cur.execute(query, parameters)

                    query_lower = query.strip().lower()
                    if query_lower.startswith(("select", "show", "describe", "explain")):
                        rows = await cur.fetchall()
                        columns = [desc[0] for desc in cur.description] if cur.description else []
                        execution_time = (datetime.now() - start_time).total_seconds()

                        return QueryResult(
                            success=True,
                            data=rows,
                            columns=columns,
                            rowcount=len(rows),
                            execution_time=execution_time,
                        )
                    else:
                        affected = cur.rowcount
                        execution_time = (datetime.now() - start_time).total_seconds()
                        return QueryResult(
                            success=True,
                            data=[],
                            rowcount=affected,
                            execution_time=execution_time,
                            message=f"Query executed successfully. {affected} rows affected.",
                        )
        except Exception as e:
            logger.error(f"MySQL query error: {e}")
            return QueryResult(success=False, data=[], message=f"Query failed: {e!s}")

    async def get_schema(self, **kwargs: Any) -> dict[str, Any]:
        """Get database schema."""
        tables = await self.get_tables()
        return {"database": self.database, "table_count": len(tables), "tables": tables}

    async def get_tables(self, **kwargs: Any) -> list[str]:
        """Get list of tables."""
        res = await self.execute_query("SHOW TABLES")
        if not res.success:
            return []
        # SHOW TABLES returns rows with one column, name depends on database
        return [next(iter(row.values())) for row in res.data]

    async def get_table_schema(self, table_name: str, **kwargs: Any) -> dict[str, Any]:
        """Get schema for a specific table."""
        res = await self.execute_query(f"DESCRIBE {table_name}")
        if not res.success:
            raise QueryError(f"Failed to describe table {table_name}: {res.message}")

        columns = []
        for i, row in enumerate(res.data):
            columns.append(
                {
                    "name": row.get("Field"),
                    "type": row.get("Type"),
                    "nullable": row.get("Null") == "YES",
                    "default": row.get("Default"),
                    "primary_key": row.get("Key") == "PRI",
                    "position": i,
                }
            )

        return {
            "table_name": table_name,
            "columns": columns,
            "column_count": len(columns),
        }

    async def health_check(self) -> dict[str, Any]:
        """Check connection health."""
        if not self.pool:
            connected = await self.connect()
        else:
            connected = True

        return {
            "status": "connected" if connected else "error",
            "database_type": "mysql",
            "host": self.host,
            "database": self.database,
            "timestamp": datetime.now().isoformat(),
        }
