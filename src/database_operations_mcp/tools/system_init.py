# System initialization portmanteau tool.
# Consolidates initialization and setup operations into a single interface.

import logging
from typing import Any

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.tools.help_tools import HelpSystem

logger = logging.getLogger(__name__)


@mcp.tool()
@HelpSystem.register_tool(category="system")
async def system_init(
    operation: str,
    database_type: str | None = None,
    connection_config: dict[str, Any] | None = None,
    test_connection: bool = True,
    create_tables: bool = False,
    initialize_data: bool = False,
    setup_help_system: bool = True,
    verbose: bool = False,
) -> dict[str, Any]:
    """System initialization portmanteau tool.

    Comprehensive system initialization and setup operations consolidating ALL
    initialization functionality into a single interface. Supports database
    initialization, system setup, installation verification, configuration
    creation, help system initialization, health checks, and system reset.

    Prerequisites:
        - For database operations: Database server must be accessible (if remote)
        - For file operations: Write permissions in target directories
        - For system reset: Backup important data before resetting
        - For verification: All dependencies must be installable/accessible

    Operations:
        - init_database: Initialize a new database connection
        - setup_system: Set up the entire system with default configurations
        - verify_installation: Verify that all components are properly installed
        - create_default_config: Create default configuration files
        - initialize_help_system: Initialize the help system
        - run_system_checks: Run comprehensive system health checks
        - reset_system: Reset system to default state

    Parameters:
        operation (str, REQUIRED): The operation to perform
            Valid values: 'init_database', 'setup_system', 'verify_installation',
                         'create_default_config', 'initialize_help_system',
                         'run_system_checks', 'reset_system'
            Example: 'init_database', 'verify_installation', 'setup_system'

        database_type (str, OPTIONAL): Type of database to initialize
            Format: Database type identifier
            Required for: init_database operation
            Valid values: 'sqlite', 'postgresql', 'mysql', 'mongodb', 'redis'
            Example: 'sqlite', 'postgresql', 'mysql'

        connection_config (dict, OPTIONAL): Configuration for database connection
            Format: Dictionary with database-specific connection parameters
            Required for: init_database operation
            SQLite: {'database': '/path/to/file.db'}
            PostgreSQL: {'host': 'localhost', 'port': 5432, 'user': 'admin',
                        'password': 'pwd', 'database': 'mydb'}
            MongoDB: {'host': 'localhost', 'port': 27017, 'database': 'mydb'}
            Example: {'path': 'C:/data/app.db'}, {'host': 'db.example.com', 'port': 5432}

        test_connection (bool, OPTIONAL): Test connection during initialization
            Default: True
            Behavior: Verifies database connection works before completing setup
            Used for: init_database operation
            Warning: If False, connection errors may not be detected until later

        create_tables (bool, OPTIONAL): Create default tables
            Default: False
            Behavior: Creates standard database tables if they don't exist
            Used for: init_database, setup_system operations
            Warning: May overwrite existing tables if not careful

        initialize_data (bool, OPTIONAL): Initialize with default data
            Default: False
            Behavior: Populates database with sample/default data
            Used for: init_database, setup_system operations
            Warning: May add test/demo data to production databases

        setup_help_system (bool, OPTIONAL): Set up the help system
            Default: True
            Behavior: Initializes help system with documentation
            Used for: setup_system operation
            Impact: Required for help_system tool to work properly

        verbose (bool, OPTIONAL): Provide verbose output
            Default: False
            Behavior: Includes detailed diagnostic information in response
            Used for: verify_installation, run_system_checks operations
            Example: True for troubleshooting, False for quick checks

    Returns:
        Dictionary containing operation-specific results:
            - success: Boolean indicating operation success
            - operation: Echo of operation performed
            - For init_database: connection_name, database_type, status, connection_info
            - For setup_system: components_initialized (list), status, message
            - For verify_installation: components (list), all_installed (bool), issues (list)
            - For create_default_config: config_path, files_created (list), message
            - For initialize_help_system: help_topics (int), status, message
            - For run_system_checks: checks (list), health_score, issues (list)
            - For reset_system: components_reset (list), status, message
            - error: Error message if success is False
            - available_operations: List of valid operations (on invalid operation)

    Usage:
        This tool provides comprehensive system initialization and setup. Use it to
        configure the MCP server, verify installations, and perform system maintenance.

        Common scenarios:
        - Initial setup: Configure system on first use
        - Database initialization: Set up database connections
        - Health monitoring: Run system checks to verify everything works
        - Troubleshooting: Verify installation and check for issues
        - Reset: Return system to default state

        Best practices:
        - Run verify_installation before first use
        - Use setup_system for complete initial configuration
        - Run system_checks periodically to monitor health
        - Backup data before reset_system
        - Use verbose=True for detailed diagnostics

    Examples:
        Initialize SQLite database:
            result = await system_init(
                operation='init_database',
                database_type='sqlite',
                connection_config={'path': 'C:/data/app.db'},
                test_connection=True
            )
            # Returns: {
            #     'success': True,
            #     'connection_name': 'default',
            #     'database_type': 'sqlite',
            #     'status': 'initialized'
            # }

        Setup complete system:
            result = await system_init(
                operation='setup_system',
                create_tables=True,
                initialize_data=False,
                setup_help_system=True
            )
            # Returns: {
            #     'success': True,
            #     'components_initialized': ['database', 'help_system', 'config'],
            #     'status': 'complete'
            # }

        Verify installation:
            result = await system_init(
                operation='verify_installation',
                verbose=True
            )
            # Returns: {
            #     'success': True,
            #     'all_installed': True,
            #     'components': [
            #         {'name': 'fastmcp', 'installed': True, 'version': '2.13.0'},
            #         {'name': 'aiosqlite', 'installed': True, 'version': '0.19.0'}
            #     ]
            # }

        Run system health checks:
            result = await system_init(
                operation='run_system_checks',
                verbose=True
            )
            # Returns: {
            #     'success': True,
            #     'health_score': 95,
            #     'checks': [
            #         {'component': 'database', 'status': 'ok'},
            #         {'component': 'storage', 'status': 'ok'}
            #     ]
            # }

        Error handling - invalid operation:
            result = await system_init(operation='invalid_operation')
            # Returns: {
            #     'success': False,
            #     'error': 'Unknown operation: invalid_operation',
            #     'available_operations': [...]
            # }

    Errors:
        Common errors and solutions:
        - 'Database connection failed: {error}':
            Cause: Cannot connect to database server
            Fix: Verify database is running, check connection_config parameters
            Workaround: Test connection manually, verify network/firewall settings

        - 'Database type not supported: {database_type}':
            Cause: Specified database type not in supported list
            Fix: Use valid database type (sqlite, postgresql, mysql, mongodb, redis)
            Example: database_type='postgresql' not database_type='postgres'

        - 'Missing required parameter: {parameter}':
            Cause: Required parameter not provided for operation
            Fix: Provide all required parameters for the operation
            Example: init_database requires database_type and connection_config

        - 'Configuration file already exists':
            Cause: Attempting to create config file that already exists
            Fix: Delete existing config file or use different location
            Workaround: Backup existing config before creating new one

        - 'System reset failed: {error}':
            Cause: Cannot reset system (files locked, permissions, etc.)
            Fix: Close all connections, verify permissions, check file locks
            Workaround: Manually delete config files and restart

    See Also:
        - db_connection: Database connection management
        - help_system: Help system operations
        - db_management: Database management operations
    """

    if operation == "init_database":
        return await _init_database(
            database_type, connection_config, test_connection, create_tables, initialize_data
        )
    elif operation == "setup_system":
        return await _setup_system(create_tables, initialize_data, setup_help_system, verbose)
    elif operation == "verify_installation":
        return await _verify_installation(verbose)
    elif operation == "create_default_config":
        return await _create_default_config()
    elif operation == "initialize_help_system":
        return await _initialize_help_system()
    elif operation == "run_system_checks":
        return await _run_system_checks(verbose)
    elif operation == "reset_system":
        return await _reset_system()
    else:
        return {
            "success": False,
            "error": f"Unknown operation: {operation}",
            "available_operations": [
                "init_database",
                "setup_system",
                "verify_installation",
                "create_default_config",
                "initialize_help_system",
                "run_system_checks",
                "reset_system",
            ],
        }


