# Database full-text search portmanteau tool.
# Consolidates all full-text search operations into a single interface.

import logging
from typing import Any

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.database_manager import db_manager
from database_operations_mcp.tools.help_tools import HelpSystem

logger = logging.getLogger(__name__)


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def db_fts(
    operation: str,
    connection_name: str = "default",
    search_query: str | None = None,
    table_name: str | None = None,
    columns: list[str] | None = None,
    limit: int = 100,
    offset: int = 0,
    highlight: bool = True,
    include_metadata: bool = True,
) -> dict[str, Any]:
    """Database full-text search portmanteau tool.

    Comprehensive full-text search operations consolidating ALL FTS operations into
    a single interface. Supports advanced search with ranking, highlighting, suggestions,
    and metadata across SQL, NoSQL, and Vector databases with full-text search capabilities.

    Prerequisites:
        - Valid database connection registered via db_connection
        - For FTS operations: Database must have full-text search indexes created
        - For fts_search: Tables must have FTS indexes on target columns
        - For fts_suggest: Database must support suggestion/autocomplete features

    Operations:
        - fts_search: Perform full-text search across tables and columns with ranking
        - fts_tables: List all tables that have full-text search indexes
        - fts_suggest: Get search suggestions and autocomplete based on partial input

    Parameters:
        operation (str, REQUIRED): The operation to perform
            Valid values: 'fts_search', 'fts_tables', 'fts_suggest'
            Example: 'fts_search', 'fts_tables', 'fts_suggest'

        connection_name (str, OPTIONAL): Name of the database connection to use
            Format: Registered connection name (from db_connection)
            Default: 'default'
            Validation: Must be previously registered
            Required for: All operations
            Example: 'prod_db', 'analytics_warehouse'

        search_query (str, OPTIONAL): Search query string for FTS operations
            Format: Free-form search text (supports phrases, operators)
            Required for: fts_search, fts_suggest operations
            Behavior: Searches indexed text columns using database FTS engine
            SQLite FTS: Supports phrase queries, boolean operators
            PostgreSQL FTS: Supports tsquery syntax, ranking
            Example: 'machine learning', 'python AND programming', '"exact phrase"'

        table_name (str, OPTIONAL): Name of the table to search in
            Format: Valid table name in database
            Required for: fts_search (if not searching all tables)
            Validation: Table must exist and have FTS index
            Example: 'articles', 'documents', 'posts'

        columns (list[str], OPTIONAL): List of columns to search in
            Format: List of column names that have FTS indexes
            Required for: fts_search (if table_name provided and not all columns)
            Validation: All columns must have FTS indexes
            Example: ['title', 'content'], ['body', 'summary']

        limit (int, OPTIONAL): Maximum number of results to return
            Format: Positive integer
            Range: 1-10,000
            Default: 100
            Used for: fts_search, fts_suggest operations
            Example: 50, 500, 1000

        offset (int, OPTIONAL): Number of results to skip (for pagination)
            Format: Non-negative integer
            Range: 0-1,000,000
            Default: 0
            Used for: fts_search operation
            Behavior: Skips N results, returns next 'limit' results
            Example: 0, 100, 200

        highlight (bool, OPTIONAL): Highlight matching terms in results
            Default: True
            Behavior: Wraps matching terms with markers or HTML tags
            Used for: fts_search operation
            Impact: Adds processing time but improves result visibility
            Example: True, False

        include_metadata (bool, OPTIONAL): Include search metadata in results
            Default: True
            Behavior: Adds relevance scores, match positions, search statistics
            Used for: fts_search operation
            Example: True, False

    Returns:
        Dictionary containing operation-specific results:
            - success: Boolean indicating operation success
            - operation: Echo of operation performed
            - For fts_search: results (list), total_results, highlighted_results (if highlight),
                            metadata (if include_metadata), pagination (limit/offset/has_more)
            - For fts_tables: fts_tables (list), count
            - For fts_suggest: suggestions (list), count
            - error: Error message if success is False
            - connection_name: Echo of connection used
            - search_query: Echo of search query (for search operations)
            - available_operations: List of valid operations (on invalid operation)

    Usage:
        This tool provides advanced full-text search capabilities across database content.
        Use it to search text content efficiently with ranking, highlighting, and pagination.

        Common scenarios:
        - Content search: Search articles, documents, or posts by content
        - Text discovery: Find relevant content across large text datasets
        - Autocomplete: Generate search suggestions for user interfaces
        - Research: Search academic papers, research notes, or documentation
        - Search optimization: Understand which tables have FTS capabilities

        Best practices:
        - Create FTS indexes before searching (use db_schema to verify)
        - Use specific table_name and columns for faster searches
        - Use pagination (offset/limit) for large result sets
        - Enable highlighting for better user experience
        - Use fts_suggest for autocomplete features

    Examples:
        Full-text search across all indexed tables:
            result = await db_fts(
                operation='fts_search',
                connection_name='production_db',
                search_query='machine learning',
                limit=50,
                highlight=True
            )
            # Returns: {
            #     'success': True,
            #     'results': [
            #         {
            #             'table': 'articles',
            #             'id': 123,
            #             'title': 'Introduction to Machine Learning',
            #             'relevance_score': 0.95,
            #             'matched_columns': ['title', 'content']
            #         }
            #     ],
            #     'total_results': 42,
            #     'highlighted_results': [
            #         {'title': 'Introduction to <mark>Machine Learning</mark>'}
            #     ],
            #     'metadata': {
            #         'search_time_ms': 12.5,
            #         'tables_searched': ['articles', 'posts']
            #     },
            #     'pagination': {'limit': 50, 'offset': 0, 'has_more': False}
            # }

        Search specific table and columns:
            result = await db_fts(
                operation='fts_search',
                connection_name='production_db',
                search_query='python programming',
                table_name='articles',
                columns=['title', 'content'],
                limit=20,
                offset=0,
                highlight=True
            )
            # Returns: {
            #     'success': True,
            #     'results': [
            #         {
            #             'id': 456,
            #             'title': 'Python Programming Guide',
            #             'content': '...',
            #             'relevance_score': 0.92
            #         }
            #     ],
            #     'total_results': 15,
            #     'table_name': 'articles',
            #     'pagination': {'limit': 20, 'offset': 0, 'has_more': False}
            # }

        List FTS-enabled tables:
            result = await db_fts(
                operation='fts_tables',
                connection_name='production_db'
            )
            # Returns: {
            #     'success': True,
            #     'fts_tables': [
            #         {
            #             'table_name': 'articles',
            #             'index_name': 'fts_articles_idx',
            #             'columns': ['title', 'content'],
            #             'status': 'active'
            #         },
            #         {
            #             'table_name': 'posts',
            #             'index_name': 'fts_posts_idx',
            #             'columns': ['body'],
            #             'status': 'active'
            #         }
            #     ],
            #     'count': 2
            # }

        Get search suggestions:
            result = await db_fts(
                operation='fts_suggest',
                connection_name='production_db',
                search_query='mach',
                limit=10
            )
            # Returns: {
            #     'success': True,
            #     'suggestions': [
            #         'machine learning',
            #         'machine vision',
            #         'machine translation',
            #         'machinery'
            #     ],
            #     'count': 4,
            #     'search_query': 'mach'
            # }

        Paginated search (get next page):
            result = await db_fts(
                operation='fts_search',
                connection_name='production_db',
                search_query='python',
                limit=20,
                offset=20
            )
            # Returns: Results 21-40 from search

        Error handling - no FTS indexes:
            result = await db_fts(
                operation='fts_search',
                connection_name='production_db',
                search_query='python',
                table_name='articles'
            )
            # Returns: {
            #     'success': False,
            #     'error': 'Table articles has no full-text search indexes'
            # }

    Errors:
        Common errors and solutions:
        - 'Table has no full-text search indexes':
            Cause: Table doesn't have FTS indexes created
            Fix: Create FTS index using database-specific commands
            Workaround: Use db_schema to check indexes, create FTS index manually

        - 'Connection not found: {connection_name}':
            Cause: Connection name doesn't exist or not registered
            Fix: Use db_connection(operation='list') to see available connections
            Workaround: Register connection first with db_connection(operation='register')

        - 'Search query is required':
            Cause: Missing search_query parameter
            Fix: Provide search_query parameter with search terms
            Example: search_query='machine learning'

        - 'FTS search failed: {error}':
            Cause: Database FTS query syntax error or unsupported operation
            Fix: Verify search query syntax for database type, check FTS support
            Workaround: Simplify query, check database FTS documentation

        - 'No FTS-enabled tables found':
            Cause: Database has no tables with full-text search indexes
            Fix: Create FTS indexes on tables you want to search
            Workaround: Use regular db_operations for text search (slower)

    See Also:
        - db_connection: Register and manage database connections
        - db_operations: Execute regular SQL queries (non-FTS)
        - db_schema: Inspect table structure and indexes
    """

    if operation == "fts_search":
        return await _fts_search(
            connection_name,
            search_query,
            table_name,
            columns,
            limit,
            offset,
            highlight,
            include_metadata,
        )
    elif operation == "fts_tables":
        return await _fts_tables(connection_name)
    elif operation == "fts_suggest":
        return await _fts_suggest(connection_name, search_query, limit)
    else:
        return {
            "success": False,
            "error": f"Unknown operation: {operation}",
            "available_operations": ["fts_search", "fts_tables", "fts_suggest"],
        }


