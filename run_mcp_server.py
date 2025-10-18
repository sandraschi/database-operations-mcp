#!/usr/bin/env python3
"""
Run the Database Operations MCP server with debug output.
"""

import logging
import sys

# Import and run the MCP server
from database_operations_mcp.main import main

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)

if __name__ == "__main__":
    print("Starting Database Operations MCP server...", file=sys.stderr)
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise
