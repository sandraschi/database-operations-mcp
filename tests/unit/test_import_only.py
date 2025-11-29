#!/usr/bin/env python3
"""
Pytest test suite to verify imports work without starting the server.

This test ensures all critical modules can be imported and tools are properly
registered before attempting to start the MCP server.
"""

import os
import sys
from pathlib import Path

import pytest

# Add src directory to path for imports
project_root = Path(__file__).parent.parent.parent
src_dir = project_root / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))


class TestPackageImports:
    """Test that the main package and its modules can be imported."""

    def test_package_import(self):
        """Test that the database_operations_mcp package can be imported."""
        import database_operations_mcp  # noqa: F401

        assert hasattr(database_operations_mcp, "__name__")
        assert database_operations_mcp.__name__ == "database_operations_mcp"

    def test_main_module_import(self):
        """Test that the main module can be imported."""
        from database_operations_mcp import main  # noqa: F401

        assert callable(main.main)

    def test_config_module_import(self):
        """Test that the config module can be imported."""
        from database_operations_mcp.config import mcp_config  # noqa: F401

        assert hasattr(mcp_config, "mcp")
        assert hasattr(mcp_config, "get_mcp")

    def test_tools_package_import(self):
        """Test that the tools package can be imported."""
        from database_operations_mcp import tools  # noqa: F401

        assert hasattr(tools, "__name__")
        assert tools.__name__ == "database_operations_mcp.tools"


class TestPortmanteauToolImports:
    """Test that all portmanteau tools can be imported."""

    def test_database_tools_import(self):
        """Test database portmanteau tools can be imported."""
        from database_operations_mcp.tools import (
            db_analysis,
            db_connection,
            db_fts,
            db_management,
            db_operations,
            db_operations_extended,
            db_schema,
        )

        assert db_connection is not None
        assert db_operations is not None
        assert db_schema is not None
        assert db_management is not None
        assert db_fts is not None
        assert db_analysis is not None
        assert db_operations_extended is not None

    def test_browser_tools_import(self):
        """Test browser portmanteau tools can be imported."""
        from database_operations_mcp.tools import (
            browser_bookmarks,
            chrome_bookmarks,
            chrome_profiles,
            chromium_portmanteau,
            firefox_backup,
            firefox_bookmarks,
            firefox_curated,
            firefox_profiles,
            firefox_tagging,
        )

        assert browser_bookmarks is not None
        assert chrome_bookmarks is not None
        assert chrome_profiles is not None
        assert chromium_portmanteau is not None
        assert firefox_bookmarks is not None
        assert firefox_profiles is not None
        assert firefox_tagging is not None
        assert firefox_curated is not None
        assert firefox_backup is not None

    def test_support_tools_import(self):
        """Test support portmanteau tools can be imported."""
        from database_operations_mcp.tools import (
            help_system,
            media_library,
            system_init,
            windows_system,
        )

        assert help_system is not None
        assert media_library is not None
        assert windows_system is not None
        assert system_init is not None

    def test_comprehensive_portmanteau_import(self):
        """Test the comprehensive portmanteau tools module can be imported."""
        from database_operations_mcp import comprehensive_portmanteau_tools  # noqa: F401

        assert comprehensive_portmanteau_tools is not None


class TestMCPInstance:
    """Test that FastMCP instance is properly configured."""

    def test_mcp_instance_exists(self):
        """Test that MCP instance exists and is configured."""
        from database_operations_mcp.config.mcp_config import get_mcp, mcp

        # Test global mcp instance
        assert mcp is not None
        assert hasattr(mcp, "name")
        assert mcp.name == "database-operations-mcp"

        # Test get_mcp function
        mcp_instance = get_mcp()
        assert mcp_instance is not None
        assert mcp_instance is mcp

    def test_mcp_has_lifespan(self):
        """Test that MCP instance has lifespan configured for persistent storage."""
        from database_operations_mcp.config.mcp_config import mcp

        assert hasattr(mcp, "_lifespan")
        assert mcp._lifespan is not None


