"""
Database Operations MCP

A FastMCP 2.10.1 compliant MCP server for database operations including
connection management, query execution, data manipulation, and schema management
across multiple database backends.
"""

__version__ = "0.1.0"
__author__ = "Sandra"
__license__ = "MIT"

# Import main components to make them available at package level
from .main import main, DatabaseOperationsMCP
from .database_manager import DatabaseManager

# Define __all__ to specify public API
__all__ = [
    'main',
    'DatabaseManager',
    'DatabaseOperationsMCP',
]