async def _fts_search(
    connection_name: str,
    search_query: str,
    table_name: str | None,
    columns: list[str] | None,
    limit: int,
    offset: int,
    highlight: bool,
    include_metadata: bool,
) -> dict[str, Any]:
    """Perform full-text search across tables and columns."""
    try:
        if not connection_name:
            raise ValueError("Connection name is required")
        if not search_query:
            raise ValueError("Search query is required")

        connector = db_manager.get_connector(connection_name)
        if not connector:
            raise ValueError(f"Connection '{connection_name}' not found")

        # Build search parameters
        search_params = {
            "query": search_query,
            "table_name": table_name,
            "columns": columns,
            "limit": limit,
            "offset": offset,
            "highlight": highlight,
            "include_metadata": include_metadata,
        }

        # Perform search
        search_result = await connector.fts_search(search_params)

        return {
            "success": True,
            "message": f"Full-text search completed for '{search_query}'",
            "connection_name": connection_name,
            "search_query": search_query,
            "table_name": table_name,
            "results": search_result.get("results", []),
            "total_results": search_result.get("total_results", 0),
            "highlighted_results": search_result.get("highlighted_results", [])
            if highlight
            else [],
            "metadata": search_result.get("metadata", {}) if include_metadata else {},
            "pagination": {
                "limit": limit,
                "offset": offset,
                "has_more": search_result.get("total_results", 0) > offset + limit,
            },
        }

    except Exception as e:
        logger.error(f"Error performing FTS search: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to perform FTS search: {str(e)}",
            "connection_name": connection_name,
            "search_query": search_query,
            "results": [],
            "total_results": 0,
        }


