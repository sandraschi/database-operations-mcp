"""
Database Connection Management Tools.

This module provides functionality for managing database connections, including:
- Listing supported database types
- Creating and testing connections
- Managing connection pools
- Handling connection lifecycle events

It supports various database backends through a unified interface.
"""

import logging
from typing import Any, Dict, List, Optional, TypedDict, Union, Literal
from fastmcp import FastMCP
from .help_tools import HelpSystem

from database_operations_mcp.database_manager import (
    db_manager, 
    create_connector, 
    get_supported_databases,
    DatabaseConnector
)

logger = logging.getLogger(__name__)

# Type definitions for better type checking
class DatabaseInfo(TypedDict, total=False):
    """Type definition for database information dictionary."""
    name: str
    display_name: str
    category: str
    description: str
    default_port: int
    required_params: List[str]
    optional_params: List[str]
    supports_ssl: bool
    supports_ssh: bool

class ConnectionResult(TypedDict, total=False):
    """Type definition for connection operation results."""
    success: bool
    message: str
    connection_id: Optional[str]
    error: Optional[str]
    details: Optional[Dict[str, Any]]

def register_tools(mcp: FastMCP) -> None:
    """Register connection management tools with the MCP server.
    
    Args:
        mcp: The FastMCP instance to register tools with.
    """
    @mcp.tool()
    @HelpSystem.register_tool(category='connection')
    async def list_supported_databases() -> Dict[str, Any]:
        """List all supported database types with categories and descriptions.
        
        Returns:
            A dictionary containing:
            - success: Boolean indicating if the operation was successful
            - databases_by_category: Dictionary of databases grouped by category
            - total_supported: Total number of supported database types
            - categories: List of all available database categories
            - error: Error message if the operation failed
            
        Example:
            ```python
            {
                "success": True,
                "databases_by_category": {
                    "SQL": [
                        {
                            "name": "postgresql",
                            "display_name": "PostgreSQL",
                            "description": "Advanced open-source relational database",
                            "default_port": 5432,
                            "supports_ssl": True
                        }
                    ],
                    # ... other categories
                },
                "total_supported": 8,
                "categories": ["SQL", "NoSQL", "Vector"]
            }
            ```
        """
        try:
            databases: List[DatabaseInfo] = get_supported_databases()
            
            # Group by category for better organization
            categorized: Dict[str, List[DatabaseInfo]] = {}
            for db in databases:
                category = db["category"]
                if category not in categorized:
                    categorized[category] = []
                categorized[category].append(db)
            
            return {
                "success": True,
                "databases_by_category": categorized,
                "total_supported": len(databases),
                "categories": list(categorized.keys())
            }
        except Exception as e:
            logger.error(f"Error listing supported databases: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to list supported databases: {str(e)}",
                "databases_by_category": {},
                "total_supported": 0,
                "categories": []
            }

    @mcp.tool()
    def register_database_connection(
        connection_name: str,
        database_type: str,
        connection_config: Dict[str, Any],
        test_connection: bool = True
    ) -> Dict[str, Any]:
        """Register a new database connection with the connection manager.
        
        Args:
            connection_name: Unique identifier for this connection (alphanumeric + underscores)
            database_type: Type of database (e.g., 'postgresql', 'mongodb', 'sqlite')
            connection_config: Dictionary containing connection parameters such as:
                - host: Database server hostname or IP
                - port: Database server port
                - username: Authentication username
                - password: Authentication password
                - database: Database/schema name
                - ssl: Boolean or SSL configuration dictionary
                - Additional database-specific parameters
            test_connection: If True, verifies the connection before registration
            
        Returns:
            A dictionary containing:
            - success: Boolean indicating if the operation was successful
            - message: Status message
            - connection_name: The registered connection name
            - database_type: The database type
            - connection_id: Internal ID of the connection
            - error: Error message if the operation failed
            
        Example:
            ```python
            # Register a PostgreSQL connection
            result = register_database_connection(
                connection_name="my_postgres",
                database_type="postgresql",
                connection_config={
                    "host": "localhost",
                    "port": 5432,
                    "username": "user",
                    "password": "password",
                    "database": "mydb",
                    "sslmode": "prefer"
                }
            )
            ```
            
        Raises:
            ValueError: If any required parameters are missing or invalid
            ConnectionError: If the connection test fails (when test_connection=True)
        """
        try:
            # Input validation
            if not connection_name or not isinstance(connection_name, str):
                raise ValueError("Connection name is required and must be a non-empty string")
                
            if not connection_name.replace('_', '').isalnum():
                raise ValueError(
                    "Connection name must be alphanumeric (underscores allowed)"
                )
                
            if not database_type or not isinstance(database_type, str):
                raise ValueError("Database type is required and must be a string")
                
            if not connection_config or not isinstance(connection_config, dict):
                raise ValueError("Connection config is required and must be a dictionary")
                
            # Create the database connector
            connector = create_connector(database_type, connection_config)
            
            # Test the connection if requested
            if test_connection:
                test_result = connector.test_connection()
                if not test_result.get("success"):
                    error_msg = test_result.get("error", "Connection test failed")
                    logger.error(f"Connection test failed: {error_msg}")
                    return {
                        "success": False,
                        "error": error_msg,
                        "connection_name": connection_name,
                        "database_type": database_type,
                        "details": test_result.get("details", {})
                    }
            
            # Register the connection
            db_manager.register_connection(connection_name, connector)
            
            logger.info(f"Successfully registered connection: {connection_name} ({database_type})")
            return {
                "success": True,
                "message": f"Successfully registered connection: {connection_name}",
                "connection_name": connection_name,
                "database_type": database_type,
                "connection_id": id(connector)
            }
            
        except ValueError as e:
            logger.error(f"Validation error in register_database_connection: {e}")
            return {
                "success": False,
                "error": f"Invalid parameters: {str(e)}",
                "connection_name": connection_name,
                "database_type": database_type
            }
        except Exception as e:
            logger.error(
                f"Error registering connection {connection_name}: {e}", 
                exc_info=True
            )
            return {
                "success": False,
                "error": f"Failed to register connection: {str(e)}",
                "connection_name": connection_name,
                "database_type": database_type
            }

    @mcp.tool()
    def list_database_connections() -> Dict[str, Any]:
        """List all registered database connections with their current status.
        
        Returns:
            A dictionary containing:
            - success: Boolean indicating if the operation was successful
            - connections: Dictionary of connection names to their details
            - total_connections: Total number of registered connections
            - error: Error message if the operation failed
            
        The connection details for each connection include:
            - type: Database type (e.g., 'postgresql', 'mongodb')
            - status: Current connection status (connected, disconnected, error)
            - info: Additional connection information (host, port, etc.)
            - last_activity: Timestamp of last activity (if available)
            
        Example:
            ```python
            {
                "success": True,
                "connections": {
                    "production_db": {
                        "type": "postgresql",
                        "status": "connected",
                        "info": {
                            "host": "db.example.com",
                            "port": 5432,
                            "database": "production"
                        },
                        "last_activity": "2023-07-30T15:30:00Z"
                    }
                },
                "total_connections": 1
            }
            ```
        """
        try:
            connections = db_manager.list_connectors()
            
            return {
                "success": True,
                "connections": connections,
                "total_connections": len(connections)
            }
            
        except Exception as e:
            logger.error(f"Error listing database connections: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to list connections: {str(e)}",
                "connections": {},
                "total_connections": 0
            }

    @mcp.tool()
    def test_database_connection(connection_name: str) -> Dict[str, Any]:
        """Test connectivity for a specific database connection.
        
        This function verifies that the database connection is working by executing a simple
        test query or ping operation. It provides detailed diagnostics about the connection
        status and any potential issues.
        
        Args:
            connection_name: Name of the registered connection to test
            
        Returns:
            A dictionary containing:
            - success: Boolean indicating if the test was successful
            - connection_name: The name of the tested connection
            - test_result: Dictionary with test details including:
                - success: Boolean indicating if the test passed
                - latency: Connection latency in milliseconds (if available)
                - server_version: Database server version (if available)
                - error: Error message if the test failed
            - connection_info: Additional connection details
            - error: Error message if an exception occurred
            
        Example:
            ```python
            # Test a connection
            result = test_database_connection("production_db")
            
            # Success response
            {
                "success": True,
                "connection_name": "production_db",
                "test_result": {
                    "success": True,
                    "latency": 24.5,
                    "server_version": "PostgreSQL 14.5"
                },
                "connection_info": {
                    "type": "postgresql",
                    "host": "db.example.com",
                    "port": 5432,
                    "database": "mydb",
                    "status": "connected"
                }
            }
            
            # Error response
            {
                "success": False,
                "connection_name": "production_db",
                "test_result": {
                    "success": False,
                    "error": "Connection refused",
                    "details": "Connection to db.example.com:5432 failed: Connection refused"
                },
                "connection_info": {
                    "type": "postgresql",
                    "host": "db.example.com",
                    "port": 5432,
                    "status": "error"
                }
            }
            ```
        """
        try:
            if not connection_name or not isinstance(connection_name, str):
                raise ValueError("Connection name is required and must be a string")
                
            connector = db_manager.get_connector(connection_name)
            if not connector:
                return {
                    "success": False,
                    "connection_name": connection_name,
                    "error": f"Connection not found: {connection_name}",
                    "test_result": {
                        "success": False,
                        "error": "Connection not found"
                    }
                }
            
            # Get connection info before testing (in case test fails)
            connection_info = connector.get_connection_info()
            
            # Test the connection
            test_result = connector.test_connection()
            
            # Log the test result
            if test_result.get("success"):
                logger.info(f"Connection test successful for {connection_name}")
            else:
                logger.warning(
                    f"Connection test failed for {connection_name}: "
                    f"{test_result.get('error', 'Unknown error')}"
                )
            
            return {
                "success": True,
                "connection_name": connection_name,
                "test_result": test_result,
                "connection_info": connection_info
            }
            
        except Exception as e:
            logger.error(
                f"Error testing connection {connection_name}: {e}",
                exc_info=True
            )
            
            # Try to get partial connection info even if test failed
            connection_info = {}
            try:
                if 'connector' in locals():
                    connection_info = connector.get_connection_info()
            except Exception as info_error:
                logger.warning(
                    f"Failed to get connection info after test failure: {info_error}"
                )
            
            return {
                "success": False,
                "connection_name": connection_name,
                "error": f"Failed to test connection: {str(e)}",
                "test_result": {
                    "success": False,
                    "error": str(e)
                },
                "connection_info": connection_info
            }

    @mcp.tool()
    def test_all_database_connections(
        parallel: bool = True,
        timeout: Optional[float] = 10.0
    ) -> Dict[str, Any]:
        """Test connectivity for all registered database connections.
        
        This function tests all registered database connections and provides a summary
        of the results. It can test connections in parallel for better performance.
        
        Args:
            parallel: If True, test connections concurrently (faster). If False,
                    test connections sequentially (easier to debug).
            timeout: Maximum time in seconds to wait for all tests to complete.
                   If None, no timeout is enforced.
                   
        Returns:
            A dictionary containing:
            - success: Boolean indicating if all tests completed (not necessarily passed)
            - test_results: Dictionary mapping connection names to their test results
            - summary: Summary statistics about the test results
            - error: Error message if an exception occurred
            
            The test result for each connection includes:
            - success: Boolean indicating if the test passed
            - latency: Connection latency in milliseconds (if available)
            - server_version: Database server version (if available)
            - error: Error message if the test failed
            - timestamp: When the test was performed
            
        Example:
            ```python
            # Test all connections in parallel with a 10-second timeout
            result = test_all_database_connections(parallel=True, timeout=10.0)
            
            # Example response
            {
                "success": True,
                "test_results": {
                    "production_db": {
                        "success": True,
                        "latency": 24.5,
                        "server_version": "PostgreSQL 14.5",
                        "timestamp": "2023-07-30T15:30:00Z"
                    },
                    "analytics_db": {
                        "success": False,
                        "error": "Connection timeout",
                        "timestamp": "2023-07-30T15:30:02Z"
                    }
                },
                "summary": {
                    "total_connections": 2,
                    "successful": 1,
                    "failed": 1,
                    "success_rate": "50.0%",
                    "execution_time": 2.1
                }
            }
            
            # Error response
            {
                "success": False,
                "error": "Timeout while testing connections",
                "test_results": {
                    # Partial results if any tests completed
                },
                "summary": {
                    "total_connections": 2,
                    "tested": 1,
                    "pending": 1,
                    "successful": 0,
                    "failed": 1
                }
            }
            ```
        """
        from time import time
        
        start_time = time()
        
        try:
            # Validate parameters
            if timeout is not None and (not isinstance(timeout, (int, float)) or timeout <= 0):
                raise ValueError("Timeout must be a positive number or None")
                
            logger.info(f"Testing all database connections (parallel={parallel}, timeout={timeout}s)")
            
            # Get all connections
            connections = db_manager.list_connectors()
            connection_names = list(connections.keys())
            
            if not connection_names:
                logger.info("No database connections found to test")
                return {
                    "success": True,
                    "test_results": {},
                    "summary": {
                        "total_connections": 0,
                        "successful": 0,
                        "failed": 0,
                        "success_rate": "0%",
                        "execution_time": time() - start_time
                    }
                }
            
            # Test connections
            test_results = {}
            
            if parallel:
                # Import here to avoid circular imports
                import asyncio
                from concurrent.futures import ThreadPoolExecutor, as_completed
                
                # Create a thread pool for parallel testing
                with ThreadPoolExecutor(max_workers=min(10, len(connection_names))) as executor:
                    # Start all tests
                    future_to_name = {
                        executor.submit(
                            db_manager.test_connection, 
                            name
                        ): name for name in connection_names
                    }
                    
                    # Process results as they complete
                    for future in as_completed(future_to_name, timeout=timeout):
                        name = future_to_name[future]
                        try:
                            test_results[name] = future.result()
                        except Exception as e:
                            logger.error(f"Error testing connection {name}: {e}")
                            test_results[name] = {
                                "success": False,
                                "error": str(e),
                                "timestamp": time().isoformat()
                            }
                            
            else:
                # Test connections sequentially
                for name in connection_names:
                    if timeout is not None and (time() - start_time) > timeout:
                        logger.warning(f"Timeout reached while testing {name}")
                        test_results[name] = {
                            "success": False,
                            "error": "Test timed out",
                            "timestamp": time().isoformat()
                        }
                        break
                        
                    try:
                        test_results[name] = db_manager.test_connection(name)
                        test_results[name]["timestamp"] = time().isoformat()
                    except Exception as e:
                        logger.error(f"Error testing connection {name}: {e}")
                        test_results[name] = {
                            "success": False,
                            "error": str(e),
                            "timestamp": time().isoformat()
                        }
            
            # Generate summary
            total = len(test_results)
            successful = sum(1 for r in test_results.values() if r.get("success", False))
            failed = total - successful
            success_rate = (successful / total * 100) if total > 0 else 0.0
            
            execution_time = time() - start_time
            
            summary = {
                "total_connections": total,
                "successful": successful,
                "failed": failed,
                "success_rate": f"{success_rate:.1f}%",
                "execution_time": round(execution_time, 3)  # Round to milliseconds
            }
            
            logger.info(
                f"Completed testing {total} connections: "
                f"{successful} successful, {failed} failed "
                f"(took {execution_time:.2f}s)"
            )
            
            return {
                "success": True,
                "test_results": test_results,
                "summary": summary
            }
            
        except asyncio.TimeoutError:
            logger.error("Timeout while testing all connections")
            return {
                "success": False,
                "error": "Timeout while testing connections",
                "test_results": test_results,
                "summary": {
                    "total_connections": len(connection_names),
                    "tested": len(test_results),
                    "pending": len(connection_names) - len(test_results),
                    "successful": sum(1 for r in test_results.values() if r.get("success", False)),
                    "failed": len(test_results) - sum(1 for r in test_results.values() if r.get("success", False))
                }
            }
            
        except Exception as e:
            logger.error(f"Error testing all connections: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to test connections: {str(e)}",
                "test_results": test_results if 'test_results' in locals() else {},
                "summary": {
                    "total_connections": len(connection_names) if 'connection_names' in locals() else 0,
                    "tested": len(test_results) if 'test_results' in locals() else 0,
                    "error": str(e)
                }
            }

