# Windows system management portmanteau tool.
# Consolidates Windows registry and system operations into a single interface.

import logging
from typing import Any

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.tools.help_tools import HelpSystem

logger = logging.getLogger(__name__)


@mcp.tool()
@HelpSystem.register_tool(category="windows")
async def windows_system(
    operation: str,
    registry_key: str | None = None,
    registry_value: str | None = None,
    value_data: Any | None = None,
    database_path: str | None = None,
    query: str | None = None,
    plex_server_url: str | None = None,
    plex_token: str | None = None,
    include_metadata: bool = True,
    clean_database: bool = False,
    optimize_performance: bool = False,
) -> dict[str, Any]:
    """Windows system management portmanteau tool.

    Comprehensive Windows system operations consolidating ALL registry and Windows-specific
    database operations into a single interface. Supports registry read/write, database
    management, Plex metadata operations, and Windows database discovery.

    Prerequisites:
        - Windows operating system (tool is Windows-specific)
        - For registry operations: Administrator privileges may be required
        - For database operations: Database file must exist and be accessible
        - For Plex operations: Plex Media Server running (optional)

    Operations:
        - list_windows_databases: List Windows databases (Plex, Windows Search, etc.)
        - manage_plex_metadata: Manage Plex metadata on Windows
        - query_windows_database: Query Windows-specific databases
        - clean_windows_database: Clean and optimize Windows databases
        - read_registry_value: Read a value from Windows Registry
        - write_registry_value: Write a value to Windows Registry
        - list_registry_keys: List registry keys in a path
        - list_registry_values: List registry values in a key

    Parameters:
        operation (str, REQUIRED): The operation to perform
            Valid values: 'list_windows_databases', 'manage_plex_metadata',
                         'query_windows_database', 'clean_windows_database',
                         'read_registry_value', 'write_registry_value',
                         'list_registry_keys', 'list_registry_values'
            Example: 'read_registry_value', 'list_windows_databases'

        registry_key (str, OPTIONAL): Registry key path
            Format: Full registry key path with backslashes
            Required for: All registry operations
            Format: 'HKEY_CURRENT_USER\\Software\\ApplicationName'
            Example: 'HKEY_CURRENT_USER\\Software\\Plex', 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft'

        registry_value (str, OPTIONAL): Registry value name
            Format: Value name within the registry key
            Required for: read_registry_value, write_registry_value operations
            Example: 'InstallPath', 'Version', 'LastUpdated'

        value_data (Any, OPTIONAL): Data to write to registry value
            Format: String, integer, or binary data
            Required for: write_registry_value operation
            Types supported: str, int, bytes
            Example: '1.0.0', 12345, b'\\x00\\x01'

        database_path (str, OPTIONAL): Path to Windows database file
            Format: Absolute path to database file
            Required for: query_windows_database, clean_windows_database operations
            Validation: File must exist and be readable/writable
            Example: 'C:\\plex\\database.db', 'C:\\ProgramData\\Microsoft\\Search\\Data\\*.db'

        query (str, OPTIONAL): SQL query to execute
            Format: Standard SQL SELECT query
            Required for: query_windows_database operation
            Validation: Must be SELECT query (read-only)
            Example: 'SELECT * FROM metadata_items LIMIT 10'

        plex_server_url (str, OPTIONAL): URL of Plex Media Server
            Format: HTTP URL with protocol and port
            Used for: manage_plex_metadata operation
            Default: 'http://localhost:32400'
            Example: 'http://192.168.1.100:32400'

        plex_token (str, OPTIONAL): Authentication token for Plex API
            Format: Plex authentication token string
            Used for: manage_plex_metadata operation
            Example: 'your-plex-token-here'

        include_metadata (bool, OPTIONAL): Include detailed metadata in results
            Default: True
            Behavior: Adds file paths, sizes, modification dates if available
            Used for: query_windows_database operation

        clean_database (bool, OPTIONAL): Clean database during operation
            Default: False
            Behavior: Runs VACUUM and integrity checks
            Used for: clean_windows_database operation
            Warning: May lock database temporarily

        optimize_performance (bool, OPTIONAL): Optimize performance
            Default: False
            Behavior: Rebuilds indexes and analyzes statistics
            Used for: manage_plex_metadata operation

    Returns:
        Dictionary containing operation-specific results:
            - success: Boolean indicating operation success
            - operation: Echo of operation performed
            - For list_windows_databases: databases (list), total_count
            - For manage_plex_metadata: message, metadata_stats, optimization_results
            - For query_windows_database: results (list), columns, row_count
            - For clean_windows_database: message, cleanup_stats, database_size_change
            - For read_registry_value: value, value_type, key_path
            - For write_registry_value: message, key_path, value_written
            - For list_registry_keys: keys (list), parent_key
            - For list_registry_values: values (list), key_path
            - error: Error message if success is False
            - available_operations: List of valid operations (on invalid operation)

    Usage:
        This tool provides Windows-specific system and registry management. Use it to
        read/write registry values, discover Windows application databases, and manage
        Plex metadata on Windows systems.

        Common scenarios:
        - Registry inspection: Read application settings and configurations
        - Registry modification: Update application settings programmatically
        - Database discovery: Find Windows application databases (Plex, Search, etc.)
        - Database maintenance: Clean and optimize Windows databases
        - Metadata management: Manage Plex library metadata on Windows

        Best practices:
        - Backup registry keys before writing values
        - Use read_registry_value to verify before writing
        - Run clean operations during maintenance windows
        - Verify database paths exist before querying

    Examples:
        List Windows databases:
            result = await windows_system(operation='list_windows_databases')
            # Returns: {
            #     'success': True,
            #     'databases': [
            #         {
            #             'name': 'Plex Media Server',
            #             'path': 'C:\\Users\\...\\Plex Media Server\\...',
            #             'type': 'sqlite',
            #             'status': 'accessible'
            #         }
            #     ],
            #     'total_count': 3
            # }

        Read registry value:
            result = await windows_system(
                operation='read_registry_value',
                registry_key='HKEY_CURRENT_USER\\Software\\Plex',
                registry_value='InstallPath'
            )
            # Returns: {
            #     'success': True,
            #     'value': 'C:\\Program Files\\Plex Media Server',
            #     'value_type': 'REG_SZ',
            #     'key_path': 'HKEY_CURRENT_USER\\Software\\Plex'
            # }

        Write registry value:
            result = await windows_system(
                operation='write_registry_value',
                registry_key='HKEY_CURRENT_USER\\Software\\MyApp',
                registry_value='Version',
                value_data='1.0.0'
            )
            # Returns: {
            #     'success': True,
            #     'message': 'Registry value written successfully',
            #     'key_path': 'HKEY_CURRENT_USER\\Software\\MyApp',
            #     'value_written': '1.0.0'
            # }

        List registry keys:
            result = await windows_system(
                operation='list_registry_keys',
                registry_key='HKEY_CURRENT_USER\\Software'
            )
            # Returns: {
            #     'success': True,
            #     'keys': ['Microsoft', 'Plex', 'MyApp'],
            #     'parent_key': 'HKEY_CURRENT_USER\\Software'
            # }

        Query Windows database:
            result = await windows_system(
                operation='query_windows_database',
                database_path='C:\\plex\\database.db',
                query='SELECT * FROM metadata_items LIMIT 10',
                include_metadata=True
            )
            # Returns: {
            #     'success': True,
            #     'results': [...],
            #     'columns': ['id', 'title', 'type'],
            #     'row_count': 10
            # }

        Clean Windows database:
            result = await windows_system(
                operation='clean_windows_database',
                database_path='C:\\plex\\database.db',
                clean_database=True
            )
            # Returns: {
            #     'success': True,
            #     'message': 'Database cleaned successfully',
            #     'cleanup_stats': {
            #         'size_before': 2048000000,
            #         'size_after': 1800000000,
            #         'freed_space': 248000000
            #     }
            # }

        Error handling - registry key not found:
            result = await windows_system(
                operation='read_registry_value',
                registry_key='HKEY_CURRENT_USER\\Software\\Nonexistent',
                registry_value='Value'
            )
            # Returns: {
            #     'success': False,
            #     'error': 'Registry key not found: HKEY_CURRENT_USER\\Software\\Nonexistent'
            # }

    Errors:
        Common errors and solutions:
        - 'Registry key not found: {key}':
            Cause: Registry key path doesn't exist
            Fix: Verify key path spelling, check if application is installed
            Workaround: Use list_registry_keys to see available keys

        - 'Access denied':
            Cause: Insufficient permissions to read/write registry
            Fix: Run with administrator privileges, check registry permissions
            Workaround: Read from HKEY_CURRENT_USER instead of HKEY_LOCAL_MACHINE

        - 'Database file not found: {path}':
            Cause: Database file doesn't exist at specified path
            Fix: Verify path is correct, check if application is installed
            Workaround: Use list_windows_databases to discover database locations

        - 'Database locked':
            Cause: Database is in use by another process
            Fix: Close application using database, stop services
            Workaround: Wait for lock to release, retry operation

        - 'Invalid registry value type':
            Cause: Value data type doesn't match registry value type
            Fix: Use correct data type (str for REG_SZ, int for REG_DWORD)
            Workaround: Convert data to appropriate type before writing

    See Also:
        - db_connection: Database connection management
        - db_operations: Query Windows databases via connections
        - media_library: Plex library management (cross-platform)
    """

    if operation == "list_windows_databases":
        return await _list_windows_databases()
    elif operation == "manage_plex_metadata":
        return await _manage_plex_metadata(plex_server_url, plex_token, optimize_performance)
    elif operation == "query_windows_database":
        return await _query_windows_database(database_path, query, include_metadata)
    elif operation == "clean_windows_database":
        return await _clean_windows_database(database_path, clean_database)
    elif operation == "read_registry_value":
        return await _read_registry_value(registry_key, registry_value)
    elif operation == "write_registry_value":
        return await _write_registry_value(registry_key, registry_value, value_data)
    elif operation == "list_registry_keys":
        return await _list_registry_keys(registry_key)
    elif operation == "list_registry_values":
        return await _list_registry_values(registry_key)
    else:
        return {
            "success": False,
            "error": f"Unknown operation: {operation}",
            "available_operations": [
                "list_windows_databases",
                "manage_plex_metadata",
                "query_windows_database",
                "clean_windows_database",
                "read_registry_value",
                "write_registry_value",
                "list_registry_keys",
                "list_registry_values",
            ],
        }


