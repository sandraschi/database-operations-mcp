"""
DuckDB database connector implementation.

Provides access to DuckDB analytical database.
"""

import logging
from datetime import datetime
from typing import Any

try:
    import duckdb
except ImportError:
    duckdb = None

from ....database_manager import (
    BaseDatabaseConnector,
    ConnectionStatus,
    DatabaseType,
    QueryResult,
)

logger = logging.getLogger(__name__)


class DuckDBConnector(BaseDatabaseConnector):
    """DuckDB database connector."""

    @property
    def database_type(self) -> DatabaseType:
        """Return the database type."""
        return DatabaseType.DUCKDB

    def __init__(self, connection_config: dict[str, Any]):
        """Initialize DuckDB connector.

        Args:
            connection_config: Must contain connection parameters
                - path: Path to DuckDB file (optional, uses :memory: if omitted)
                - read_only: Boolean for read-only access
        """
        super().__init__(connection_config)
        self.path = connection_config.get("path", ":memory:")
        self.read_only = connection_config.get("read_only", False)
        self.conn = None

    async def connect(self) -> bool:
        """Establish DuckDB connection."""
        if duckdb is None:
            self.status = ConnectionStatus.ERROR
            self.last_error = "duckdb is not installed"
            logger.error(self.last_error)
            return False

        try:
            # DuckDB connection is blocking, but typically fast
            self.conn = duckdb.connect(database=self.path, read_only=self.read_only)
            self.status = ConnectionStatus.CONNECTED
            self.last_error = None
            logger.info(f"Connected to DuckDB: {self.path}")
            return True
        except Exception as e:
            self.status = ConnectionStatus.ERROR
            self.last_error = str(e)
            logger.error(f"Failed to connect to DuckDB: {e}")
            return False

    async def disconnect(self) -> bool:
        """Close DuckDB connection."""
        try:
            if self.conn:
                self.conn.close()
                self.conn = None
            self.status = ConnectionStatus.DISCONNECTED
            self.last_error = None
            return True
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error disconnecting from DuckDB: {e}")
            return False

    async def execute_query(self, query: str, parameters: dict[str, Any] | None = None, **kwargs: Any) -> QueryResult:
        """Execute DuckDB query."""
        if not self.conn:
            if not await self.connect():
                return QueryResult(success=False, data=[], message="Not connected to DuckDB")

        try:
            start_time = datetime.now()

            # Use DuckDB connection to execute
            # Note: DuckDB's execute is blocking, we might want to wrap in run_in_executor
            # if we expect long running analytical queries, but for MCP usually fine.
            res = self.conn.execute(query, parameters or [])

            query_lower = query.strip().lower()
            if query_lower.startswith(("select", "show", "describe", "explain", "summarize")):
                rows = res.fetchall()
                columns = [desc[0] for desc in res.description] if res.description else []

                # Convert to list of dicts
                data = [dict(zip(columns, row, strict=False)) for row in rows]

                execution_time = (datetime.now() - start_time).total_seconds()
                return QueryResult(
                    success=True,
                    data=data,
                    columns=columns,
                    rowcount=len(rows),
                    execution_time=execution_time,
                )
            else:
                affected = res.rowcount
                execution_time = (datetime.now() - start_time).total_seconds()
                return QueryResult(
                    success=True,
                    data=[],
                    rowcount=affected,
                    execution_time=execution_time,
                    message=f"Query executed successfully. {affected} rows affected.",
                )
        except Exception as e:
            logger.error(f"DuckDB query error: {e}")
            return QueryResult(success=False, data=[], message=f"Query failed: {e!s}")

    async def get_schema(self, **kwargs: Any) -> dict[str, Any]:
        """Get database schema."""
        tables = await self.get_tables()
        return {"path": self.path, "table_count": len(tables), "tables": tables}

    async def get_tables(self, **kwargs: Any) -> list[str]:
        """Get list of tables."""
        res = await self.execute_query("SHOW TABLES")
        if not res.success:
            return []
        return [next(iter(row.values())) for row in res.data]

    async def get_table_schema(self, table_name: str, **kwargs: Any) -> dict[str, Any]:
        """Get schema information for a specific table."""
        res = await self.execute_query(f"DESCRIBE {table_name}")
        if not res.success:
            return {"table_name": table_name, "error": f"Failed to describe table: {res.message}"}

        columns = []
        for i, row in enumerate(res.data):
            columns.append(
                {
                    "name": row.get("column_name"),
                    "type": row.get("column_type"),
                    "nullable": row.get("null") == "YES",
                    "default": row.get("key"),
                    "primary_key": row.get("key") == "PRI",
                    "position": i,
                }
            )
        return {
            "table_name": table_name,
            "columns": columns,
            "column_count": len(columns),
        }

    async def health_check(self) -> dict[str, Any]:
        """Check DuckDB health."""
        connected = self.conn is not None
        return {
            "status": "connected" if connected else "disconnected",
            "database_type": "duckdb",
            "path": self.path,
            "timestamp": datetime.now().isoformat(),
        }
