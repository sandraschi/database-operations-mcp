# Database connection management portmanteau tool.
# Consolidates all database connection operations into a single interface.

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import time
from typing import Any

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.database_manager import (
    create_connector,
    db_manager,
    get_supported_databases,
)
from database_operations_mcp.tools.help_tools import HelpSystem

logger = logging.getLogger(__name__)


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def db_connection(
    operation: str,
    connection_name: str | None = None,
    database_type: str | None = None,
    connection_config: dict[str, Any] | None = None,
    connection_params: dict[str, Any] | None = None,
    test_connection: bool = True,
    timeout: float | None = None,
    parallel: bool = False,
    auto_reconnect: bool = False,
    preferences: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Database connection management portmanteau tool.

    Comprehensive database connection lifecycle management consolidating ALL connection
    operations into a single interface. Supports connection registration, testing, persistence,
    and preferences management across SQL, NoSQL, and Vector databases.

    Prerequisites:
        - For register/init operations: Valid database credentials and network access
        - For test operations: Database must be running and accessible
        - For restore operations: Previously saved connections in persistent storage

    Operations:
        - list_supported: List all supported database types with categories and descriptions
        - register: Register a new database connection with the connection manager
        - init: Initialize new database connection and register it (alias for register, legacy)
        - list: List all registered database connections with their current status
        - test: Test connectivity for a specific database connection
        - test_all: Test connectivity for all registered database connections
        - close: Close database connection and release resources
        - get_info: Get detailed information about registered database connection
        - restore: Restore saved database connections from persistent storage
        - set_active: Set the active/default database connection
        - get_active: Get the active/default database connection name
        - get_preferences: Get user preferences from persistent storage
        - set_preferences: Set user preferences in persistent storage

    Parameters:
        operation (str, REQUIRED): The operation to perform
            Valid values: 'list_supported', 'register', 'init', 'list', 'test', 'test_all',
                         'close', 'get_info', 'restore', 'set_active', 'get_active',
                         'get_preferences', 'set_preferences'
            Example: 'register', 'test', 'list'

        connection_name (str, OPTIONAL): Unique identifier for the connection
            Format: Alphanumeric characters and underscores only
            Validation: Must match pattern r'^[a-zA-Z0-9_]+$'
            Range: 1-50 characters
            Required for: register, init, test, close, get_info, set_active
            Example: 'prod_db', 'analytics_warehouse', 'local_sqlite'

        database_type (str, OPTIONAL): Type of database to connect to
            Valid values: 'sqlite', 'postgresql', 'mysql', 'mongodb', 'chromadb', 'redis', 'duckdb'
            Required for: register, init
            Example: 'postgresql', 'sqlite', 'mongodb'

        connection_config (dict, OPTIONAL): Dictionary containing connection parameters
            Format: Database-specific configuration dictionary
            Required for: register, init operations
            SQLite example: {'database': '/path/to/database.db'}
            PostgreSQL example: {'host': 'localhost', 'port': 5432, 'user': 'admin',
                                 'password': 'secret', 'database': 'mydb', 'sslmode': 'prefer'}
            MongoDB example: {'host': 'localhost', 'port': 27017, 'database': 'myapp'}
            Validation: Must be non-empty dictionary with required keys for database type

        connection_params (dict, OPTIONAL): Alias for connection_config (legacy compatibility)
            Format: Same as connection_config
            Required for: init operation (if connection_config not provided)
            Example: {'database': 'app.db'}

        test_connection (bool, OPTIONAL): Verify connection before registration
            Default: True
            Behavior: If True, validates connection succeeds before registering
            Use False: Only when you want to register without testing (advanced)

        timeout (float, OPTIONAL): Timeout in seconds for connection tests
            Format: Positive floating point number
            Range: 1.0 - 300.0 seconds
            Default: 10.0 seconds
            Used for: test, test_all operations
            Example: 30.0

        parallel (bool, OPTIONAL): Test connections concurrently (test_all operation)
            Default: False
            Behavior: If True, tests all connections simultaneously for better performance
            Warning: May cause high network/CPU usage with many connections

        auto_reconnect (bool, OPTIONAL): Automatically reconnect to saved connections
            Default: False
            Behavior: If True, restores and connects to all saved connections (restore operation)
            DEV MODE ONLY: Requires ENABLE_PASSWORD_STORAGE=1 environment variable

        preferences (dict, OPTIONAL): User preference key-value pairs
            Format: Dictionary of preference names to values
            Required for: set_preferences operation
            Common keys: 'default_query_limit', 'default_page_size', 'show_metadata', 'sort_order'
            Example: {'default_query_limit': 50, 'default_page_size': 20, 'show_metadata': True}

    Returns:
        Dictionary containing operation-specific results:
            - status: 'success' or 'error'
            - operation: Echo of operation performed
            - For list_supported: databases_by_category, total_supported, categories
            - For register/init: connection_name, database_type, connection_id, message
            - For list: connections (dict of connection details), total_connections
            - For test/test_all: test_result, connection_info, latency, server_version
            - For close: message, connection_name
            - For get_info: connection_name, db_type, is_connected, params, connection_info
            - For restore: saved_connections, reconnected (list), message
            - For set_active/get_active: active_connection, message
            - For get_preferences: preferences dictionary
            - For set_preferences: status, message
            - error: Error message if status is 'error'
            - available_operations: List of valid operations (on invalid operation)

    Usage:
        This tool is the foundation for all database operations. Use it to establish
        connections before performing queries, schema operations, or data manipulation.

        Common scenarios:
        - Setup: Register database connections at startup or first use
        - Testing: Verify connections are healthy before operations
        - Management: List and monitor active database connections
        - Persistence: Save connections to survive Claude Desktop restarts
        - Configuration: Set user preferences for database operations

        Best practices:
        - Always test connections after registration
        - Use descriptive connection names (e.g., 'prod_postgres' not 'db1')
        - Close connections when done to free resources
        - Use persistent storage for frequently-used connections
        - Set timeouts appropriately for network databases

    Examples:
        List all supported database types:
            result = await db_connection(operation='list_supported')
            # Returns: {
            #     'status': 'success',
            #     'databases_by_category': {
            #         'SQL': [{'name': 'postgresql', 'display_name': 'PostgreSQL', ...}],
            #         'NoSQL': [{'name': 'mongodb', ...}]
            #     },
            #     'total_supported': 8,
            #     'categories': ['SQL', 'NoSQL', 'Vector']
            # }

        Register PostgreSQL connection with test:
            result = await db_connection(
                operation='register',
                connection_name='production_db',
                database_type='postgresql',
                connection_config={
                    'host': 'db.example.com',
                    'port': 5432,
                    'user': 'admin',
                    'password': 'secret',
                    'database': 'production',
                    'sslmode': 'prefer'
                },
                test_connection=True
            )
            # Returns: {
            #     'status': 'success',
            #     'connection_name': 'production_db',
            #     'database_type': 'postgresql',
            #     'message': 'Successfully connected to postgresql database'
            # }

        Initialize SQLite database (legacy):
            result = await db_connection(
                operation='init',
                connection_name='local_db',
                database_type='sqlite',
                connection_params={'database': 'C:/data/app.db'}
            )
            # Returns: Connection established and registered

        List all registered connections:
            result = await db_connection(operation='list')
            # Returns: {
            #     'status': 'success',
            #     'connections': {
            #         'production_db': {'type': 'postgresql', 'status': 'connected', ...},
            #         'local_db': {'type': 'sqlite', 'status': 'connected', ...}
            #     },
            #     'total_connections': 2
            # }

        Test specific connection:
            result = await db_connection(
                operation='test',
                connection_name='production_db',
                timeout=30.0
            )
            # Returns: {
            #     'status': 'success',
            #     'connection_name': 'production_db',
            #     'test_result': {
            #         'success': True,
            #         'latency': 24.5,
            #         'server_version': 'PostgreSQL 14.5'
            #     }
            # }

        Test all connections in parallel:
            result = await db_connection(
                operation='test_all',
                parallel=True,
                timeout=10.0
            )
            # Returns: {
            #     'status': 'success',
            #     'test_results': {
            #         'production_db': {'success': True, 'latency': 24.5, ...},
            #         'local_db': {'success': True, 'latency': 0.5, ...}
            #     },
            #     'summary': {'total': 2, 'successful': 2, 'failed': 0}
            # }

        Close connection:
            result = await db_connection(
                operation='close',
                connection_name='temp_db'
            )
            # Returns: {
            #     'status': 'success',
            #     'message': 'Closed connection: temp_db',
            #     'connection_name': 'temp_db'
            # }

        Get connection information:
            result = await db_connection(
                operation='get_info',
                connection_name='production_db'
            )
            # Returns: {
            #     'status': 'success',
            #     'connection_name': 'production_db',
            #     'db_type': 'postgresql',
            #     'is_connected': True,
            #     'params': {'host': 'db.example.com', 'port': 5432, ...}
            # }

        Restore saved connections:
            result = await db_connection(
                operation='restore',
                auto_reconnect=True
            )
            # Returns: {
            #     'status': 'success',
            #     'saved_connections': [...],
            #     'reconnected': ['prod_db', 'local_db'],
            #     'message': 'Restored 2 connections'
            # }

        Set active connection:
            result = await db_connection(
                operation='set_active',
                connection_name='production_db'
            )
            # Returns: {'status': 'success', 'message': 'Set active connection: production_db'}

        Get user preferences:
            result = await db_connection(operation='get_preferences')
            # Returns: {
            #     'status': 'success',
            #     'preferences': {
            #         'default_query_limit': 50,
            #         'default_page_size': 20,
            #         'show_metadata': True
            #     }
            # }

        Set user preferences:
            result = await db_connection(
                operation='set_preferences',
                preferences={
                    'default_query_limit': 100,
                    'default_page_size': 25,
                    'show_metadata': False
                }
            )
            # Returns: {'status': 'success', 'message': 'Preferences updated'}

        Error handling - invalid operation:
            result = await db_connection(operation='invalid_op')
            # Returns: {
            #     'success': False,
            #     'error': 'Unknown operation: invalid_op',
            #     'available_operations': ['list_supported', 'register', ...]
            # }

        Error handling - connection not found:
            result = await db_connection(
                operation='test',
                connection_name='nonexistent'
            )
            # Returns: {
            #     'status': 'error',
            #     'error': 'No such connection: nonexistent',
            #     'message': 'Use db_connection(operation='list') to see available connections'
            # }

    Errors:
        Common errors and solutions:
        - 'Unknown operation: {operation}':
            Cause: Invalid operation name provided
            Fix: Use one of the valid operations listed in 'available_operations'
            Example: Check spelling, use 'list' not 'list_all'

        - 'No such connection: {connection_name}':
            Cause: Connection name doesn't exist
            Fix: Use db_connection(operation='list') to see available connections
            Workaround: Register connection first with 'register' operation

        - 'Connection failed: {error}':
            Cause: Database connection test failed
            Fix: Verify database is running, credentials are correct, network is accessible
            Workaround: Set test_connection=False to register without testing

        - 'Connection config is required and must be a dictionary':
            Cause: Missing or invalid connection_config parameter
            Fix: Provide connection_config dict with required keys for database type
            Example: For SQLite: {'database': '/path/to.db'}

        - 'Timeout while testing connections':
            Cause: Connection test exceeded timeout duration
            Fix: Increase timeout parameter, check network latency, verify database is responsive
            Workaround: Test connections individually with higher timeout

    See Also:
        - db_operations: Execute queries on registered connections
        - db_schema: Inspect database schema on connections
        - db_management: Database administration operations
    """

    if operation == "list_supported":
        return await _list_supported_databases()
    elif operation == "register":
        return await _register_database_connection(
            connection_name, database_type, connection_config, test_connection
        )
    elif operation == "init":
        # Legacy init_database operation
        # Use connection_params if provided, otherwise connection_config
        config = connection_params or connection_config
        return await _init_database(database_type, config, connection_name)
    elif operation == "list":
        return await _list_database_connections()
    elif operation == "test":
        return await _test_database_connection(connection_name)
    elif operation == "test_all":
        return await _test_all_database_connections(timeout, parallel)
    elif operation == "close":
        return await _close_connection(connection_name)
    elif operation == "get_info":
        return await _get_connection_info(connection_name)
    elif operation == "restore":
        return await _restore_saved_connections(auto_reconnect)
    elif operation == "set_active":
        return await _set_active_connection(connection_name)
    elif operation == "get_active":
        return await _get_active_connection()
    elif operation == "get_preferences":
        return await _get_user_preferences()
    elif operation == "set_preferences":
        return await _set_user_preferences(preferences)
    else:
        return {
            "success": False,
            "operation": operation,
            "message": f"I don't recognize the '{operation}' operation. Here are the available database connection operations you can use.",
            "error": f"Unknown operation: {operation}",
            "error_code": "INVALID_OPERATION",
            "available_operations": [
                "list_supported",
                "register",
                "init",
                "list",
                "test",
                "test_all",
                "close",
                "get_info",
                "restore",
                "set_active",
                "get_active",
                "get_preferences",
                "set_preferences",
            ],
            "suggestions": [
                "Use 'list_supported' to see all available database types",
                "Use 'register' to add a new database connection",
                "Use 'list' to see your existing connections"
            ]
        }


async def _list_supported_databases() -> dict[str, Any]:
    """List all supported database types with categories and descriptions."""
    try:
        databases = get_supported_databases()

        # Group by category for better organization
        categorized = {}
        for db in databases:
            category = db["category"]
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(db)

        return {
            "success": True,
            "operation": "list_supported",
            "message": f"I found {len(databases)} supported database types across {len(categorized)} categories. You can connect to SQL databases (PostgreSQL, MySQL, SQLite), NoSQL databases (MongoDB), vector databases (ChromaDB), and more.",
            "databases_by_category": categorized,
            "total_supported": len(databases),
            "categories": list(categorized.keys()),
            "next_steps": [
                "Use 'register' operation to connect to one of these databases",
                "Use 'init' operation for legacy connection setup",
                "Use 'list' to see your existing connections"
            ]
        }
    except Exception as e:
        logger.error(f"Error listing supported databases: {e}", exc_info=True)
        return {
            "success": False,
            "operation": "list_supported",
            "message": f"Sorry, I encountered an error while listing supported databases. The error was: {str(e)}. Please try again or check the system logs.",
            "error": f"Failed to list supported databases: {str(e)}",
            "error_code": "LIST_DATABASES_FAILED",
            "databases_by_category": {},
            "total_supported": 0,
            "categories": [],
            "suggestions": [
                "Try the operation again",
                "Check system logs for more details",
                "Verify the database operations service is running"
            ]
        }


async def _register_database_connection(
    connection_name: str,
    database_type: str,
    connection_config: dict[str, Any],
    test_connection: bool,
) -> dict[str, Any]:
    """Register a new database connection with the connection manager."""
    try:
        # Input validation
        if not connection_name or not isinstance(connection_name, str):
            raise ValueError("Connection name is required and must be a non-empty string")

        if not database_type or not isinstance(database_type, str):
            raise ValueError("Database type is required and must be a non-empty string")

        if not connection_config or not isinstance(connection_config, dict):
            raise ValueError("Connection config is required and must be a dictionary")

        # Create connector
        connector = create_connector(database_type, connection_config)

        # Test connection if requested
        if test_connection:
            test_result = await connector.test_connection()
            if not test_result["success"]:
                raise ConnectionError(
                    f"Connection test failed: {test_result.get('error', 'Unknown error')}"
                )

        # Register with manager
        db_manager.register_connector(connection_name, connector)

        return {
            "success": True,
            "message": f"Database connection '{connection_name}' registered successfully",
            "connection_name": connection_name,
            "database_type": database_type,
            "test_passed": test_connection,
        }

    except Exception as e:
        logger.error(f"Error registering database connection: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to register database connection: {str(e)}",
            "connection_name": connection_name,
            "database_type": database_type,
        }


async def _list_database_connections() -> dict[str, Any]:
    """List all registered database connections with their current status."""
    try:
        connections = db_manager.list_connectors()

        return {"success": True, "connections": connections, "total_connections": len(connections)}

    except Exception as e:
        logger.error(f"Error listing database connections: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to list database connections: {str(e)}",
            "connections": {},
            "total_connections": 0,
        }


async def _test_database_connection(connection_name: str) -> dict[str, Any]:
    """Test connectivity for a specific database connection."""
    try:
        if not connection_name or not isinstance(connection_name, str):
            raise ValueError("Connection name is required and must be a string")

        connector = db_manager.get_connector(connection_name)
        if not connector:
            raise ValueError(f"Connection '{connection_name}' not found")

        start_time = time()
        test_result = await connector.test_connection()
        latency = time() - start_time

        return {
            "success": True,
            "connection_name": connection_name,
            "test_result": {
                "success": test_result.get("success", False),
                "latency": round(latency * 1000, 2),  # Convert to milliseconds
                "error": test_result.get("error") if not test_result.get("success") else None,
            },
        }

    except Exception as e:
        logger.error(f"Error testing database connection: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to test database connection: {str(e)}",
            "connection_name": connection_name,
        }


async def _test_all_database_connections(timeout: float | None, parallel: bool) -> dict[str, Any]:
    """Test connectivity for all registered database connections."""
    start_time = time()

    try:
        # Validate parameters
        if timeout is not None and (not isinstance(timeout, (int, float)) or timeout <= 0):
            raise ValueError("Timeout must be a positive number")

        connections = db_manager.list_connectors()
        connection_names = list(connections.keys())

        if not connection_names:
            return {
                "success": True,
                "message": "No connections to test",
                "test_results": {},
                "summary": {
                    "total_connections": 0,
                    "successful": 0,
                    "failed": 0,
                    "success_rate": "0%",
                    "execution_time": round(time() - start_time, 3),
                },
            }

        test_results = {}

        if parallel:
            # Test connections in parallel
            with ThreadPoolExecutor(max_workers=min(len(connection_names), 10)) as executor:
                future_to_name = {
                    executor.submit(_test_single_connection, name, timeout): name
                    for name in connection_names
                }

                for future in as_completed(future_to_name, timeout=timeout):
                    name = future_to_name[future]
                    try:
                        result = future.result()
                        test_results[name] = result
                    except Exception as e:
                        test_results[name] = {"success": False, "error": str(e)}
        else:
            # Test connections sequentially
            for name in connection_names:
                test_results[name] = await _test_single_connection(name, timeout)

        # Calculate summary
        total = len(test_results)
        successful = sum(1 for r in test_results.values() if r.get("success", False))
        failed = total - successful
        success_rate = (successful / total * 100) if total > 0 else 0
        execution_time = time() - start_time

        return {
            "success": True,
            "test_results": test_results,
            "summary": {
                "total_connections": total,
                "successful": successful,
                "failed": failed,
                "success_rate": f"{success_rate:.1f}%",
                "execution_time": round(execution_time, 3),
            },
        }

    except Exception as e:
        logger.error(f"Error testing all database connections: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to test all database connections: {str(e)}",
            "test_results": {},
            "summary": {
                "total_connections": len(connection_names) if "connection_names" in locals() else 0,
                "tested": len(test_results) if "test_results" in locals() else 0,
                "error": str(e),
            },
        }


async def _test_single_connection(connection_name: str, timeout: float | None) -> dict[str, Any]:
    """Test a single connection (helper function)."""
    try:
        connector = db_manager.get_connector(connection_name)
        if not connector:
            return {"success": False, "error": f"Connection '{connection_name}' not found"}

        start_time = time()
        test_result = await connector.test_connection()
        latency = time() - start_time

        return {
            "success": test_result.get("success", False),
            "latency": round(latency * 1000, 2),
            "error": test_result.get("error") if not test_result.get("success") else None,
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


async def _init_database(
    db_type: str | None, connection_params: dict[str, Any] | None, connection_name: str | None
) -> dict[str, Any]:
    """Initialize new database connection and register it (legacy operation)."""
    try:
        if not db_type:
            raise ValueError("database_type is required")
        if not connection_params:
            raise ValueError("connection_params is required")
        if not connection_name:
            connection_name = "default"

        from database_operations_mcp.services.database.connectors import (
            ChromaDBConnector,
            MongoDBConnector,
            PostgreSQLConnector,
            SQLiteConnector,
        )

        connectors = {
            "sqlite": SQLiteConnector,
            "postgresql": PostgreSQLConnector,
            "mongodb": MongoDBConnector,
            "chromadb": ChromaDBConnector,
        }

        if db_type.lower() not in connectors:
            return {
                "status": "error",
                "message": f"Unsupported database type: {db_type}",
                "success": False,
            }

        # Create a new connection
        connector = connectors[db_type.lower()](**connection_params)
        await connector.connect()

        # Register with manager
        db_manager.register_connector(connection_name, connector)

        # Save connection config to persistent storage
        try:
            from database_operations_mcp.storage.persistence import get_storage

            storage = get_storage()
            if storage:
                await storage.save_connection(connection_name, db_type, connection_params)
                logger.info(f"Saved connection '{connection_name}' to persistent storage")
        except Exception as storage_error:
            logger.debug(f"Could not save to storage: {storage_error}")

        return {
            "status": "success",
            "message": f"Successfully connected to {db_type} database",
            "connection_name": connection_name,
            "db_type": db_type,
            "success": True,
        }
    except Exception as e:
        logger.error(f"Error initializing {db_type} database: {e}")
        return {
            "status": "error",
            "message": f"Failed to initialize database: {str(e)}",
            "success": False,
        }


async def _close_connection(connection_name: str | None) -> dict[str, Any]:
    """Close database connection and release resources."""
    if not connection_name:
        return {"status": "error", "message": "connection_name is required", "success": False}

    try:
        connector = db_manager.get_connector(connection_name)
        if not connector:
            return {
                "status": "error",
                "message": f"No such connection: {connection_name}",
                "success": False,
            }

        # Close the connection
        if hasattr(connector, "close"):
            await connector.close()

        # Remove from manager
        db_manager.unregister_connector(connection_name)

        # Remove from persistent storage
        try:
            from database_operations_mcp.storage.persistence import get_storage

            storage = get_storage()
            if storage:
                await storage.delete_connection(connection_name)
        except Exception:
            pass  # Graceful degradation

        return {
            "status": "success",
            "message": f"Closed connection: {connection_name}",
            "success": True,
        }
    except Exception as e:
        logger.error(f"Error closing connection: {e}")
        return {
            "status": "error",
            "message": f"Error closing connection: {str(e)}",
            "success": False,
        }


async def _get_connection_info(connection_name: str | None) -> dict[str, Any]:
    """Get detailed information about registered database connection."""
    if not connection_name:
        return {"status": "error", "message": "connection_name is required", "success": False}

    try:
        connector = db_manager.get_connector(connection_name)
        if not connector:
            return {
                "status": "error",
                "message": f"No such connection: {connection_name}",
                "success": False,
            }

        # Get connection info
        info = (
            await connector.get_connection_info()
            if hasattr(connector, "get_connection_info")
            else {}
        )
        is_connected = (
            await connector.is_connected() if hasattr(connector, "is_connected") else False
        )

        return {
            "status": "success",
            "connection_name": connection_name,
            "db_type": connector.database_type.value
            if hasattr(connector, "database_type")
            else "unknown",
            "is_connected": is_connected,
            "connection_info": info,
            "success": True,
        }
    except Exception as e:
        logger.error(f"Error getting connection info: {e}")
        return {
            "status": "error",
            "message": f"Error getting connection info: {str(e)}",
            "connection_name": connection_name,
            "success": False,
        }


async def _restore_saved_connections(auto_reconnect: bool) -> dict[str, Any]:
    """Restore saved database connections from persistent storage."""
    try:
        from database_operations_mcp.storage.persistence import get_storage

        storage = get_storage()
        if not storage:
            return {
                "status": "error",
                "message": "Persistent storage not available",
                "saved_connections": {},
                "reconnected": [],
                "success": False,
            }

        saved_connections = await storage.get_all_connections()
        reconnected = []

        # DEV MODE: Auto-reconnect if passwords are saved
        if auto_reconnect:
            import os

            enable_password_storage = os.getenv("ENABLE_PASSWORD_STORAGE", "0").lower() in (
                "1",
                "true",
                "yes",
            )

            if enable_password_storage:
                for conn_name, conn_info in saved_connections.items():
                    try:
                        params = conn_info.get("params", {})
                        if "password" in params:
                            # Use register operation to reconnect
                            result = await _register_database_connection(
                                conn_name, conn_info["type"], params, test_connection=True
                            )
                            if result.get("success"):
                                reconnected.append(conn_name)
                                logger.info(f"Auto-reconnected to {conn_name} (dev mode)")
                    except Exception as e:
                        logger.error(f"Failed to auto-reconnect {conn_name}: {e}")
            else:
                logger.warning(
                    "auto_reconnect=True but ENABLE_PASSWORD_STORAGE not set. "
                    "Passwords not saved, cannot auto-reconnect."
                )

        return {
            "status": "success",
            "saved_connections": saved_connections,
            "reconnected": reconnected,
            "message": (
                f"Found {len(saved_connections)} saved connections, reconnected {len(reconnected)}"
            ),
            "success": True,
        }
    except Exception as e:
        logger.error(f"Error restoring saved connections: {e}")
        return {
            "status": "error",
            "message": f"Failed to restore: {str(e)}",
            "saved_connections": {},
            "reconnected": [],
            "success": False,
        }


async def _set_active_connection(connection_name: str | None) -> dict[str, Any]:
    """Set the active/default database connection."""
    if not connection_name:
        return {"status": "error", "message": "connection_name is required", "success": False}

    try:
        from database_operations_mcp.storage.persistence import get_storage

        storage = get_storage()
        if not storage:
            return {
                "status": "error",
                "message": "Persistent storage not available",
                "success": False,
            }

        await storage.set_active_connection(connection_name)
        return {
            "status": "success",
            "message": f"Set active connection: {connection_name}",
            "success": True,
        }
    except Exception as e:
        logger.error(f"Error setting active connection: {e}")
        return {
            "status": "error",
            "message": f"Failed to set active connection: {str(e)}",
            "success": False,
        }


async def _get_active_connection() -> dict[str, Any]:
    """Get the active/default database connection name."""
    try:
        from database_operations_mcp.storage.persistence import get_storage

        storage = get_storage()
        if not storage:
            return {
                "status": "error",
                "message": "Persistent storage not available",
                "active_connection": None,
                "success": False,
            }

        active_conn = await storage.get_active_connection()
        return {"status": "success", "active_connection": active_conn, "success": True}
    except Exception as e:
        logger.error(f"Error getting active connection: {e}")
        return {
            "status": "error",
            "message": f"Failed to get active connection: {str(e)}",
            "active_connection": None,
            "success": False,
        }


async def _get_user_preferences() -> dict[str, Any]:
    """Get user preferences from persistent storage."""
    try:
        from database_operations_mcp.storage.persistence import get_storage

        storage = get_storage()
        if not storage:
            return {
                "status": "error",
                "message": "Persistent storage not available",
                "preferences": {},
                "success": False,
            }

        prefs = await storage.get_user_preferences()
        return {"status": "success", "preferences": prefs, "success": True}
    except Exception as e:
        logger.error(f"Error getting preferences: {e}")
        return {
            "status": "error",
            "message": f"Failed to get preferences: {str(e)}",
            "preferences": {},
            "success": False,
        }


async def _set_user_preferences(preferences: dict[str, Any] | None) -> dict[str, Any]:
    """Set user preferences in persistent storage."""
    if not preferences:
        return {"status": "error", "message": "preferences is required", "success": False}

    try:
        from database_operations_mcp.storage.persistence import get_storage

        storage = get_storage()
        if not storage:
            return {
                "status": "error",
                "message": "Persistent storage not available",
                "success": False,
            }

        await storage.set_user_preferences(preferences)
        return {"status": "success", "message": "Preferences saved", "success": True}
    except Exception as e:
        logger.error(f"Error setting preferences: {e}")
        return {
            "status": "error",
            "message": f"Failed to set preferences: {str(e)}",
            "success": False,
        }
