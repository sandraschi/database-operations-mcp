# Media library management portmanteau tool.
# Consolidates Calibre, Plex, and media operations into a single interface.

import logging
from typing import Any

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.operation_types import MediaLibraryOperation
from database_operations_mcp.tool_responses import unknown_operation_response
from database_operations_mcp.tools.help_tools import HelpSystem

logger = logging.getLogger(__name__)
_MEDIA_MAX_LIMIT = 500
_MEDIA_MAX_OFFSET = 100_000


@mcp.tool()
@HelpSystem.register_tool(category="media")
async def media_library(
    operation: MediaLibraryOperation,
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
    action: str | None = None,
    library_section: str | None = None,
    item_id: int | None = None,
    limit: int = 50,
    offset: int = 0,
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
        - search_calibre_library: Metadata search in Calibre `metadata.db` (fast title/author/tag style lookup)
        - get_calibre_book_metadata: Get detailed metadata for a specific book
        - search_calibre_fts: Alias of search_calibre_fts_db for backward compatibility
        - search_calibre_fts_db: Content search in Calibre `full-text-search.db` (slower, deeper text matching)
        - find_plex_database: Locate Plex Media Server database file
        - optimize_plex_database: Optimize Plex database performance
        - manage_plex_metadata: Analyze or export Plex metadata
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
            Required for: search_calibre_library, search_calibre_fts, search_calibre_fts_db operations
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

        limit (int, OPTIONAL): Maximum items returned for paginated list/search operations
            Range: 1-500 (server clamps out-of-range values)
            Default: 50
            Used for: search_calibre_library, search_calibre_fts, search_calibre_fts_db

        offset (int, OPTIONAL): Zero-based row offset for paginated list/search operations
            Range: 0-100000 (server clamps out-of-range values)
            Default: 0
            Used for: search_calibre_library, search_calibre_fts, search_calibre_fts_db

    Returns:
        Dictionary containing operation-specific results:
            - success: Boolean indicating operation success
            - operation: Echo of operation performed
            - For search_calibre_library: results (list), count, total_count, pagination{limit,offset,has_more}, library_path
            - For get_calibre_book_metadata: book_info (dict), metadata (if requested)
            - For search_calibre_fts: results (list with highlights), count, total_count, pagination, fts_db_path
            - For search_calibre_fts_db: results (list with metadata), count, total_count, pagination, fts_db_path
            - For find_plex_database: database_path, server_info, status
            - For optimize_plex_database: message, optimization_stats
            - For export_database_schema: export_path, format, schema_data
            - For get_plex_library_stats: stats (dict), library_name, item_counts
            - For get_plex_library_sections: sections (list), total_sections
            - error: Error message if success is False
            - error_type: invalid_input | user_fixable | retryable | fatal
            - recovery_options: Suggested next steps after failures
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

        Search Calibre FTS database:
            result = await media_library(
                operation='search_calibre_fts_db',
                library_path='C:/Users/Username/Calibre Library',
                search_query='python programming',
                include_metadata=True
            )
            # Returns: {
            #     'success': True,
            #     'results': [
            #         {
            #             'book_id': 123,
            #             'title': 'Python Cookbook',
            #             'author': 'David Beazley',
            #             'format': 'EPUB',
            #             'text_preview': '...python programming...',
            #             'relevance_score': 0.89
            #         }
            #     ],
            #     'count': 12,
            #     'fts_db_path': 'C:/Users/Username/Calibre Library/full-text-search.db'
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

    limit = max(1, min(limit, _MEDIA_MAX_LIMIT))
    offset = max(0, min(offset, _MEDIA_MAX_OFFSET))

    if operation == "search_calibre_library":
        return await _search_calibre_library(
            library_path, book_title, author, search_query, include_metadata, limit, offset
        )
    elif operation == "get_calibre_book_metadata":
        return await _get_calibre_book_metadata(
            library_path, book_title, author, include_metadata
        )
    elif operation == "search_calibre_fts":
        return await _search_calibre_fts(
            library_path, search_query, limit=limit, offset=offset
        )
    elif operation == "search_calibre_fts_db":
        return await _search_calibre_fts_db(
            library_path, search_query, include_metadata, limit=limit, offset=offset
        )
    elif operation == "find_plex_database":
        return await _find_plex_database(plex_server_url)
    elif operation == "optimize_plex_database":
        return await _optimize_plex_database(
            plex_server_url, plex_token, optimize_database
        )
    elif operation == "export_database_schema":
        return await _export_database_schema(library_path, export_format, export_path)
    elif operation == "get_plex_library_stats":
        return await _get_plex_library_stats(plex_server_url, plex_token, library_name)
    elif operation == "manage_plex_metadata":
        return await _manage_plex_metadata(action, library_section, item_id)
    elif operation == "get_plex_library_sections":
        return await _get_plex_library_sections(plex_server_url, plex_token)
    else:
        return unknown_operation_response(
            operation,
            [
                "search_calibre_library",
                "get_calibre_book_metadata",
                "search_calibre_fts",
                "search_calibre_fts_db",
                "find_plex_database",
                "optimize_plex_database",
                "manage_plex_metadata",
                "export_database_schema",
                "get_plex_library_stats",
                "get_plex_library_sections",
            ],
        )


async def _search_calibre_library(
    library_path: str | None,
    book_title: str | None,
    author: str | None,
    search_query: str | None,
    include_metadata: bool,
    limit: int,
    offset: int,
) -> dict[str, Any]:
    """Search books in Calibre library."""
    try:
        if not library_path:
            raise ValueError("Library path is required")

        import os
        import sqlite3

        db_path = os.path.join(library_path, "metadata.db")
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Calibre database not found at {db_path}")

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

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
            WHERE 1=1
        """
        params = []

        if book_title:
            query += " AND b.title LIKE ?"
            params.append(f"%{book_title}%")

        if author:
            query += " AND authors LIKE ?"
            params.append(f"%{author}%")

        if search_query:
            query += " AND (b.title LIKE ? OR authors LIKE ?)"
            params.extend([f"%{search_query}%", f"%{search_query}%"])

        count_query = f"SELECT COUNT(*) FROM ({query}) as q"  # noqa: S608  # subquery built from trusted code
        cursor.execute(count_query, params)
        total_count = int(cursor.fetchone()[0])

        query += " ORDER BY b.timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()
        results = [dict(row) for row in rows]

        if include_metadata:
            for res in results:
                # Add tags
                cursor.execute(
                    """
                    SELECT t.name
                    FROM tags t
                    JOIN books_tags_link btl ON t.id = btl.tag
                    WHERE btl.book = ?
                """,
                    (res["id"],),
                )
                res["tags"] = [row["name"] for row in cursor.fetchall()]

        conn.close()

        return {
            "success": True,
            "results": results,
            "count": len(results),
            "total_count": total_count,
            "library_path": library_path,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "returned_count": len(results),
                "total_count": total_count,
                "has_more": total_count > (offset + len(results)),
            },
        }

    except Exception as e:
        logger.error(f"Error searching Calibre library: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to search Calibre library: {e!s}",
            "error_type": "user_fixable",
            "recovery_options": [
                "Verify library_path contains metadata.db.",
                "Ensure Calibre is not locking the database (close Calibre or retry).",
            ],
            "library_path": library_path,
            "results": [],
            "count": 0,
            "total_count": 0,
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

        import os
        import sqlite3

        db_path = os.path.join(library_path, "metadata.db")
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Calibre database not found at {db_path}")

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
            SELECT b.*, c.text as comments,
            (SELECT GROUP_CONCAT(name, ' & ') FROM authors a JOIN books_authors_link bal ON a.id = bal.author WHERE bal.book = b.id) as authors_list
            FROM books b
            LEFT JOIN comments c ON b.id = c.book
            WHERE 1=1
        """
        params = []
        if book_title:
            query += " AND b.title = ?"
            params.append(book_title)
        if author:
            query += " AND authors_list LIKE ?"
            params.append(f"%{author}%")

        query += " LIMIT 1"

        cursor.execute(query, params)
        row = cursor.fetchone()

        if not row:
            return {"success": False, "error": "Book not found"}

        book_info = dict(row)

        if include_metadata:
            # Get tags
            cursor.execute(
                """
                SELECT t.name FROM tags t JOIN books_tags_link btl ON t.id = btl.tag WHERE btl.book = ?
            """,
                (book_info["id"],),
            )
            book_info["tags"] = [r["name"] for r in cursor.fetchall()]

            # Get formats
            cursor.execute(
                """
                SELECT format, name || '.' || LOWER(format) as filename FROM data WHERE book = ?
            """,
                (book_info["id"],),
            )
            book_info["formats"] = [dict(r) for r in cursor.fetchall()]

        conn.close()

        return {"success": True, "book_info": book_info, "library_path": library_path}

    except Exception as e:
        logger.error(f"Error getting Calibre book metadata: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to get Calibre book metadata: {e!s}",
            "library_path": library_path,
            "book_title": book_title,
            "metadata": {},
        }


async def _search_calibre_fts(
    library_path: str | None, search_query: str | None, limit: int, offset: int
) -> dict[str, Any]:
    """Perform full-text search in Calibre library."""
    # Deflecting to _search_calibre_fts_db as it is the same functionality
    return await _search_calibre_fts_db(
        library_path, search_query, include_metadata=True, limit=limit, offset=offset
    )


async def _search_calibre_fts_db(
    library_path: str | None,
    search_query: str | None,
    include_metadata: bool,
    limit: int,
    offset: int,
) -> dict[str, Any]:
    """Search Calibre's full-text-search database."""
    try:
        if not library_path:
            raise ValueError("Library path is required")
        if not search_query:
            raise ValueError("Search query is required")

        import os
        import sqlite3

        # Path to FTS database
        fts_db_path = os.path.join(library_path, "full-text-search.db")
        metadata_db_path = os.path.join(library_path, "metadata.db")

        if not os.path.exists(fts_db_path):
            return {
                "success": False,
                "error": f"FTS database not found: {fts_db_path}",
                "library_path": library_path,
                "search_query": search_query,
                "error_type": "user_fixable",
                "recovery_options": [
                    "Enable Calibre full-text indexing and reopen the library.",
                    "Use search_calibre_library for metadata-only search.",
                ],
                "results": [],
                "count": 0,
                "total_count": 0,
            }

        # Connect to FTS database
        fts_conn = sqlite3.connect(fts_db_path)
        fts_cursor = fts_conn.cursor()

        # Build search query - use LIKE for now since custom tokenizer isn't available
        search_pattern = f"%{search_query}%"

        # Search in books_text table
        fts_cursor.execute(
            """
            SELECT COUNT(*)
            FROM books_text
            WHERE searchable_text LIKE ? AND searchable_text IS NOT NULL
        """,
            (search_pattern,),
        )
        total_count = int(fts_cursor.fetchone()[0])

        fts_cursor.execute(
            """
            SELECT book, format, text_size, searchable_text
            FROM books_text
            WHERE searchable_text LIKE ? AND searchable_text IS NOT NULL
            ORDER BY text_size DESC
            LIMIT ? OFFSET ?
        """,
            (search_pattern, limit, offset),
        )

        fts_results = fts_cursor.fetchall()

        results = []
        book_metadata = {}

        # If metadata is requested, get book info from metadata.db
        if include_metadata and os.path.exists(metadata_db_path):
            try:
                meta_conn = sqlite3.connect(metadata_db_path)
                meta_cursor = meta_conn.cursor()

                # Get unique book IDs
                book_ids = list({row[0] for row in fts_results})
                if book_ids:
                    # Get book titles and authors
                    placeholders = ",".join("?" * len(book_ids))
                    meta_cursor.execute(
                        f"""
                        SELECT id, title, author_sort
                        FROM books
                        WHERE id IN ({placeholders})
                    """,  # noqa: S608  # hardcoded table, parameterized IN clause
                        book_ids,
                    )

                    book_metadata = {
                        row[0]: {"title": row[1], "author": row[2]}
                        for row in meta_cursor.fetchall()
                    }

                meta_conn.close()
            except Exception as e:
                logger.warning(f"Could not load book metadata: {e}")

        # Process results
        for row in fts_results:
            book_id, format_name, text_size, full_text = row

            # Find context around search term
            search_lower = search_query.lower()
            text_lower = full_text.lower()
            idx = text_lower.find(search_lower)

            if idx >= 0:
                # Extract context around the match
                start = max(0, idx - 100)
                end = min(len(full_text), idx + len(search_query) + 100)
                context = full_text[start:end]

                # Highlight the search term
                context_lower = context.lower()
                highlight_start = context_lower.find(search_lower)
                if highlight_start >= 0:
                    highlighted = (
                        context[:highlight_start]
                        + "**"
                        + context[highlight_start : highlight_start + len(search_query)]
                        + "**"
                        + context[highlight_start + len(search_query) :]
                    )
                else:
                    highlighted = context
            else:
                # Fallback if we can't find the term (shouldn't happen with LIKE)
                highlighted = full_text[:200] + "..."

            result = {
                "book_id": book_id,
                "format": format_name,
                "text_size": text_size,
                "text_preview": highlighted,
                "relevance_score": 1.0,  # Basic relevance for LIKE search
            }

            if include_metadata and book_id in book_metadata:
                result.update(book_metadata[book_id])

            results.append(result)

        fts_conn.close()

        return {
            "success": True,
            "operation": "search_calibre_fts_db",
            "library_path": library_path,
            "fts_db_path": fts_db_path,
            "search_query": search_query,
            "results": results,
            "count": len(results),
            "total_count": total_count,
            "include_metadata": include_metadata,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "returned_count": len(results),
                "total_count": total_count,
                "has_more": total_count > (offset + len(results)),
            },
        }

    except Exception as e:
        logger.error(f"Error searching Calibre FTS database: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to search Calibre FTS database: {e!s}",
            "library_path": library_path,
            "search_query": search_query,
            "error_type": "retryable",
            "recovery_options": [
                "Retry once in case the DB was temporarily locked.",
                "If persistent, rebuild Calibre full-text index then retry.",
            ],
            "results": [],
            "count": 0,
            "total_count": 0,
        }


