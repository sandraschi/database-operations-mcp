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

    Parameters:
        database_type: Type of database to operate on
            - 'sqlite': SQLite database (file-based)
            - 'postgresql': PostgreSQL database
            - 'mysql': MySQL/MariaDB database
            - 'redis': Redis key-value store
            - 'duckdb': DuckDB analytical database
            - 'mongodb': MongoDB document database
        operation: Database operation to perform
            - 'execute_query': Execute SELECT query
            - 'execute_non_query': Execute INSERT/UPDATE/DELETE
            - 'get_tables': List all tables/collections
            - 'get_table_structure': Describe table structure
            - 'get_keys': Get Redis keys matching pattern
            - 'get_value': Get Redis value by key
            - 'set_value': Set Redis key-value pair
            - 'health_check': Check connection health
        connection_string: Database connection string
            - For SQLite: file path
            - For MySQL/PostgreSQL: "host:port:user:password:database"
            - For Redis: "host:port:password:db"
            - For DuckDB: file path or ":memory:"
        query: SQL query string
            - Used for execute_query and execute_non_query operations
            - Parameterized queries supported
        table_name: Name of table/collection to operate on
            - Used for table-specific operations
        key: Redis key for key-value operations
            - Used with get_value, set_value operations
        value: Value to set for Redis operations
            - Used with set_value operation
        parameters: Query parameters for parameterized queries
            - Dictionary of parameter name-value pairs

    Returns:
        Dictionary containing operation result:
            {
                'success': bool,
                'database_type': str,
                'operation': str,
                'result': Any,
                'message': str
            }
    """
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
        if "connector" in locals() and connector:
            await connector.disconnect()