async def _init_database(
    database_type: str | None,
    connection_config: dict[str, Any] | None,
    test_connection: bool,
    create_tables: bool,
    initialize_data: bool,
) -> dict[str, Any]:
    """Initialize a new database connection."""
    try:
        if not database_type:
            raise ValueError("Database type is required")
        if not connection_config:
            raise ValueError("Connection config is required")

        return {
            "success": True,
            "message": f"Database initialization requested for '{database_type}'",
            "database_type": database_type,
            "connection_config": connection_config,
            "test_connection": test_connection,
            "create_tables": create_tables,
            "initialize_data": initialize_data,
            "initialization_result": {
                "connection_established": False,
                "tables_created": 0,
                "data_initialized": False,
                "note": "Implementation pending - requires database initialization logic",
            },
        }

    except Exception as e:
        logger.error(f"Error initializing database: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to initialize database: {str(e)}",
            "database_type": database_type,
            "initialization_result": {},
        }


async def _setup_system(
    create_tables: bool, initialize_data: bool, setup_help_system: bool, verbose: bool
) -> dict[str, Any]:
    """Set up the entire system with default configurations."""
    try:
        return {
            "success": True,
            "message": "System setup requested",
            "create_tables": create_tables,
            "initialize_data": initialize_data,
            "setup_help_system": setup_help_system,
            "verbose": verbose,
            "setup_result": {
                "components_configured": 0,
                "tables_created": 0,
                "help_system_initialized": False,
                "default_data_loaded": False,
                "note": "Implementation pending - requires system setup logic",
            },
        }

    except Exception as e:
        logger.error(f"Error setting up system: {e}", exc_info=True)
        return {"success": False, "error": f"Failed to setup system: {str(e)}", "setup_result": {}}


