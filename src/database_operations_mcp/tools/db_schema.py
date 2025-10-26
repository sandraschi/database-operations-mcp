# Database schema management portmanteau tool.
# Consolidates all database schema operations into a single interface.

import logging
from typing import Any, Dict, Optional

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.database_manager import db_manager
from database_operations_mcp.tools.help_tools import HelpSystem

logger = logging.getLogger(__name__)


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def db_schema(
    operation: str,
    connection_name: str,
    database_name: Optional[str] = None,
    table_name: Optional[str] = None,
    schema_name: Optional[str] = None,
    include_metadata: bool = True,
    include_indexes: bool = True,
    include_constraints: bool = True,
    compare_with: Optional[str] = None,
) -> Dict[str, Any]:
    """Database schema management portmanteau tool.

    This tool consolidates all database schema operations into a single interface,
    providing unified access to schema management functionality.

    Operations:
    - list_databases: List all databases available on the connection
    - list_tables: List all tables in a database or across all databases
    - describe_table: Get detailed information about a specific table
    - get_schema_diff: Compare schemas between two databases or connections

    Args:
        operation: The operation to perform (required)
        connection_name: Name of the database connection to use
        database_name: Name of the database to query (optional)
        table_name: Name of the table to describe
        schema_name: Name of the schema (for databases that support schemas)
        include_metadata: Include metadata information in results
        include_indexes: Include index information in table descriptions
        include_constraints: Include constraint information in table descriptions
        compare_with: Connection name to compare schema with (for diff operations)

    Returns:
        Dictionary with operation results and schema information

    Examples:
        List all databases:
        db_schema(operation='list_databases', connection_name='prod_db')

        List tables in specific database:
        db_schema(operation='list_tables', connection_name='prod_db', database_name='myapp')

        Describe specific table:
        db_schema(operation='describe_table', connection_name='prod_db',
                 table_name='users', include_indexes=True)

        Compare schemas:
        db_schema(operation='get_schema_diff', connection_name='prod_db',
                 compare_with='dev_db')
    """

    if operation == "list_databases":
        return await _list_databases(connection_name)
    elif operation == "list_tables":
        return await _list_tables(connection_name, database_name, schema_name)
    elif operation == "describe_table":
        return await _describe_table(
            connection_name, table_name, include_metadata, include_indexes, include_constraints
        )
    elif operation == "get_schema_diff":
        return await _get_schema_diff(connection_name, compare_with)
    else:
        return {
            "success": False,
            "error": f"Unknown operation: {operation}",
            "available_operations": [
                "list_databases",
                "list_tables",
                "describe_table",
                "get_schema_diff",
            ],
        }


async def _list_databases(connection_name: str) -> Dict[str, Any]:
    """List all databases available on the connection."""
    try:
        if not connection_name:
            raise ValueError("Connection name is required")

        connector = db_manager.get_connector(connection_name)
        if not connector:
            raise ValueError(f"Connection '{connection_name}' not found")

        databases = await connector.list_databases()

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
            "error": f"Failed to list databases: {str(e)}",
            "connection_name": connection_name,
            "databases": [],
            "count": 0,
        }


async def _list_tables(
    connection_name: str, database_name: Optional[str], schema_name: Optional[str]
) -> Dict[str, Any]:
    """List all tables in a database or across all databases."""
    try:
        if not connection_name:
            raise ValueError("Connection name is required")

        connector = db_manager.get_connector(connection_name)
        if not connector:
            raise ValueError(f"Connection '{connection_name}' not found")

        tables = await connector.list_tables(database_name, schema_name)

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
            "error": f"Failed to list tables: {str(e)}",
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
) -> Dict[str, Any]:
    """Get detailed information about a specific table."""
    try:
        if not connection_name:
            raise ValueError("Connection name is required")
        if not table_name:
            raise ValueError("Table name is required")

        connector = db_manager.get_connector(connection_name)
        if not connector:
            raise ValueError(f"Connection '{connection_name}' not found")

        table_info = await connector.describe_table(
            table_name, include_metadata, include_indexes, include_constraints
        )

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
            "error": f"Failed to describe table: {str(e)}",
            "connection_name": connection_name,
            "table_name": table_name,
            "table_info": {},
        }


async def _get_schema_diff(connection_name: str, compare_with: Optional[str]) -> Dict[str, Any]:
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
                "columns_added": sum(
                    len(t.get("columns_added", [])) for t in diff_result.get("tables_modified", [])
                ),
                "columns_removed": sum(
                    len(t.get("columns_removed", []))
                    for t in diff_result.get("tables_modified", [])
                ),
            },
        }

    except Exception as e:
        logger.error(f"Error comparing schemas: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to compare schemas: {str(e)}",
            "connection_name": connection_name,
            "compare_with": compare_with,
            "schema_diff": {},
        }


async def _compare_schemas(schema1: Dict[str, Any], schema2: Dict[str, Any]) -> Dict[str, Any]:
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

                columns_added = [
                    col for col_name, col in columns2.items() if col_name not in columns1
                ]
                columns_removed = [
                    col for col_name, col in columns1.items() if col_name not in columns2
                ]
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