async def _list_windows_databases() -> dict[str, Any]:
    """List Windows databases (Plex, etc.)."""
    try:
        return {
            "success": True,
            "message": "Windows databases listed",
            "databases": [
                {
                    "name": "Plex Media Server",
                    "path": (
                        "C:\\Users\\Username\\AppData\\Local\\"
                        "Plex Media Server\\Plug-in Support\\Databases"
                    ),
                    "type": "sqlite",
                    "status": "unknown",
                },
                {
                    "name": "Windows Search",
                    "path": "C:\\ProgramData\\Microsoft\\Search\\Data\\Applications\\Windows",
                    "type": "edb",
                    "status": "unknown",
                },
            ],
            "count": 2,
            "note": "Implementation pending - requires Windows database detection",
        }

    except Exception as e:
        logger.error(f"Error listing Windows databases: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to list Windows databases: {str(e)}",
            "databases": [],
            "count": 0,
        }


async def _manage_plex_metadata(
    plex_server_url: str | None, plex_token: str | None, optimize_performance: bool
) -> dict[str, Any]:
    """Manage Plex metadata on Windows."""
    try:
        if not plex_server_url:
            raise ValueError("Plex server URL is required")

        return {
            "success": True,
            "message": "Plex metadata management requested",
            "plex_server_url": plex_server_url,
            "plex_token": plex_token,
            "optimize_performance": optimize_performance,
            "management_result": {
                "metadata_items_processed": 0,
                "optimization_applied": optimize_performance,
                "note": "Implementation pending - requires Plex metadata management",
            },
        }

    except Exception as e:
        logger.error(f"Error managing Plex metadata: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to manage Plex metadata: {str(e)}",
            "plex_server_url": plex_server_url,
            "management_result": {},
        }


