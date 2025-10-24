"""
Database schema inspection and metadata tools.

Handles table/collection discovery, schema analysis, and metadata operations.
"""

import logging
from typing import Any, Dict, Optional

# Import the global MCP instance
from database_operations_mcp.config.mcp_config import mcp

from ..database_manager import db_manager
from .help_tools import HelpSystem

logger = logging.getLogger(__name__)

# Register tools using the @mcp.tool decorator
# The mcp instance is imported from the centralized config


@mcp.tool()
@HelpSystem.register_tool
async def list_databases(connection_name: str) -> Dict[str, Any]:
    """List all databases/schemas on database server.

    Retrieves complete list of databases or schemas available on the specified
    database connection. Useful for discovery and exploration of database servers.

    Parameters:
        connection_name: Name of registered database connection
            - Must be previously registered
            - Case-sensitive string
            - Only alphanumeric and underscores

    Returns:
        Dictionary containing:
            - success: Boolean indicating operation success
            - connection_name: Echo of connection used
            - databases: List of database/schema names
            - total_databases: Count of databases found
            - error: Error message if success is False

    Usage:
        Use this to discover what databases exist on a server. Essential for
        initial exploration and before performing schema or data operations.

        Common scenarios:
        - Explore new database servers
        - Verify database existence before operations
        - Audit available databases
        - Plan data migration routes

        Best practices:
        - Run this before other schema operations
        - Verify database name spelling
        - Check permissions on listed databases

    Examples:
        List PostgreSQL databases:
            result = await list_databases("postgres_server")
            # Returns: {
            #     'success': True,
            #     'databases': ['production', 'staging', 'development', 'postgres'],
            #     'total_databases': 4
            # }

        Check specific database exists:
            result = await list_databases("prod_server")
            if 'my_database' in result.get('databases', []):
                print("Database exists!")
            # Checks if database is available

        Error handling:
            result = await list_databases("invalid_connection")
            if not result['success']:
                print(f"Failed: {result['error']}")
            # Logs: Failed: Connection not found: invalid_connection

    Notes:
        - Some databases may not be accessible due to permissions
        - System databases (like 'postgres') are included
        - MongoDB shows database list from connection
        - SQLite only shows attached databases

    See Also:
        - list_tables: List tables within a database
        - describe_table: Get table structure
    """
    try:
        connector = db_manager.get_connector(connection_name)
        if not connector:
            return {"success": False, "error": f"Connection not found: {connection_name}"}

        # Get list of databases (implementation depends on database type)
        databases = await connector.list_databases()

        return {
            "success": True,
            "connection_name": connection_name,
            "databases": databases,
            "total_databases": len(databases),
        }

    except Exception as e:
        logger.error(f"Error listing databases for {connection_name}: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
@HelpSystem.register_tool
async def list_tables(connection_name: str, database_name: Optional[str] = None) -> Dict[str, Any]:
    """List all tables/collections in database or schema.

    Retrieves complete list of tables (SQL) or collections (NoSQL) from specified
    database. Essential for database exploration, schema discovery, and planning
    data operations.

    Parameters:
        connection_name: Name of registered database connection
            - Must be previously registered
            - Case-sensitive

        database_name: Database or schema name (default: None)
            - PostgreSQL: Schema name (use 'public' for default)
            - MySQL: Database name
            - SQLite: Not used (always main database)
            - MongoDB: Database name
            - None uses connection default

    Returns:
        Dictionary containing:
            - success: Boolean indicating operation success
            - connection_name: Echo of connection used
            - database_name: Database/schema name used
            - tables: List of table/collection names
            - total_tables: Count of tables found
            - error: Error message if success is False

    Usage:
        Use this to discover available tables before querying or analyzing data.
        Essential first step in database exploration and schema analysis.

        Common scenarios:
        - Explore database structure
        - Find tables matching naming patterns
        - Verify table existence before queries
        - Plan data migration or backup operations

        Best practices:
        - Specify database_name for PostgreSQL
        - Use with describe_table for full schema info
        - Check table existence before operations

    Examples:
        List PostgreSQL tables in schema:
            result = await list_tables(
                connection_name="postgres_db",
                database_name="public"
            )
            # Returns: {
            #     'success': True,
            #     'tables': ['users', 'orders', 'products', 'invoices'],
            #     'total_tables': 4
            # }

        List SQLite tables (no database needed):
            result = await list_tables(connection_name="sqlite_db")
            # Returns: All tables in SQLite database

        List MongoDB collections:
            result = await list_tables(
                connection_name="mongo_conn",
                database_name="production"
            )
            # Returns: All collections in production database

        Check if table exists:
            result = await list_tables("prod_db", "public")
            if 'my_table' in result.get('tables', []):
                print("Table exists!")
            else:
                print("Table not found")

    Notes:
        - PostgreSQL requires schema name (use 'public' for default schema)
        - System tables may be included in some databases
        - Views and materialized views may also appear
        - MongoDB shows only collections with documents

    See Also:
        - list_databases: List available databases first
        - describe_table: Get detailed table structure
        - quick_data_sample: Sample data from listed tables
    """
    try:
        connector = db_manager.get_connector(connection_name)
        if not connector:
            return {"success": False, "error": f"Connection not found: {connection_name}"}

        # Get list of tables (implementation depends on database type)
        tables = await connector.list_tables(database=database_name)

        return {
            "success": True,
            "connection_name": connection_name,
            "database_name": database_name,
            "tables": tables,
            "total_tables": len(tables),
        }

    except Exception as e:
        logger.error(f"Error listing tables for {connection_name}.{database_name}: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
@HelpSystem.register_tool
async def describe_table(
    connection_name: str, table_name: str, database_name: Optional[str] = None
) -> Dict[str, Any]:
    """Get detailed schema information about table or collection.

    Retrieves complete schema details including columns, data types, constraints,
    indexes, and relationships. Essential for understanding table structure before
    writing queries or performing data operations.

    Parameters:
        connection_name: Name of registered database connection
            - Must be previously registered
            - Case-sensitive

        table_name: Name of table or collection
            - SQL: Table name (e.g., 'users', 'orders')
            - MongoDB: Collection name
            - ChromaDB: Collection name

        database_name: Database or schema name (default: None)
            - PostgreSQL: Schema name
            - MySQL: Database name
            - SQLite: Not used
            - MongoDB: Database name

    Returns:
        Dictionary containing:
            - success: Boolean indicating operation success
            - connection_name: Echo of connection used
            - database_name: Database/schema name
            - table_name: Table/collection name
            - schema: Schema information dictionary with:
                - columns: List of column definitions
                - primary_keys: List of primary key columns
                - foreign_keys: List of foreign key relationships
                - indexes: List of indexes
                - constraints: List of constraints
            - error: Error message if success is False

    Usage:
        Use this to understand table structure before writing queries or performing
        data operations. Provides comprehensive schema metadata for all database types.

        Common scenarios:
        - Understand table structure before querying
        - Plan data migrations
        - Verify schema changes after migrations
        - Generate dynamic queries based on schema
        - Document database structures

        Best practices:
        - Run before writing complex queries
        - Use to validate expected schema
        - Check data types before inserts
        - Review indexes for query optimization

    Examples:
        Describe PostgreSQL table:
            result = await describe_table(
                connection_name="postgres_db",
                table_name="users",
                database_name="public"
            )
            # Returns: {
            #     'success': True,
            #     'schema': {
            #         'columns': [
            #             {'name': 'id', 'type': 'integer', 'nullable': False},
            #             {'name': 'email', 'type': 'varchar(255)', 'nullable': False},
            #             {'name': 'created_at', 'type': 'timestamp', 'nullable': True}
            #         ],
            #         'primary_keys': ['id'],
            #         'indexes': [{'name': 'idx_email', 'columns': ['email']}]
            #     }
            # }

        Describe SQLite table:
            result = await describe_table(
                connection_name="sqlite_db",
                table_name="products"
            )
            # Returns: Schema with column details and constraints

        Describe MongoDB collection:
            result = await describe_table(
                connection_name="mongo_conn",
                table_name="users",
                database_name="production"
            )
            # Returns: Inferred schema from document sampling

        Error handling:
            result = await describe_table(
                connection_name="prod_db",
                table_name="nonexistent"
            )
            if not result['success']:
                print(f"Schema fetch failed: {result['error']}")
            # Logs: Schema fetch failed: Table 'nonexistent' does not exist

    Notes:
        - MongoDB schema is inferred from document sampling
        - Some databases may restrict schema access
        - Index information may vary by database type
        - Foreign keys not supported in all databases

    See Also:
        - list_tables: Discover available tables
        - get_schema_diff: Compare two table schemas
        - quick_data_sample: See actual data samples
    """
    try:
        connector = db_manager.get_connector(connection_name)
        if not connector:
            return {"success": False, "error": f"Connection not found: {connection_name}"}

        # Get table schema (implementation depends on database type)
        schema_info = await connector.get_table_schema(table_name, database=database_name)

        return {
            "success": True,
            "connection_name": connection_name,
            "database_name": database_name,
            "table_name": table_name,
            "schema": schema_info,
        }

    except Exception as e:
        logger.error(f"Error describing table {table_name} in {connection_name}: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
@HelpSystem.register_tool
async def get_schema_diff(
    connection_name: str,
    table1: str,
    table2: str,
    database1: Optional[str] = None,
    database2: Optional[str] = None,
) -> Dict[str, Any]:
    """Compare schemas of two tables to find differences.

    Analyzes and compares column structures, types, and constraints between two
    tables. Useful for migration validation, schema synchronization, and detecting
    schema drift across environments.

    Parameters:
        connection_name: Name of registered database connection
            - Must be previously registered
            - Both tables must be on same connection

        table1: First table/collection name
            - SQL: Table name
            - MongoDB: Collection name

        table2: Second table/collection name
            - SQL: Table name for comparison
            - MongoDB: Collection name

        database1: Database/schema for first table (default: None)
            - PostgreSQL: Schema name
            - MySQL: Database name
            - None uses connection default

        database2: Database/schema for second table (default: None)
            - Can be different from database1
            - Allows cross-database comparisons

    Returns:
        Dictionary containing:
            - success: Boolean indicating operation success
            - connection_name: Echo of connection used
            - table1: Dictionary with table1 details
            - table2: Dictionary with table2 details
            - diff: Comparison results with:
                - tables_match: Boolean if schemas identical
                - column_differences: Columns in one but not other
                - type_differences: Columns with different types
                - constraint_differences: Different constraints
            - error: Error message if success is False

    Usage:
        Use this to compare table schemas for migration validation, detecting
        schema drift, or ensuring consistency across environments.

        Common scenarios:
        - Validate schema migrations
        - Compare prod vs staging schemas
        - Detect schema drift
        - Verify replication accuracy
        - Plan schema synchronization

        Best practices:
        - Compare similar tables (same purpose)
        - Review both column and type differences
        - Use before data migration
        - Document differences for tracking

    Examples:
        Compare tables in same schema:
            result = await get_schema_diff(
                connection_name="postgres_db",
                table1="users_old",
                table2="users_new",
                database1="public",
                database2="public"
            )
            # Returns: {
            #     'success': True,
            #     'diff': {
            #         'tables_match': False,
            #         'column_differences': [
            #             {'column': 'phone', 'status': 'only_in_table2'}
            #         ],
            #         'type_differences': [
            #             {'column': 'email', 'table1_type': 'varchar(100)',
            #              'table2_type': 'varchar(255)'}
            #         ]
            #     }
            # }

        Compare across databases:
            result = await get_schema_diff(
                connection_name="multi_db",
                table1="users",
                table2="users",
                database1="production",
                database2="staging"
            )
            # Returns: Differences between prod and staging users tables

        Check if schemas match:
            result = await get_schema_diff("db", "table_v1", "table_v2")
            if result.get('diff', {}).get('tables_match'):
                print("Schemas are identical!")
            else:
                print("Schemas differ:", result['diff'])

    Notes:
        - Comparison is structural (columns/types), not data
        - Both tables must exist
        - Cross-database comparison requires appropriate permissions
        - MongoDB comparisons based on inferred schemas

    See Also:
        - describe_table: Get individual table schema
        - list_tables: Discover tables to compare
    """
    try:
        connector = db_manager.get_connector(connection_name)
        if not connector:
            return {"success": False, "error": f"Connection not found: {connection_name}"}

        # Get both table schemas
        schema1 = await connector.get_table_schema(table1, database=database1)
        schema2 = await connector.get_table_schema(table2, database=database2)

        # Compare schemas (simple implementation)
        diff = {"tables_match": table1 == table2, "column_differences": [], "type_differences": []}

        # This is a simplified comparison - actual implementation would be more detailed
        if isinstance(schema1, dict) and isinstance(schema2, dict):
            cols1 = {col["name"]: col for col in schema1.get("columns", [])}
            cols2 = {col["name"]: col for col in schema2.get("columns", [])}

            # Find columns in table1 but not in table2
            for col_name, col_info in cols1.items():
                if col_name not in cols2:
                    diff["column_differences"].append(
                        {
                            "column": col_name,
                            "status": "only_in_table1",
                            "table1_type": col_info.get("type"),
                        }
                    )

            # Find columns in table2 but not in table1
            for col_name, col_info in cols2.items():
                if col_name not in cols1:
                    diff["column_differences"].append(
                        {
                            "column": col_name,
                            "status": "only_in_table2",
                            "table2_type": col_info.get("type"),
                        }
                    )

            # Find columns with different types
            for col_name, col_info in cols1.items():
                if col_name in cols2 and col_info.get("type") != cols2[col_name].get("type"):
                    diff["type_differences"].append(
                        {
                            "column": col_name,
                            "table1_type": col_info.get("type"),
                            "table2_type": cols2[col_name].get("type"),
                        }
                    )

        return {
            "success": True,
            "connection_name": connection_name,
            "table1": {"name": table1, "database": database1},
            "table2": {"name": table2, "database": database2},
            "diff": diff,
        }

    except Exception as e:
        logger.error(f"Error comparing schemas for {table1} and {table2}: {e}")
        return {"success": False, "error": str(e)}
