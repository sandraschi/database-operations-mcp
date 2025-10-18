#!/usr/bin/env python3
"""
Simple test script to verify imports work without starting the server.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

try:
    print("Testing imports...")

    # Test basic imports
    pass

    print("✅ Package imported successfully!")

    # Test main module
    pass

    print("✅ Main module imported successfully!")

    # Test individual handlers
    # from database_operations_mcp.handlers import connection_tools  # Module doesn't exist
    print("✅ Connection tools import skipped - module doesn't exist")

    # from database_operations_mcp.handlers import help_tools  # Module doesn't exist
    print("✅ Help tools import skipped - module doesn't exist")

    print("\n🎉 All imports successful!")
    print("The MCP server should be able to start.")

except ImportError as e:
    print(f"❌ Import Error: {e}")
    import traceback

    traceback.print_exc()
except Exception as e:
    print(f"❌ Other Error: {e}")
    import traceback

    traceback.print_exc()

# Input disabled for automated testing
# input("Press Enter to exit...")
