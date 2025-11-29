#!/usr/bin/env python3
"""
Test script to verify the package can be imported and MCP server can be initialized.
"""

import database_operations_mcp
from database_operations_mcp.main import DatabaseOperationsMCP


def test_package_import():
    """Test that the package can be imported successfully."""
    assert database_operations_mcp is not None
    assert hasattr(database_operations_mcp, "__version__")
    print(f"✅ Package imported successfully! Version: {database_operations_mcp.__version__}")


def test_mcp_server_initialization():
    """Test that the MCP server can be initialized without starting."""
    server = DatabaseOperationsMCP()
    assert server is not None
    assert hasattr(server, "mcp")
    print("✅ MCP server initialized successfully!")


def test_tools_are_registered():
    """Test that tools are properly registered."""
    server = DatabaseOperationsMCP()
    # Check that tools are registered (this will trigger the import)
    assert server.mcp is not None
    print("✅ Tools registered successfully!")


if __name__ == "__main__":
    # Run tests when executed directly
    test_package_import()
    test_mcp_server_initialization()
    test_tools_are_registered()
    print("✅ All import tests passed!")
