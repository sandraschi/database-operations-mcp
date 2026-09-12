# Database Connection Management Tools.
#
# DEPRECATED: This module is deprecated. Use db_connection portmanteau tool instead.
#
# All operations have been consolidated into db_connection():
# - list_supported_databases() → db_connection(operation='list_supported')
# - register_database_connection() → db_connection(operation='register')
# - list_database_connections() → db_connection(operation='list')
# - test_database_connection() → db_connection(operation='test')
# - test_all_database_connections() → db_connection(operation='test_all')
#
# This module is kept for backwards compatibility but tools are no longer registered.

import asyncio
import logging
from datetime import UTC, datetime
from time import time
from typing import Any, TypedDict

# NOTE: @mcp.tool decorators removed - functionality moved to db_connection portmanteau
# Import kept for backwards compatibility in case code references these functions
from database_operations_mcp.database_manager import (
    create_connector,
    db_manager,
    get_supported_databases,
)

logger = logging.getLogger(__name__)


def _utcnow() -> str:
    """Current UTC time as an ISO-8601 string (validates timestamps without float.isoformat bugs)."""
    return datetime.now(UTC).isoformat()


# Type definitions for better type checking
class DatabaseInfo(TypedDict, total=False):
    """Type definition for database information dictionary."""

    name: str
    display_name: str
    category: str
    description: str
    default_port: int
    required_params: list[str]
    optional_params: list[str]
    supports_ssl: bool
    supports_ssh: bool


class ConnectionResult(TypedDict, total=False):
    """Type definition for connection operation results."""

    success: bool
    message: str
    connection_id: str | None
    error: str | None
    details: dict[str, Any] | None


# DEPRECATED: Use db_connection(operation='list_supported') instead
async def list_supported_databases() -> dict[str, Any]:
    """List all supported database types with categories and descriptions.

    ## Return Format
    Returns success plus databases_by_category, total_supported, and categories.

    ## Examples
    List everything:
        result = await list_supported_databases()
    """
    try:
        databases: list[dict[str, Any]] = get_supported_databases()

        # Group by category for better organization
        categorized: dict[str, list[dict[str, Any]]] = {}
        for db in databases:
            category = str(db.get("category", "Other"))
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
            "error": f"Failed to list supported databases: {e!s}",
            "databases_by_category": {},
            "total_supported": 0,
            "categories": [],
        }


# DEPRECATED: Use db_connection(operation='register') instead
async def register_database_connection(
    connection_name: str | None,
    database_type: str | None,
    connection_config: dict[str, Any] | None,
    test_connection: bool = True,
) -> dict[str, Any]:
    """Register a new database connection with the connection manager.

    ## Return Format
    Returns success plus connection_name/database_type/connection_id, or an error dict.

    ## Examples
    Register a PostgreSQL connection:
        result = await register_database_connection(
            connection_name="my_postgres",
            database_type="postgresql",
            connection_config={"host": "localhost", "port": 5432, "database": "mydb"},
        )
    """
    try:
        # Input validation
        if not connection_name or not isinstance(connection_name, str):
            raise ValueError("Connection name is required and must be a non-empty string")

        if not connection_name.replace("_", "").isalnum():
            raise ValueError("Connection name must be alphanumeric (underscores allowed)")

        if not database_type or not isinstance(database_type, str):
            raise ValueError("Database type is required and must be a string")

        if not connection_config or not isinstance(connection_config, dict):
            raise ValueError("Connection config is required and must be a dictionary")

        # Create the database connector
        connector = create_connector(database_type, connection_config)
        if not connector:
            raise ValueError(f"Unsupported database type or invalid config for '{database_type}'")

        # Test the connection if requested
        if test_connection:
            test_result = await connector.test_connection()
            if not test_result.get("success"):
                error_msg = test_result.get("error", "Connection test failed")
                logger.error(f"Connection test failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "connection_name": connection_name,
                    "database_type": database_type,
                    "details": test_result.get("details", {}),
                }

        # Register the connection
        db_manager.register_connection(connection_name, connector)

        logger.info(f"Successfully registered connection: {connection_name} ({database_type})")
        return {
            "success": True,
            "message": f"Successfully registered connection: {connection_name}",
            "connection_name": connection_name,
            "database_type": database_type,
            "connection_id": id(connector),
        }

    except ValueError as e:
        logger.error(f"Validation error in register_database_connection: {e}")
        return {
            "success": False,
            "error": f"Invalid parameters: {e!s}",
            "connection_name": connection_name,
            "database_type": database_type,
        }
    except Exception as e:
        logger.error(f"Error registering connection {connection_name}: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to register connection: {e!s}",
            "connection_name": connection_name,
            "database_type": database_type,
        }


