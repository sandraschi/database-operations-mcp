# Database management portmanteau tool.
# Consolidates database initialization, health checks, and management operations.

import logging
from typing import Any

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.database_manager import db_manager
from database_operations_mcp.operation_types import DbManagementOperation
from database_operations_mcp.tool_responses import unknown_operation_response
from database_operations_mcp.tools.help_tools import HelpSystem

logger = logging.getLogger(__name__)


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def db_management(
    operation: DbManagementOperation,
    connection_name: str | None = None,
    database_type: str | None = None,
    connection_config: dict[str, Any] | None = None,
    test_connection: bool = True,
    include_metrics: bool = True,
    vacuum_mode: str = "full",
) -> dict[str, Any]:
    """Database management portmanteau tool.

    Comprehensive database administration and lifecycle management consolidating ALL
    management operations into a single interface. Supports initialization, health checks,
    performance monitoring, maintenance, and connection lifecycle across SQL, NoSQL,
    and Vector databases.

    Prerequisites:
        - For init_database: Valid database credentials and network access
        - For health/metrics operations: Database must be running and accessible
        - For vacuum operations: Database must support VACUUM (SQLite, PostgreSQL)
        - For all operations: Connection must exist (except init_database)

    Operations:
        - init_database: Initialize a new database connection and register it
        - list_connections: List all registered database connections with status
        - close_connection: Close specific database connection and release resources
        - test_connection: Test connectivity and responsiveness for specific connection
        - get_connection_info: Get detailed information about registered connection
        - database_health_check: Perform comprehensive health check on database
        - get_database_metrics: Get performance and usage metrics
        - vacuum_database: Perform database maintenance (vacuum/optimize)
        - disconnect_database: Disconnect from database and clean up resources

    Parameters:
        operation (str, REQUIRED): The operation to perform
            Valid values: 'init_database', 'list_connections', 'close_connection',
                         'test_connection', 'get_connection_info',
                         'database_health_check', 'get_database_metrics',
                         'vacuum_database', 'disconnect_database'
            Example: 'database_health_check', 'get_database_metrics', 'vacuum_database'

        connection_name (str, OPTIONAL): Name of the database connection
            Format: Registered connection name (from db_connection)
            Required for: All operations except list_connections, init_database
            Validation: Must be previously registered (except init)
            Example: 'prod_db', 'analytics_warehouse', 'local_sqlite'

        database_type (str, OPTIONAL): Type of database to connect to
            Valid values: 'sqlite', 'postgresql', 'mysql', 'mongodb', 'chromadb', 'redis', 'duckdb'
            Required for: init_database operation
            Example: 'postgresql', 'sqlite', 'mongodb'

        connection_config (dict, OPTIONAL): Configuration for database connection
            Format: Database-specific configuration dictionary
            Required for: init_database operation
            SQLite example: {'database': '/path/to/database.db'}
            PostgreSQL example: {
                'host': 'localhost',
                'port': 5432,
                'user': 'admin',
                'password': 'secret',
                'database': 'mydb'
            }
            Validation: Must be non-empty dictionary with required keys

        test_connection (bool, OPTIONAL): Test connection during initialization
            Default: True
            Behavior: If True, validates connection succeeds before registering
            Used for: init_database operation
            Warning: If False, invalid connections may be registered

        include_metrics (bool, OPTIONAL): Include detailed metrics in results
            Default: True
            Behavior: Adds performance counters, usage stats, resource consumption
            Used for: database_health_check operation
            Impact: May increase response time slightly

        vacuum_mode (str, OPTIONAL): Database vacuum/optimization mode
            Valid values: 'full', 'analyze', 'reindex'
            Default: 'full'
            Used for: vacuum_database operation
            'full': Complete vacuum (reclaims space, defragments)
            'analyze': Update query optimizer statistics only
            'reindex': Rebuild all indexes for better performance
            Warning: 'full' may lock database and take significant time

    Returns:
        Dictionary containing operation-specific results:
            - success: Boolean indicating operation success
            - operation: Echo of operation performed
            - For init_database: connection_name, database_type, message, test_passed
            - For list_connections: connections (dict), total_connections
            - For close_connection: message, connection_name
            - For test_connection: test_result (dict), connection_name
            - For get_connection_info: connection_info (dict), connection_name
            - For database_health_check: health_status, health_details, metrics (if included)
            - For get_database_metrics: metrics (dict), connection_name
            - For vacuum_database: vacuum_result (dict), vacuum_mode
            - For disconnect_database: message, connection_name
            - error: Error message if success is False
            - available_operations: List of valid operations (on invalid operation)

    Usage:
        This tool provides database administration and maintenance capabilities. Use it to
        monitor database health, optimize performance, and manage connection lifecycle.

        Common scenarios:
        - Initialization: Set up new database connections with validation
        - Health monitoring: Regular health checks to detect issues early
        - Performance tuning: Monitor metrics and optimize with vacuum operations
        - Maintenance: Clean up and optimize databases during maintenance windows
        - Resource management: Close connections when done to free resources

        Best practices:
        - Run health checks regularly to catch issues early
        - Use vacuum operations during low-traffic periods
        - Monitor metrics to understand database usage patterns
        - Close connections when done to prevent resource leaks
        - Test connections after initialization to verify setup

    Examples:
        Initialize database connection:
            result = await db_management(
                operation='init_database',
                connection_name='production_db',
                database_type='postgresql',
                connection_config={
                    'host': 'db.example.com',
                    'port': 5432,
                    'user': 'admin',
                    'password': 'secret',
                    'database': 'production'
                },
                test_connection=True
            )
            # Returns: {
            #     'success': True,
            #     'message': "Database connection 'production_db' initialized successfully",
            #     'connection_name': 'production_db',
            #     'database_type': 'postgresql',
            #     'test_passed': True
            # }

        List all connections:
            result = await db_management(operation='list_connections')
            # Returns: {
            #     'success': True,
            #     'connections': {
            #         'production_db': {'type': 'postgresql', 'status': 'connected'},
            #         'local_db': {'type': 'sqlite', 'status': 'connected'}
            #     },
            #     'total_connections': 2
            # }

        Perform health check:
            result = await db_management(
                operation='database_health_check',
                connection_name='production_db',
                include_metrics=True
            )

        Vacuum database (full optimization):
            result = await db_management(
                operation='vacuum_database',
                connection_name='production_db',
                vacuum_mode='full'
            )

    Errors:
        Common errors and solutions:
        - 'Connection not found: {connection_name}':
            Cause: Connection name doesn't exist or not registered
            Fix: Use db_management(operation='list_connections') to see available connections
            Workaround: Register connection first with db_connection(operation='register')

        - 'Vacuum operation failed: {error}':
            Cause: Database locked, insufficient permissions, or unsupported operation
            Fix: Ensure database is not in use, check permissions, verify database supports VACUUM
            Workaround: Use vacuum_mode='analyze' instead of 'full', retry when database is idle

    See Also:
        - db_connection: Register and manage database connections (preferred for new connections)
        - db_operations: Execute queries on managed connections
        - db_schema: Inspect database structure
    """

    if operation == "init_database":
        result = await _init_database(connection_name, database_type, connection_config, test_connection)
    elif operation == "list_connections":
        result = await _list_connections()
    elif operation == "close_connection":
        result = await _close_connection(connection_name)
    elif operation == "test_connection":
        result = await _test_connection(connection_name)
    elif operation == "get_connection_info":
        result = await _get_connection_info(connection_name)
    elif operation == "database_health_check":
        result = await _database_health_check(connection_name, include_metrics)
    elif operation == "get_database_metrics":
        result = await _get_database_metrics(connection_name)
    elif operation == "vacuum_database":
        result = await _vacuum_database(connection_name, vacuum_mode)
    elif operation == "disconnect_database":
        result = await _disconnect_database(connection_name)
    else:
        return unknown_operation_response(
            operation,
            [
                "init_database",
                "list_connections",
                "close_connection",
                "test_connection",
                "get_connection_info",
                "database_health_check",
                "get_database_metrics",
                "vacuum_database",
                "disconnect_database",
            ],
        )

    # Standardize result with a conversational summary
    summary = result.get("message", "")
    if not summary:
        if result.get("success"):
            if operation == "list_connections":
                count = result.get("total_connections", 0)
                summary = f"Found {count} registered database connections."
            elif operation == "database_health_check":
                status = result.get("health_status", "unknown")
                summary = f"Database health check for '{connection_name}' completed with status: {status}."
            elif operation == "vacuum_database":
                mode = result.get("vacuum_mode", "unknown")
                summary = f"Successfully performed '{mode}' vacuum/optimization on '{connection_name}'."
            else:
                summary = f"Successfully completed '{operation}' operation on '{connection_name}'."
        else:
            summary = f"Error: {result.get('error', 'Unknown database management error')}"

    return {"content": summary, "data": result}


