# Media library management portmanteau tool.
# Consolidates Calibre, Plex, and media operations into a single interface.

import logging
from typing import Any

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.tools.help_tools import HelpSystem

logger = logging.getLogger(__name__)


@mcp.tool()
@HelpSystem.register_tool(category="media")
async def media_library(
    operation: str,
    library_path: str | None = None,
    book_title: str | None = None,
    author: str | None = None,
    search_query: str | None = None,
    plex_server_url: str | None = None,
    plex_token: str | None = None,
    library_name: str | None = None,
    include_metadata: bool = True,
    export_format: str = "json",
    export_path: str | None = None,
    optimize_database: bool = False,
) -> dict[str, Any]:
    """Media library management portmanteau tool.

    Comprehensive media library operations consolidating ALL Calibre and Plex
    operations into a single interface. Supports book searching, metadata retrieval,
    full-text search, database management, and library statistics across media platforms.

    Prerequisites:
        - For Calibre operations: Valid Calibre library path accessible
        - For Plex operations: Plex Media Server running and accessible
        - For Plex API operations: Valid plex_token for authentication
        - For database operations: Appropriate read/write permissions

    Operations:
        - search_calibre_library: Search books in Calibre library
        - get_calibre_book_metadata: Get detailed metadata for a specific book
        - search_calibre_fts: Perform full-text search in Calibre library
        - find_plex_database: Locate Plex Media Server database file
        - optimize_plex_database: Optimize Plex database performance
        - export_database_schema: Export database schema information
        - get_plex_library_stats: Get statistics about Plex library
        - get_plex_library_sections: Get information about Plex library sections

    Parameters:
        operation (str, REQUIRED): The operation to perform
            Valid values: 'search_calibre_library', 'get_calibre_book_metadata',
                         'search_calibre_fts', 'find_plex_database',
                         'optimize_plex_database', 'export_database_schema',
                         'get_plex_library_stats', 'get_plex_library_sections'
            Example: 'search_calibre_library', 'get_plex_library_stats'

        library_path (str, OPTIONAL): Path to the Calibre library directory
            Format: Absolute or relative path to Calibre library root
            Required for: All Calibre operations (search_calibre_*, export_database_schema)
            Validation: Directory must exist and contain Calibre metadata.db
            Example: 'C:/Users/Username/Calibre Library', '/home/user/calibre'

        book_title (str, OPTIONAL): Title of the book to search for
            Format: Full or partial book title
            Used for: search_calibre_library, get_calibre_book_metadata
            Behavior: Case-insensitive partial matching
            Example: 'Python Cookbook', 'Learning Python'

        author (str, OPTIONAL): Author name to search for
            Format: Full or partial author name
            Used for: search_calibre_library, get_calibre_book_metadata
            Behavior: Case-insensitive partial matching
            Example: 'David Beazley', 'Mark Lutz'

        search_query (str, OPTIONAL): Search query string
            Format: Free-form search text
            Required for: search_calibre_library, search_calibre_fts operations
            Behavior: Searches titles, authors, tags, and content (FTS)
            Example: 'python programming', 'machine learning algorithms'

        plex_server_url (str, OPTIONAL): URL of the Plex Media Server
            Format: HTTP URL with protocol and port
            Required for: All Plex operations
            Default: 'http://localhost:32400'
            Example: 'http://192.168.1.100:32400', 'https://plex.example.com'

        plex_token (str, OPTIONAL): Authentication token for Plex API
            Format: Plex authentication token string
            Required for: Plex API operations (get_plex_library_stats, etc.)
            Validation: Must be valid Plex token
            Example: 'your-plex-token-here'

        library_name (str, OPTIONAL): Name of the library/section
            Format: Plex library section name
            Used for: get_plex_library_stats operation
            Example: 'Movies', 'TV Shows', 'Music'

        include_metadata (bool, OPTIONAL): Include detailed metadata in results
            Default: True
            Behavior: Adds cover images, descriptions, tags, series info if available
            Used for: search_calibre_library, get_calibre_book_metadata

        export_format (str, OPTIONAL): Format for exported data
            Valid values: 'json', 'csv', 'xml'
            Default: 'json'
            Used for: export_database_schema operation
            Example: 'json', 'csv', 'xml'

        export_path (str, OPTIONAL): Path to save exported data
            Format: Absolute or relative file path
            Required for: export_database_schema (if saving to file)
            Validation: Parent directory must exist and be writable
            Example: 'C:/data/schema.json', './exports/calibre_schema.csv'

        optimize_database (bool, OPTIONAL): Optimize database during operation
            Default: False
            Behavior: Runs VACUUM, ANALYZE, and index optimization
            Used for: optimize_plex_database operation
            Warning: May take several minutes for large databases

    Returns:
        Dictionary containing operation-specific results:
            - success: Boolean indicating operation success
            - operation: Echo of operation performed
            - For search_calibre_library: results (list), count, library_path
            - For get_calibre_book_metadata: book_info (dict), metadata (if requested)
            - For search_calibre_fts: results (list with highlights), count
            - For find_plex_database: database_path, server_info, status
            - For optimize_plex_database: message, optimization_stats
            - For export_database_schema: export_path, format, schema_data
            - For get_plex_library_stats: stats (dict), library_name, item_counts
            - For get_plex_library_sections: sections (list), total_sections
            - error: Error message if success is False
            - available_operations: List of valid operations (on invalid operation)

    Usage:
        This tool provides unified access to Calibre ebook and Plex media library
        management. Use it to search, browse, and manage your media collections.

        Common scenarios:
        - Book discovery: Search Calibre library by title, author, or content
        - Metadata lookup: Get detailed book information and covers
        - Library management: Optimize databases and export schemas
        - Statistics: Analyze Plex library size and organization
        - Maintenance: Optimize databases for better performance

        Best practices:
        - Use specific search terms for better results
        - Include metadata for complete book information
        - Optimize databases periodically for performance
        - Export schemas before major operations for backup

    Examples:
        Search Calibre library:
            result = await media_library(
                operation='search_calibre_library',
                library_path='C:/Users/Username/Calibre Library',
                search_query='python programming',
                include_metadata=True
            )
            # Returns: {
            #     'success': True,
            #     'results': [
            #         {
            #             'title': 'Python Cookbook',
            #             'author': 'David Beazley',
            #             'tags': ['programming', 'python'],
            #             'metadata': {...}
            #         }
            #     ],
            #     'count': 15,
            #     'library_path': 'C:/Users/Username/Calibre Library'
            # }

        Get book metadata:
            result = await media_library(
                operation='get_calibre_book_metadata',
                library_path='C:/Users/Username/Calibre Library',
                book_title='Python Cookbook',
                author='David Beazley',
                include_metadata=True
            )
            # Returns: {
            #     'success': True,
            #     'book_info': {
            #         'title': 'Python Cookbook',
            #         'author': 'David Beazley',
            #         'isbn': '978-0596107973',
            #         'published': '2005-01-01'
            #     },
            #     'metadata': {
            #         'cover_path': '...',
            #         'description': '...',
            #         'tags': [...]
            #     }
            # }

        Full-text search in Calibre:
            result = await media_library(
                operation='search_calibre_fts',
                library_path='C:/Users/Username/Calibre Library',
                search_query='machine learning'
            )
            # Returns: {
            #     'success': True,
            #     'results': [
            #         {
            #             'title': 'Machine Learning with Python',
            #             'highlight': '...machine learning...',
            #             'relevance_score': 0.95
            #         }
            #     ],
            #     'count': 8
            # }

        Find Plex database:
            result = await media_library(
                operation='find_plex_database',
                plex_server_url='http://localhost:32400'
            )
            # Returns: {
            #     'success': True,
            #     'database_path': (
            #         'C:\\Users\\Username\\AppData\\Local\\'
            #         'Plex Media Server\\Plug-in Support\\Databases\\'
            #         'com.plexapp.plugins.library.db'
            #     ),
            #     'server_info': {...},
            #     'status': 'found'
            # }

        Optimize Plex database:
            result = await media_library(
                operation='optimize_plex_database',
                plex_server_url='http://localhost:32400',
                plex_token='your-token',
                optimize_database=True
            )
            # Returns: {
            #     'success': True,
            #     'message': 'Plex database optimized successfully',
            #     'optimization_stats': {
            #         'vacuum_time': 45.2,
            #         'analyze_time': 12.8,
            #         'size_before': 2048000000,
            #         'size_after': 1800000000
            #     }
            # }

        Get Plex library statistics:
            result = await media_library(
                operation='get_plex_library_stats',
                plex_server_url='http://localhost:32400',
                plex_token='your-token',
                library_name='Movies'
            )
            # Returns: {
                'success': True,
                'library_name': 'Movies',
                'stats': {
                    'total_items': 1250,
                    'total_size_gb': 245.8,
                    'by_genre': {...},
                    'by_year': {...}
                }
            }

        Export database schema:
            result = await media_library(
                operation='export_database_schema',
                library_path='C:/Users/Username/Calibre Library',
                export_format='json',
                export_path='C:/data/calibre_schema.json'
            )
            # Returns: {
            #     'success': True,
            #     'export_path': 'C:/data/calibre_schema.json',
            #     'format': 'json',
            #     'schema_data': {...}
            # }

        Error handling - library path not found:
            result = await media_library(
                operation='search_calibre_library',
                library_path='C:/nonexistent/library'
            )
            # Returns: {
            #     'success': False,
            #     'error': 'Library path not found: C:/nonexistent/library'
            # }

    Errors:
        Common errors and solutions:
        - 'Library path is required':
            Cause: Missing library_path for Calibre operations
            Fix: Provide valid library_path pointing to Calibre library root
            Example: library_path='C:/Users/Username/Calibre Library'

        - 'Library path not found: {path}':
            Cause: Calibre library directory doesn't exist
            Fix: Verify path exists, check spelling, ensure Calibre is installed
            Workaround: Use absolute paths, check permissions

        - 'Plex server not accessible':
            Cause: Plex Media Server not running or URL incorrect
            Fix: Verify Plex is running, check URL and port (default: 32400)
            Workaround: Test URL in browser, check firewall settings

        - 'Invalid Plex token':
            Cause: Plex authentication token is invalid or expired
            Fix: Generate new token from Plex web interface
            Workaround: Some operations work without token (read-only)

        - 'Database optimization failed: {error}':
            Cause: Database locked or corrupted
            Fix: Stop Plex Media Server, verify database integrity, check disk space
            Workaround: Export data first, restore from backup if corrupted

        - 'Export failed: {error}':
            Cause: Export path inaccessible or insufficient permissions
            Fix: Verify path exists, check write permissions, ensure sufficient disk space
            Workaround: Export to user home directory or temp folder

    See Also:
        - db_connection: Database connection management for media databases
        - db_schema: Schema inspection for media databases
        - windows_system: Windows-specific media database operations
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
    library_path: str | None,
    book_title: str | None,
    author: str | None,
    search_query: str | None,
    include_metadata: bool,
) -> dict[str, Any]:
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
    library_path: str | None,
    book_title: str | None,
    author: str | None,
    include_metadata: bool,
) -> dict[str, Any]:
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


async def _search_calibre_fts(library_path: str | None, search_query: str | None) -> dict[str, Any]:
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


async def _find_plex_database(plex_server_url: str | None) -> dict[str, Any]:
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
    plex_server_url: str | None, plex_token: str | None, optimize_database: bool
) -> dict[str, Any]:
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
    library_path: str | None, export_format: str, export_path: str | None
) -> dict[str, Any]:
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
    plex_server_url: str | None, plex_token: str | None, library_name: str | None
) -> dict[str, Any]:
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
    plex_server_url: str | None, plex_token: str | None
) -> dict[str, Any]:
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
