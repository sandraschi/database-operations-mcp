"""
Calibre Library Search Tools

DEPRECATED: This module is deprecated. Use media_library portmanteau tool instead.

All operations have been consolidated into media_library():
- search_calibre_library() → media_library(operation='search_calibre_library')
- get_calibre_book_metadata() → media_library(operation='get_calibre_book_metadata')
- search_calibre_fts() → media_library(operation='search_calibre_fts')

This module is kept for backwards compatibility but tools are no longer registered.
"""

import logging
from pathlib import Path
from typing import Any

# NOTE: @mcp.tool decorators removed - functionality moved to media_library portmanteau
logger = logging.getLogger(__name__)


def _get_fts_db_path(library_path: str | Path) -> Path:
    """Get the path to the full-text search database."""
    lib_path = Path(library_path)
    return lib_path / "full-text-search.db"


# DEPRECATED: Use media_library(operation='search_calibre_library') instead
async def search_calibre_library(
    query: str,
    library_path: str,
    search_fields: list[str] | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    """Search a Calibre library for books matching the query.

    Args:
        query: Search query string
        library_path: Path to the Calibre library
        search_fields: Optional list of fields to search (title, author, tags, etc.)
        limit: Maximum number of results to return
        offset: Number of results to skip (for pagination)

    Returns:
        Dictionary containing search results and metadata
    """
    try:
        # Implementation of search_calibre_library
        # ... existing implementation ...
        return {
            "status": "success",
            "results": [],  # Replace with actual results
            "total": 0,  # Replace with actual total
            "query": query,
            "library_path": str(library_path),
        }
    except Exception as e:
        logger.error(f"Error searching Calibre library: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Failed to search Calibre library: {str(e)}",
            "error_type": type(e).__name__,
        }


# DEPRECATED: Use media_library(operation='get_calibre_book_metadata') instead
async def get_calibre_book_metadata(book_id: int, library_path: str) -> dict[str, Any]:
    """Get metadata for a specific Calibre book.

    Args:
        book_id: ID of the book in the Calibre library
        library_path: Path to the Calibre library

    Returns:
        Dictionary containing the book's metadata
    """
    try:
        # Implementation of get_calibre_book_metadata
        # ... existing implementation ...
        return {
            "status": "success",
            "book_id": book_id,
            "metadata": {},  # Replace with actual metadata
        }
    except Exception as e:
        logger.error(f"Error getting book metadata: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Failed to get book metadata: {str(e)}",
            "error_type": type(e).__name__,
        }


# DEPRECATED: Use media_library(operation='search_calibre_fts') instead
async def search_calibre_fts(
    query: str, library_path: str, highlight: bool = True, limit: int = 20, offset: int = 0
) -> dict[str, Any]:
    """Perform a full-text search in a Calibre library.

    Args:
        query: Search query string
        library_path: Path to the Calibre library
        highlight: Whether to include highlighted snippets in results
        limit: Maximum number of results to return
        offset: Number of results to skip (for pagination)

    Returns:
        Dictionary containing full-text search results and metadata
    """
    try:
        # Implementation of search_calibre_fts
        # ... existing implementation ...
        return {
            "status": "success",
            "results": [],  # Replace with actual results
            "total": 0,  # Replace with actual total
            "query": query,
            "highlight": highlight,
        }
    except Exception as e:
        logger.error(f"Error in Calibre FTS: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Full-text search failed: {str(e)}",
            "error_type": type(e).__name__,
        }


# Add other tool functions with @mcp.tool() decorator as needed
