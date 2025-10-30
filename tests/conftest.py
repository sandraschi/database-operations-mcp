"""
Pytest configuration and fixtures for database operations MCP tests.
"""

import os
import sys
from typing import Any

import pytest

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))


@pytest.fixture
def connection_config() -> dict[str, Any]:
    """Provide a sample database connection configuration for testing."""
    return {
        "name": "test_connection",
        "type": "sqlite",
        "host": "localhost",
        "port": 5432,
        "database": "test_db",
        "username": "test_user",
        "password": "test_password",
        "ssl_mode": "prefer",
        "timeout": 30,
        "max_connections": 10,
        "connection_pool_size": 5,
    }


@pytest.fixture
def mongodb_config() -> dict[str, Any]:
    """Provide a sample MongoDB connection configuration for testing."""
    return {
        "name": "test_mongodb",
        "type": "mongodb",
        "host": "localhost",
        "port": 27017,
        "database": "test_db",
        "username": "test_user",
        "password": "test_password",
        "auth_source": "admin",
        "ssl": False,
        "timeout": 30,
    }


@pytest.fixture
def postgresql_config() -> dict[str, Any]:
    """Provide a sample PostgreSQL connection configuration for testing."""
    return {
        "name": "test_postgresql",
        "type": "postgresql",
        "host": "localhost",
        "port": 5432,
        "database": "test_db",
        "username": "test_user",
        "password": "test_password",
        "ssl_mode": "prefer",
        "timeout": 30,
    }


@pytest.fixture
def sqlite_config() -> dict[str, Any]:
    """Provide a sample SQLite connection configuration for testing."""
    return {"name": "test_sqlite", "type": "sqlite", "database": ":memory:", "timeout": 30}


@pytest.fixture
def chromadb_config() -> dict[str, Any]:
    """Provide a sample ChromaDB connection configuration for testing."""
    return {
        "name": "test_chromadb",
        "type": "chromadb",
        "host": "localhost",
        "port": 8000,
        "database": "test_db",
        "collection": "test_collection",
        "timeout": 30,
    }


@pytest.fixture(autouse=True)
def reset_monitors():
    """Reset active monitors before each test."""
    # Import here to avoid circular imports
    try:
        from src.database_operations_mcp.tools.registry_tools import _active_monitors

        _active_monitors.clear()
    except (ImportError, NameError):
        # If the module doesn't exist or _active_monitors isn't defined, skip
        pass
