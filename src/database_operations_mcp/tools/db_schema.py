# Database schema management portmanteau tool.
# Consolidates all database schema operations into a single interface.

import logging
from typing import Any

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.database_manager import db_manager
from database_operations_mcp.tool_responses import unknown_operation_response
from database_operations_mcp.tools.help_tools import HelpSystem

logger = logging.getLogger(__name__)


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def db_schema(
    operation: str,
    connection_name: str,
    database_name: str | None = None,
    table_name: str | None = None,
    schema_name: str | None = None,
    include_metadata: bool = True,
    include_indexes: bool = True,
    include_constraints: bool = True,
    compare_with: str | None = None,
) -> dict[str, Any]:
    """Database schema management portmanteau tool.

    Operations: list_databases, list_tables, describe_table, get_schema_diff.
    Requires a registered db_connection. For full docs call help_system.
    """

    if operation == "list_databases":
        result = await _list_databases(connection_name)
    elif operation == "list_tables":
        result = await _list_tables(connection_name, database_name, schema_name)
    elif operation == "describe_table":
        result = await _describe_table(
            connection_name, table_name, include_metadata, include_indexes, include_constraints
        )
    elif operation == "get_schema_diff":
        result = await _get_schema_diff(connection_name, compare_with)
    else:
        return unknown_operation_response(
            operation,
            [
                "list_databases",
                "list_tables",
                "describe_table",
                "get_schema_diff",
            ],
        )

    # Standardize result with a conversational summary
    summary = result.get("message", "")
    if not summary:
        if result.get("success"):
            if operation == "list_databases":
                count = result.get("count", 0)
                summary = f"Found {count} databases on '{connection_name}'."
            elif operation == "list_tables":
                count = result.get("count", 0)
                summary = f"Found {count} tables in '{connection_name}' (DB: {database_name or 'Default'})."
            elif operation == "describe_table":
                summary = f"Retrieved detailed schema/metadata for table '{table_name}' in '{connection_name}'."
            else:
                summary = f"Successfully completed '{operation}' operation."
        else:
            summary = f"Error: {result.get('error', 'Unknown database schema error')}"

    return {"content": summary, "data": result}


async def _list_databases(connection_name: str) -> dict[str, Any]:
    """List all databases available on the connection."""
    import inspect
    import os

    try:
        if not connection_name:
            raise ValueError("Connection name is required")

        connector = db_manager.get_connector(connection_name)
        if not connector:
            raise ValueError(f"Connection '{connection_name}' not found")

        if hasattr(connector, "list_databases"):
            method = connector.list_databases
            if inspect.iscoroutinefunction(method):
                databases = await method()
            else:
                databases = method()
        else:
            # Fallback for connectors that do not define list_databases
            db_name = (
                connector.connection_config.get("database")
                or connector.connection_config.get("database_path")
                or "main"
            )
            if isinstance(db_name, str):
                db_name = os.path.basename(db_name.strip("\"'"))
            databases = [
                {
                    "database_name": db_name,
                    "type": "main",
                    "allow_connections": True,
                }
            ]

        return {
            "success": True,
            "message": "Databases listed successfully",
            "connection_name": connection_name,
            "databases": databases,
            "count": len(databases),
        }

    except Exception as e:
        logger.error(f"Error listing databases: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to list databases: {e!s}",
            "connection_name": connection_name,
            "databases": [],
            "count": 0,
        }


async def _list_tables(connection_name: str, database_name: str | None, schema_name: str | None) -> dict[str, Any]:
    """List all tables in a database or across all databases."""
    import inspect

    try:
        if not connection_name:
            raise ValueError("Connection name is required")

        connector = db_manager.get_connector(connection_name)
        if not connector:
            raise ValueError(f"Connection '{connection_name}' not found")

        if hasattr(connector, "list_tables"):
            method = connector.list_tables
            sig = inspect.signature(method)
            params = sig.parameters

            kwargs = {}
            if "database" in params:
                kwargs["database"] = database_name
            elif "database_name" in params:
                kwargs["database_name"] = database_name

            if "schema" in params:
                kwargs["schema"] = schema_name
            elif "schema_name" in params:
                kwargs["schema_name"] = schema_name

            if inspect.iscoroutinefunction(method):
                tables = await method(**kwargs)
            else:
                tables = method(**kwargs)
        else:
            # Fallback to get_tables
            method = getattr(connector, "get_tables", None)
            if method:
                if inspect.iscoroutinefunction(method):
                    raw_tables = await method()
                else:
                    raw_tables = method()
                tables = [{"table_name": t} for t in raw_tables]
            else:
                tables = []

        return {
            "success": True,
            "message": "Tables listed successfully",
            "connection_name": connection_name,
            "database_name": database_name,
            "schema_name": schema_name,
            "tables": tables,
            "count": len(tables),
        }

    except Exception as e:
        logger.error(f"Error listing tables: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to list tables: {e!s}",
            "connection_name": connection_name,
            "database_name": database_name,
            "tables": [],
            "count": 0,
        }


