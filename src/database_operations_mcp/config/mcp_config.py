"""
Central FastMCP Configuration

This module provides a centralized FastMCP instance for the application.
All tools should import the MCP instance from this module to ensure
consistent registration and configuration.
"""
from fastmcp import FastMCP

# Create a single FastMCP instance for the entire application
# Only using 'name' as it's the only consistently working parameter
mcp = FastMCP(name="database-operations-mcp")

def get_mcp() -> FastMCP:
    """Get the global MCP instance."""
    return mcp
