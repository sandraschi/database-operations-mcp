"""
Database connectors package.

Contains specific implementations for each supported database type.
"""

from .chromadb_connector import ChromaDBConnector
from .duckdb_connector import DuckDBConnector
from .lancedb_connector import LanceDBConnector
from .mongodb_connector import MongoDBConnector
from .mysql_connector import MySQLConnector
from .postgresql_connector import PostgreSQLConnector
from .redis_connector import RedisConnector
from .sqlite_connector import SQLiteConnector

__all__ = [
    "ChromaDBConnector",
    "DuckDBConnector",
    "LanceDBConnector",
    "MongoDBConnector",
    "MySQLConnector",
    "PostgreSQLConnector",
    "RedisConnector",
    "SQLiteConnector",
]

# Connector availability mapping
AVAILABLE_CONNECTORS = {
    "sqlite": SQLiteConnector,
    "postgresql": PostgreSQLConnector,
    "chromadb": ChromaDBConnector,
    "mongodb": MongoDBConnector,
    "mysql": MySQLConnector,
    "redis": RedisConnector,
    "duckdb": DuckDBConnector,
    "lancedb": LanceDBConnector,
}


def get_available_connectors():
    """Get list of available database connectors."""
    return list(AVAILABLE_CONNECTORS.keys())


def get_connector_class(database_type: str):
    """Get connector class for database type."""
    return AVAILABLE_CONNECTORS.get(database_type.lower())
