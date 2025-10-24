# Media library management portmanteau tool.
# Consolidates Calibre, Plex, and media operations into a single interface.

import logging
from typing import Any, Dict, List, Optional

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.tools.help_tools import HelpSystem

logger = logging.getLogger(__name__)


@mcp.tool()
@HelpSystem.register_tool(category="media")
async def media_library(
    operation: str,
    library_path: Optional[str] = None,
    book_title: Optional[str] = None,
    author: Optional[str] = None,
    search_query: Optional[str] = None,
    plex_server_url: Optional[str] = None,
    plex_token: Optional[str] = None,
    library_name: Optional[str] = None,
    include_metadata: bool = True,
    export_format: str = "json",
    export_path: Optional[str] = None,
    optimize_database: bool = False,
) -> Dict[str, Any]:
    """Media library management portmanteau tool.

    This tool consolidates all media library operations into a single interface,
    providing unified access to Calibre, Plex, and general media functionality.

    Operations:
    - search_calibre_library: Search books in Calibre library
    - get_calibre_book_metadata: Get detailed metadata for a specific book
    - search_calibre_fts: Perform full-text search in Calibre library
    - find_plex_database: Locate Plex Media Server database
    - optimize_plex_database: Optimize Plex database performance
    - export_database_schema: Export database schema information
    - get_plex_library_stats: Get statistics about Plex library
    - get_plex_library_sections: Get information about Plex library sections

    Args:
        operation: The operation to perform (required)
        library_path: Path to the Calibre library
        book_title: Title of the book to search for
        author: Author name to search for
        search_query: Search query string
        plex_server_url: URL of the Plex Media Server
        plex_token: Authentication token for Plex
        library_name: Name of the library/section
        include_metadata: Whether to include detailed metadata
        export_format: Format for exported data (json, csv, xml)
        export_path: Path to save exported data
        optimize_database: Whether to optimize database performance

    Returns:
        Dictionary with operation results and media information

    Examples:
        Search Calibre library:
        media_library(operation='search_calibre_library', library_path='/books',
                     search_query='python programming')

        Get book metadata:
        media_library(operation='get_calibre_book_metadata', library_path='/books',
                     book_title='Python Cookbook', include_metadata=True)

        Search with FTS:
        media_library(operation='search_calibre_fts', library_path='/books',
                     search_query='machine learning')

        Find Plex database:
        media_library(operation='find_plex_database', plex_server_url='http://localhost:32400')

        Optimize Plex database:
        media_library(operation='optimize_plex_database', plex_server_url='http://localhost:32400',
                     optimize_database=True)

        Get Plex library stats:
        media_library(operation='get_plex_library_stats', plex_server_url='http://localhost:32400',
                     plex_token='your_token')

        Export schema:
        media_library(operation='export_database_schema', library_path='/books',
                     export_format='json', export_path='schema.json')
    """

    if operation == "search_calibre_library":
        return await _search_calibre_library(
            library_path, book_title, author, search_query, include_metadata
        )
    elif operation == "get_calibre_book_metadata":
        return await _get_calibre_book_metadata(library_path, book_title, author, include_metadata)
    elif operation == "search_calibre_fts":
        return await _search_calibre_fts(library_path, search_query)
    elif operation == "find_plex_database":
        return await _find_plex_database(plex_server_url)
    elif operation == "optimize_plex_database":
        return await _optimize_plex_database(plex_server_url, plex_token, optimize_database)
    elif operation == "export_database_schema":
        return await _export_database_schema(library_path, export_format, export_path)
    elif operation == "get_plex_library_stats":
        return await _get_plex_library_stats(plex_server_url, plex_token, library_name)
    elif operation == "get_plex_library_sections":
        return await _get_plex_library_sections(plex_server_url, plex_token)
    else:
        return {
            "success": False,
            "error": f"Unknown operation: {operation}",
            "available_operations": [
                "search_calibre_library",
                "get_calibre_book_metadata",
                "search_calibre_fts",
                "find_plex_database",
                "optimize_plex_database",
                "export_database_schema",
                "get_plex_library_stats",
                "get_plex_library_sections",
            ],
        }


async def _search_calibre_library(
    library_path: Optional[str],
    book_title: Optional[str],
    author: Optional[str],
    search_query: Optional[str],
    include_metadata: bool,
) -> Dict[str, Any]:
    """Search books in Calibre library."""
    try:
        if not library_path:
            raise ValueError("Library path is required")

        return {
            "success": True,
            "message": "Calibre library search requested",
            "library_path": library_path,
            "book_title": book_title,
            "author": author,
            "search_query": search_query,
            "include_metadata": include_metadata,
            "results": [],
            "count": 0,
            "note": "Implementation pending - requires Calibre library integration",
        }

    except Exception as e:
        logger.error(f"Error searching Calibre library: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to search Calibre library: {str(e)}",
            "library_path": library_path,
            "results": [],
            "count": 0,
        }


