# Database operations portmanteau tool.
# Consolidates data manipulation and query execution operations.

import logging
from typing import Any

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.database_manager import DatabaseType, db_manager
from database_operations_mcp.tools.help_tools import HelpSystem

logger = logging.getLogger(__name__)


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def db_operations(
    operation: str,
    connection_name: str | None = None,
    query: str | None = None,
    params: dict[str, Any] | None = None,
    data: list[dict[str, Any]] | None = None,
    table_name: str | None = None,
    batch_size: int = 1000,
    output_format: str = "json",
    output_path: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    """Database operations portmanteau tool.

    Comprehensive database data manipulation and query execution consolidating ALL data
    operations into a single interface. Supports transactions, writes, batch inserts,
    queries, sampling, and export operations across SQL, NoSQL, and Vector databases.

    Prerequisites:
        - For all operations: Valid database connection registered via db_connection
        - For write operations: Appropriate database permissions (INSERT, UPDATE, DELETE)
        - For batch operations: Sufficient memory for batch processing
        - For export operations: Write permissions to output_path directory

    Operations:
        - execute_transaction: Execute a database transaction with multiple operations
        - execute_write: Execute write operations (INSERT, UPDATE, DELETE)
        - batch_insert: Insert multiple records in batches for better performance
        - execute_query: Execute read-only queries (SELECT)
        - quick_data_sample: Get a quick sample of data from a table
        - export_query_results: Export query results to various formats

    Parameters:
        operation (str, REQUIRED): The operation to perform
            Valid values: 'execute_transaction', 'execute_write', 'batch_insert',
                         'execute_query', 'quick_data_sample', 'export_query_results'
            Example: 'execute_query', 'batch_insert', 'export_query_results'

        connection_name (str, REQUIRED): Name of the database connection to use
            Format: Registered connection name (from db_connection)
            Validation: Must be previously registered via db_connection(operation='register')
            Required for: All operations
            Example: 'prod_db', 'analytics_warehouse', 'local_sqlite'

        query (str, OPTIONAL): SQL or database-specific query to execute
            Format: SQL SELECT, INSERT, UPDATE, DELETE statements
            Required for: execute_transaction, execute_write, execute_query, export_query_results
            SQL example: 'SELECT * FROM users WHERE active = ?'
            Parameterized: Use ? or :param_name placeholders for security
            Maximum length: 10,000 characters
            Example: 'INSERT INTO users (name, email) VALUES (?, ?)'

        params (dict, OPTIONAL): Parameters for parameterized queries
            Format: Dictionary mapping parameter names to values
            Purpose: Prevents SQL injection, enables prepared statements
            Required for: Parameterized queries (when query contains placeholders)
            Example: {'user_id': 123, 'status': 'active', 'active': True}

        data (list[dict], OPTIONAL): List of records to insert
            Format: List of dictionaries where keys are column names
            Required for: batch_insert operation
            Validation: All dictionaries must have same keys
            Maximum: 100,000 records per batch
            Example: [
                {'name': 'John', 'email': 'john@example.com'},
                {'name': 'Jane', 'email': 'jane@example.com'}
            ]

        table_name (str, OPTIONAL): Name of the table for operations
            Format: Valid table name in database
            Required for: batch_insert, quick_data_sample
            Validation: Table must exist in database
            Example: 'users', 'orders', 'products'

        batch_size (int, OPTIONAL): Number of records to process per batch
            Format: Positive integer
            Range: 1-10,000
            Default: 1000
            Used for: batch_insert operation
            Recommendation: 1000 for optimal performance, 100 for memory-constrained systems
            Example: 500, 2000

        output_format (str, OPTIONAL): Format for exported data
            Valid values: 'json', 'csv', 'excel'
            Default: 'json'
            Used for: export_query_results operation
            Example: 'csv', 'json', 'excel'

        output_path (str, OPTIONAL): Path to save exported data
            Format: Absolute or relative file path
            Required for: export_query_results (if saving to file)
            Validation: Parent directory must exist and be writable
            Example: 'C:/data/users.csv', './exports/results.json', '/tmp/query_results.xlsx'

        limit (int, OPTIONAL): Maximum number of records to return
            Format: Positive integer
            Range: 1-10,000
            Default: 100
            Used for: execute_query, quick_data_sample operations
            Behavior: Automatically applied if not in query
            Example: 50, 500, 1000

    Returns:
        Dictionary containing operation-specific results:
            - success: Boolean indicating operation success
            - operation: Echo of operation performed
            - For execute_transaction: message, rows_affected, transaction_id
            - For execute_write: message, rows_affected, last_insert_id (if INSERT)
            - For batch_insert: message, total_inserted, batches_processed
            - For execute_query: result (dict with rows, columns, row_count), applied_limit
            - For quick_data_sample: sample_data (list), columns (list), row_count
            - For export_query_results: message, export_path, format, record_count
            - error: Error message if success is False
            - connection_name: Echo of connection used
            - available_operations: List of valid operations (on invalid operation)

    Usage:
        This tool is the primary interface for all database data operations. Use it to
        query, insert, update, delete, and export data across all supported database types.

        Common scenarios:
        - Data retrieval: Execute SELECT queries to fetch data for analysis
        - Data modification: Insert, update, or delete records with transactions
        - Bulk operations: Import large datasets efficiently with batch inserts
        - Data exploration: Quickly sample table contents without full queries
        - Data export: Export query results to files for reporting or migration

        Best practices:
        - Always use parameterized queries (params) for user input
        - Use transactions for multi-step operations requiring atomicity
        - Use batch inserts for inserting more than 100 records
        - Apply appropriate limits to prevent memory issues
        - Test queries with quick_data_sample before full execution

    Examples:
        Execute parameterized SELECT query:
            result = await db_operations(
                operation='execute_query',
                connection_name='production_db',
                query='SELECT id, name, email FROM users WHERE active = ? AND created_date > ?',
                params={'active': True, 'created_date': '2024-01-01'},
                limit=50
            )
            # Returns: {
            #     'success': True,
            #     'result': {
            #         'rows': [{'id': 1, 'name': 'Alice', 'email': 'alice@example.com'}, ...],
            #         'columns': ['id', 'name', 'email'],
            #         'row_count': 42
            #     },
            #     'applied_limit': 50,
            #     'connection_name': 'production_db'
            # }

        Insert single record:
            result = await db_operations(
                operation='execute_write',
                connection_name='production_db',
                query='INSERT INTO users (name, email, created_at) VALUES (?, ?, ?)',
                params={'name': 'John Doe', 'email': 'john@example.com', 'created_at': '2024-01-15'}
            )
            # Returns: {
            #     'success': True,
            #     'message': 'Write operation executed successfully',
            #     'rows_affected': 1,
            #     'last_insert_id': 12345
            # }

        Batch insert multiple records:
            result = await db_operations(
                operation='batch_insert',
                connection_name='production_db',
                table_name='users',
                data=[
                    {'name': 'John', 'email': 'john@example.com'},
                    {'name': 'Jane', 'email': 'jane@example.com'},
                    {'name': 'Bob', 'email': 'bob@example.com'}
                ],
                batch_size=100
            )
            # Returns: {
            #     'success': True,
            #     'message': 'Batch insert completed successfully',
            #     'total_inserted': 3,
            #     'batches_processed': 1
            # }

        Execute transaction (atomic multi-step operation):
            result = await db_operations(
                operation='execute_transaction',
                connection_name='production_db',
                query='''
                    BEGIN;
                    INSERT INTO orders (user_id, total) VALUES (?, ?);
                    UPDATE users SET last_order_date = ? WHERE id = ?;
                    COMMIT;
                ''',
                params={'user_id': 123, 'total': 99.99, 'last_order_date': '2024-01-15', 'id': 123}
            )
            # Returns: {
            #     'success': True,
            #     'message': 'Transaction executed successfully',
            #     'rows_affected': 2,
            #     'transaction_id': 'txn_abc123'
            # }

        Quick data sample:
            result = await db_operations(
                operation='quick_data_sample',
                connection_name='production_db',
                table_name='users',
                limit=10
            )
            # Returns: {
            #     'success': True,
            #     'sample_data': [
            #         {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'},
            #         {'id': 2, 'name': 'Bob', 'email': 'bob@example.com'},
            #         ...
            #     ],
            #     'columns': ['id', 'name', 'email'],
            #     'row_count': 10
            # }

        Export query results to CSV:
            result = await db_operations(
                operation='export_query_results',
                connection_name='production_db',
                query='SELECT * FROM users WHERE active = 1',
                output_format='csv',
                output_path='C:/data/active_users.csv'
            )
            # Returns: {
            #     'success': True,
            #     'message': 'Query results exported successfully',
            #     'export_path': 'C:/data/active_users.csv',
            #     'format': 'csv',
            #     'record_count': 1250
            # }

        Error handling - connection not found:
            result = await db_operations(
                operation='execute_query',
                connection_name='nonexistent',
                query='SELECT * FROM users'
            )
            # Returns: {
            #     'success': False,
            #     'error': 'Connection not found: nonexistent',
            #     'connection_name': 'nonexistent'
            # }

        Error handling - invalid operation:
            result = await db_operations(operation='invalid_op')
            # Returns: {
            #     'success': False,
            #     'error': 'Unknown operation: invalid_op',
            #     'available_operations': ['execute_transaction', 'execute_write', ...]
            # }

    Errors:
        Common errors and solutions:
        - 'Connection not found: {connection_name}':
            Cause: Connection name doesn't exist or not registered
            Fix: Use db_connection(operation='list') to see available connections
            Workaround: Register connection first with db_connection(operation='register')

        - 'Query is required':
            Cause: Missing query parameter for operation requiring query
            Fix: Provide query parameter with valid SQL statement
            Example: query='SELECT * FROM users'

        - 'Table not found: {table_name}':
            Cause: Table doesn't exist in database
            Fix: Use db_schema(operation='list_tables') to see available tables
            Workaround: Create table first or check spelling

        - 'Batch insert failed: {error}':
            Cause: Data format mismatch or constraint violation
            Fix: Ensure all records have same keys, verify data types match schema
            Workaround: Insert smaller batches or check individual record validity

        - 'Export failed: {error}':
            Cause: Output path inaccessible or insufficient permissions
            Fix: Verify path exists, check write permissions, ensure sufficient disk space
            Workaround: Use different output_path or export to user home directory

        - 'Query execution failed: {error}':
            Cause: SQL syntax error or database-specific issue
            Fix: Validate SQL syntax, check database compatibility, verify table/column names
            Workaround: Test query with quick_data_sample first, simplify query

    See Also:
        - db_connection: Register and manage database connections
        - db_schema: Inspect database structure and schema
        - db_management: Database administration and health checks
    """

    if operation == "execute_transaction":
        return await _execute_transaction(connection_name, query, params)
    elif operation == "execute_write":
        return await _execute_write(connection_name, query, params)
    elif operation == "batch_insert":
        return await _batch_insert(connection_name, table_name, data, batch_size)
    elif operation == "execute_query":
        return await _execute_query(connection_name, query, params, limit)
    elif operation == "quick_data_sample":
        return await _quick_data_sample(connection_name, table_name, limit)
    elif operation == "export_query_results":
        return await _export_query_results(
            connection_name, query, params, output_format, output_path
        )
    else:
        return {
            "success": False,
            "error": f"Unknown operation: {operation}",
            "available_operations": [
                "execute_transaction",
                "execute_write",
                "batch_insert",
                "execute_query",
                "quick_data_sample",
                "export_query_results",
            ],
        }


async def _execute_transaction(
    connection_name: str, query: str, params: dict[str, Any] | None
) -> dict[str, Any]:
    """Execute a database transaction with multiple operations."""
    try:
        if not connection_name:
            raise ValueError("Connection name is required")
        if not query:
            raise ValueError("Query is required")

        connector = db_manager.get_connector(connection_name)
        if not connector:
            raise ValueError(f"Connection '{connection_name}' not found")

        result = await connector.execute_transaction(query, params or {})

        return {
            "success": True,
            "message": "Transaction executed successfully",
            "connection_name": connection_name,
            "rows_affected": result.get("rows_affected", 0),
            "transaction_id": result.get("transaction_id"),
        }

    except Exception as e:
        logger.error(f"Error executing transaction: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to execute transaction: {str(e)}",
            "connection_name": connection_name,
        }


async def _execute_write(
    connection_name: str, query: str, params: dict[str, Any] | None
) -> dict[str, Any]:
    """Execute write operations (INSERT, UPDATE, DELETE)."""
    try:
        if not connection_name:
            raise ValueError("Connection name is required")
        if not query:
            raise ValueError("Query is required")

        connector = db_manager.get_connector(connection_name)
        if not connector:
            raise ValueError(f"Connection '{connection_name}' not found")

        result = await connector.execute_write(query, params or {})

        return {
            "success": True,
            "message": "Write operation executed successfully",
            "connection_name": connection_name,
            "rows_affected": result.get("rows_affected", 0),
            "last_insert_id": result.get("last_insert_id"),
        }

    except Exception as e:
        logger.error(f"Error executing write operation: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to execute write operation: {str(e)}",
            "connection_name": connection_name,
        }


async def _batch_insert(
    connection_name: str, table_name: str, data: list[dict[str, Any]], batch_size: int
) -> dict[str, Any]:
    """Insert multiple records in batches for better performance."""
    try:
        if not connection_name:
            raise ValueError("Connection name is required")
        if not table_name:
            raise ValueError("Table name is required")
        if not data:
            raise ValueError("Data is required")

        connector = db_manager.get_connector(connection_name)
        if not connector:
            raise ValueError(f"Connection '{connection_name}' not found")

        result = await connector.batch_insert(table_name, data, batch_size)

        return {
            "success": True,
            "message": "Batch insert completed successfully",
            "connection_name": connection_name,
            "table_name": table_name,
            "records_inserted": result.get("records_inserted", 0),
            "batches_processed": result.get("batches_processed", 0),
        }

    except Exception as e:
        logger.error(f"Error executing batch insert: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to execute batch insert: {str(e)}",
            "connection_name": connection_name,
            "table_name": table_name,
        }


async def _execute_query(
    connection_name: str | None, query: str | None, params: dict[str, Any] | None, limit: int
) -> dict[str, Any]:
    """Execute read-only queries (SELECT)."""
    try:
        if not connection_name:
            return {"success": False, "error": "Connection name is required"}
        if not query:
            return {"success": False, "error": "Query is required"}

        connector = db_manager.get_connector(connection_name)
        if not connector:
            return {"success": False, "error": f"Connection not found: {connection_name}"}

        # Apply limit to query if not already present
        limited_query = _apply_query_limit(query, limit, connector.database_type)

        # Execute the query
        result = await connector.execute_query(limited_query, params or {})

        return {
            "success": True,
            "connection_name": connection_name,
            "query": query,
            "parameters": params,
            "applied_limit": limit,
            "result": {
                "rows": result.get("rows", []),
                "columns": result.get("columns", []),
                "row_count": len(result.get("rows", [])),
            },
        }

    except Exception as e:
        logger.error(f"Error executing query on {connection_name}: {e}")
        return {
            "success": False,
            "error": str(e),
            "query": query,
            "connection_name": connection_name,
        }


async def _quick_data_sample(
    connection_name: str | None, table_name: str | None, limit: int
) -> dict[str, Any]:
    """Get a quick sample of data from a table."""
    try:
        if not connection_name:
            return {"success": False, "error": "Connection name is required"}
        if not table_name:
            return {"success": False, "error": "Table name is required"}

        connector = db_manager.get_connector(connection_name)
        if not connector:
            return {"success": False, "error": f"Connection not found: {connection_name}"}

        # Generate appropriate query based on database type
        query = _generate_sample_query(connector.database_type, table_name, None, limit, None, None)

        # Execute the query
        result = await connector.execute_query(query, {})

        return {
            "success": True,
            "connection_name": connection_name,
            "table_name": table_name,
            "sample_size": limit,
            "generated_query": query,
            "result": {
                "rows": result.get("rows", []),
                "columns": result.get("columns", []),
                "row_count": len(result.get("rows", [])),
            },
        }

    except Exception as e:
        logger.error(f"Error getting data sample from {table_name}: {e}")
        return {
            "success": False,
            "error": str(e),
            "connection_name": connection_name,
            "table_name": table_name,
        }


async def _export_query_results(
    connection_name: str | None,
    query: str | None,
    params: dict[str, Any] | None,
    output_format: str,
    output_path: str | None,
) -> dict[str, Any]:
    """Export query results to various formats."""
    try:
        if not connection_name:
            return {"success": False, "error": "Connection name is required"}
        if not query:
            return {"success": False, "error": "Query is required"}

        connector = db_manager.get_connector(connection_name)
        if not connector:
            return {"success": False, "error": f"Connection not found: {connection_name}"}

        # Execute query with limit
        limited_query = _apply_query_limit(query, 10000, connector.database_type)
        result = await connector.execute_query(limited_query, params or {})

        # Format results based on export format
        formatted_data = _format_export_data(result, output_format)

        # Save to file if path provided
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                if output_format.lower() == "json":
                    import json

                    json.dump(formatted_data, f, indent=2)
                else:
                    f.write(
                        formatted_data if isinstance(formatted_data, str) else str(formatted_data)
                    )

        return {
            "success": True,
            "connection_name": connection_name,
            "query": query,
            "export_format": output_format,
            "row_count": len(result.get("rows", [])),
            "exported_data": formatted_data if not output_path else None,
            "file_path": output_path if output_path else None,
        }

    except Exception as e:
        logger.error(f"Error exporting query results: {e}")
        return {
            "success": False,
            "error": str(e),
            "connection_name": connection_name,
            "export_format": output_format,
        }


def _apply_query_limit(query: str, limit: int | None, database_type: DatabaseType) -> str:
    """Apply LIMIT clause to query based on database type."""
    if not limit:
        return query

    query_lower = query.lower().strip()

    # Check if LIMIT already exists
    if "limit" in query_lower:
        return query

    # Add LIMIT based on database type
    if database_type in [DatabaseType.POSTGRESQL, DatabaseType.SQLITE]:
        return f"{query.rstrip(';')} LIMIT {limit}"
    else:
        # For NoSQL databases, limit logic will be handled in connectors
        return query


def _generate_sample_query(
    database_type: DatabaseType,
    table_name: str,
    database_name: str | None,
    sample_size: int,
    include_columns: list[str] | None,
    exclude_columns: list[str] | None,
) -> str:
    """Generate appropriate sample query based on database type."""
    if database_type in [DatabaseType.POSTGRESQL, DatabaseType.SQLITE]:
        table_ref = f"{database_name}.{table_name}" if database_name else table_name

        # Build column list if specified
        if include_columns:
            columns = ", ".join(include_columns)
        else:
            columns = "*"

        return f"SELECT {columns} FROM {table_ref} LIMIT {sample_size}"
    elif database_type == DatabaseType.MONGODB:
        # MongoDB query will be handled in connector
        return f"db.{table_name}.find().limit({sample_size})"
    elif database_type == DatabaseType.CHROMADB:
        # ChromaDB query will be handled in connector
        return f"collection.peek({sample_size})"
    else:
        return f"/* Sample query for {table_name} */"


def _format_export_data(result: dict[str, Any], export_format: str) -> Any:
    """Format query results for export."""
    rows = result.get("rows", [])
    columns = result.get("columns", [])

    if export_format.lower() == "json":
        return {
            "columns": columns,
            "rows": rows,
            "metadata": {"row_count": len(rows), "column_count": len(columns)},
        }
    elif export_format.lower() == "csv":
        # Convert to CSV-like structure
        csv_lines = []
        if columns:
            csv_lines.append(",".join(str(col) for col in columns))
        for row in rows:
            if isinstance(row, dict):
                csv_lines.append(",".join(str(val) for val in row.values()))
            else:
                csv_lines.append(",".join(str(val) for val in row))
        return "\n".join(csv_lines)
    elif export_format.lower() == "excel":
        # Excel format (simplified structure)
        return {"worksheets": [{"name": "Query Results", "headers": columns, "data": rows}]}
    else:
        return {"format": export_format, "columns": columns, "rows": rows}