class TestToolRegistration:
    """Test that tools are properly registered with FastMCP."""

    def test_tools_registered_after_import(self):
        """Test that importing tools registers them with FastMCP."""
        from database_operations_mcp.config.mcp_config import mcp
        from fastmcp.utilities.inspect import get_tools

        # Import all tools to trigger registration
        from database_operations_mcp.tools import (  # noqa: F401
            db_connection,
            db_operations,
            firefox_bookmarks,
        )

        # Get registered tools
        tools = get_tools(mcp)
        assert isinstance(tools, dict)

        # Verify key portmanteau tools are registered
        expected_tools = [
            "db_connection",
            "db_operations",
            "db_schema",
            "firefox_bookmarks",
            "firefox_profiles",
            "browser_bookmarks",
            "help_system",
        ]

        for tool_name in expected_tools:
            assert tool_name in tools, f"Tool {tool_name} not found in registered tools"

    def test_tool_registration_count(self):
        """Test that we have a reasonable number of tools registered."""
        from database_operations_mcp.config.mcp_config import mcp
        from fastmcp.utilities.inspect import get_tools

        # Import comprehensive tools to trigger all registrations
        from database_operations_mcp.main import DatabaseOperationsMCP

        # Create server instance which imports all tools
        server = DatabaseOperationsMCP()

        # Get registered tools
        tools = get_tools(mcp)

        # We should have at least the portmanteau tools (around 20+)
        assert len(tools) >= 15, (
            f"Expected at least 15 tools, got {len(tools)}. "
            f"Registered tools: {list(tools.keys())}"
        )


class TestServerInitialization:
    """Test that the server can be initialized without errors."""

    def test_server_class_can_be_created(self):
        """Test that DatabaseOperationsMCP class can be instantiated."""
        from database_operations_mcp.main import DatabaseOperationsMCP

        server = DatabaseOperationsMCP()
        assert server is not None
        assert hasattr(server, "mcp")
        assert server.mcp is not None

    def test_server_has_import_method(self):
        """Test that server has the _import_all_tools method."""
        from database_operations_mcp.main import DatabaseOperationsMCP

        server = DatabaseOperationsMCP()
        assert hasattr(server, "_import_all_tools")
        assert callable(server._import_all_tools)


class TestNoCriticalImportErrors:
    """Test that there are no critical import errors that would prevent startup."""

    def test_no_syntax_errors_in_tools(self):
        """Test that all tool modules can be imported without syntax errors."""
        import importlib

        tool_modules = [
            "database_operations_mcp.tools.db_connection",
            "database_operations_mcp.tools.db_operations",
            "database_operations_mcp.tools.db_schema",
            "database_operations_mcp.tools.firefox_bookmarks",
            "database_operations_mcp.tools.firefox_profiles",
            "database_operations_mcp.tools.browser_bookmarks",
            "database_operations_mcp.tools.help_system",
        ]

        failed_imports = []
        for module_name in tool_modules:
            try:
                importlib.import_module(module_name)
            except Exception as e:
                failed_imports.append({"module": module_name, "error": str(e)})

        assert len(failed_imports) == 0, (
            f"Failed to import {len(failed_imports)} modules: {failed_imports}"
        )

    def test_no_name_errors(self):
        """Test that there are no NameError issues (like undefined HelpSystem)."""
        import importlib

        # Test importing firefox tools that previously had NameError issues
        firefox_modules = [
            "database_operations_mcp.tools.firefox.year_based_tagging",
            "database_operations_mcp.tools.firefox.folder_based_tagging",
        ]

        failed_imports = []
        for module_name in firefox_modules:
            try:
                importlib.import_module(module_name)
            except NameError as e:
                failed_imports.append({"module": module_name, "error": str(e)})

        assert len(failed_imports) == 0, (
            f"NameError in {len(failed_imports)} modules: {failed_imports}"
        )


if __name__ == "__main__":
    # Allow running as standalone script for quick testing
    pytest.main([__file__, "-v"])