async def _describe_table(
    connection_name: str,
    table_name: str,
    include_metadata: bool,
    include_indexes: bool,
    include_constraints: bool,
) -> dict[str, Any]:
    """Get detailed information about a specific table."""
    import inspect

    try:
        if not connection_name:
            raise ValueError("Connection name is required")
        if not table_name:
            raise ValueError("Table name is required")

        connector = db_manager.get_connector(connection_name)
        if not connector:
            raise ValueError(f"Connection '{connection_name}' not found")

        if hasattr(connector, "describe_table"):
            method = connector.describe_table
            if inspect.iscoroutinefunction(method):
                table_info = await method(table_name, include_metadata, include_indexes, include_constraints)
            else:
                table_info = method(table_name, include_metadata, include_indexes, include_constraints)
        else:
            # Fallback to get_table_schema
            method = getattr(connector, "get_table_schema", None)
            if not method:
                raise AttributeError("Connector has no describe_table or get_table_schema method")
            if inspect.iscoroutinefunction(method):
                table_info = await method(table_name)
            else:
                table_info = method(table_name)

        return {
            "success": True,
            "message": f"Table '{table_name}' described successfully",
            "connection_name": connection_name,
            "table_name": table_name,
            "table_info": table_info,
            "columns": table_info.get("columns", []),
            "indexes": table_info.get("indexes", []) if include_indexes else [],
            "constraints": table_info.get("constraints", []) if include_constraints else [],
            "metadata": table_info.get("metadata", {}) if include_metadata else {},
        }

    except Exception as e:
        logger.error(f"Error describing table: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to describe table: {e!s}",
            "connection_name": connection_name,
            "table_name": table_name,
            "table_info": {},
        }


async def _get_schema_diff(connection_name: str, compare_with: str | None) -> dict[str, Any]:
    """Compare schemas between two databases or connections."""
    try:
        if not connection_name:
            raise ValueError("Connection name is required")
        if not compare_with:
            raise ValueError("Compare with connection name is required")

        connector1 = db_manager.get_connector(connection_name)
        if not connector1:
            raise ValueError(f"Connection '{connection_name}' not found")

        connector2 = db_manager.get_connector(compare_with)
        if not connector2:
            raise ValueError(f"Connection '{compare_with}' not found")

        # Get schemas from both connections
        schema1 = await connector1.get_schema()
        schema2 = await connector2.get_schema()

        # Compare schemas
        diff_result = await _compare_schemas(schema1, schema2)

        return {
            "success": True,
            "message": "Schema comparison completed",
            "connection_name": connection_name,
            "compare_with": compare_with,
            "schema_diff": diff_result,
            "summary": {
                "tables_added": len(diff_result.get("tables_added", [])),
                "tables_removed": len(diff_result.get("tables_removed", [])),
                "tables_modified": len(diff_result.get("tables_modified", [])),
                "columns_added": sum(len(t.get("columns_added", [])) for t in diff_result.get("tables_modified", [])),
                "columns_removed": sum(
                    len(t.get("columns_removed", [])) for t in diff_result.get("tables_modified", [])
                ),
            },
        }

    except Exception as e:
        logger.error(f"Error comparing schemas: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to compare schemas: {e!s}",
            "connection_name": connection_name,
            "compare_with": compare_with,
            "schema_diff": {},
        }


async def _compare_schemas(schema1: dict[str, Any], schema2: dict[str, Any]) -> dict[str, Any]:
    """Compare two schemas and return differences."""
    tables1 = {table["name"]: table for table in schema1.get("tables", [])}
    tables2 = {table["name"]: table for table in schema2.get("tables", [])}

    tables_added = []
    tables_removed = []
    tables_modified = []

    # Find added tables
    for table_name in tables2:
        if table_name not in tables1:
            tables_added.append(tables2[table_name])

    # Find removed tables
    for table_name in tables1:
        if table_name not in tables2:
            tables_removed.append(tables1[table_name])

    # Find modified tables
    for table_name in tables1:
        if table_name in tables2:
            table1 = tables1[table_name]
            table2 = tables2[table_name]

            if table1 != table2:
                # Compare columns
                columns1 = {col["name"]: col for col in table1.get("columns", [])}
                columns2 = {col["name"]: col for col in table2.get("columns", [])}

                columns_added = [col for col_name, col in columns2.items() if col_name not in columns1]
                columns_removed = [col for col_name, col in columns1.items() if col_name not in columns2]
                columns_modified = []

                for col_name in columns1:
                    if col_name in columns2 and columns1[col_name] != columns2[col_name]:
                        columns_modified.append(
                            {"name": col_name, "old": columns1[col_name], "new": columns2[col_name]}
                        )

                if columns_added or columns_removed or columns_modified:
                    tables_modified.append(
                        {
                            "name": table_name,
                            "columns_added": columns_added,
                            "columns_removed": columns_removed,
                            "columns_modified": columns_modified,
                        }
                    )

    return {
        "tables_added": tables_added,
        "tables_removed": tables_removed,
        "tables_modified": tables_modified,
    }