async def _find_plex_database(plex_server_url: str | None) -> dict[str, Any]:
    """Locate Plex Media Server database."""
    try:
        from database_operations_mcp.tools.plex_tools import PlexDatabase

        # We don't even need the URL if we are looking locally,
        # but we could use it to verify server if needed.
        plex = PlexDatabase()
        db_path = plex.db_path

        return {
            "success": True,
            "database_path": str(db_path),
            "status": "found" if db_path.exists() else "not_found",
            "server_url": plex_server_url,
        }

    except Exception as e:
        logger.error(f"Error finding Plex database: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to find Plex database: {e!s}",
            "plex_server_url": plex_server_url,
            "database_path": None,
        }


async def _optimize_plex_database(
    plex_server_url: str | None, plex_token: str | None, optimize_database: bool
) -> dict[str, Any]:
    """Optimize Plex database performance."""
    try:
        import time

        from database_operations_mcp.tools.plex_tools import PlexDatabase

        if not optimize_database:
            return {
                "success": True,
                "message": "Optimization not requested (optimize_database=False)",
                "plex_server_url": plex_server_url,
            }

        with PlexDatabase() as plex:
            db_path = plex.db_path
            if not db_path.exists():
                raise FileNotFoundError(f"Plex database not found at {db_path}")

            size_before = db_path.stat().st_size

            # Note: We use a separate connection for optimization to avoid 'file:...?mode=ro' limitations
            # but we must be careful as Plex might be running.
            import sqlite3

            opt_conn = sqlite3.connect(str(db_path))
            cursor = opt_conn.cursor()

            start_time = time.time()
            cursor.execute("VACUUM")
            vacuum_time = time.time() - start_time

            start_time = time.time()
            cursor.execute("ANALYZE")
            analyze_time = time.time() - start_time

            opt_conn.close()

            size_after = db_path.stat().st_size

            return {
                "success": True,
                "message": "Plex database optimized successfully",
                "plex_server_url": plex_server_url,
                "optimization_stats": {
                    "vacuum_time_sec": round(vacuum_time, 2),
                    "analyze_time_sec": round(analyze_time, 2),
                    "size_before_bytes": size_before,
                    "size_after_bytes": size_after,
                    "saved_bytes": size_before - size_after,
                },
            }

    except Exception as e:
        logger.error(f"Error optimizing Plex database: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to optimize Plex database: {e!s}",
            "plex_server_url": plex_server_url,
        }


