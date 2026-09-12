"""
SQLite Inspector Tools.

This module provides tools for inspecting arbitrary SQLite database files on the filesystem.
All operations are read-only by default.
"""

import logging
import os
from typing import Any

from database_operations_mcp.services.database.connectors.sqlite_connector import (
    SQLiteConnector,
)

logger = logging.getLogger(__name__)


async def get_connector(db_path: str) -> SQLiteConnector | None:
    """Get a connected SQLite connector for the specified path."""
    if not os.path.exists(db_path):
        logger.warning(f"Database not found at {db_path}")
        return None

    try:
        connector = SQLiteConnector({"database_path": db_path})
        if await connector.connect():
            return connector
    except Exception as e:
        logger.error(f"Error connecting to database at {db_path}: {e}")

    return None


# @mcp.tool()
async def sqlite_inspect_db(db_path: str) -> dict[str, Any]:
    """Inspect an arbitrary SQLite database file and return its schema summary.

    ## Return Format
    Returns success plus tables/table_count, or an error dict.

    ## Examples
    Inspect a file:
        result = await sqlite_inspect_db("C:/data/app.db")
    """
    connector = await get_connector(db_path)
    if not connector:
        return {
            "success": False,
            "error": f"Database not found or could not be opened at {db_path}",
        }

    try:
        tables = await connector.list_tables()
        await connector.disconnect()

        return {
            "success": True,
            "database": os.path.basename(db_path),
            "tables": tables,
            "table_count": len(tables),
            "database_path": db_path,
        }
    except Exception as e:
        logger.error(f"Error inspecting DB at {db_path}: {e}")
        return {"success": False, "error": str(e)}


# @mcp.tool()
async def sqlite_get_table_data(db_path: str, table_name: str, limit: int = 100, offset: int = 0) -> dict[str, Any]:
    """Get raw data from a specific table in an arbitrary SQLite database (Read-Only).

    ## Return Format
    Returns success plus data/columns/row_count, or an error dict.

    ## Examples
    Read rows:
        result = await sqlite_get_table_data("C:/data/app.db", "users", limit=10)
    """
    connector = await get_connector(db_path)
    if not connector:
        return {"success": False, "error": "Database not found"}

    try:
        # We wrap the table name in brackets to prevent SQL injection or issues with special names
        query = f"SELECT * FROM [{table_name}] LIMIT ? OFFSET ?"  # noqa: S608  # bracket-wrapped prevents injection in SQLite
        result = await connector.execute_query(query, (limit, offset))
        await connector.disconnect()

        return {
            "success": result.success,
            "data": result.data,
            "columns": result.columns,
            "row_count": result.rowcount,
            "message": result.message,
        }
    except Exception as e:
        logger.error(f"Error reading table {table_name} from {db_path}: {e}")
        return {"success": False, "error": str(e)}


# @mcp.tool()
async def sqlite_get_table_schema(db_path: str, table_name: str) -> dict[str, Any]:
    """Get the schema (columns, types, indices) for a table in an arbitrary SQLite database.

    ## Return Format
    Returns success plus schema/create_sql, or an error dict.

    ## Examples
    Describe a table:
        result = await sqlite_get_table_schema("C:/data/app.db", "users")
    """
    connector = await get_connector(db_path)
    if not connector:
        return {"success": False, "error": "Database not found"}

    try:
        schema = await connector.get_table_schema(table_name)

        # Also get CREATE TABLE statement
        connection = connector.connection
        if connection is None:
            raise ValueError("SQLite connection was lost")
        cursor = connection.cursor()
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        row = cursor.fetchone()
        create_sql = row[0] if row else ""

        await connector.disconnect()

        return {"success": True, "schema": schema, "create_sql": create_sql}
    except Exception as e:
        logger.error(f"Error getting schema for {table_name} from {db_path}: {e}")
        return {"success": False, "error": str(e)}
