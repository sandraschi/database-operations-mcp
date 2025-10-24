# Database full-text search portmanteau tool.
# Consolidates all full-text search operations into a single interface.

import logging
from typing import Any, Dict, List, Optional

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
    search_query: Optional[str] = None,
    table_name: Optional[str] = None,
    columns: Optional[List[str]] = None,
    limit: int = 100,
    offset: int = 0,
    highlight: bool = True,
    include_metadata: bool = True,
) -> Dict[str, Any]:
    """Database full-text search portmanteau tool.

    This tool consolidates all full-text search operations into a single interface,
    providing unified access to FTS functionality across different database types.

    Operations:
    - fts_search: Perform full-text search across tables and columns
    - fts_tables: List all tables that have full-text search indexes
    - fts_suggest: Get search suggestions based on partial input

    Args:
        operation: The operation to perform (required)
        connection_name: Name of the database connection to use
        search_query: Search query string for FTS operations
        table_name: Name of the table to search in
        columns: List of columns to search in (optional)
        limit: Maximum number of results to return
        offset: Number of results to skip (for pagination)
        highlight: Whether to highlight matching terms in results
        include_metadata: Whether to include search metadata in results

    Returns:
        Dictionary with operation results and search data

    Examples:
        Search across all tables:
        db_fts(operation='fts_search', connection_name='prod_db',
               search_query='machine learning', limit=50)

        Search specific table:
        db_fts(operation='fts_search', connection_name='prod_db',
               search_query='python', table_name='articles', columns=['title', 'content'])

        List FTS-enabled tables:
        db_fts(operation='fts_tables', connection_name='prod_db')

        Get search suggestions:
        db_fts(operation='fts_suggest', connection_name='prod_db',
               search_query='machine', limit=10)
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
    table_name: Optional[str],
    columns: Optional[List[str]],
    limit: int,
    offset: int,
    highlight: bool,
    include_metadata: bool,
) -> Dict[str, Any]:
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


async def _fts_tables(connection_name: str) -> Dict[str, Any]:
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


async def _fts_suggest(connection_name: str, search_query: str, limit: int) -> Dict[str, Any]:
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