async def _manage_plex_metadata(
    action: str, library_section: str | None = None, item_id: int | None = None
) -> dict[str, Any]:
    """Manage Plex metadata through analysis or export."""
    try:
        from database_operations_mcp.tools.plex_tools import PlexDatabase

        with PlexDatabase() as plex:
            if action == "analyze":
                sections = plex.get_library_sections()
                # Get basic counts for each section
                section_summaries = []
                for section in sections:
                    plex.get_media_items(section_id=section["id"], limit=1)
                    # This is just a summary, we'd need a real count query for full stats
                    section_summaries.append(
                        {
                            "id": section["id"],
                            "name": section["name"],
                            "type": section.get("section_type"),
                        }
                    )

                return {
                    "success": True,
                    "operation": "manage_plex_metadata",
                    "action": action,
                    "database_path": str(plex.db_path),
                    "sections": section_summaries,
                    "total_sections": len(sections),
                }

            elif action == "export":
                # Implementation delegated to PlexDatabase.export_library
                # We'll use a temporary path if none provided or just return data
                result = plex.export_library(output_format="json")
                return {
                    "success": True,
                    "operation": "manage_plex_metadata",
                    "action": action,
                    "data": result.get("data") if "data" in result else result,
                }

            else:
                return {
                    "success": False,
                    "error": f"Unsupported Plex metadata action: {action}",
                    "supported_actions": ["analyze", "export"],
                }

    except Exception as e:
        logger.error(f"Error managing Plex metadata: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to manage Plex metadata: {e!s}",
        }


