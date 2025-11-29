#!/usr/bin/env python3
"""
Quick pytest test script to verify database_operations package structure.

This test verifies that critical modules can be imported without errors.
"""

import sys
from pathlib import Path

import pytest

# Add src directory to path for imports
project_root = Path(__file__).parent.parent.parent
src_dir = project_root / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))


class TestQuickImports:
    """Quick import tests for critical modules."""

    def test_database_operations_package_import(self):
        """Test that the database_operations_mcp package can be imported."""
        import database_operations_mcp  # noqa: F401

        assert database_operations_mcp is not None
        assert hasattr(database_operations_mcp, "__name__")
        assert database_operations_mcp.__name__ == "database_operations_mcp"

    def test_main_module_import(self):
        """Test that the main module and main function can be imported."""
        from database_operations_mcp import main  # noqa: F401

        assert main is not None
        assert hasattr(main, "main")
        assert callable(main.main)

        # Test that DatabaseOperationsMCP class exists
        assert hasattr(main, "DatabaseOperationsMCP")
        assert main.DatabaseOperationsMCP is not None

    def test_config_module_import(self):
        """Test that the config module can be imported."""
        from database_operations_mcp.config import mcp_config  # noqa: F401

        assert mcp_config is not None
        assert hasattr(mcp_config, "mcp")
        assert hasattr(mcp_config, "get_mcp")

    def test_tools_package_import(self):
        """Test that the tools package can be imported."""
        from database_operations_mcp import tools  # noqa: F401

        assert tools is not None
        assert hasattr(tools, "__name__")
        assert tools.__name__ == "database_operations_mcp.tools"

        # Test that key portmanteau tools are available
        assert hasattr(tools, "db_connection")
        assert hasattr(tools, "db_operations")
        assert hasattr(tools, "firefox_bookmarks")


if __name__ == "__main__":
    # Allow running as standalone script for quick testing
    pytest.main([__file__, "-v"])
