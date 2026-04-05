# Database full-text search portmanteau tool.
# Consolidates all full-text search operations into a single interface.

import logging
from typing import Any

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.database_manager import db_manager
from database_operations_mcp.operation_types import DbFtsOperation
from database_operations_mcp.tool_responses import (
    connection_not_found,
    mcp_error,
    unknown_operation_response,
)
from database_operations_mcp.tools.help_tools import HelpSystem

logger = logging.getLogger(__name__)

_FTS_MAX_LIMIT = 10_000
_FTS_MAX_OFFSET = 1_000_000


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def db_fts(
    operation: DbFtsOperation,
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

    Requires a registered `db_connection` with FTS-capable tables. See `help_system`
    for extended documentation.

    Parameters:
        operation: Exactly one of fts_search | fts_tables | fts_suggest.
        connection_name: Registered connection name (same identifier as `db_connection`).
        search_query: Required for fts_search and fts_suggest.
        table_name / columns: Optional FTS narrowing for fts_search.
        limit: Max rows or suggestions to return (clamped server-side to 1..10000).
        offset: Row offset for paginated fts_search (clamped; use with total_results/has_more).
        highlight: When True, include highlighted snippets in highlighted_results when the
            backend supports it. When False, highlighted_results is empty; full rows may
            still appear in results.
        include_metadata: When True, include connector metadata in the response when available.

    Returns (success=True):
        Common: success, message, connection_name, operation.
        fts_search: results (list), total_results (int), highlighted_results (list, may be empty),
            metadata (dict), pagination: { limit, offset, has_more, total_results }.
        fts_tables: fts_tables (list), count (int).
        fts_suggest: suggestions (list), count (int).

    Returns (success=False):
        success, message, error, error_type (invalid_input | user_fixable | fatal | retryable),
        recovery_options (when applicable), plus operation-specific empty fields.

    Pagination:
        total_results is the full match count when the connector provides it.
        has_more is True when more rows exist beyond offset+limit. Requests above the cap
        are clamped; check pagination.limit for the applied value.
    """

    limit = max(1, min(limit, _FTS_MAX_LIMIT))
    offset = max(0, min(offset, _FTS_MAX_OFFSET))

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
    if operation == "fts_tables":
        return await _fts_tables(connection_name)
    if operation == "fts_suggest":
        return await _fts_suggest(connection_name, search_query, limit)
    return unknown_operation_response(operation, ["fts_search", "fts_tables", "fts_suggest"])


async def _fts_search(
    connection_name: str,
    search_query: str | None,
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
            return mcp_error(
                message="connection_name is required",
                error="connection_name is required",
                error_type="invalid_input",
                recovery_options=["Pass a non-empty connection_name registered via db_connection."],
            )
        if not search_query:
            return mcp_error(
                message="search_query is required for fts_search",
                error="search_query is required for fts_search",
                error_type="invalid_input",
                recovery_options=["Provide search_query, or use fts_tables / fts_suggest as needed."],
            )

        connector = db_manager.get_connector(connection_name)
        if not connector:
            return connection_not_found(connection_name)

        search_params = {
            "query": search_query,
            "table_name": table_name,
            "columns": columns,
            "limit": limit,
            "offset": offset,
            "highlight": highlight,
            "include_metadata": include_metadata,
        }

        search_result = await connector.fts_search(search_params)
        total = int(search_result.get("total_results", 0) or 0)

        return {
            "success": True,
            "message": f"Full-text search completed for '{search_query}'",
            "connection_name": connection_name,
            "search_query": search_query,
            "table_name": table_name,
            "results": search_result.get("results", []),
            "total_results": total,
            "highlighted_results": search_result.get("highlighted_results", [])
            if highlight
            else [],
            "metadata": search_result.get("metadata", {}) if include_metadata else {},
            "pagination": {
                "limit": limit,
                "offset": offset,
                "has_more": total > offset + limit,
                "total_results": total,
            },
        }

    except Exception as e:
        logger.error(f"Error performing FTS search: {e}", exc_info=True)
        return mcp_error(
            message=f"Failed to perform FTS search: {e!s}",
            error=str(e),
            error_type="retryable",
            retryable=True,
            recovery_options=[
                "Retry after closing other connections holding locks on the DB file.",
                "Verify FTS tables exist (db_fts operation='fts_tables').",
                "Re-register the connection with db_connection if the path moved.",
            ],
            connection_name=connection_name,
            search_query=search_query,
            results=[],
            total_results=0,
        )


async def _fts_tables(connection_name: str) -> dict[str, Any]:
    """List all tables that have full-text search indexes."""
    try:
        if not connection_name:
            return mcp_error(
                message="connection_name is required",
                error="connection_name is required",
                error_type="invalid_input",
                recovery_options=["Pass connection_name for a registered connection."],
            )

        connector = db_manager.get_connector(connection_name)
        if not connector:
            return connection_not_found(connection_name)

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
        return mcp_error(
            message=f"Failed to list FTS tables: {e!s}",
            error=str(e),
            error_type="fatal",
            recovery_options=["Ensure the database file is readable and the connector supports FTS."],
            connection_name=connection_name,
            fts_tables=[],
            count=0,
        )


async def _fts_suggest(connection_name: str, search_query: str | None, limit: int) -> dict[str, Any]:
    """Get search suggestions based on partial input."""
    try:
        if not connection_name:
            return mcp_error(
                message="connection_name is required",
                error="connection_name is required",
                error_type="invalid_input",
                recovery_options=["Pass connection_name for a registered connection."],
            )
        if not search_query:
            return mcp_error(
                message="search_query is required for fts_suggest",
                error="search_query is required for fts_suggest",
                error_type="invalid_input",
                recovery_options=["Provide a prefix or term in search_query."],
            )

        connector = db_manager.get_connector(connection_name)
        if not connector:
            return connection_not_found(connection_name)

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
        return mcp_error(
            message=f"Failed to generate FTS suggestions: {e!s}",
            error=str(e),
            error_type="retryable",
            retryable=True,
            recovery_options=["Retry once; if persistent, check connector FTS support."],
            connection_name=connection_name,
            search_query=search_query,
            suggestions=[],
            count=0,
        )
