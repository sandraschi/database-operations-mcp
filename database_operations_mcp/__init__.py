"""
Database Operations MCP - FastMCP 2.10.1 Implementation

Universal database operations server supporting traditional SQL databases,
modern NoSQL databases, and specialized databases like vector stores.

Austrian dev efficiency: One interface for all database operations.
"""

__version__ = "1.0.0"
__author__ = "Sandra"

from .mcp_server import mcp, main

__all__ = ["mcp", "main"]