async def _export_database_schema(
    library_path: str | None, export_format: str, export_path: str | None
) -> dict[str, Any]:
    """Export database schema information."""
    try:
        import json
        import os
        import sqlite3

        # Determine which database to export (Calibre if library_path provided, else try Plex)
        db_path = None
        if library_path:
            db_path = os.path.join(library_path, "metadata.db")
        else:
            from database_operations_mcp.tools.plex_tools import PlexDatabase

            db_path = str(PlexDatabase().db_path)

        if not db_path or not os.path.exists(db_path):
            raise FileNotFoundError(f"Database not found at {db_path}")

        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cursor = conn.cursor()

        # Get all tables and their schemas
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
        schema_data = {row[0]: row[1] for row in cursor.fetchall()}

        # Also get indices
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index'")
        indices = {row[0]: row[1] for row in cursor.fetchall()}

        full_schema = {
            "tables": schema_data,
            "indices": indices,
            "database_path": db_path,
        }

        conn.close()

        if export_path:
            with open(export_path, "w", encoding="utf-8") as f:
                if export_format == "json":
                    json.dump(full_schema, f, indent=2)
                else:
                    # Basic text export for other formats for now
                    f.write(str(full_schema))

        return {
            "success": True,
            "message": f"Database schema exported successfully ({export_format})",
            "library_path": library_path or "Plex Default",
            "export_path": export_path,
            "schema": full_schema if not export_path else "Saved to file",
        }

    except Exception as e:
        logger.error(f"Error exporting database schema: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to export database schema: {e!s}",
            "library_path": library_path,
        }


