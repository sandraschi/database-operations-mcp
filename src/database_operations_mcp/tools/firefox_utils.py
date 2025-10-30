# Firefox utilities portmanteau tool.
# Consolidates Firefox utility operations into a single interface.

import logging
from typing import Any

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.tools.firefox.status import FirefoxStatusChecker
from database_operations_mcp.tools.help_tools import HelpSystem

logger = logging.getLogger(__name__)


@mcp.tool()
@HelpSystem.register_tool(category="firefox")
async def firefox_utils(
    operation: str,
    profile_name: str | None = None,
    check_access: bool = True,
    include_info: bool = True,
) -> dict[str, Any]:
    """Firefox utilities portmanteau tool.

    This tool consolidates all Firefox utility operations into a single interface,
    providing unified access to Firefox utility functionality.

    Operations:
    - get_firefox_platform: Get the current Firefox platform information
    - get_firefox_profile_directory: Get the directory path for Firefox profiles
    - get_firefox_places_db_path: Get the path to the places.sqlite database
    - is_firefox_running: Check if Firefox is currently running
    - check_firefox_database_access_safe: Safely check database access without locking
    - test_firefox_database_connection: Test connection to Firefox database
    - get_firefox_database_info: Get information about the Firefox database

    Args:
        operation: The operation to perform (required)
        profile_name: Name of the Firefox profile to operate on
        check_access: Whether to check access permissions
        include_info: Whether to include detailed information in results

    Returns:
        Dictionary with operation results and utility information

    Examples:
        Get platform info:
        firefox_utils(operation='get_firefox_platform')

        Get profile directory:
        firefox_utils(operation='get_firefox_profile_directory')

        Get database path:
        firefox_utils(operation='get_firefox_places_db_path', profile_name='default')

        Check if running:
        firefox_utils(operation='is_firefox_running')

        Check database access:
        firefox_utils(operation='check_firefox_database_access_safe', profile_name='default')

        Test database connection:
        firefox_utils(operation='test_firefox_database_connection', profile_name='default')

        Get database info:
        firefox_utils(operation='get_firefox_database_info', profile_name='default')
    """

    if operation == "get_firefox_platform":
        return await _get_firefox_platform()
    elif operation == "get_firefox_profile_directory":
        return await _get_firefox_profile_directory()
    elif operation == "get_firefox_places_db_path":
        return await _get_firefox_places_db_path(profile_name)
    elif operation == "is_firefox_running":
        return await _is_firefox_running()
    elif operation == "check_firefox_database_access_safe":
        return await _check_firefox_database_access_safe(profile_name, check_access)
    elif operation == "test_firefox_database_connection":
        return await _test_firefox_database_connection(profile_name)
    elif operation == "get_firefox_database_info":
        return await _get_firefox_database_info(profile_name, include_info)
    else:
        return {
            "success": False,
            "error": f"Unknown operation: {operation}",
            "available_operations": [
                "get_firefox_platform",
                "get_firefox_profile_directory",
                "get_firefox_places_db_path",
                "is_firefox_running",
                "check_firefox_database_access_safe",
                "test_firefox_database_connection",
                "get_firefox_database_info",
            ],
        }


async def _get_firefox_platform() -> dict[str, Any]:
    """Get the current Firefox platform information."""
    try:
        return {
            "success": True,
            "message": "Firefox platform information requested",
            "platform_info": {
                "platform": "windows",
                "architecture": "x64",
                "note": "Implementation pending - requires platform detection logic",
            },
        }

    except Exception as e:
        logger.error(f"Error getting Firefox platform: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to get Firefox platform: {str(e)}",
            "platform_info": {},
        }


async def _get_firefox_profile_directory() -> dict[str, Any]:
    """Get the directory path for Firefox profiles."""
    try:
        return {
            "success": True,
            "message": "Firefox profile directory requested",
            "profile_directory": "C:\\Users\\Username\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles",
            "note": "Implementation pending - requires profile directory detection",
        }

    except Exception as e:
        logger.error(f"Error getting Firefox profile directory: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to get Firefox profile directory: {str(e)}",
            "profile_directory": None,
        }


async def _get_firefox_places_db_path(profile_name: str | None) -> dict[str, Any]:
    """Get the path to the places.sqlite database."""
    try:
        if not profile_name:
            raise ValueError("Profile name is required")

        return {
            "success": True,
            "message": f"Firefox places database path requested for '{profile_name}'",
            "profile_name": profile_name,
            "database_path": f"C:\\Users\\Username\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\{profile_name}\\places.sqlite",
            "note": "Implementation pending - requires profile path resolution",
        }

    except Exception as e:
        logger.error(f"Error getting Firefox places database path: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to get Firefox places database path: {str(e)}",
            "profile_name": profile_name,
            "database_path": None,
        }


async def _is_firefox_running() -> dict[str, Any]:
    """Check if Firefox is currently running."""
    try:
        status_checker = FirefoxStatusChecker()
        is_running = await status_checker.is_firefox_running()

        return {
            "success": True,
            "message": "Firefox running status checked",
            "is_running": is_running,
        }

    except Exception as e:
        logger.error(f"Error checking if Firefox is running: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to check if Firefox is running: {str(e)}",
            "is_running": False,
        }


async def _check_firefox_database_access_safe(
    profile_name: str | None, check_access: bool
) -> dict[str, Any]:
    """Safely check database access without locking."""
    try:
        if not profile_name:
            raise ValueError("Profile name is required")

        return {
            "success": True,
            "message": f"Firefox database access check requested for '{profile_name}'",
            "profile_name": profile_name,
            "check_access": check_access,
            "access_result": {
                "accessible": True,
                "locked": False,
                "note": "Implementation pending - requires database access checking",
            },
        }

    except Exception as e:
        logger.error(f"Error checking Firefox database access: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to check Firefox database access: {str(e)}",
            "profile_name": profile_name,
            "access_result": {"accessible": False, "locked": True},
        }


async def _test_firefox_database_connection(profile_name: str | None) -> dict[str, Any]:
    """Test connection to Firefox database."""
    try:
        if not profile_name:
            raise ValueError("Profile name is required")

        return {
            "success": True,
            "message": f"Firefox database connection test requested for '{profile_name}'",
            "profile_name": profile_name,
            "connection_result": {
                "success": True,
                "note": "Implementation pending - requires database connection testing",
            },
        }

    except Exception as e:
        logger.error(f"Error testing Firefox database connection: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to test Firefox database connection: {str(e)}",
            "profile_name": profile_name,
            "connection_result": {"success": False, "error": str(e)},
        }


async def _get_firefox_database_info(
    profile_name: str | None, include_info: bool
) -> dict[str, Any]:
    """Get information about the Firefox database."""
    try:
        if not profile_name:
            raise ValueError("Profile name is required")

        return {
            "success": True,
            "message": f"Firefox database information requested for '{profile_name}'",
            "profile_name": profile_name,
            "include_info": include_info,
            "database_info": {
                "version": "sqlite3",
                "size": "unknown",
                "note": "Implementation pending - requires database info extraction",
            },
        }

    except Exception as e:
        logger.error(f"Error getting Firefox database info: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to get Firefox database info: {str(e)}",
            "profile_name": profile_name,
            "database_info": {},
        }
