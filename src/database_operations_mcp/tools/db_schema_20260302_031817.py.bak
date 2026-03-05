# Database schema management portmanteau tool.
# Consolidates all database schema operations into a single interface.

import logging
from typing import Any

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
    database_name: str | None = None,
    table_name: str | None = None,
    schema_name: str | None = None,
    include_metadata: bool = True,
    include_indexes: bool = True,
    include_constraints: bool = True,
    compare_with: str | None = None,
) -> dict[str, Any]:
    """Database schema management portmanteau tool.

    Comprehensive database schema inspection and comparison consolidating ALL schema
    operations into a single interface. Supports database discovery, table listing,
    detailed schema inspection, and schema comparison across SQL, NoSQL, and Vector databases.

    Prerequisites:
        - Valid database connection registered via db_connection
        - Read permissions on database/system tables
        - For comparison: Two valid connections to compare

    Operations:
        - list_databases: List all databases available on the connection
        - list_tables: List all tables in a database or across all databases
        - describe_table: Get detailed information about a specific table
        - get_schema_diff: Compare schemas between two databases or connections

    Parameters:
        operation (str, REQUIRED): The operation to perform
            Valid values: 'list_databases', 'list_tables', 'describe_table', 'get_schema_diff'
            Example: 'list_tables', 'describe_table', 'get_schema_diff'

        connection_name (str, REQUIRED): Name of the database connection to use
            Format: Registered connection name (from db_connection)
            Validation: Must be previously registered
            Required for: All operations
            Example: 'prod_db', 'analytics_warehouse'

        database_name (str, OPTIONAL): Name of the database to query
            Format: Valid database name in connection
            Required for: list_tables, describe_table (for multi-database systems)
            Example: 'myapp', 'analytics', 'production'

        table_name (str, OPTIONAL): Name of the table to describe
            Format: Valid table name in database
            Required for: describe_table operation
            Validation: Table must exist in database
            Example: 'users', 'orders', 'products'

        schema_name (str, OPTIONAL): Name of the schema (for databases supporting schemas)
            Format: Valid schema name (PostgreSQL, MySQL)
            Default: 'public' (PostgreSQL), 'default' (others)
            Example: 'public', 'analytics', 'audit'

        include_metadata (bool, OPTIONAL): Include metadata information in results
            Default: True
            Behavior: Adds table size, row counts, creation dates if available
            Used for: describe_table operation

        include_indexes (bool, OPTIONAL): Include index information
            Default: True
            Behavior: Lists all indexes, their columns, and types
            Used for: describe_table operation

        include_constraints (bool, OPTIONAL): Include constraint information
            Default: True
            Behavior: Lists primary keys, foreign keys, unique constraints, checks
            Used for: describe_table operation

        compare_with (str, OPTIONAL): Connection name to compare schema with
            Format: Registered connection name
            Required for: get_schema_diff operation
            Validation: Both connections must exist and be compatible database types
            Example: 'dev_db', 'staging_db'

    Returns:
        Dictionary containing operation-specific results:
            - success: Boolean indicating operation success
            - operation: Echo of operation performed
            - For list_databases: databases (list), total_count
            - For list_tables: tables (list with metadata), database_name, total_count
            - For describe_table: table_info (columns, indexes, constraints, metadata)
            - For get_schema_diff: differences (list), summary (added/removed/modified counts)
            - error: Error message if success is False
            - available_operations: List of valid operations (on invalid operation)

    Usage:
        This tool is essential for database exploration and schema management. Use it to
        discover database structure, understand table schemas, and compare database versions.

        Common scenarios:
        - Discovery: Find all databases and tables in a connection
        - Documentation: Generate schema documentation for databases
        - Migration: Compare schemas between environments before/after migration
        - Analysis: Understand database structure for query optimization
        - Validation: Verify schema changes match expected structure

        Best practices:
        - Use list_databases first to see available databases
        - Use list_tables to discover all tables before querying
        - Include indexes and constraints for complete schema understanding
        - Compare schemas before/after migrations to verify changes

    Examples:
        List all databases:
            result = await db_schema(
                operation='list_databases',
                connection_name='production_db'
            )
            # Returns: {
            #     'success': True,
            #     'databases': ['myapp', 'analytics', 'logs'],
            #     'total_count': 3
            # }

        List tables in specific database:
            result = await db_schema(
                operation='list_tables',
                connection_name='production_db',
                database_name='myapp'
            )
            # Returns: {
            #     'success': True,
            #     'tables': [
            #         {'name': 'users', 'type': 'table', 'row_count': 1250},
            #         {'name': 'orders', 'type': 'table', 'row_count': 5420}
            #     ],
            #     'database_name': 'myapp',
            #     'total_count': 2
            # }

        Describe table with full details:
            result = await db_schema(
                operation='describe_table',
                connection_name='production_db',
                table_name='users',
                include_indexes=True,
                include_constraints=True,
                include_metadata=True
            )
            # Returns: {
            #     'success': True,
            #     'table_info': {
            #         'columns': [
            #             {'name': 'id', 'type': 'INTEGER', 'nullable': False, 'primary_key': True},
            #             {
            #                 'name': 'email',
            #                 'type': 'VARCHAR(255)',
            #                 'nullable': False,
            #                 'unique': True
            #             }
            #         ],
            #         'indexes': [{'name': 'idx_email', 'columns': ['email'], 'unique': True}],
            #         'constraints': [...],
            #         'metadata': {'row_count': 1250, 'size_bytes': 2048000}
            #     }
            # }

        Compare schemas between environments:
            result = await db_schema(
                operation='get_schema_diff',
                connection_name='production_db',
                compare_with='dev_db'
            )
            # Returns: {
            #     'success': True,
            #     'differences': [
            #         {'type': 'added_table', 'name': 'new_feature_table'},
            #         {
            #             'type': 'modified_column',
            #             'table': 'users',
            #             'column': 'email',
            #             'change': 'length increased'
            #         }
            #     ],
            #     'summary': {'added': 1, 'removed': 0, 'modified': 1}
            # }

        Error handling - connection not found:
            result = await db_schema(
                operation='list_databases',
                connection_name='nonexistent'
            )
            # Returns: {
            #     'success': False,
            #     'error': 'Connection not found: nonexistent'
            # }

    Errors:
        Common errors and solutions:
        - 'Connection not found: {connection_name}':
            Cause: Connection name doesn't exist or not registered
            Fix: Use db_connection(operation='list') to see available connections
            Workaround: Register connection first with db_connection(operation='register')

        - 'Table not found: {table_name}':
            Cause: Table doesn't exist in specified database
            Fix: Use list_tables operation first to see available tables
            Workaround: Check database_name and schema_name parameters

        - 'Database not found: {database_name}':
            Cause: Database doesn't exist on connection
            Fix: Use list_databases operation to see available databases
            Workaround: Omit database_name to search across all databases

        - 'Schema comparison failed: {error}':
            Cause: Incompatible database types or connection issues
            Fix: Ensure both connections are same database type, verify connections are valid
            Workaround: Compare schemas manually using describe_table on both connections

    See Also:
        - db_connection: Register and manage database connections
        - db_operations: Execute queries on discovered tables
        - db_management: Database administration operations
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


async def _list_databases(connection_name: str) -> dict[str, Any]:
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
    connection_name: str, database_name: str | None, schema_name: str | None
) -> dict[str, Any]:
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
) -> dict[str, Any]:
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
