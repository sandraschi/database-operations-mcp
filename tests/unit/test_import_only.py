#!/usr/bin/env python3
"""
Pytest test suite to verify imports work without starting the server.
"""

import importlib
import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent
src_dir = project_root / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))


class TestPackageImports:
    def test_package_import(self):
        import database_operations_mcp

        assert database_operations_mcp.__name__ == "database_operations_mcp"

    def test_main_module_import(self):
        from database_operations_mcp.main import main as main_fn

        assert callable(main_fn)

    def test_config_module_import(self):
        from database_operations_mcp.config import mcp_config

        assert hasattr(mcp_config, "mcp")
        assert hasattr(mcp_config, "get_mcp")

    def test_tools_package_import(self):
        from database_operations_mcp import tools

        assert tools.__name__ == "database_operations_mcp.tools"


class TestPortmanteauToolImports:
    def test_database_tools_import(self):
        from database_operations_mcp.tools import (
            db_analyzer,
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
        assert db_analyzer is not None
        assert db_operations_extended is not None

    def test_support_tools_import(self):
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


class TestMCPInstance:
    def test_mcp_instance_exists(self):
        from database_operations_mcp.config.mcp_config import get_mcp, mcp

        assert mcp is not None
        assert mcp.name == "database-operations-mcp"
        assert get_mcp() is mcp

    def test_mcp_has_lifespan(self):
        from database_operations_mcp.config.mcp_config import mcp

        assert hasattr(mcp, "_lifespan")
        assert mcp._lifespan is not None


class TestToolRegistration:
    def test_tools_registered_after_import(self):
        from database_operations_mcp.main import DatabaseOperationsMCP

        server = DatabaseOperationsMCP()
        assert server.mcp is not None
        assert hasattr(server.mcp, "name")

    def test_tool_registration_count(self):
        from database_operations_mcp.main import DatabaseOperationsMCP

        server = DatabaseOperationsMCP()
        tool_manager = getattr(server.mcp, "_tool_manager", None)
        if tool_manager is not None and hasattr(tool_manager, "list_tools"):
            tools = tool_manager.list_tools()
            assert len(tools) >= 10, f"Expected at least 10 tools, got {len(tools)}"
        else:
            assert server.mcp is not None


class TestServerInitialization:
    def test_server_class_can_be_created(self):
        from database_operations_mcp.main import DatabaseOperationsMCP

        server = DatabaseOperationsMCP()
        assert server.mcp is not None

    def test_server_has_import_method(self):
        from database_operations_mcp.main import DatabaseOperationsMCP

        server = DatabaseOperationsMCP()
        assert callable(server._import_all_tools)


class TestNoCriticalImportErrors:
    def test_no_syntax_errors_in_tools(self):
        tool_modules = [
            "database_operations_mcp.tools.db_connection",
            "database_operations_mcp.tools.db_operations",
            "database_operations_mcp.tools.db_schema",
            "database_operations_mcp.tools.help_system",
            "database_operations_mcp.tools.media_library",
        ]

        failed_imports = []
        for module_name in tool_modules:
            try:
                importlib.import_module(module_name)
            except Exception as e:
                failed_imports.append({"module": module_name, "error": str(e)})

        assert failed_imports == [], f"Failed imports: {failed_imports}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
