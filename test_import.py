#!/usr/bin/env python3
"""
Test script to verify that the database-operations-mcp package can be imported correctly.
"""

import importlib
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


def test_import(module_name):
    """Test importing a module and log the result."""
    try:
        module = importlib.import_module(module_name)
        version = getattr(module, "__version__", "version not found")
        logger.info(f"✅ Successfully imported {module_name} (version: {version})")
        return True
    except ImportError as e:
        logger.error(f"❌ Failed to import {module_name}: {e}")
        return False
    except Exception as e:
        logger.error(f"⚠️  Error importing {module_name}: {e}", exc_info=True)
        return False


def main():
    """Main function to test imports."""
    print("=== Testing Database Operations MCP Imports ===")

    # Test importing main module
    if not test_import("database_operations_mcp"):
        print("\n❌ Critical: Failed to import database_operations_mcp")
        return 1

    # Test importing database manager
    if not test_import("database_operations_mcp.database_manager"):
        print("\n❌ Warning: Failed to import database_manager")

    # Test importing handlers
    if not test_import("database_operations_mcp.handlers.connection_tools"):
        print("\n❌ Warning: Failed to import connection_tools")

    if not test_import("database_operations_mcp.handlers.data_tools"):
        print("\n❌ Warning: Failed to import data_tools")

    print("\n=== Import Tests Complete ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
