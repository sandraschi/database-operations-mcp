"""
Database connectors package.

Contains specific implementations for each supported database type.
"""

from .sqlite_connector import SQLiteConnector
from .postgresql_connector import PostgreSQLConnector
from .chromadb_connector import ChromaDBConnector

__all__ = [
    "SQLiteConnector",
    "PostgreSQLConnector", 
    "ChromaDBConnector"
]

# Connector availability mapping
AVAILABLE_CONNECTORS = {
    "sqlite": SQLiteConnector,
    "postgresql": PostgreSQLConnector,
    "chromadb": ChromaDBConnector
}

def get_available_connectors():
    """Get list of available database connectors."""
    return list(AVAILABLE_CONNECTORS.keys())

def get_connector_class(database_type: str):
    """Get connector class for database type."""
    return AVAILABLE_CONNECTORS.get(database_type.lower())