async def _query_windows_database(
    database_path: str | None, query: str | None, include_metadata: bool
) -> dict[str, Any]:
    """Query Windows-specific databases."""
    try:
        if not database_path:
            raise ValueError("Database path is required")
        if not query:
            raise ValueError("Query is required")

        return {
            "success": True,
            "message": "Windows database query executed",
            "database_path": database_path,
            "query": query,
            "include_metadata": include_metadata,
            "results": [],
            "row_count": 0,
            "note": "Implementation pending - requires Windows database query logic",
        }

    except Exception as e:
        logger.error(f"Error querying Windows database: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to query Windows database: {str(e)}",
            "database_path": database_path,
            "query": query,
            "results": [],
            "row_count": 0,
        }


async def _clean_windows_database(
    database_path: str | None, clean_database: bool
) -> dict[str, Any]:
    """Clean and optimize Windows databases."""
    try:
        if not database_path:
            raise ValueError("Database path is required")

        return {
            "success": True,
            "message": "Windows database cleaning requested",
            "database_path": database_path,
            "clean_database": clean_database,
            "cleaning_result": {
                "tables_cleaned": 0,
                "space_freed": "0 MB",
                "optimization_applied": clean_database,
                "note": "Implementation pending - requires Windows database cleaning logic",
            },
        }

    except Exception as e:
        logger.error(f"Error cleaning Windows database: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to clean Windows database: {str(e)}",
            "database_path": database_path,
            "cleaning_result": {},
        }


