#!/usr/bin/env python3
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

print("Testing MCP import...")

try:
    # Import the MCP config first
    from database_operations_mcp.config.mcp_config import mcp
    print("MCP config imported")

    # Import the db_analysis tool
    from database_operations_mcp.tools.db_analysis import db_analysis
    print("db_analysis imported")

    # Check what type it is
    print(f"db_analysis type: {type(db_analysis)}")

    # Try to get the function signature
    import inspect
    try:
        sig = inspect.signature(db_analysis)
        print(f"Function signature: {sig}")
    except Exception as e:
        print(f"Could not get signature: {e}")

    print("Import test completed successfully")

except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()
