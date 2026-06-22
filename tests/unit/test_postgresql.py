"""
Test script for PostgreSQL connection using the database-operations-mcp package.
"""

from database_operations_mcp.services.database.connectors.postgresql_connector import PostgreSQLConnector


def test_postgres_instantiation():
    """Verify that PostgreSQLConnector can be instantiated and is no longer abstract."""
    config = {
        "host": "localhost",
        "port": 5432,
        "database": "postgres",
        "user": "postgres",
        "password": "password",
    }
    connector = PostgreSQLConnector(config)
    assert connector is not None
    assert connector.database_type == "postgresql"
