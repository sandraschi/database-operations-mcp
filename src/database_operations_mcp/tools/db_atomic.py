"""Atomic database tools replacing operation-dispatch portmanteau tools."""

from __future__ import annotations

from typing import Any

from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.tools import db_connection as _db_connection
from database_operations_mcp.tools import db_operations as _db_operations
from database_operations_mcp.tools.help_tools import HelpSystem


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def list_supported_databases() -> dict[str, Any]:
    """List supported database engines and categories.

    Returns:
        dict: {"success": bool, "databases_by_category": dict, "total_supported": int, "categories": list[str]}
    """
    return await _db_connection._list_supported_databases()


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def register_database_connection(
    connection_name: str,
    database_type: str,
    connection_config: dict[str, Any],
    test_connection: bool = True,
) -> dict[str, Any]:
    """Register one database connection.

    Returns:
        dict: {"success": bool, "connection_name": str, "database_type": str, "error": str|None}
    """
    return await _db_connection._register_database_connection(
        connection_name=connection_name,
        database_type=database_type,
        connection_config=connection_config,
        test_connection=test_connection,
    )


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def list_database_connections() -> dict[str, Any]:
    """List currently registered connection names and metadata.

    Returns:
        dict: {"success": bool, "connections": dict, "total_connections": int}
    """
    return await _db_connection._list_database_connections()


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def test_database_connection(connection_name: str) -> dict[str, Any]:
    """Test one registered database connection.

    Returns:
        dict: {"success": bool, "connection_name": str, "test_result": {"success": bool, "latency": float, "error": str|None}}
    """
    return await _db_connection._test_database_connection(connection_name=connection_name)


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def test_all_database_connections(
    timeout: float | None = None,
    parallel: bool = False,
) -> dict[str, Any]:
    """Test all registered database connections.

    Returns:
        dict: {"success": bool, "test_results": dict, "summary": {"total_connections": int, "successful": int, "failed": int}}
    """
    return await _db_connection._test_all_database_connections(timeout=timeout, parallel=parallel)


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def close_database_connection(connection_name: str) -> dict[str, Any]:
    """Close and unregister one database connection.

    Returns:
        dict: {"success": bool, "message": str, "connection_name": str|None}
    """
    return await _db_connection._close_connection(connection_name=connection_name)


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def get_database_connection_info(connection_name: str) -> dict[str, Any]:
    """Get detailed information for one registered connection.

    Returns:
        dict: {"success": bool, "connection_name": str, "db_type": str, "is_connected": bool, "connection_info": dict}
    """
    return await _db_connection._get_connection_info(connection_name=connection_name)


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def restore_saved_database_connections(auto_reconnect: bool = False) -> dict[str, Any]:
    """Restore saved connections from persistent storage.

    Returns:
        dict: {"success": bool, "saved_connections": dict, "reconnected": list[str], "message": str}
    """
    return await _db_connection._restore_saved_connections(auto_reconnect=auto_reconnect)


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def set_active_database_connection(connection_name: str) -> dict[str, Any]:
    """Set the active/default connection in persistent storage.

    Returns:
        dict: {"success": bool, "message": str}
    """
    return await _db_connection._set_active_connection(connection_name=connection_name)


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def get_active_database_connection() -> dict[str, Any]:
    """Get the active/default connection from persistent storage.

    Returns:
        dict: {"success": bool, "active_connection": str|None}
    """
    return await _db_connection._get_active_connection()


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def get_database_user_preferences() -> dict[str, Any]:
    """Get persisted user preferences for DB operations.

    Returns:
        dict: {"success": bool, "preferences": dict}
    """
    return await _db_connection._get_user_preferences()


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def set_database_user_preferences(preferences: dict[str, Any]) -> dict[str, Any]:
    """Set persisted user preferences for DB operations.

    Returns:
        dict: {"success": bool, "message": str}
    """
    return await _db_connection._set_user_preferences(preferences=preferences)


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def execute_database_transaction(
    connection_name: str,
    query: str,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute a transaction query against one connection.

    Returns:
        dict: {"success": bool, "connection_name": str, "rows_affected": int, "transaction_id": str|None, "error": str|None}
    """
    return await _db_operations._execute_transaction(
        connection_name=connection_name, query=query, params=params
    )


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def execute_database_write(
    connection_name: str,
    query: str,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute INSERT/UPDATE/DELETE against one connection.

    Returns:
        dict: {"success": bool, "connection_name": str, "rows_affected": int, "last_insert_id": Any, "error": str|None}
    """
    return await _db_operations._execute_write(
        connection_name=connection_name, query=query, params=params
    )


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def batch_insert_records(
    connection_name: str,
    table_name: str,
    data: list[dict[str, Any]],
    batch_size: int = 1000,
) -> dict[str, Any]:
    """Insert multiple records into one table.

    Returns:
        dict: {"success": bool, "connection_name": str, "table_name": str, "records_inserted": int, "batches_processed": int, "error": str|None}
    """
    return await _db_operations._batch_insert(
        connection_name=connection_name,
        table_name=table_name,
        data=data,
        batch_size=batch_size,
    )


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def execute_database_query(
    connection_name: str,
    query: str,
    params: dict[str, Any] | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    """Execute read query and return rows/columns/row_count.

    Returns:
        dict: {"success": bool, "connection_name": str, "query": str, "applied_limit": int, "result": {"rows": list, "columns": list, "row_count": int}, "error": str|None}
    """
    return await _db_operations._execute_query(
        connection_name=connection_name, query=query, params=params, limit=limit
    )


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def quick_table_data_sample(
    connection_name: str,
    table_name: str,
    limit: int = 100,
) -> dict[str, Any]:
    """Get a quick sample from one table.

    Returns:
        dict: {"success": bool, "connection_name": str, "table_name": str, "sample_size": int, "generated_query": str, "result": {"rows": list, "columns": list, "row_count": int}}
    """
    return await _db_operations._quick_data_sample(
        connection_name=connection_name, table_name=table_name, limit=limit
    )


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def export_database_query_results(
    connection_name: str,
    query: str,
    params: dict[str, Any] | None = None,
    output_format: str = "json",
    output_path: str | None = None,
) -> dict[str, Any]:
    """Export query results to JSON/CSV/Excel-like structures.

    Returns:
        dict: {"success": bool, "connection_name": str, "export_format": str, "row_count": int, "file_path": str|None, "exported_data": Any|None, "error": str|None}
    """
    return await _db_operations._export_query_results(
        connection_name=connection_name,
        query=query,
        params=params,
        output_format=output_format,
        output_path=output_path,
    )