async def _fts_tables(connection_name: str) -> dict[str, Any]:
    """List all tables that have full-text search indexes."""
    try:
        if not connection_name:
            raise ValueError("Connection name is required")

        connector = db_manager.get_connector(connection_name)
        if not connector:
            raise ValueError(f"Connection '{connection_name}' not found")

        fts_tables = await connector.get_fts_tables()

        return {
            "success": True,
            "message": "FTS-enabled tables listed successfully",
            "connection_name": connection_name,
            "fts_tables": fts_tables,
            "count": len(fts_tables),
        }

    except Exception as e:
        logger.error(f"Error listing FTS tables: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to list FTS tables: {str(e)}",
            "connection_name": connection_name,
            "fts_tables": [],
            "count": 0,
        }


async def _fts_suggest(connection_name: str, search_query: str, limit: int) -> dict[str, Any]:
    """Get search suggestions based on partial input."""
    try:
        if not connection_name:
            raise ValueError("Connection name is required")
        if not search_query:
            raise ValueError("Search query is required")

        connector = db_manager.get_connector(connection_name)
        if not connector:
            raise ValueError(f"Connection '{connection_name}' not found")

        suggestions = await connector.fts_suggest(search_query, limit)

        return {
            "success": True,
            "message": f"Search suggestions generated for '{search_query}'",
            "connection_name": connection_name,
            "search_query": search_query,
            "suggestions": suggestions,
            "count": len(suggestions),
        }

    except Exception as e:
        logger.error(f"Error generating FTS suggestions: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to generate FTS suggestions: {str(e)}",
            "connection_name": connection_name,
            "search_query": search_query,
            "suggestions": [],
            "count": 0,
        }