async def _init_database(
    connection_name: str,
    database_type: str,
    connection_config: dict[str, Any],
    test_connection: bool,
) -> dict[str, Any]:
    """Initialize a new database connection."""
    try:
        if not connection_name:
            raise ValueError("Connection name is required")
        if not database_type:
            raise ValueError("Database type is required")
        if not connection_config:
            raise ValueError("Connection config is required")

        # Check if connection already exists
        if db_manager.get_connector(connection_name):
            return {
                "success": False,
                "error": f"Connection '{connection_name}' already exists",
                "connection_name": connection_name,
            }

        # Create and register connector
        from database_operations_mcp.database_manager import create_connector

        connector = create_connector(database_type, connection_config)

        if test_connection:
            test_result = await connector.test_connection()
            if not test_result["success"]:
                raise ConnectionError(f"Connection test failed: {test_result.get('error', 'Unknown error')}")

        db_manager.register_connector(connection_name, connector)

        return {
            "success": True,
            "message": f"Database connection '{connection_name}' initialized successfully",
            "connection_name": connection_name,
            "database_type": database_type,
            "test_passed": test_connection,
        }

    except Exception as e:
        logger.error(f"Error initializing database: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to initialize database: {e!s}",
            "connection_name": connection_name,
            "database_type": database_type,
        }


