"""
Extended database operations portmanteau tool.

Provides unified operations across multiple database types: SQLite, PostgreSQL,
MySQL, Redis, DuckDB, MongoDB, and more.
"""

import logging
from typing import Any

from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.database_manager import create_connector
from database_operations_mcp.operation_types import DbOperationsExtendedOperation
from database_operations_mcp.tool_responses import unknown_operation_response

logger = logging.getLogger(__name__)


@mcp.tool()
async def db_operations_extended(
    database_type: str,
    operation: DbOperationsExtendedOperation,
    connection_string: str | None = None,
    query: str | None = None,
    table_name: str | None = None,
    key: str | None = None,
    value: str | None = None,
    parameters: dict[str, Any] | None = None,
    config_overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Extended database operations across multiple database types.

    Provides a unified interface for database operations across SQLite,
    PostgreSQL, MySQL, Redis, DuckDB, MongoDB, and more. Routes operations
    to the appropriate database-specific connector based on database type.

    ## Return Format
    Returns success plus database_type/operation/result/message, or an error dict.

    ## Examples
    Run a SQLite query:
        result = await db_operations_extended(
            database_type="sqlite",
            operation="execute_query",
            connection_string="C:/data/app.db",
            query="SELECT * FROM users LIMIT 5",
        )
    """
    connector = None
    try:
        # Parse connection string into a config dict
        # Format depends on database type
        config = {}
        if connection_string:
            if database_type in ["mysql", "postgresql"]:
                parts = connection_string.split(":")
                if len(parts) >= 5:
                    config = {
                        "host": parts[0],
                        "port": int(parts[1]),
                        "user": parts[2],
                        "password": parts[3],
                        "database": parts[4],
                    }
            elif database_type == "redis":
                parts = connection_string.split(":")
                config = {
                    "host": parts[0],
                    "port": int(parts[1]) if len(parts) > 1 else 6379,
                    "password": parts[2] if len(parts) > 2 else None,
                    "db": int(parts[3]) if len(parts) > 3 else 0,
                }
            elif database_type in ["sqlite", "duckdb"]:
                config = {"path": connection_string}

        # Merge with config overrides
        if config_overrides:
            config.update(config_overrides)

        # Get or create connector
        connector = create_connector(database_type, config)
        if not connector:
            return {
                "success": False,
                "database_type": database_type,
                "operation": operation,
                "message": f"Failed to create connector for {database_type}",
            }

        # Perform operation
        result = None
        message = ""
        success = True

        if operation == "execute_query":
            if not query:
                return {"success": False, "message": "Query required for execute_query"}
            res = await connector.execute_query(query, parameters)
            success = res.success
            result = res.data
            message = res.message

        elif operation == "execute_non_query":
            if not query:
                return {
                    "success": False,
                    "message": "Query required for execute_non_query",
                }
            res = await connector.execute_query(query, parameters)
            success = res.success
            result = {"affected_rows": res.rowcount}
            message = res.message

        elif operation == "get_tables":
            result = await connector.get_tables()
            message = f"Found {len(result)} tables"

        elif operation == "get_table_structure":
            if not table_name:
                return {"success": False, "message": "table_name required"}
            result = await connector.get_table_schema(table_name)
            message = f"Schema for table {table_name}"

        elif operation == "health_check":
            result = await connector.health_check()
            success = result.get("status") == "connected"

        # Redis specific operations
        elif database_type == "redis":
            if operation == "get_keys":
                res = await connector.execute_query(f"KEYS {key or '*'}")
                success = res.success
                result = res.data
            elif operation == "get_value":
                if not key:
                    return {"success": False, "message": "key required for get_value"}
                res = await connector.execute_query(f"GET {key}")
                success = res.success
                result = res.data
            elif operation == "set_value":
                if not key or value is None:
                    return {
                        "success": False,
                        "message": "key and value required for set_value",
                    }
                res = await connector.execute_query(f"SET {key} {value}")
                success = res.success
                result = res.data
            else:
                return unknown_operation_response(
                    operation,
                    ["get_keys", "get_value", "set_value"],
                    extra_recovery=["For non-Redis types, use execute_query, get_tables, etc."],
                )

        else:
            return unknown_operation_response(
                operation,
                [
                    "execute_query",
                    "execute_non_query",
                    "get_tables",
                    "get_table_structure",
                    "health_check",
                ],
                extra_recovery=[f"Unsupported operation for database_type={database_type!r}."],
            )

        return {
            "success": success,
            "database_type": database_type,
            "operation": operation,
            "result": result,
            "message": message,
        }

    except Exception as e:
        logger.exception(f"Error in db_operations_extended: {e}")
        return {
            "success": False,
            "database_type": database_type,
            "operation": operation,
            "message": f"Unexpected error: {e!s}",
            "error_type": "fatal",
            "retryable": False,
            "recovery_options": [
                "Verify connection_string format for the selected database_type.",
                "Check network reachability and credentials, then retry once.",
            ],
        }
    finally:
        # Disconnect if we created a temporary connector
        if connector is not None:
            await connector.disconnect()
