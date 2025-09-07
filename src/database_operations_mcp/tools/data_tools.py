"""
Data read/write operations for databases.

This module provides tools for executing queries, inserting, updating, and deleting data
across various database backends through a unified interface.
"""

from typing import Dict, Any, List, Optional, Union, TypeVar, Type, cast

# Import the global MCP instance
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.database_manager import QueryError, QueryResult
from database_operations_mcp.tools.help_tools import HelpSystem
from database_operations_mcp.tools import init_tools as DATABASE_CONNECTIONS
import logging
import json

# Type variable for generic type hints
T = TypeVar('T')

logger = logging.getLogger(__name__)

# Register tools using the @mcp.tool decorator
# The mcp instance is imported from the centralized config

@mcp.tool()
@HelpSystem.register_tool
async def execute_transaction(
    queries: List[Dict[str, Any]],
    connection_name: str = "default"
) -> Dict[str, Any]:
    """Execute multiple queries in a transaction.
    
    Args:
        queries: List of query objects with 'query' and 'parameters' keys
        connection_name: Name of the database connection to use
        
    Returns:
        Dict containing the results of all queries and transaction status
        
    Example:
        ```python
        queries = [
            {
                'query': 'INSERT INTO users (name, email) VALUES (?, ?)',
                'parameters': ['John Doe', 'john@example.com']
            },
            {
                'query': 'UPDATE counters SET value = value + 1 WHERE name = ?',
                'parameters': ['user_count']
            }
        ]
        result = await execute_transaction(queries, 'sqlite')
        ```
    """
    if connection_name not in DATABASE_CONNECTIONS:
        return {
            'status': 'error',
            'message': f'No such connection: {connection_name}',
            'error_type': 'ConnectionError'
        }
        
    connector = DATABASE_CONNECTIONS[connection_name].get('connector')
    if not connector:
        return {
            'status': 'error',
            'message': f'No connector found for connection: {connection_name}',
            'error_type': 'ConnectionError'
        }
    
    results = {'status': 'success', 'results': []}
    
    try:
        async with await connector.connection() as conn:
            for query_info in queries:
                query = query_info.get('query')
                parameters = query_info.get('parameters', {})
                
                if not query:
                    raise ValueError("Query is required for each operation")
                    
                result = await conn.execute_query(query, parameters)
                results['results'].append({
                    'status': 'success',
                    'data': result.data,
                    'rowcount': result.rowcount,
                    'execution_time': result.execution_time,
                    'columns': result.columns
                })
        
        return results
        
    except QueryError as e:
        return {
            'status': 'error',
            'message': 'Transaction failed',
            'error': str(e),
            'completed_queries': len(results['results'])
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Unexpected error: {str(e)}',
            'completed_queries': len(results['results'])
        }

@mcp.tool()
@HelpSystem.register_tool
async def execute_write(
    query: str,
    parameters: Optional[Union[Dict[str, Any], List[Any]]] = None,
    connection_name: str = "default"
) -> Dict[str, Any]:
    """Execute a write operation (INSERT, UPDATE, DELETE, etc.) on the database.
    
    Args:
        query: SQL or database-specific write operation string
        parameters: Optional parameters for the query
        connection_name: Name of the database connection to use
        
    Returns:
        Dict containing the operation result and status
    """
    if connection_name not in DATABASE_CONNECTIONS:
        return {
            'status': 'error',
            'message': f'No such connection: {connection_name}'
        }
    
    connector = DATABASE_CONNECTIONS[connection_name].get('connector')
    if not connector:
        return {
            'status': 'error',
            'message': f'No connector found for connection: {connection_name}'
        }
    
    try:
        async with await connector.connection() as conn:
            result = await conn.execute_query(query, parameters or {})
            return {
                'status': 'success',
                'rowcount': result.rowcount,
                'execution_time': result.execution_time
            }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Query execution failed: {str(e)}',
            'error_type': type(e).__name__
        }

@mcp.tool()
@HelpSystem.register_tool
async def batch_insert(
    table: str,
    data: List[Dict[str, Any]],
    connection_name: str = "default",
    batch_size: int = 1000
) -> Dict[str, Any]:
    """Insert multiple rows into a table in batches.
    
    Args:
        table: Name of the table to insert into
        data: List of dictionaries where keys are column names
        connection_name: Name of the database connection to use
        batch_size: Number of rows to insert per batch
        
    Returns:
        Dict containing the insert status and statistics
    """
    if not data:
        return {
            'status': 'error',
            'message': 'No data provided'
        }
    
    if connection_name not in DATABASE_CONNECTIONS:
        return {
            'status': 'error',
            'message': f'No such connection: {connection_name}'
        }
    
    connector = DATABASE_CONNECTIONS[connection_name].get('connector')
    if not connector:
        return {
            'status': 'error',
            'message': f'No connector found for connection: {connection_name}'
        }
    
    # Get column names from the first row
    columns = list(data[0].keys())
    if not columns:
        return {
            'status': 'error',
            'message': 'No columns found in data'
        }
    
    # Prepare the base query
    columns_str = ', '.join(f'"{col}"' for col in columns)
    placeholders = ', '.join(['?'] * len(columns))
    query = f'INSERT INTO "{table}" ({columns_str}) VALUES ({placeholders})'
    
    total_rows = len(data)
    processed = 0
    
    try:
        async with await connector.connection() as conn:
            # Process in batches
            for i in range(0, total_rows, batch_size):
                batch = data[i:i + batch_size]
                
                # Flatten parameters for the batch
                params = []
                for row in batch:
                    params.append([row.get(col) for col in columns])
                
                # Execute the batch insert
                await conn.executemany(query, params)
                processed += len(batch)
            
            return {
                'status': 'success',
                'processed': processed,
                'message': f'Successfully inserted {processed} rows into {table}'
            }
    
    except Exception as e:
        logger.exception("Error in batch insert")
        return {
            'status': 'error',
            'message': f'Batch insert failed: {str(e)}',
            'processed': processed,
            'error_type': type(e).__name__
        }
