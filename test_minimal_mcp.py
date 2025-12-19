#!/usr/bin/env python3
"""Minimal MCP server test to isolate the SQL syntax error issue."""

from fastmcp import FastMCP

# Create a minimal MCP instance
mcp = FastMCP(name="test-mcp")

@mcp.tool()
async def test_tool(message: str):
    """A minimal test tool."""
    return {"result": f"Echo: {message}"}

if __name__ == "__main__":
    print("Testing minimal MCP server...")
    # This should work if FastMCP itself is not the issue
    mcp.run()
