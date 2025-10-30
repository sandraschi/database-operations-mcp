# Database management portmanteau tool.
# Consolidates database initialization, health checks, and management operations.

import logging
from typing import Any

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.database_manager import db_manager
from database_operations_mcp.tools.help_tools import HelpSystem

logger = logging.getLogger(__name__)


@mcp.tool()
@HelpSystem.register_tool(category="database")
async def db_management(
    operation: str,
    connection_name: str | None = None,
    database_type: str | None = None,
    connection_config: dict[str, Any] | None = None,
    test_connection: bool = True,
    include_metrics: bool = True,
    vacuum_mode: str = "full",
) -> dict[str, Any]:
    """Database management portmanteau tool.

    This tool consolidates all database management operations into a single interface,
    providing unified access to database lifecycle management functionality.

    Operations:
    - init_database: Initialize a new database connection
    - list_connections: List all registered database connections
    - close_connection: Close a specific database connection
    - test_connection: Test connectivity for a specific connection
    - get_connection_info: Get detailed information about a connection
    - database_health_check: Perform comprehensive health check on database
    - get_database_metrics: Get performance and usage metrics
    - vacuum_database: Perform database maintenance (vacuum/optimize)
    - disconnect_database: Disconnect from database and clean up resources

    Args:
        operation: The operation to perform (required)
        connection_name: Name of the database connection
        database_type: Type of database (for initialization)
        connection_config: Configuration for database connection
        test_connection: Whether to test connection during initialization
        include_metrics: Include detailed metrics in health checks
        vacuum_mode: Vacuum mode (full, analyze, reindex)

    Returns:
        Dictionary with operation results and management information

    Examples:
        Initialize database:
        db_management(operation='init_database', connection_name='prod_db',
                     database_type='postgresql', connection_config={'host': 'localhost'})

        List connections:
        db_management(operation='list_connections')

        Test connection:
        db_management(operation='test_connection', connection_name='prod_db')

        Health check:
        db_management(operation='database_health_check', connection_name='prod_db',
                     include_metrics=True)

        Get metrics:
        db_management(operation='get_database_metrics', connection_name='prod_db')

        Vacuum database:
        db_management(operation='vacuum_database', connection_name='prod_db',
                     vacuum_mode='full')

        Close connection:
        db_management(operation='close_connection', connection_name='prod_db')
    """

    if operation == "init_database":
        return await _init_database(
            connection_name, database_type, connection_config, test_connection
        )
    elif operation == "list_connections":
        return await _list_connections()
    elif operation == "close_connection":
        return await _close_connection(connection_name)
    elif operation == "test_connection":
        return await _test_connection(connection_name)
    elif operation == "get_connection_info":
        return await _get_connection_info(connection_name)
    elif operation == "database_health_check":
        return await _database_health_check(connection_name, include_metrics)
    elif operation == "get_database_metrics":
        return await _get_database_metrics(connection_name)
    elif operation == "vacuum_database":
        return await _vacuum_database(connection_name, vacuum_mode)
    elif operation == "disconnect_database":
        return await _disconnect_database(connection_name)
    else:
        return {
            "success": False,
            "error": f"Unknown operation: {operation}",
            "available_operations": [
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
        }


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
                raise ConnectionError(
                    f"Connection test failed: {test_result.get('error', 'Unknown error')}"
                )

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
            "error": f"Failed to initialize database: {str(e)}",
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
            "error": f"Failed to list connections: {str(e)}",
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
            "error": f"Failed to close connection: {str(e)}",
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
            "error": f"Failed to test connection: {str(e)}",
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
            "error": f"Failed to get connection info: {str(e)}",
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
            "error": f"Failed to perform health check: {str(e)}",
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
            "error": f"Failed to get database metrics: {str(e)}",
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
            "error": f"Failed to vacuum database: {str(e)}",
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
            "error": f"Failed to disconnect database: {str(e)}",
            "connection_name": connection_name,
        }



