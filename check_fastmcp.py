#!/usr/bin/env python3

import importlib.util

try:
    import fastmcp

    print(f"✅ FastMCP version: {fastmcp.__version__}")
    print(f"✅ Available imports: {[x for x in dir(fastmcp) if not x.startswith('_')]}")

    # Check for specific imports
    if importlib.util.find_spec("fastmcp.mcp_tool"):
        print("✅ mcp_tool import: OK")
    else:
        print("❌ mcp_tool import failed: module not found")

    if importlib.util.find_spec("fastmcp.FastMCP"):
        print("✅ FastMCP class import: OK")
    else:
        print("❌ FastMCP class import failed: module not found")

    if importlib.util.find_spec("fastmcp.tool"):
        print("✅ tool decorator import: OK")
    else:
        print("❌ tool decorator import failed: module not found")

except ImportError as e:
    print(f"❌ FastMCP not found: {e}")
