"""
Database Operations MCP Server - FastMCP 2.10 Implementation

Universal database operations server with modular tool organization.
Austrian dev efficiency: One unified interface for all database operations.
"""

import logging
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server with stdio transport
mcp = FastMCP("Database Operations")

# Import and register tool modules
from .tools import (
    connection_tools,
    query_tools,
    schema_tools,
    management_tools
)

# Register all tool groups
connection_tools.register_tools(mcp)
query_tools.register_tools(mcp)
schema_tools.register_tools(mcp)
management_tools.register_tools(mcp)

logger.info("Database Operations MCP server initialized with all tool modules")

def main():
    """Main entry point for Database Operations MCP server."""
    import sys
    
    logger.info("Starting Database Operations MCP server with stdio transport")
    
    # Run the FastMCP server with stdio transport
    mcp.run_stdio()

if __name__ == "__main__":
    main()
