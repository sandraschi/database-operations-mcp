# Database operations portmanteau tool.
# Consolidates data manipulation and query execution operations.

import logging
from typing import Any, Dict, List, Optional

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.database_manager import db_manager
from database_operations_mcp.tools.help_tools import HelpSystem

logger = logging.getLogger(__name__)


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def db_operations(
    operation: str,
    connection_name: Optional[str] = None,
    query: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[List[Dict[str, Any]]] = None,
    table_name: Optional[str] = None,
    batch_size: int = 1000,
    output_format: str = "json",
    output_path: Optional[str] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    """Database operations portmanteau tool.

    This tool consolidates all database data manipulation and query execution operations
    into a single interface, providing unified access to database operations.

    Operations:
    - execute_transaction: Execute a database transaction with multiple operations
    - execute_write: Execute write operations (INSERT, UPDATE, DELETE)
    - batch_insert: Insert multiple records in batches for better performance
    - execute_query: Execute read-only queries (SELECT)
    - quick_data_sample: Get a quick sample of data from a table
    - export_query_results: Export query results to various formats

    Args:
        operation: The operation to perform (required)
        connection_name: Name of the database connection to use
        query: SQL query to execute
        params: Parameters for parameterized queries
        data: List of records to insert (for batch operations)
        table_name: Name of the table for sampling operations
        batch_size: Number of records to process per batch
        output_format: Format for exported data (json, csv, excel)
        output_path: Path to save exported data
        limit: Maximum number of records to return

    Returns:
        Dictionary with operation results and data

    Examples:
        Execute transaction:
        db_operations(operation='execute_transaction', connection_name='prod_db',
                     query='BEGIN; INSERT INTO users VALUES (?, ?); COMMIT;')

        Execute write operation:
        db_operations(operation='execute_write', connection_name='prod_db',
                     query='INSERT INTO users (name, email) VALUES (?, ?)',
                     params={'name': 'John', 'email': 'john@example.com'})

        Batch insert:
        db_operations(operation='batch_insert', connection_name='prod_db',
                     table_name='users', data=[{'name': 'John'}, {'name': 'Jane'}])

        Execute query:
        db_operations(operation='execute_query', connection_name='prod_db',
                     query='SELECT * FROM users WHERE active = ?', params={'active': True})

        Quick data sample:
        db_operations(operation='quick_data_sample', connection_name='prod_db',
                     table_name='users', limit=10)

        Export results:
        db_operations(operation='export_query_results', connection_name='prod_db',
                     query='SELECT * FROM users', output_format='csv', output_path='users.csv')
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
    connection_name: str, query: str, params: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
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
    connection_name: str, query: str, params: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
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
    connection_name: str, table_name: str, data: List[Dict[str, Any]], batch_size: int
) -> Dict[str, Any]:
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
    connection_name: str, query: str, params: Optional[Dict[str, Any]], limit: int
) -> Dict[str, Any]:
    """Execute read-only queries (SELECT)."""
    try:
        if not connection_name:
            raise ValueError("Connection name is required")
        if not query:
            raise ValueError("Query is required")

        connector = db_manager.get_connector(connection_name)
        if not connector:
            raise ValueError(f"Connection '{connection_name}' not found")

        result = await connector.execute_query(query, params or {}, limit)

        return {
            "success": True,
            "message": "Query executed successfully",
            "connection_name": connection_name,
            "data": result.get("data", []),
            "row_count": len(result.get("data", [])),
            "columns": result.get("columns", []),
        }

    except Exception as e:
        logger.error(f"Error executing query: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to execute query: {str(e)}",
            "connection_name": connection_name,
        }


async def _quick_data_sample(connection_name: str, table_name: str, limit: int) -> Dict[str, Any]:
    """Get a quick sample of data from a table."""
    try:
        if not connection_name:
            raise ValueError("Connection name is required")
        if not table_name:
            raise ValueError("Table name is required")

        connector = db_manager.get_connector(connection_name)
        if not connector:
            raise ValueError(f"Connection '{connection_name}' not found")

        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        result = await connector.execute_query(query, {}, limit)

        return {
            "success": True,
            "message": f"Data sample retrieved from {table_name}",
            "connection_name": connection_name,
            "table_name": table_name,
            "data": result.get("data", []),
            "row_count": len(result.get("data", [])),
            "columns": result.get("columns", []),
        }

    except Exception as e:
        logger.error(f"Error getting data sample: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to get data sample: {str(e)}",
            "connection_name": connection_name,
            "table_name": table_name,
        }


async def _export_query_results(
    connection_name: str,
    query: str,
    params: Optional[Dict[str, Any]],
    output_format: str,
    output_path: Optional[str],
) -> Dict[str, Any]:
    """Export query results to various formats."""
    try:
        if not connection_name:
            raise ValueError("Connection name is required")
        if not query:
            raise ValueError("Query is required")

        connector = db_manager.get_connector(connection_name)
        if not connector:
            raise ValueError(f"Connection '{connection_name}' not found")

        # Execute query
        result = await connector.execute_query(query, params or {}, limit=10000)
        data = result.get("data", [])
        columns = result.get("columns", [])

        # Export based on format
        if output_format.lower() == "json":
            export_data = data
        elif output_format.lower() == "csv":
            # Convert to CSV format
            import csv
            import io

            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=columns)
            writer.writeheader()
            writer.writerows(data)
            export_data = output.getvalue()
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

        # Save to file if path provided
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                if output_format.lower() == "json":
                    import json

                    json.dump(export_data, f, indent=2)
                else:
                    f.write(export_data)

        return {
            "success": True,
            "message": f"Query results exported to {output_format}",
            "connection_name": connection_name,
            "output_format": output_format,
            "output_path": output_path,
            "row_count": len(data),
            "columns": columns,
        }

    except Exception as e:
        logger.error(f"Error exporting query results: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to export query results: {str(e)}",
            "connection_name": connection_name,
            "output_format": output_format,
        }