# DEPRECATED: Use db_connection(operation='list') instead
def list_database_connections() -> dict[str, Any]:
    """List all registered database connections with their current status.

    ## Return Format
    Returns success plus connections and total_connections, or an error dict.

    ## Examples
    List connections:
        result = list_database_connections()
    """
    try:
        connections = db_manager.list_connectors()

        return {"success": True, "connections": connections, "total_connections": len(connections)}

    except Exception as e:
        logger.error(f"Error listing database connections: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to list connections: {e!s}",
            "connections": {},
            "total_connections": 0,
        }


# DEPRECATED: Use db_connection(operation='test') instead
async def test_database_connection(connection_name: str | None) -> dict[str, Any]:
    """Test connectivity for a specific database connection.

    ## Return Format
    Returns success plus test_result/connection_info, or an error dict.

    ## Examples
    Test a connection:
        result = await test_database_connection("production_db")
    """
    connector = None
    try:
        if not connection_name or not isinstance(connection_name, str):
            raise ValueError("Connection name is required and must be a string")

        connector = db_manager.get_connector(connection_name)
        if not connector:
            return {
                "success": False,
                "connection_name": connection_name,
                "error": f"Connection not found: {connection_name}",
                "test_result": {"success": False, "error": "Connection not found"},
            }

        # Get connection info before testing (in case test fails)
        connection_info = await connector.get_connection_info()

        # Test the connection
        test_result = await connector.test_connection()

        # Log the test result
        if test_result.get("success"):
            logger.info(f"Connection test successful for {connection_name}")
        else:
            logger.warning(f"Connection test failed for {connection_name}: {test_result.get('error', 'Unknown error')}")

        return {
            "success": True,
            "connection_name": connection_name,
            "test_result": test_result,
            "connection_info": connection_info,
        }

    except Exception as e:
        logger.error(f"Error testing connection {connection_name}: {e}", exc_info=True)

        # Try to get partial connection info even if test failed
        connection_info: dict[str, Any] = {}
        try:
            if connector is not None:
                connection_info = await connector.get_connection_info()
        except Exception as info_error:
            logger.warning(f"Failed to get connection info after test failure: {info_error}")

        return {
            "success": False,
            "connection_name": connection_name,
            "error": f"Failed to test connection: {e!s}",
            "test_result": {"success": False, "error": str(e)},
            "connection_info": connection_info,
        }


# DEPRECATED: Use db_connection(operation='test_all') instead
async def test_all_database_connections(parallel: bool = True, timeout: float | None = 10.0) -> dict[str, Any]:
    """Test connectivity for all registered database connections.

    This function tests all registered database connections and provides a summary
    of the results. It can test connections in parallel for better performance.

    ## Return Format
    Returns success plus per-connection test_results and a summary, or an error dict.

    ## Examples
    Test everything with a 10-second budget:
        result = await test_all_database_connections(parallel=True, timeout=10.0)
    """
    start_time = time()
    connection_names: list[str] = []
    test_results: dict[str, Any] = {}

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
                    "execution_time": time() - start_time,
                },
            }

        async def _test_one(name: str) -> tuple[str, dict[str, Any]]:
            if timeout is not None and (time() - start_time) > timeout:
                logger.warning(f"Timeout reached while testing {name}")
                return name, {"success": False, "error": "Test timed out", "timestamp": _utcnow()}
            try:
                res = await asyncio.wait_for(db_manager.test_connection(name), timeout)
                res["timestamp"] = _utcnow()
                return name, res
            except TimeoutError:
                logger.warning(f"Timeout reached while testing {name}")
                return name, {"success": False, "error": "Test timed out", "timestamp": _utcnow()}
            except Exception as e:
                logger.error(f"Error testing connection {name}: {e}")
                return name, {"success": False, "error": str(e), "timestamp": _utcnow()}

        if parallel:
            # Test connections concurrently
            results = await asyncio.gather(*(_test_one(name) for name in connection_names))
            test_results = dict(results)

        else:
            # Test connections sequentially
            for name in connection_names:
                key, res = await _test_one(name)
                test_results[key] = res
                if res.get("error") == "Test timed out":
                    break

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
            "execution_time": round(execution_time, 3),  # Round to milliseconds
        }

        logger.info(
            f"Completed testing {total} connections: "
            f"{successful} successful, {failed} failed "
            f"(took {execution_time:.2f}s)"
        )

        return {"success": True, "test_results": test_results, "summary": summary}

    except TimeoutError:
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
                "failed": len(test_results) - sum(1 for r in test_results.values() if r.get("success", False)),
            },
        }

    except Exception as e:
        logger.error(f"Error testing all connections: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to test connections: {e!s}",
            "test_results": test_results,
            "summary": {
                "total_connections": len(connection_names),
                "tested": len(test_results),
                "error": str(e),
            },
        }
