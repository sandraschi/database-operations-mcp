"""
Calibre Database Integration Tool.

This module provides specialized tools for interacting with Calibre metadata.db.
"""

import logging
import os
from typing import Any

from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.services.database.connectors.sqlite_connector import SQLiteConnector

logger = logging.getLogger(__name__)

# Hardcoded path relative to repo root for the surfaced database
# The user copied it to tests/assets/metadata.db
ASSET_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "tests",
    "assets",
    "metadata.db",
)


async def get_calibre_connector():
    """Get a connected SQLite connector for the Calibre database."""
    if not os.path.exists(ASSET_DB_PATH):
        logger.warning(f"Calibre database not found at {ASSET_DB_PATH}")
        return None

    connector = SQLiteConnector({"database_path": ASSET_DB_PATH})
    if await connector.connect():
        return connector
    return None


@mcp.tool()
async def calibre_list_books(limit: int = 50, offset: int = 0) -> dict[str, Any]:
    """List books from the Calibre library.

    Args:
        limit: Maximum number of books to return.
        offset: Number of books to skip.

    Returns:
        A list of books with basic metadata (title, authors, series).
    """
    connector = await get_calibre_connector()
    if not connector:
        return {"success": False, "error": f"Calibre database not found at {ASSET_DB_PATH}"}

    query = """
        SELECT 
            b.id, 
            b.title, 
            b.sort as title_sort,
            b.timestamp, 
            b.pubdate,
            (SELECT GROUP_CONCAT(name, ' & ') FROM authors a JOIN books_authors_link bal ON a.id = bal.author WHERE bal.book = b.id) as authors,
            s.name as series,
            b.series_index
        FROM books b
        LEFT JOIN books_series_link bsl ON b.id = bsl.book
        LEFT JOIN series s ON bsl.series = s.id
        ORDER BY b.timestamp DESC
        LIMIT ? OFFSET ?
    """

    try:
        result = await connector.execute_query(query, (limit, offset))
        await connector.disconnect()

        if result.success:
            return {
                "success": True,
                "books": result.data,
                "count": result.rowcount,
                "database_path": ASSET_DB_PATH,
            }
        else:
            return {"success": False, "error": result.message}

    except Exception as e:
        logger.error(f"Error listing Calibre books: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
async def calibre_get_book_details(book_id: int) -> dict[str, Any]:
    """Get detailed information for a specific book.

    Args:
        book_id: The ID of the book in the Calibre database.

    Returns:
        Detailed metadata including tags, comments, and formats.
    """
    connector = await get_calibre_connector()
    if not connector:
        return {"success": False, "error": "Calibre database not found"}

    try:
        # Get basic info + comments
        book_query = """
            SELECT b.*, c.text as comments
            FROM books b
            LEFT JOIN comments c ON b.id = c.book
            WHERE b.id = ?
        """
        book_result = await connector.execute_query(book_query, (book_id,))

        if not book_result.success or not book_result.data:
            return {"success": False, "error": f"Book with ID {book_id} not found"}

        book_data = book_result.data[0]

        # Get tags
        tags_query = """
            SELECT t.name
            FROM tags t
            JOIN books_tags_link btl ON t.id = btl.tag
            WHERE btl.book = ?
        """
        tags_result = await connector.execute_query(tags_query, (book_id,))
        book_data["tags"] = [row["name"] for row in tags_result.data] if tags_result.success else []

        # Get formats (file paths)
        formats_query = """
            SELECT format, name || '.' || LOWER(format) as filename
            FROM data
            WHERE book = ?
        """
        formats_result = await connector.execute_query(formats_query, (book_id,))
        book_data["formats"] = formats_result.data if formats_result.success else []

        await connector.disconnect()

        return {"success": True, "book": book_data}

    except Exception as e:
        logger.error(f"Error getting Calibre book details: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
async def calibre_query(query: str, params: list[Any] | None = None) -> dict[str, Any]:
    """Execute a custom SQL query against the Calibre database.

    Only SELECT queries are allowed for safety.
    """
    if not query.strip().lower().startswith("select"):
        return {"success": False, "error": "Only SELECT queries are allowed for safety."}

    connector = await get_calibre_connector()
    if not connector:
        return {"success": False, "error": "Calibre database not found"}

    try:
        result = await connector.execute_query(query, tuple(params) if params else None)
        await connector.disconnect()

        return {
            "success": result.success,
            "rows": result.data,
            "columns": result.columns,
            "row_count": result.rowcount,
            "error": result.message if not result.success else None,
        }
    except Exception as e:
        logger.error(f"Error executing Calibre query: {e}")
        return {"success": False, "error": str(e)}
