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
from database_operations_mcp.tools.connection_tools import (
    list_database_connections,
    register_database_connection,
    test_database_connection,
    test_all_database_connections
)

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
@patch("database_operations_mcp.tools.connection_tools.mcp")
def test_connection_tools_are_registered(mock_mcp):
    """Test that connection tools are registered via decorators when module is imported."""
    # Import the module to trigger @mcp.tool decorators
    import database_operations_mcp.tools.connection_tools  # noqa: F401

    # Assert
    # Verify that tool() was called for each expected function
    tool_calls = [call[0][0].__name__ for call in mock_mcp.tool.call_args_list]

    # Get the actual function names from the module that have @mcp.tool decorators
    from database_operations_mcp.tools import connection_tools

    expected_functions = [
        "register_database_connection",
        "list_database_connections",
        "test_database_connection",
        "test_all_database_connections"
    ]

    for func_name in expected_functions:
        assert func_name in tool_calls, f"{func_name} was not registered"


def test_list_supported_databases(mock_mcp, mock_db_manager):
    """Test listing supported databases."""
    # Arrange
    with patch(
        "database_operations_mcp.tools.connection_tools.get_supported_databases",
        return_value=SAMPLE_DATABASES,
    ):
        # Import the module to register tools via decorators
        import database_operations_mcp.tools.connection_tools  # noqa: F401

        # Get the list_database_connections function
        from database_operations_mcp.tools.connection_tools import list_database_connections

        # Act
        result = list_database_connections()

        # Assert
        assert result == SAMPLE_DATABASES


def test_register_database_connection_success(mock_mcp, mock_db_manager, mock_connector):
    """Test successful database connection registration."""
    # Arrange
    with patch(
        "database_operations_mcp.tools.connection_tools.create_connector",
        return_value=mock_connector,
    ):
        # Import the function directly
        from database_operations_mcp.tools.connection_tools import register_database_connection

        # Act
        result = register_database_connection(
            connection_name="test_conn",
            database_type="postgresql",
            connection_config={
                "host": "localhost",
                "port": 5432,
                "username": "user",
                "password": "pass",
                "database": "testdb",
            },
        )

        # Assert
        assert result["success"] is True
        assert result["connection_name"] == "test_conn"
        assert result["database_type"] == "postgresql"

        # Verify the connection was registered with the manager
        mock_db_manager.register_connection.assert_called_once_with("test_conn", mock_connector)


def test_test_database_connection_success(mock_mcp, mock_db_manager, mock_connector):
    """Test successful database connection test."""
    # Arrange
    mock_db_manager.get_connector.return_value = mock_connector

    # Import the function directly
    from database_operations_mcp.tools.connection_tools import test_database_connection

    # Act
    result = test_database_connection(connection_name="test_conn")

    # Assert
    assert result["success"] is True
    assert result["connection_name"] == "test_conn"

    # Verify the connector was retrieved and tested
    mock_db_manager.get_connector.assert_called_once_with("test_conn")
    mock_connector.test_connection.assert_called_once()


# Add more test cases for error scenarios, edge cases, and other functions


def test_test_all_database_connections_parallel(mock_mcp, mock_db_manager, mock_connector):
    """Test testing all database connections in parallel mode."""
    # Arrange
    connections = {"conn1": mock_connector, "conn2": mock_connector}
    mock_db_manager.list_connectors.return_value = connections

    # Create a mock ThreadPoolExecutor
    with patch("concurrent.futures.ThreadPoolExecutor") as mock_executor:
        # Mock the executor's behavior
        future = MagicMock()
        future.result.return_value = {"success": True, "latency": 10.5}
        mock_executor.return_value.__enter__.return_value.submit.return_value = future

        # Import the function directly
        from database_operations_mcp.tools.connection_tools import test_all_database_connections

        # Act
        result = test_all_database_connections(parallel=True, timeout=5.0)

        # Assert
        assert result["success"] is True
        assert result["total_connections"] == 2
        assert result["successful_tests"] == 2
        assert result["failed_tests"] == 0

        # Verify the manager was called correctly
        mock_db_manager.list_connectors.assert_called_once()
        assert result["summary"]["success_rate"] == "100.0%"


# Add more test cases for error handling, edge cases, etc.

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
