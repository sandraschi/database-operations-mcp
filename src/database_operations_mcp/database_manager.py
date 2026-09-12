"""
Database Manager Module.

Defines the base database connector interface and common functionality
for all database connectors in the application.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any, TypeVar

# Type variable for the connection type
T = TypeVar("T")

# Query parameter contract: named (dict) or positional (list/tuple) bindings.
QueryParameters = dict[str, Any] | list[Any] | tuple[Any, ...] | None


class DatabaseType(StrEnum):
    """Supported database types."""

    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    CHROMADB = "chromadb"
    MYSQL = "mysql"
    REDIS = "redis"
    DUCKDB = "duckdb"
    LANCEDB = "lancedb"


class ConnectionStatus(StrEnum):
    """Connection status enumeration."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class QueryResult:
    """Container for query results."""

    success: bool
    data: list[dict[str, Any]]
    columns: list[str] | None = None
    rowcount: int = 0
    message: str | None = None
    execution_time: float | None = None
    timestamp: datetime | None = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class DatabaseError(Exception):
    """Base exception for database-related errors."""

    pass


class DatabaseConnectionError(DatabaseError):
    """Raised when a database connection fails."""

    pass


class QueryError(DatabaseError):
    """Raised when a database query fails."""

    pass


class BaseDatabaseConnector[T](ABC):
    """
    Abstract base class for all database connectors.

    This class defines the common interface that all database connectors
    must implement to be used with the database operations MCP.
    """

    def __init__(self, connection_config: dict[str, Any]):
        """Initialize the database connector with connection configuration."""
        self.connection_config = connection_config
        self.connection: T | None = None
        self.client: Any = None
        self.status: ConnectionStatus = ConnectionStatus.DISCONNECTED
        self.last_error: str | None = None
        self.logger = logging.getLogger(self.__class__.__name__)

    @property
    @abstractmethod
    def database_type(self) -> DatabaseType:
        """Return the type of the database this connector handles."""
        pass

    @abstractmethod
    async def connect(self) -> bool:
        """Establish a connection to the database."""
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """Close the database connection."""
        pass

    @abstractmethod
    async def execute_query(self, query: str, parameters: QueryParameters = None, **kwargs: Any) -> QueryResult:
        """Execute a query and return the results."""
        pass

    @abstractmethod
    async def get_schema(self, **kwargs: Any) -> dict[str, Any]:
        """Get the database schema."""
        pass

    @abstractmethod
    async def get_tables(self, **kwargs: Any) -> list[str]:
        """Get list of tables in the database."""
        pass

    @abstractmethod
    async def get_table_schema(self, table_name: str, **kwargs: Any) -> dict[str, Any]:
        """Get schema information for a specific table."""
        pass

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Perform a health check of the database connection."""
        pass

    @property
    def is_connected(self) -> bool:
        """Check if the connector is currently connected to the database."""
        return self.status == ConnectionStatus.CONNECTED and self.connection is not None

    async def test_connection(self) -> dict[str, Any]:
        """Test the connection (connect if needed, then health-check)."""
        try:
            if not self.is_connected:
                connected = await self.connect()
                if not connected:
                    return {"success": False, "error": self.last_error or "Connect failed"}
            health = await self.health_check()
            ok = health.get("success", True) if isinstance(health, dict) else True
            return {"success": bool(ok), "status": self.status, "details": health}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def close(self) -> bool:
        """Close the connection (alias for disconnect)."""
        return await self.disconnect()

    async def get_connection_info(self) -> dict[str, Any]:
        """Return connector metadata and status."""
        return {
            "type": str(self.database_type),
            "status": str(self.status),
            "connected": self.is_connected,
            "last_error": self.last_error,
        }

    async def execute_write(self, query: str, parameters: QueryParameters = None) -> QueryResult:
        """Execute a write query (default: delegate to execute_query)."""
        return await self.execute_query(query, parameters)

    async def execute_transaction(self, queries: list[str | dict[str, Any]]) -> QueryResult:
        """Execute queries sequentially (default: no atomic rollback guarantee).

        Connectors with native transaction support should override this.
        """
        results: list[dict[str, Any]] = []
        for item in queries:
            if isinstance(item, str):
                result = await self.execute_query(item)
            else:
                result = await self.execute_query(str(item.get("query", "")), item.get("parameters"))
            results.append({"success": result.success, "rowcount": result.rowcount})
            if not result.success:
                return QueryResult(success=False, data=results, message="Transaction step failed")
        return QueryResult(success=True, data=results, rowcount=len(results))

    async def batch_insert(self, table_name: str, data: list[dict[str, Any]]) -> QueryResult:
        """Insert many rows (default: unsupported, override per dialect)."""
        raise DatabaseError(f"batch_insert is not supported by {self.__class__.__name__}")

    async def list_databases(self) -> list[dict[str, Any]]:
        """List databases (default: unsupported, override per connector)."""
        raise DatabaseError(f"list_databases is not supported by {self.__class__.__name__}")

    async def list_tables(self, database: str | None = None) -> list[dict[str, Any]]:
        """List tables (default: adapt get_tables)."""
        del database
        return [{"name": name} for name in await self.get_tables()]

    async def describe_table(self, table_name: str, database: str | None = None) -> dict[str, Any]:
        """Describe a table (default: adapt get_table_schema)."""
        del database
        return await self.get_table_schema(table_name)

    async def get_metrics(self) -> dict[str, Any]:
        """Return performance metrics (default: unsupported, override per connector)."""
        raise DatabaseError(f"get_metrics is not supported by {self.__class__.__name__}")

    async def vacuum(self, mode: str = "auto") -> dict[str, Any]:
        """Reclaim storage (default: unsupported, override per connector)."""
        raise DatabaseError(f"vacuum is not supported by {self.__class__.__name__} (mode={mode})")

    async def fts_search(self, query: str, **kwargs: Any) -> dict[str, Any]:
        """Full-text search (default: unsupported, override per connector)."""
        raise DatabaseError(f"fts_search is not supported by {self.__class__.__name__}")

    async def get_fts_tables(self) -> list[dict[str, Any]]:
        """List FTS-indexed tables (default: unsupported, override per connector)."""
        raise DatabaseError(f"get_fts_tables is not supported by {self.__class__.__name__}")

    async def fts_suggest(self, prefix: str, **kwargs: Any) -> dict[str, Any]:
        """Suggest FTS completions (default: unsupported, override per connector)."""
        raise DatabaseError(f"fts_suggest is not supported by {self.__class__.__name__}")

    async def get_collection_stats(self, database_name: str, collection_name: str) -> dict[str, Any]:
        """Collection stats (default: unsupported, override per connector)."""
        raise DatabaseError(f"get_collection_stats is not supported by {self.__class__.__name__}")

    def _handle_error(self, error: Exception, error_message: str) -> None:
        """Handle database errors consistently."""
        self.status = ConnectionStatus.ERROR
        self.last_error = str(error)
        self.logger.error(f"{error_message}: {error}", exc_info=True)
        raise DatabaseError(f"{error_message}: {error}") from error

    def __str__(self) -> str:
        """String representation of the connector."""
        return f"{self.__class__.__name__}(status={self.status}, database={self.database_type})"


class DatabaseManager:
    """Centralized database connection manager."""

    def __init__(self):
        self.connectors: dict[str, BaseDatabaseConnector] = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    def register_connector(self, name: str, connector: BaseDatabaseConnector) -> bool:
        """Register a database connector."""
        try:
            self.connectors[name] = connector
            self.logger.info(f"Registered connector: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register connector {name}: {e}")
            return False

    def register_connection(self, name: str, connector: BaseDatabaseConnector) -> bool:
        """Register a connection (legacy alias for register_connector)."""
        return self.register_connector(name, connector)

    async def unregister_connector(self, name: str) -> bool:
        """Disconnect and remove a registered connector."""
        connector = self.connectors.get(name)
        if connector is None:
            return False
        try:
            await connector.disconnect()
        except Exception as e:
            self.logger.warning(f"Error disconnecting {name} during unregister: {e}")
        self.connectors.pop(name, None)
        self.logger.info(f"Unregistered connector: {name}")
        return True

    async def test_connection(self, name: str) -> dict[str, Any]:
        """Test a registered connection by name."""
        connector = self.connectors.get(name)
        if connector is None:
            return {"success": False, "error": f"Connection not found: {name}"}
        try:
            return await connector.test_connection()
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def disconnect(self, name: str) -> bool:
        """Disconnect a registered connection by name (keeps registration)."""
        connector = self.connectors.get(name)
        if connector is None:
            return False
        try:
            return await connector.disconnect()
        except Exception as e:
            self.logger.warning(f"Error disconnecting {name}: {e}")
            return False

    def get_connector(self, name: str) -> BaseDatabaseConnector | None:
        """Get a registered connector by name."""
        return self.connectors.get(name)

    def list_connectors(self) -> dict[str, dict[str, Any]]:
        """List all registered connectors."""
        result = {}
        for name, connector in self.connectors.items():
            result[name] = {
                "name": name,
                "type": connector.database_type,
                "status": connector.status,
                "connected": connector.is_connected,
            }
        return result

    def test_all_connections(self) -> dict[str, dict[str, Any]]:
        """Test all registered connections."""
        results = {}
        for name, connector in self.connectors.items():
            try:
                # Basic test - check if connector exists and status
                results[name] = {
                    "success": connector.is_connected,
                    "status": connector.status,
                    "type": connector.database_type,
                    "error": connector.last_error,
                }
            except Exception as e:
                results[name] = {
                    "success": False,
                    "error": str(e),
                    "type": connector.database_type if hasattr(connector, "database_type") else "unknown",
                }
        return results


def normalize_query_result(result: QueryResult | dict[str, Any]) -> dict[str, Any]:
    """Normalize a QueryResult or raw dict into a rows/columns dict.

    Connectors return QueryResult; legacy paths may hand back plain dicts.
    """
    if isinstance(result, dict):
        return result
    return {
        "success": result.success,
        "rows": result.data,
        "data": result.data,
        "columns": result.columns or [],
        "row_count": result.rowcount,
        "rowcount": result.rowcount,
        "message": result.message,
        "execution_time": result.execution_time,
    }


def get_supported_databases() -> list[dict[str, Any]]:
    """Get list of supported database types."""
    return [
        {
            "type": DatabaseType.SQLITE,
            "name": "SQLite",
            "category": "File-based",
            "description": "Lightweight file-based SQL database",
        },
        {
            "type": DatabaseType.POSTGRESQL,
            "name": "PostgreSQL",
            "category": "SQL Server",
            "description": "Advanced open-source relational database",
        },
        {
            "type": DatabaseType.MONGODB,
            "name": "MongoDB",
            "category": "NoSQL",
            "description": "Document-oriented NoSQL database",
        },
        {
            "type": DatabaseType.CHROMADB,
            "name": "ChromaDB",
            "category": "Vector",
            "description": "Vector database for embeddings and AI applications",
        },
        {
            "type": DatabaseType.MYSQL,
            "name": "MySQL/MariaDB",
            "category": "SQL Server",
            "description": "Popular open-source relational database",
        },
        {
            "type": DatabaseType.REDIS,
            "name": "Redis",
            "category": "NoSQL",
            "description": "In-memory data structure store",
        },
        {
            "type": DatabaseType.DUCKDB,
            "name": "DuckDB",
            "category": "Analytical",
            "description": "In-process analytical SQL database",
        },
        {
            "type": DatabaseType.LANCEDB,
            "name": "LanceDB",
            "category": "Vector",
            "description": "Embedding store and vector search (local or LanceDB Cloud)",
        },
    ]


def create_connector(database_type: str, connection_config: dict[str, Any]) -> BaseDatabaseConnector | None:
    """Create a database connector instance."""
    from .services.database.connectors import AVAILABLE_CONNECTORS

    try:
        connector_class = AVAILABLE_CONNECTORS.get(database_type.lower())
        if not connector_class:
            logging.error(f"Unsupported database type: {database_type}")
            return None

        # Create and return the connector instance
        connector = connector_class(connection_config)
        logging.info(f"Created connector for {database_type}")
        return connector

    except Exception as e:
        logging.error(f"Failed to create connector for {database_type}: {e}")
        return None


# Global instance
db_manager = DatabaseManager()

# Export commonly used classes and types
__all__ = [
    "BaseDatabaseConnector",
    "ConnectionStatus",
    "DatabaseConnectionError",
    "DatabaseError",
    "DatabaseManager",
    "DatabaseType",
    "QueryError",
    "QueryParameters",
    "QueryResult",
    "create_connector",
    "db_manager",
    "get_supported_databases",
    "normalize_query_result",
]
