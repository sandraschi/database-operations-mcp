"""
Database connectors package.

Contains specific implementations for each supported database type.
"""

from .chromadb_connector import ChromaDBConnector
from .mongodb_connector import MongoDBConnector
from .postgresql_connector import PostgreSQLConnector
from .sqlite_connector import SQLiteConnector

__all__ = ["SQLiteConnector", "PostgreSQLConnector", "ChromaDBConnector", "MongoDBConnector"]

# Connector availability mapping
AVAILABLE_CONNECTORS = {
    "sqlite": SQLiteConnector,
    "postgresql": PostgreSQLConnector,
    "chromadb": ChromaDBConnector,
    "mongodb": MongoDBConnector,
}


def get_available_connectors():
    """Get list of available database connectors."""
    return list(AVAILABLE_CONNECTORS.keys())


def get_connector_class(database_type: str):
    """Get connector class for database type."""
    return AVAILABLE_CONNECTORS.get(database_type.lower())
