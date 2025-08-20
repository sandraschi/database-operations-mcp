"""
Database Operations MCP - Main Entry Point

Universal database operations server supporting SQLite, PostgreSQL, and ChromaDB.
Built with FastMCP 2.10.1 for Austrian development efficiency.
"""

from .mcp_server import main

if __name__ == "__main__":
    main()
