"""
LanceDB vector database connector implementation.

Provides access to LanceDB for vector search and embedding storage.
Supports local path or LanceDB Cloud (uri + api_key).
"""

import logging
from datetime import datetime
from typing import Any

try:
    import lancedb
except ImportError:
    lancedb = None

from ....database_manager import (
    BaseDatabaseConnector,
    ConnectionStatus,
    DatabaseType,
    QueryResult,
)

logger = logging.getLogger(__name__)


class LanceDBConnector(BaseDatabaseConnector):
    """LanceDB vector database connector."""

    @property
    def database_type(self) -> DatabaseType:
        """Return the database type."""
        return DatabaseType.LANCEDB

    def __init__(self, connection_config: dict[str, Any]):
        """Initialize LanceDB connector.

        Args:
            connection_config: Connection parameters
                - uri or path (str): Local path or LanceDB Cloud URI (e.g. "data/lancedb" or "db://project")
                - api_key (str, optional): For LanceDB Cloud
                - region (str, optional): For LanceDB Cloud (e.g. "us-east-1")
        """
        super().__init__(connection_config)
        self.uri = connection_config.get("uri") or connection_config.get("path", "./lancedb")
        self.api_key = connection_config.get("api_key")
        self.region = connection_config.get("region")
        self._db: Any = None

    async def connect(self) -> bool:
        """Establish LanceDB connection."""
        if lancedb is None:
            self.status = ConnectionStatus.ERROR
            self.last_error = "lancedb is not installed. Install with: pip install lancedb"
            logger.error(self.last_error)
            return False

        try:
            if self.api_key:
                self._db = lancedb.connect(
                    uri=self.uri,
                    api_key=self.api_key,
                    region=self.region or "us-east-1",
                )
            else:
                self._db = lancedb.connect(self.uri)
            self.connection = self._db
            self.status = ConnectionStatus.CONNECTED
            self.last_error = None
            logger.info("Connected to LanceDB: %s", self.uri)
            return True
        except Exception as e:
            self.status = ConnectionStatus.ERROR
            self.last_error = str(e)
            logger.error("Failed to connect to LanceDB: %s", e)
            return False

    async def disconnect(self) -> bool:
        """Close LanceDB connection (no-op for file-based; clears reference)."""
        try:
            self._db = None
            self.connection = None
            self.status = ConnectionStatus.DISCONNECTED
            self.last_error = None
            return True
        except Exception as e:
            self.last_error = str(e)
            logger.error("Error disconnecting from LanceDB: %s", e)
            return False

    async def execute_query(self, query: str, parameters: dict[str, Any] | None = None, **kwargs: Any) -> QueryResult:
        """Execute LanceDB operation (vector search or list).

        Query hint: "search" for vector search, "list" to list table rows.
        Parameters:
            - table: table name
            - vector: query vector (list of floats) for search
            - limit: max results (default 10)
            - where: optional filter expression (e.g. "category = 'x'")
        """
        if not self._db:
            if not await self.connect():
                return QueryResult(success=False, data=[], message="Not connected to LanceDB")

        params = parameters or {}
        op = query.strip().lower() or "search"
        table_name = params.get("table")
        if not table_name:
            return QueryResult(
                success=False,
                data=[],
                message="LanceDB execute_query requires parameter 'table'",
            )

        try:
            start_time = datetime.now()
            table = self._db.open_table(table_name)

            if op == "list":
                # Return first N rows (no vector)
                limit = params.get("limit", 100)
                rows = table.to_pandas().head(limit)
                data = rows.to_dict("records")
                execution_time = (datetime.now() - start_time).total_seconds()
                return QueryResult(
                    success=True,
                    data=data,
                    columns=list(rows.columns) if len(data) else [],
                    rowcount=len(data),
                    execution_time=execution_time,
                )
            # search: vector similarity
            vector = params.get("vector")
            if not vector:
                return QueryResult(
                    success=False,
                    data=[],
                    message="Vector search requires parameter 'vector' (list of floats)",
                )
            limit = params.get("limit", 10)
            where = params.get("where")
            search_builder = table.search(vector).limit(limit)
            if where:
                search_builder = search_builder.where(where)
            results = search_builder.to_list()
            execution_time = (datetime.now() - start_time).total_seconds()
            return QueryResult(
                success=True,
                data=results,
                rowcount=len(results),
                execution_time=execution_time,
            )
        except Exception as e:
            logger.exception("LanceDB query error")
            return QueryResult(success=False, data=[], message=str(e))

    async def get_schema(self, **kwargs: Any) -> dict[str, Any]:
        """Get database schema (table list and counts)."""
        tables = await self.get_tables()
        return {"uri": self.uri, "table_count": len(tables), "tables": tables}

    async def get_tables(self, **kwargs: Any) -> list[str]:
        """Get list of table names."""
        if not self._db:
            if not await self.connect():
                return []
        try:
            try:
                return self._db.list_tables()
            except AttributeError:
                return self._db.table_names()
        except Exception as e:
            logger.error("LanceDB get_tables: %s", e)
            return []

    async def get_table_schema(self, table_name: str, **kwargs: Any) -> dict[str, Any]:
        """Get table schema (column names and types from PyArrow)."""
        if not self._db:
            if not await self.connect():
                return {}
        try:
            table = self._db.open_table(table_name)
            schema = table.schema
            columns = []
            for i in range(schema.num_fields):
                f = schema.field(i)
                columns.append({"name": f.name, "type": str(f.type)})
            return {"table": table_name, "columns": columns}
        except Exception as e:
            logger.error("LanceDB get_table_schema %s: %s", table_name, e)
            return {"table": table_name, "error": str(e)}

    async def health_check(self) -> dict[str, Any]:
        """LanceDB health check."""
        connected = self._db is not None
        try:
            if self._db:
                try:
                    names = self._db.list_tables()
                except AttributeError:
                    names = self._db.table_names()
                table_count = len(names)
            else:
                table_count = 0
        except Exception as e:
            table_count = 0
            connected = False
            self.last_error = str(e)
        return {
            "status": "connected" if connected else "disconnected",
            "database_type": "lancedb",
            "uri": self.uri,
            "table_count": table_count,
            "timestamp": datetime.now().isoformat(),
        }
