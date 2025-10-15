#!/usr/bin/env python3

try:
    import fastmcp

    print(f"✅ FastMCP version: {fastmcp.__version__}")
    print(f"✅ Available imports: {[x for x in dir(fastmcp) if not x.startswith('_')]}")

    # Check for specific imports
    try:
        from fastmcp import mcp_tool

        print("✅ mcp_tool import: OK")
    except ImportError as e:
        print(f"❌ mcp_tool import failed: {e}")

    try:
        from fastmcp import FastMCP

        print("✅ FastMCP class import: OK")
    except ImportError as e:
        print(f"❌ FastMCP class import failed: {e}")

    try:
        from fastmcp import tool

        print("✅ tool decorator import: OK")
    except ImportError as e:
        print(f"❌ tool decorator import failed: {e}")

except ImportError as e:
    print(f"❌ FastMCP not found: {e}")