async def _list_connections() -> dict[str, Any]:
    """List all registered database connections."""
    try:
        connections = db_manager.list_connectors()

        return {
            "success": True,
            "message": "Connections listed successfully",
            "connections": connections,
            "total_connections": len(connections),
        }

    except Exception as e:
        logger.error(f"Error listing connections: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to list connections: {e!s}",
            "connections": {},
            "total_connections": 0,
        }


async def _close_connection(connection_name: str) -> dict[str, Any]:
    """Close a specific database connection."""
    try:
        if not connection_name:
            raise ValueError("Connection name is required")

        connector = db_manager.get_connector(connection_name)
        if not connector:
            raise ValueError(f"Connection '{connection_name}' not found")

        await connector.close()
        db_manager.unregister_connector(connection_name)

        return {
            "success": True,
            "message": f"Connection '{connection_name}' closed successfully",
            "connection_name": connection_name,
        }

    except Exception as e:
        logger.error(f"Error closing connection: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to close connection: {e!s}",
            "connection_name": connection_name,
        }


async def _test_connection(connection_name: str) -> dict[str, Any]:
    """Test connectivity for a specific connection."""
    try:
        if not connection_name:
            raise ValueError("Connection name is required")

        connector = db_manager.get_connector(connection_name)
        if not connector:
            raise ValueError(f"Connection '{connection_name}' not found")

        test_result = await connector.test_connection()

        return {
            "success": True,
            "message": f"Connection test completed for '{connection_name}'",
            "connection_name": connection_name,
            "test_result": test_result,
        }

    except Exception as e:
        logger.error(f"Error testing connection: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to test connection: {e!s}",
            "connection_name": connection_name,
        }