async def _get_calibre_book_metadata(
    library_path: Optional[str],
    book_title: Optional[str],
    author: Optional[str],
    include_metadata: bool,
) -> Dict[str, Any]:
    """Get detailed metadata for a specific book."""
    try:
        if not library_path:
            raise ValueError("Library path is required")
        if not book_title and not author:
            raise ValueError("Book title or author is required")

        return {
            "success": True,
            "message": f"Calibre book metadata requested for '{book_title or author}'",
            "library_path": library_path,
            "book_title": book_title,
            "author": author,
            "include_metadata": include_metadata,
            "metadata": {},
            "note": "Implementation pending - requires Calibre metadata extraction",
        }

    except Exception as e:
        logger.error(f"Error getting Calibre book metadata: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to get Calibre book metadata: {str(e)}",
            "library_path": library_path,
            "book_title": book_title,
            "metadata": {},
        }


async def _search_calibre_fts(
    library_path: Optional[str], search_query: Optional[str]
) -> Dict[str, Any]:
    """Perform full-text search in Calibre library."""
    try:
        if not library_path:
            raise ValueError("Library path is required")
        if not search_query:
            raise ValueError("Search query is required")

        return {
            "success": True,
            "message": f"Calibre FTS search requested for '{search_query}'",
            "library_path": library_path,
            "search_query": search_query,
            "results": [],
            "count": 0,
            "note": "Implementation pending - requires Calibre FTS integration",
        }

    except Exception as e:
        logger.error(f"Error performing Calibre FTS search: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to perform Calibre FTS search: {str(e)}",
            "library_path": library_path,
            "search_query": search_query,
            "results": [],
            "count": 0,
        }


async def _find_plex_database(plex_server_url: Optional[str]) -> Dict[str, Any]:
    """Locate Plex Media Server database."""
    try:
        if not plex_server_url:
            raise ValueError("Plex server URL is required")

        return {
            "success": True,
            "message": "Plex database location requested",
            "plex_server_url": plex_server_url,
            "database_path": None,
            "note": "Implementation pending - requires Plex database detection",
        }

    except Exception as e:
        logger.error(f"Error finding Plex database: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to find Plex database: {str(e)}",
            "plex_server_url": plex_server_url,
            "database_path": None,
        }


async def _optimize_plex_database(
    plex_server_url: Optional[str], plex_token: Optional[str], optimize_database: bool
) -> Dict[str, Any]:
    """Optimize Plex database performance."""
    try:
        if not plex_server_url:
            raise ValueError("Plex server URL is required")

        return {
            "success": True,
            "message": "Plex database optimization requested",
            "plex_server_url": plex_server_url,
            "plex_token": plex_token,
            "optimize_database": optimize_database,
            "optimization_result": {},
            "note": "Implementation pending - requires Plex optimization logic",
        }

    except Exception as e:
        logger.error(f"Error optimizing Plex database: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to optimize Plex database: {str(e)}",
            "plex_server_url": plex_server_url,
            "optimization_result": {},
        }


async def _export_database_schema(
    library_path: Optional[str], export_format: str, export_path: Optional[str]
) -> Dict[str, Any]:
    """Export database schema information."""
    try:
        if not library_path:
            raise ValueError("Library path is required")

        return {
            "success": True,
            "message": "Database schema export requested",
            "library_path": library_path,
            "export_format": export_format,
            "export_path": export_path,
            "schema_data": {},
            "note": "Implementation pending - requires schema export logic",
        }

    except Exception as e:
        logger.error(f"Error exporting database schema: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to export database schema: {str(e)}",
            "library_path": library_path,
            "export_format": export_format,
            "schema_data": {},
        }


async def _get_plex_library_stats(
    plex_server_url: Optional[str], plex_token: Optional[str], library_name: Optional[str]
) -> Dict[str, Any]:
    """Get statistics about Plex library."""
    try:
        if not plex_server_url:
            raise ValueError("Plex server URL is required")

        return {
            "success": True,
            "message": "Plex library statistics requested",
            "plex_server_url": plex_server_url,
            "plex_token": plex_token,
            "library_name": library_name,
            "stats": {
                "total_items": 0,
                "total_size": "0 GB",
                "last_updated": None,
                "note": "Implementation pending - requires Plex API integration",
            },
        }

    except Exception as e:
        logger.error(f"Error getting Plex library stats: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to get Plex library stats: {str(e)}",
            "plex_server_url": plex_server_url,
            "library_name": library_name,
            "stats": {},
        }


async def _get_plex_library_sections(
    plex_server_url: Optional[str], plex_token: Optional[str]
) -> Dict[str, Any]:
    """Get information about Plex library sections."""
    try:
        if not plex_server_url:
            raise ValueError("Plex server URL is required")

        return {
            "success": True,
            "message": "Plex library sections requested",
            "plex_server_url": plex_server_url,
            "plex_token": plex_token,
            "sections": [],
            "count": 0,
            "note": "Implementation pending - requires Plex API integration",
        }

    except Exception as e:
        logger.error(f"Error getting Plex library sections: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to get Plex library sections: {str(e)}",
            "plex_server_url": plex_server_url,
            "sections": [],
            "count": 0,
        }