async def _get_plex_library_stats(
    plex_server_url: str | None, plex_token: str | None, library_name: str | None
) -> dict[str, Any]:
    """Get statistics about Plex library."""
    try:
        from database_operations_mcp.tools.plex_tools import PlexDatabase

        with PlexDatabase() as plex:
            sections = plex.get_library_sections()

            target_section = None
            if library_name:
                for s in sections:
                    if s["name"].lower() == library_name.lower():
                        target_section = s
                        break

            if library_name and not target_section:
                return {
                    "success": False,
                    "error": f"Library section '{library_name}' not found",
                }

            stats = {}
            if target_section:
                items = plex.get_media_items(
                    section_id=target_section["id"], limit=10000
                )
                stats = {
                    "total_items": len(items),
                    "total_size_bytes": sum(
                        item.get("file_size", 0)
                        for item in items
                        if item.get("file_size")
                    ),
                    "section_type": target_section["section_type"],
                    "created_at": target_section["created_at"],
                }
            else:
                # Stats for all sections
                total_items = 0
                total_size = 0
                for s in sections:
                    sec_items = plex.get_media_items(section_id=s["id"], limit=10000)
                    total_items += len(sec_items)
                    total_size += sum(
                        item.get("file_size", 0)
                        for item in sec_items
                        if item.get("file_size")
                    )

                stats = {
                    "total_sections": len(sections),
                    "total_items": total_items,
                    "total_size_bytes": total_size,
                }

            return {
                "success": True,
                "library_name": library_name or "All Sections",
                "stats": stats,
            }

    except Exception as e:
        logger.error(f"Error getting Plex library stats: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to get Plex library stats: {e!s}",
            "plex_server_url": plex_server_url,
            "library_name": library_name,
            "stats": {},
        }


async def _get_plex_library_sections(
    plex_server_url: str | None, plex_token: str | None
) -> dict[str, Any]:
    """Get information about Plex library sections."""
    try:
        from database_operations_mcp.tools.plex_tools import PlexDatabase

        with PlexDatabase() as plex:
            sections = plex.get_library_sections()
            return {"success": True, "sections": sections, "count": len(sections)}
    except Exception as e:
        return {"success": False, "error": str(e)}