async def _get_connection_info(connection_name: str) -> dict[str, Any]:
    """Get detailed information about a connection."""
    try:
        if not connection_name:
            raise ValueError("Connection name is required")

        connector = db_manager.get_connector(connection_name)
        if not connector:
            raise ValueError(f"Connection '{connection_name}' not found")

        info = await connector.get_connection_info()

        return {
            "success": True,
            "message": f"Connection info retrieved for '{connection_name}'",
            "connection_name": connection_name,
            "connection_info": info,
        }

    except Exception as e:
        logger.error(f"Error getting connection info: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to get connection info: {e!s}",
            "connection_name": connection_name,
        }


async def _database_health_check(connection_name: str, include_metrics: bool) -> dict[str, Any]:
    """Perform comprehensive health check on database."""
    try:
        if not connection_name:
            raise ValueError("Connection name is required")

        connector = db_manager.get_connector(connection_name)
        if not connector:
            raise ValueError(f"Connection '{connection_name}' not found")

        health_result = await connector.health_check(include_metrics)

        return {
            "success": True,
            "message": f"Health check completed for '{connection_name}'",
            "connection_name": connection_name,
            "health_status": health_result.get("status", "unknown"),
            "health_details": health_result,
            "metrics": health_result.get("metrics", {}) if include_metrics else {},
        }

    except Exception as e:
        logger.error(f"Error performing health check: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to perform health check: {e!s}",
            "connection_name": connection_name,
            "health_status": "error",
        }


async def _get_database_metrics(connection_name: str) -> dict[str, Any]:
    """Get performance and usage metrics."""
    try:
        if not connection_name:
            raise ValueError("Connection name is required")

        connector = db_manager.get_connector(connection_name)
        if not connector:
            raise ValueError(f"Connection '{connection_name}' not found")

        metrics = await connector.get_metrics()

        return {
            "success": True,
            "message": f"Metrics retrieved for '{connection_name}'",
            "connection_name": connection_name,
            "metrics": metrics,
        }

    except Exception as e:
        logger.error(f"Error getting database metrics: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to get database metrics: {e!s}",
            "connection_name": connection_name,
            "metrics": {},
        }


async def _vacuum_database(connection_name: str, vacuum_mode: str) -> dict[str, Any]:
    """Perform database maintenance (vacuum/optimize)."""
    try:
        if not connection_name:
            raise ValueError("Connection name is required")

        connector = db_manager.get_connector(connection_name)
        if not connector:
            raise ValueError(f"Connection '{connection_name}' not found")

        vacuum_result = await connector.vacuum(vacuum_mode)

        return {
            "success": True,
            "message": f"Database vacuum completed for '{connection_name}'",
            "connection_name": connection_name,
            "vacuum_mode": vacuum_mode,
            "vacuum_result": vacuum_result,
        }

    except Exception as e:
        logger.error(f"Error vacuuming database: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to vacuum database: {e!s}",
            "connection_name": connection_name,
            "vacuum_mode": vacuum_mode,
        }


async def _disconnect_database(connection_name: str) -> dict[str, Any]:
    """Disconnect from database and clean up resources."""
    try:
        if not connection_name:
            raise ValueError("Connection name is required")

        connector = db_manager.get_connector(connection_name)
        if not connector:
            raise ValueError(f"Connection '{connection_name}' not found")

        await connector.disconnect()
        db_manager.unregister_connector(connection_name)

        return {
            "success": True,
            "message": f"Database disconnected successfully for '{connection_name}'",
            "connection_name": connection_name,
        }

    except Exception as e:
        logger.error(f"Error disconnecting database: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to disconnect database: {e!s}",
            "connection_name": connection_name,
        }