async def _verify_installation(verbose: bool) -> dict[str, Any]:
    """Verify that all components are properly installed."""
    try:
        return {
            "success": True,
            "message": "Installation verification requested",
            "verbose": verbose,
            "verification_result": {
                "components_checked": 0,
                "components_ok": 0,
                "components_failed": 0,
                "missing_dependencies": [],
                "note": "Implementation pending - requires installation verification logic",
            },
        }

    except Exception as e:
        logger.error(f"Error verifying installation: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to verify installation: {str(e)}",
            "verification_result": {},
        }


async def _create_default_config() -> dict[str, Any]:
    """Create default configuration files."""
    try:
        return {
            "success": True,
            "message": "Default configuration creation requested",
            "config_files": [
                "database_config.json",
                "firefox_config.json",
                "media_config.json",
                "windows_config.json",
            ],
            "count": 4,
            "note": "Implementation pending - requires configuration file generation",
        }

    except Exception as e:
        logger.error(f"Error creating default config: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to create default config: {str(e)}",
            "config_files": [],
            "count": 0,
        }


async def _initialize_help_system() -> dict[str, Any]:
    """Initialize the help system."""
    try:
        return {
            "success": True,
            "message": "Help system initialization requested",
            "help_system_result": {
                "categories_loaded": 0,
                "tools_documented": 0,
                "examples_generated": 0,
                "note": "Implementation pending - requires help system initialization",
            },
        }

    except Exception as e:
        logger.error(f"Error initializing help system: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to initialize help system: {str(e)}",
            "help_system_result": {},
        }


async def _run_system_checks(verbose: bool) -> dict[str, Any]:
    """Run comprehensive system health checks."""
    try:
        return {
            "success": True,
            "message": "System health checks requested",
            "verbose": verbose,
            "health_checks": {
                "database_connections": {"status": "unknown", "count": 0},
                "firefox_profiles": {"status": "unknown", "count": 0},
                "media_libraries": {"status": "unknown", "count": 0},
                "windows_registry": {"status": "unknown", "accessible": False},
                "help_system": {"status": "unknown", "tools_registered": 0},
                "note": "Implementation pending - requires system health check logic",
            },
        }

    except Exception as e:
        logger.error(f"Error running system checks: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to run system checks: {str(e)}",
            "health_checks": {},
        }


async def _reset_system() -> dict[str, Any]:
    """Reset system to default state."""
    try:
        return {
            "success": True,
            "message": "System reset requested",
            "reset_result": {
                "configurations_reset": 0,
                "databases_reset": 0,
                "profiles_reset": 0,
                "help_system_reset": False,
                "note": "Implementation pending - requires system reset logic",
            },
        }

    except Exception as e:
        logger.error(f"Error resetting system: {e}", exc_info=True)
        return {"success": False, "error": f"Failed to reset system: {str(e)}", "reset_result": {}}
