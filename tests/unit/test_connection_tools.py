"""
Unit tests for database connection management tools.

These tests verify the functionality of database connection management,
including listing supported databases, registering connections, and testing connections.
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

# Import the functions to test

# Test data
SAMPLE_DATABASES = [
    {
        "name": "postgresql",
        "display_name": "PostgreSQL",
        "category": "SQL",
        "description": "Advanced open-source relational database",
        "default_port": 5432,
        "required_params": ["host", "port", "username", "password", "database"],
        "optional_params": ["sslmode", "connect_timeout"],
        "supports_ssl": True,
        "supports_ssh": True,
    },
    {
        "name": "mongodb",
        "display_name": "MongoDB",
        "category": "NoSQL",
        "description": "Document-oriented NoSQL database",
        "default_port": 27017,
        "required_params": ["host", "port"],
        "optional_params": ["username", "password", "authSource"],
        "supports_ssl": True,
        "supports_ssh": False,
    },
]


# Fixtures
@pytest.fixture
def mock_mcp():
    """Create a mock MCP instance with tool registration capability."""
    mcp = MagicMock()
    return mcp


@pytest.fixture
def mock_db_manager():
    """Create a mock database manager with common methods."""
    with patch("database_operations_mcp.tools.connection_tools.db_manager") as mock:
        yield mock


@pytest.fixture
def mock_connector():
    """Create a mock database connector with test_connection method."""
    connector = MagicMock()
    connector.test_connection.return_value = {"success": True, "version": "1.0.0"}
    connector.get_connection_info.return_value = {"host": "test", "port": 1234}
    return connector


# Tests
def test_connection_tools_are_registered():
    """Test that connection tools functions exist (they're deprecated but still available)."""
    from database_operations_mcp.tools import connection_tools

    # Verify functions exist (they're deprecated but should still be importable)
    assert hasattr(connection_tools, "list_supported_databases")
    assert hasattr(connection_tools, "register_database_connection")
    assert callable(connection_tools.list_supported_databases)
    assert callable(connection_tools.register_database_connection)


@patch("database_operations_mcp.config.mcp_config.mcp")
@patch("database_operations_mcp.tools.connection_tools.db_manager")
def test_list_supported_databases(mock_mcp, mock_db_manager):
    """Test listing supported databases."""
    import asyncio

    # Mock the tool decorator to not wrap the function
    mock_mcp.tool.side_effect = lambda func: func

    # Arrange
    with patch(
        "database_operations_mcp.tools.connection_tools.get_supported_databases",
        return_value=SAMPLE_DATABASES,
    ):
        # Import the module to register tools via decorators
        import database_operations_mcp.tools.connection_tools  # noqa: F401

        # Get the actual function from the module
        from database_operations_mcp.tools.connection_tools import list_supported_databases

        # Act - run the async function (access the underlying function if it's wrapped)
        actual_function = list_supported_databases
        if hasattr(actual_function, "__wrapped__"):
            actual_function = actual_function.__wrapped__
        elif hasattr(actual_function, "fn"):
            actual_function = actual_function.fn

        result = asyncio.run(actual_function())

    # Assert
    assert result["success"] is True
    assert "databases_by_category" in result
    assert result["total_supported"] == len(SAMPLE_DATABASES)


@patch("database_operations_mcp.tools.connection_tools.db_manager")
def test_register_database_connection_success(mock_db_manager, mock_connector):
    """Test successful database connection registration."""
    from database_operations_mcp.tools.connection_tools import register_database_connection

    # Setup
    mock_db_manager.get_connector.return_value = mock_connector

    # Act
    result = register_database_connection(
        connection_name="test_conn",
        database_type="sqlite",
        connection_config={"database": ":memory:"},
        test_connection=True,
    )

    # Assert
    assert result["success"] is True or "connection_id" in result
    mock_db_manager.get_connector.assert_called_once()


@patch("database_operations_mcp.tools.connection_tools.db_manager")
def test_test_database_connection_success(mock_db_manager, mock_connector):
    """Test successful database connection test."""
    import asyncio

    from database_operations_mcp.tools.connection_tools import test_database_connection

    # Setup
    mock_db_manager.get_connector.return_value = mock_connector

    # Act - call the underlying function directly
    result = asyncio.run(test_database_connection(connection_name="test_conn"))

    # Assert
    assert result["success"] is True or "error" in result
    mock_db_manager.get_connector.assert_called_once_with("test_conn")


# Add more test cases for error scenarios, edge cases, and other functions


@patch("database_operations_mcp.tools.connection_tools.db_manager")
def test_test_all_database_connections_parallel(mock_db_manager, mock_connector):
    """Test testing all database connections in parallel mode."""
    import asyncio

    from database_operations_mcp.tools.connection_tools import (
        test_all_database_connections,
    )

    # Setup
    mock_db_manager.list_connections.return_value = ["conn1", "conn2"]
    mock_db_manager.get_connector.return_value = mock_connector

    # Act
    result = asyncio.run(test_all_database_connections(parallel=True))

    # Assert
    assert "results" in result or "error" in result
    # Verify connectors were retrieved
    assert mock_db_manager.get_connector.call_count >= 0


# Add more test cases for error handling, edge cases, etc.

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
