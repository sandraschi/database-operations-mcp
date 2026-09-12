"""
Data read/write operations for databases.

DEPRECATED: This module is deprecated. Use db_operations portmanteau tool instead.

All operations have been consolidated into db_operations():
- execute_transaction() → db_operations(operation='execute_transaction')
- execute_write() → db_operations(operation='execute_write')
- batch_insert() → db_operations(operation='batch_insert')

This module is kept for backwards compatibility but tools are no longer registered.
"""

import logging
from typing import Any

# NOTE: @mcp.tool decorators removed - functionality moved to db_operations portmanteau
# Import kept for backwards compatibility in case code references these functions
from database_operations_mcp.database_manager import QueryError, db_manager

logger = logging.getLogger(__name__)


def _resolve_connector(connection_name: str) -> tuple[Any, dict[str, Any] | None]:
    """Return (connector, error_dict) for a connection name."""
    connector = db_manager.get_connector(connection_name)
    if not connector:
        return None, {
            "status": "error",
            "message": f"No such connection: {connection_name}",
            "error_type": "ConnectionError",
        }
    return connector, None


# DEPRECATED: Use db_operations(operation='execute_transaction') instead
async def execute_transaction(queries: list[dict[str, Any]], connection_name: str = "default") -> dict[str, Any]:
    """Execute multiple queries in a transaction.

    ## Return Format
    Returns status plus per-query results, or an error dict.

    ## Examples
    Run two writes atomically:
        result = await execute_transaction(
            [{"query": "INSERT INTO users (name) VALUES (?)", "parameters": ["Ann"]}],
            "sqlite",
        )
    """
    connector, error = _resolve_connector(connection_name)
    if error:
        return error

    try:
        result = await connector.execute_transaction(queries)
        return {
            "status": "success" if result.success else "error",
            "results": result.data,
            "rowcount": result.rowcount,
            "message": result.message,
        }
    except QueryError as e:
        return {"status": "error", "message": "Transaction failed", "error": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {e!s}"}


# DEPRECATED: Use db_operations(operation='execute_write') instead
async def execute_write(
    query: str,
    parameters: dict[str, Any] | None = None,
    connection_name: str = "default",
) -> dict[str, Any]:
    """Execute a write operation (INSERT, UPDATE, DELETE, etc.) on the database.

    ## Return Format
    Returns status plus rowcount/execution_time, or an error dict.

    ## Examples
    Insert a row:
        result = await execute_write("INSERT INTO users (name) VALUES (?)", ["Ann"], "sqlite")
    """
    connector, error = _resolve_connector(connection_name)
    if error:
        return error

    try:
        result = await connector.execute_write(query, parameters or {})
        return {
            "status": "success" if result.success else "error",
            "rowcount": result.rowcount,
            "execution_time": result.execution_time,
            "message": result.message,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Query execution failed: {e!s}",
            "error_type": type(e).__name__,
        }


# DEPRECATED: Use db_operations(operation='batch_insert') instead
async def batch_insert(
    table: str, data: list[dict[str, Any]], connection_name: str = "default", batch_size: int = 1000
) -> dict[str, Any]:
    """Insert multiple rows into a table in batches.

    ## Return Format
    Returns status plus processed count, or an error dict.

    ## Examples
    Insert rows:
        result = await batch_insert("users", [{"name": "Ann"}], "sqlite")
    """
    if not data:
        return {"status": "error", "message": "No data provided"}

    connector, error = _resolve_connector(connection_name)
    if error:
        return error

    chunk = max(int(batch_size or 1000), 1)
    processed = 0

    try:
        for start in range(0, len(data), chunk):
            batch_result = await connector.batch_insert(table, data[start : start + chunk])
            processed += batch_result.rowcount

        return {
            "status": "success",
            "processed": processed,
            "message": f"Successfully inserted {processed} rows into {table}",
        }

    except Exception as e:
        logger.exception("Error in batch insert")
        return {
            "status": "error",
            "message": f"Batch insert failed: {e!s}",
            "processed": processed,
            "error_type": type(e).__name__,
        }
