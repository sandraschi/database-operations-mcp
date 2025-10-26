# Database connection management portmanteau tool.
# Consolidates all database connection operations into a single interface.

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import time
from typing import Any, Dict, Optional

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
    connection_name: Optional[str] = None,
    database_type: Optional[str] = None,
    connection_config: Optional[Dict[str, Any]] = None,
    test_connection: bool = True,
    timeout: Optional[float] = None,
    parallel: bool = False,
) -> Dict[str, Any]:
    """Database connection management portmanteau tool.

    This tool consolidates all database connection operations into a single interface,
    providing unified access to connection management functionality.

    Operations:
    - list_supported: List all supported database types with categories and descriptions
    - register: Register a new database connection with the connection manager
    - list: List all registered database connections with their current status
    - test: Test connectivity for a specific database connection
    - test_all: Test connectivity for all registered database connections

    Args:
        operation: The operation to perform (required)
        connection_name: Unique identifier for the connection (alphanumeric + underscores)
        database_type: Type of database (e.g., 'postgresql', 'mongodb', 'sqlite')
        connection_config: Dictionary containing connection parameters
        test_connection: If True, verifies the connection before registration
        timeout: Timeout in seconds for connection tests
        parallel: If True, test connections in parallel for better performance

    Returns:
        Dictionary with operation results and status information

    Examples:
        List supported databases:
        db_connection(operation='list_supported')

        Register PostgreSQL connection:
        db_connection(operation='register', connection_name='prod_db',
                     database_type='postgresql', connection_config={'host': 'localhost'})

        List all connections:
        db_connection(operation='list')

        Test specific connection:
        db_connection(operation='test', connection_name='prod_db')

        Test all connections:
        db_connection(operation='test_all', parallel=True, timeout=10.0)
    """

    if operation == "list_supported":
        return await _list_supported_databases()
    elif operation == "register":
        return await _register_database_connection(
            connection_name, database_type, connection_config, test_connection
        )
    elif operation == "list":
        return await _list_database_connections()
    elif operation == "test":
        return await _test_database_connection(connection_name)
    elif operation == "test_all":
        return await _test_all_database_connections(timeout, parallel)
    else:
        return {
            "success": False,
            "error": f"Unknown operation: {operation}",
            "available_operations": ["list_supported", "register", "list", "test", "test_all"],
        }


async def _list_supported_databases() -> Dict[str, Any]:
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
            "databases_by_category": categorized,
            "total_supported": len(databases),
            "categories": list(categorized.keys()),
        }
    except Exception as e:
        logger.error(f"Error listing supported databases: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to list supported databases: {str(e)}",
            "databases_by_category": {},
            "total_supported": 0,
            "categories": [],
        }


async def _register_database_connection(
    connection_name: str,
    database_type: str,
    connection_config: Dict[str, Any],
    test_connection: bool,
) -> Dict[str, Any]:
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


async def _list_database_connections() -> Dict[str, Any]:
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


async def _test_database_connection(connection_name: str) -> Dict[str, Any]:
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


async def _test_all_database_connections(
    timeout: Optional[float], parallel: bool
) -> Dict[str, Any]:
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


async def _test_single_connection(connection_name: str, timeout: Optional[float]) -> Dict[str, Any]:
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
