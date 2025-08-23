"""
Data read/write operations for databases.

This module provides tools for executing queries, inserting, updating, and deleting data
across various database backends through a unified interface.
"""

from typing import Dict, Any, List, Optional, Union, TypeVar, Type, cast
from fastmcp import FastMCP
from ..database_manager import QueryError, QueryResult
from .help_tools import HelpSystem
import logging
import json

# Type variable for generic type hints
T = TypeVar('T')

logger = logging.getLogger(__name__)

def register_tools(mcp: FastMCP) -> None:
    """Register data operation tools with the MCP server.
    
    Args:
        mcp: The FastMCP instance to register tools with.
    """
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
        from .init_tools import DATABASE_CONNECTIONS
        
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
            logger.exception("Error executing transaction")
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
            parameters: Parameters for parameterized queries. Can be a dictionary for named
                      parameters or a list for positional parameters.
            connection_name: Name of the database connection to use. Defaults to 'default'.
            
        Returns:
            A dictionary containing:
            - status: 'success' or 'error'
            - rowcount: Number of rows affected by the write operation
            - lastrowid: The primary key of the last inserted row (if applicable)
            - message: Status message or error details
            - execution_time: Time taken to execute the query in seconds
            
        Example:
            ```python
            # Insert operation with named parameters
            result = await execute_write(
                "INSERT INTO users (name, email) VALUES (:name, :email)",
                {"name": "John Doe", "email": "john@example.com"},
                "postgres"
            )
            
            # Update operation with positional parameters
            result = await execute_write(
                "UPDATE users SET active = ? WHERE id = ?",
                [True, 42],
                "sqlite"
            )
            ```
        """
        from .init_tools import DATABASE_CONNECTIONS
        
        if connection_name not in DATABASE_CONNECTIONS:
            return {
                'status': 'error',
                'message': f'No such connection: {connection_name}',
                'error_type': 'ConnectionError'
            }
        
        try:
            connector = DATABASE_CONNECTIONS[connection_name]['connector']
            result = await connector.execute_write(query, parameters or {})
            return {
                'status': 'success',
                'rowcount': result.rowcount,
                'lastrowid': getattr(result, 'lastrowid', None),
                'execution_time': result.execution_time
            }
        except QueryError as e:
            return {
                'status': 'error',
                'message': 'Write operation failed',
                'error': str(e),
                'query': query,
                'parameters': parameters
            }

    @mcp.tool()
    @HelpSystem.register_tool
    async def batch_execute(
        queries: List[Dict[str, Any]],
        connection_name: str = "default"
    ) -> Dict[str, Any]:
        """Execute multiple queries in a transaction.
        
        Args:
            queries: List of query objects with 'query' and 'parameters' keys
            connection_name: Name of the database connection to use
            
        Returns:
            Results for each query in the batch
        """
        from .init_tools import DATABASE_CONNECTIONS
        
        if connection_name not in DATABASE_CONNECTIONS:
            return {
                'status': 'error',
                'message': f'No such connection: {connection_name}'
            }
        
        connector = DATABASE_CONNECTIONS[connection_name]['connector']
        results = []
        
        try:
            async with await connector.begin_transaction():
                for i, query_obj in enumerate(queries):
                    query = query_obj.get('query')
                    params = query_obj.get('parameters', {})
                    
                    try:
                        if query_obj.get('write', False):
                            result = await connector.execute_write(query, params)
                            results.append({
                                'status': 'success',
                                'query_index': i,
                                'rowcount': result.rowcount,
                                'lastrowid': getattr(result, 'lastrowid', None)
                            })
                        else:
                            result = await connector.execute_query(query, params)
                            results.append({
                                'status': 'success',
                                'query_index': i,
                                'data': result.data,
                                'rowcount': result.rowcount
                            })
                    except Exception as e:
                        await connector.rollback()
                        return {
                            'status': 'error',
                            'message': f'Batch failed at query {i+1}',
                            'error': str(e),
                            'failed_query': query,
                            'parameters': params,
                            'completed_queries': results
                        }
                
                await connector.commit()
                return {
                    'status': 'success',
                    'results': results,
                    'total_queries': len(queries)
                }
                
        except Exception as e:
            logger.exception("Error in batch execution")
            if 'connector' in locals():
                await connector.rollback()
            return {
                'status': 'error',
                'message': f'Batch execution failed: {str(e)}',
                'completed_queries': results
            }

    @mcp.tool()
    @HelpSystem.register_tool
    async def export_data(
        self,
        query: str,
        format: str = 'json',
        output_file: Optional[str] = None,
        connection_name: str = "default"
    ) -> Dict[str, Any]:
        """Export query results to a file or return in specified format.
        
        Args:
            query: SQL or database-specific query
            format: Output format (json, csv, tsv)
            output_file: Optional file path to save results
            connection_name: Name of the database connection to use
            
        Returns:
            Export status and result
        """
        from .init_tools import DATABASE_CONNECTIONS
        import json
        
        if connection_name not in DATABASE_CONNECTIONS:
            return {
                'status': 'error',
                'message': f'No such connection: {connection_name}'
            }
        
        connector = DATABASE_CONNECTIONS[connection_name]['connector']
        
        try:
            result = await connector.execute_query(query)
            
            if format == 'json':
                output = json.dumps(result.data, indent=2)
            elif format in ('csv', 'tsv'):
                import csv
                import io
                
                delimiter = ',' if format == 'csv' else '\t'
                output_io = io.StringIO()
                
                if result.data:
                    writer = csv.DictWriter(
                        output_io, 
                        fieldnames=result.data[0].keys(),
                        delimiter=delimiter
                    )
                    writer.writeheader()
                    writer.writerows(result.data)
                
                output = output_io.getvalue()
            else:
                return {
                    'status': 'error',
                    'message': f'Unsupported format: {format}',
                    'supported_formats': ['json', 'csv', 'tsv']
                }
        
            if output_file:
                try:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(output)
                    return {
                        'status': 'success',
                        'message': f'Exported {len(result.data)} rows to {output_file}',
                        'row_count': len(result.data),
                        'file_path': output_file
                    }
                except Exception as e:
                    return {
                        'status': 'error',
                        'message': f'Failed to write to file: {str(e)}',
                        'row_count': len(result.data)
                    }
            else:
                return {
                    'status': 'success',
                    'data': result.data if format == 'json' else output,
                    'row_count': len(result.data),
                    'format': format
                }
                
        except Exception as e:
            logger.exception(f"Error exporting data to {format}")
            return {
                'status': 'error',
                'message': f'Export failed: {str(e)}',
                'error_type': type(e).__name__,
                'query': query
            }
