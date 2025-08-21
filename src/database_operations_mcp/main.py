"""
Main module for Database Operations MCP.

This module provides the main entry point for the Database Operations MCP server,
which communicates via stdio with the FastMCP 2.10.1 client.
"""
import sys
import logging
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Create MCP server instance
mcp = FastMCP("database-operations-mcp")  # Updated to match package name

def main():
    """Main entry point for Database Operations MCP server."""
    # Import and register handlers - they need access to the mcp instance
    # Import all tool modules
    from .handlers import (
        connection_tools, 
        query_tools, 
        schema_tools, 
        management_tools,
        data_tools,
        fts_tools,
        registry_tools,
        windows_tools,
        calibre_tools,
        media_tools,
        init_tools,
        help_tools
    )
    
    # Register all tool modules with the mcp instance
    connection_tools.register_tools(mcp)
    query_tools.register_tools(mcp)
    schema_tools.register_tools(mcp)
    management_tools.register_tools(mcp)
    data_tools.register_tools(mcp)
    fts_tools.register_tools(mcp)
    registry_tools.register_tools(mcp)
    windows_tools.register_tools(mcp)
    calibre_tools.register_tools(mcp)
    media_tools.register_tools(mcp)
    init_tools.register_tools(mcp)
    help_tools.register_tools(mcp)
    
    # Run MCP server in stdio mode
    mcp.run()

if __name__ == "__main__":
    main()
