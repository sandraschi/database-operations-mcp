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

    ## Return Format
    Always returns not_implemented - use the media_library portmanteau.

    ## Examples
    Use the portmanteau instead:
        result = await media_library(operation="search_calibre_library", ...)
    """
    _ = (query, library_path, search_fields, limit, offset)
    return {
        "status": "error",
        "error": "not_implemented: use media_library(operation='search_calibre_library')",
        "error_type": "NotImplementedError",
    }


# DEPRECATED: Use media_library(operation='get_calibre_book_metadata') instead
async def get_calibre_book_metadata(book_id: int, library_path: str) -> dict[str, Any]:
    """Get metadata for a specific Calibre book.

    ## Return Format
    Always returns not_implemented - use the media_library portmanteau.

    ## Examples
    Use the portmanteau instead:
        result = await media_library(operation="get_calibre_book_metadata", ...)
    """
    _ = (book_id, library_path)
    return {
        "status": "error",
        "error": "not_implemented: use media_library(operation='get_calibre_book_metadata')",
        "error_type": "NotImplementedError",
    }


# DEPRECATED: Use media_library(operation='search_calibre_fts') instead
async def search_calibre_fts(
    query: str, library_path: str, highlight: bool = True, limit: int = 20, offset: int = 0
) -> dict[str, Any]:
    """Perform a full-text search in a Calibre library.

    ## Return Format
    Always returns not_implemented - use the media_library portmanteau.

    ## Examples
    Use the portmanteau instead:
        result = await media_library(operation="search_calibre_fts", ...)
    """
    _ = (query, library_path, highlight, limit, offset)
    return {
        "status": "error",
        "error": "not_implemented: use media_library(operation='search_calibre_fts')",
        "error_type": "NotImplementedError",
    }


# Add other tool functions with @mcp.tool() decorator as needed
