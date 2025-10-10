"""
Unit tests for database connection management tools.

These tests verify the functionality of database connection management,
including listing supported databases, registering connections, and testing connections.
"""

import sys
import os
import pytest
from unittest.mock import MagicMock, patch, ANY, call
from typing import Dict, Any, Optional

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

# Import the functions to test
from database_operations_mcp.tools.connection_tools import (
    register_tools,
    DatabaseInfo,
    ConnectionResult
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
        "supports_ssh": True
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
        "supports_ssh": False
    }
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
    with patch('database_operations_mcp.tools.connection_tools.db_manager') as mock:
        yield mock

@pytest.fixture
def mock_connector():
    """Create a mock database connector with test_connection method."""
    connector = MagicMock()
    connector.test_connection.return_value = {"success": True, "version": "1.0.0"}
    connector.get_connection_info.return_value = {"host": "test", "port": 1234}
    return connector

# Tests
def test_register_tools_registers_functions(mock_mcp):
    """Test that register_tools registers all expected functions."""
    # Act
    register_tools(mock_mcp)
    
    # Assert
    # Verify that tool() was called for each expected function
    tool_calls = [call[0][0].__name__ for call in mock_mcp.tool.call_args_list]
    
    # Get the actual function names from the module
    from database_operations_mcp.tools import connection_tools
    expected_functions = [
        name for name, obj in connection_tools.__dict__.items()
        if callable(obj) and not name.startswith('_')
    ]
    # Remove the register_tools function from the list
    expected_functions = [f for f in expected_functions if f != 'register_tools']
    
    for func_name in expected_functions:
        assert func_name in tool_calls, f"{func_name} was not registered"

def test_list_supported_databases(mock_mcp, mock_db_manager):
    """Test listing supported databases."""
    # Arrange
    from database_operations_mcp.database_manager import get_supported_databases
    with patch('database_operations_mcp.tools.connection_tools.get_supported_databases', 
              return_value=SAMPLE_DATABASES):
        # Register the tools with our mock MCP
        register_tools(mock_mcp)
        
        # Get the registered function
        tool_func = mock_mcp.tool.call_args_list[0][0][0]
        
        # Act
        result = tool_func()
        
        # Assert
        assert result["success"] is True
        assert "databases_by_category" in result
        assert "SQL" in result["databases_by_category"]
        assert "NoSQL" in result["databases_by_category"]
        assert result["total_supported"] == 2
        assert set(result["categories"]) == {"SQL", "NoSQL"}

def test_register_database_connection_success(mock_mcp, mock_db_manager, mock_connector):
    """Test successful database connection registration."""
    # Arrange
    with patch('database_operations_mcp.tools.connection_tools.create_connector', 
              return_value=mock_connector):
        register_tools(mock_mcp)
        
        # Get the register_database_connection function (second registered tool)
        tool_func = mock_mcp.tool.call_args_list[1][0][0]
        
        # Act
        result = tool_func(
            connection_name="test_conn",
            database_type="postgresql",
            connection_config={
                "host": "localhost",
                "port": 5432,
                "username": "user",
                "password": "pass",
                "database": "testdb"
            }
        )
        
        # Assert
        assert result["success"] is True
        assert result["connection_name"] == "test_conn"
        assert result["database_type"] == "postgresql"
        assert "connection_id" in result
        
        # Verify the connection was registered with the manager
        mock_db_manager.register_connection.assert_called_once_with("test_conn", mock_connector)

def test_test_database_connection_success(mock_mcp, mock_db_manager, mock_connector):
    """Test successful database connection test."""
    # Arrange
    mock_db_manager.get_connector.return_value = mock_connector
    
    register_tools(mock_mcp)
    
    # Get the test_database_connection function (fourth registered tool)
    tool_func = mock_mcp.tool.call_args_list[3][0][0]
    
    # Act
    result = tool_func(connection_name="test_conn")
    
    # Assert
    assert result["success"] is True
    assert result["connection_name"] == "test_conn"
    assert result["test_result"]["success"] is True
    assert "connection_info" in result
    
    # Verify the connector was retrieved and tested
    mock_db_manager.get_connector.assert_called_once_with("test_conn")
    mock_connector.test_connection.assert_called_once()
    mock_connector.get_connection_info.assert_called_once()

# Add more test cases for error scenarios, edge cases, and other functions

def test_test_all_database_connections_parallel(mock_mcp, mock_db_manager, mock_connector):
    """Test testing all database connections in parallel mode."""
    # Arrange
    connections = {
        "conn1": mock_connector,
        "conn2": mock_connector
    }
    mock_db_manager.list_connectors.return_value = connections
    
    # Create a mock ThreadPoolExecutor
    with patch('concurrent.futures.ThreadPoolExecutor') as mock_executor:
        # Mock the executor's behavior
        future = MagicMock()
        future.result.return_value = {"success": True, "latency": 10.5}
        mock_executor.return_value.__enter__.return_value.submit.return_value = future
        
        register_tools(mock_mcp)
        
        # Get the test_all_database_connections function (fifth registered tool)
        tool_func = mock_mcp.tool.call_args_list[4][0][0]
        
        # Act
        result = tool_func(parallel=True, timeout=5.0)
        
        # Assert
        assert result["success"] is True
        assert "test_results" in result
        assert "summary" in result
        assert result["summary"]["total_connections"] == 2
        assert result["summary"]["successful"] == 2
        assert result["summary"]["success_rate"] == "100.0%"

# Add more test cases for error handling, edge cases, etc.

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

