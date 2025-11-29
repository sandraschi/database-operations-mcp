#!/usr/bin/env python3
"""
Final integration test to verify the module can be executed as a package.

This test verifies that the database_operations_mcp package can be run
using `python -m database_operations_mcp` syntax.
"""

import runpy
import sys
from pathlib import Path

import pytest

# Add src directory to path for imports
project_root = Path(__file__).parent.parent.parent
src_dir = project_root / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))


class TestModuleExecution:
    """Test that the module can be executed as a package."""

    def test_package_can_be_imported(self):
        """Test that the database_operations_mcp package can be imported."""
        import database_operations_mcp  # noqa: F401

        assert database_operations_mcp is not None
        assert hasattr(database_operations_mcp, "__name__")

    def test_main_function_can_be_imported(self):
        """Test that the main function can be imported."""
        from database_operations_mcp.main import main  # noqa: F401

        assert callable(main)

    def test_module_can_be_run_as_main(self):
        """Test that the module can be executed using runpy.run_module."""
        # This test verifies the -m execution pattern works
        # We catch SystemExit because main() calls sys.exit()
        try:
            runpy.run_module("database_operations_mcp", run_name="__main__")
            # If we get here without SystemExit, that's unexpected but not necessarily wrong
            pytest.fail("Expected SystemExit when running module as main")
        except SystemExit as e:
            # SystemExit is expected - it means the module executed and called sys.exit()
            # Exit code 0 or 1 are both acceptable for this test
            assert e.code in (0, 1, None)
        except ImportError as e:
            # Module not found is a failure
            pytest.fail(f"Failed to import module for execution: {e}")
        except Exception as e:
            # Other exceptions are failures
            pytest.fail(f"Unexpected error when running module as main: {e}")


if __name__ == "__main__":
    # Allow running as standalone script for quick testing
    pytest.main([__file__, "-v"])
