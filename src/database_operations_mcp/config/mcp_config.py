"""
Central FastMCP Configuration

This module provides a centralized FastMCP instance for the application.
All tools should import the MCP instance from this module to ensure
consistent registration and configuration.
"""

import os
from fastmcp import FastMCP

# Create a single FastMCP instance for the entire application
# Only using 'name' as it's the only consistently working parameter
mcp = FastMCP(name="database-operations-mcp")

# Flag to control individual tool registration
# Set to False to only register portmanteau tools
ENABLE_INDIVIDUAL_TOOLS = os.getenv("ENABLE_INDIVIDUAL_TOOLS", "false").lower() == "true"


# Check if we're being imported by a portmanteau module
def is_portmanteau_import():
    """Check if the current import is from a portmanteau module."""
    import inspect

    frame = inspect.currentframe()
    try:
        # Go up the call stack to find the importing module
        for i in range(10):  # Check up to 10 frames up
            frame = frame.f_back
            if frame is None:
                break
            filename = frame.f_code.co_filename
            if (
                "portmanteau" in filename.lower()
                or "firefox_bookmarks" in filename
                or "db_connection" in filename
            ):
                return True
    finally:
        del frame
    return False


def get_mcp() -> FastMCP:
    """Get the global MCP instance."""
    return mcp
