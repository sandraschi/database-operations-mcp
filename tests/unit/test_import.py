#!/usr/bin/env python3
"""
Simple test script to verify the package can be imported and MCP server can be started.
"""

import sys

import database_operations_mcp
from database_operations_mcp.main import main

print("✅ Package imported successfully!")
print(f"Package version: {database_operations_mcp.__version__}")
print("\nAttempting to start MCP server... (Press Ctrl+C to stop)")

try:
    # This will block until interrupted
    main()
except KeyboardInterrupt:
    print("\nMCP server stopped.")
except Exception as e:
    print(f"\n❌ Error starting MCP server: {e}", file=sys.stderr)
    sys.exit(1)