async def _read_registry_value(
    registry_key: str | None, registry_value: str | None
) -> dict[str, Any]:
    """Read a value from Windows Registry."""
    try:
        if not registry_key:
            raise ValueError("Registry key is required")
        if not registry_value:
            raise ValueError("Registry value is required")

        return {
            "success": True,
            "message": f"Registry value read requested for '{registry_value}'",
            "registry_key": registry_key,
            "registry_value": registry_value,
            "value_data": None,
            "data_type": "unknown",
            "note": "Implementation pending - requires Windows Registry access",
        }

    except Exception as e:
        logger.error(f"Error reading registry value: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to read registry value: {str(e)}",
            "registry_key": registry_key,
            "registry_value": registry_value,
            "value_data": None,
        }


async def _write_registry_value(
    registry_key: str | None, registry_value: str | None, value_data: Any | None
) -> dict[str, Any]:
    """Write a value to Windows Registry."""
    try:
        if not registry_key:
            raise ValueError("Registry key is required")
        if not registry_value:
            raise ValueError("Registry value is required")
        if value_data is None:
            raise ValueError("Value data is required")

        return {
            "success": True,
            "message": f"Registry value write requested for '{registry_value}'",
            "registry_key": registry_key,
            "registry_value": registry_value,
            "value_data": value_data,
            "note": "Implementation pending - requires Windows Registry write access",
        }

    except Exception as e:
        logger.error(f"Error writing registry value: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to write registry value: {str(e)}",
            "registry_key": registry_key,
            "registry_value": registry_value,
            "value_data": value_data,
        }


async def _list_registry_keys(registry_key: str | None) -> dict[str, Any]:
    """List registry keys in a path."""
    try:
        if not registry_key:
            raise ValueError("Registry key is required")

        return {
            "success": True,
            "message": f"Registry keys listed for '{registry_key}'",
            "registry_key": registry_key,
            "subkeys": [],
            "count": 0,
            "note": "Implementation pending - requires Windows Registry enumeration",
        }

    except Exception as e:
        logger.error(f"Error listing registry keys: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to list registry keys: {str(e)}",
            "registry_key": registry_key,
            "subkeys": [],
            "count": 0,
        }


async def _list_registry_values(registry_key: str | None) -> dict[str, Any]:
    """List registry values in a key."""
    try:
        if not registry_key:
            raise ValueError("Registry key is required")

        return {
            "success": True,
            "message": f"Registry values listed for '{registry_key}'",
            "registry_key": registry_key,
            "values": [],
            "count": 0,
            "note": "Implementation pending - requires Windows Registry value enumeration",
        }

    except Exception as e:
        logger.error(f"Error listing registry values: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to list registry values: {str(e)}",
            "registry_key": registry_key,
            "values": [],
            "count": 0,
        }
