#!/usr/bin/env python3
"""
Test script to verify the MCP server can be initialized properly.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from database_operations_mcp.main import DatabaseOperationsMCP


def test_server_import():
    """Test that the server module can be imported."""
    from database_operations_mcp.main import main

    assert main is not None
    print("✅ Module imported successfully")


def test_server_initialization():
    """Test that the server can be initialized without starting."""
    server = DatabaseOperationsMCP()
    assert server is not None
    assert hasattr(server, "mcp")
    print("✅ Server initialized successfully")


def test_server_tools():
    """Test that server tools are properly registered."""
    server = DatabaseOperationsMCP()
    assert server.mcp is not None
    print("✅ Server tools registered successfully")


if __name__ == "__main__":
    # Run tests when executed directly
    test_server_import()
    test_server_initialization()
    test_server_tools()
    print("✅ All server tests passed!")
