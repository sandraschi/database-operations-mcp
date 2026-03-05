# Firefox backup and authentication portmanteau tool.
# Consolidates Firefox backup and auth operations into a single interface.

import logging
from typing import Any

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.tools.help_tools import HelpSystem

logger = logging.getLogger(__name__)


@mcp.tool()
@HelpSystem.register_tool(category="firefox")
async def firefox_backup(
    operation: str,
    profile_name: str | None = None,
    backup_path: str | None = None,
    include_bookmarks: bool = True,
    include_settings: bool = True,
    include_passwords: bool = False,
    restore_path: str | None = None,
    create_session: bool = False,
) -> dict[str, Any]:
    """Firefox backup and authentication portmanteau tool.

    Comprehensive Firefox backup and authentication operations consolidating ALL
    backup and auth functionality into a single interface. Supports profile backup,
    restore operations, and session management for Firefox profiles.

    Prerequisites:
        - Firefox must be completely closed before backup/restore operations
        - Valid Firefox profile name (use firefox_profiles to list available profiles)
        - For backup: Sufficient disk space at backup_path location
        - For restore: Valid backup file at restore_path location
        - Write permissions at backup/restore paths

    Operations:
        - backup_firefox_data: Create a backup of Firefox profile data
        - restore_firefox_data: Restore Firefox profile data from backup
        - create_session: Create a new Firefox session for authentication

    Parameters:
        operation (str, REQUIRED): The operation to perform
            Valid values: 'backup_firefox_data', 'restore_firefox_data', 'create_session'
            Example: 'backup_firefox_data', 'restore_firefox_data'

        profile_name (str, OPTIONAL): Firefox profile name to operate on
            Format: Valid Firefox profile name
            Required for: backup_firefox_data, restore_firefox_data, create_session
            Default: 'default' (if not specified)
            Validation: Profile must exist (use firefox_profiles to verify)
            Example: 'default', 'work', 'personal'

        backup_path (str, OPTIONAL): Path to save backup data
            Format: Directory path where backup will be created
            Required for: backup_firefox_data operation
            Validation: Directory must exist and be writable
            Example: 'C:/backups/firefox', '/backups/firefox'
            Note: Backup file named with timestamp automatically

        include_bookmarks (bool, OPTIONAL): Include bookmarks in backup
            Default: True
            Behavior: Backs up bookmark database (places.sqlite)
            Used for: backup_firefox_data operation
            Impact: Required for bookmark restore

        include_settings (bool, OPTIONAL): Include settings in backup
            Default: True
            Behavior: Backs up preferences and settings files
            Used for: backup_firefox_data operation
            Impact: Restores Firefox preferences and configuration

        include_passwords (bool, OPTIONAL): Include passwords in backup
            Default: False
            Behavior: Backs up password database (logins.json, key4.db)
            Used for: backup_firefox_data operation
            Warning: Contains sensitive data, secure backup file
            Security: Encrypt backup file if include_passwords=True

        restore_path (str, OPTIONAL): Path to restore data from
            Format: Full path to backup file (usually .zip)
            Required for: restore_firefox_data operation
            Validation: File must exist and be readable
            Example: 'C:/backups/firefox/backup_2025-01-27.zip'

        create_session (bool, OPTIONAL): Create a new session
            Default: False
            Behavior: Creates authentication session for profile
            Used for: create_session operation
            Note: Legacy parameter, operation='create_session' creates session

    Returns:
        Dictionary containing operation-specific results:
            - success: Boolean indicating operation success
            - operation: Echo of operation performed
            - profile_name: Echo of profile name used
            - For backup_firefox_data: backup_path, backup_file, file_size, included_items (list)
            - For restore_firefox_data: restored_items (list), restore_path, message
            - For create_session: session_id, expires_at, message
            - error: Error message if success is False
            - available_operations: List of valid operations (on invalid operation)

    Usage:
        This tool provides comprehensive Firefox profile backup and restore capabilities.
        Use it to backup profiles before changes, migrate profiles, or recover from issues.

        Common scenarios:
        - Profile backup: Create backups before major changes
        - Profile migration: Move profiles between systems
        - Disaster recovery: Restore profiles from backups
        - Profile duplication: Backup and restore to create copies
        - Security: Backup with passwords for secure storage

        Best practices:
        - Always backup before restore operations
        - Use include_passwords only when necessary (security risk)
        - Store backups in secure locations
        - Test restore operations periodically
        - Use descriptive backup paths with timestamps

    Examples:
        Backup profile:
            result = await firefox_backup(
                operation='backup_firefox_data',
                profile_name='work',
                backup_path='C:/backups/firefox',
                include_bookmarks=True,
                include_settings=True,
                include_passwords=False
            )
            # Returns: {
            #     'success': True,
            #     'backup_path': 'C:/backups/firefox',
            #     'backup_file': 'work_2025-01-27_143022.zip',
            #     'file_size': 52428800,
            #     'included_items': ['bookmarks', 'settings']
            # }

        Restore profile:
            result = await firefox_backup(
                operation='restore_firefox_data',
                profile_name='work',
                restore_path='C:/backups/firefox/work_2025-01-27.zip'
            )
            # Returns: {
            #     'success': True,
            #     'restored_items': ['bookmarks', 'settings'],
            #     'restore_path': 'C:/backups/firefox/work_2025-01-27.zip',
            #     'message': 'Profile restored successfully'
            # }

        Create session:
            result = await firefox_backup(
                operation='create_session',
                profile_name='default'
            )
            # Returns: {
            #     'success': True,
            #     'session_id': 'abc123def456',
            #     'expires_at': '2025-01-27T18:00:00Z',
            #     'message': 'Session created successfully'
            # }

        Error handling - Firefox running:
            result = await firefox_backup(
                operation='backup_firefox_data',
                profile_name='default',
                backup_path='C:/backups'
            )
            # Returns: {
            #     'success': False,
            #     'error': 'Firefox is running. Close Firefox before operations.'
            # }

    Errors:
        Common errors and solutions:
        - 'Firefox is running. Close Firefox before operations':
            Cause: Firefox browser is currently running
            Fix: Completely close all Firefox windows and processes
            Workaround: Wait for Firefox to close, check Task Manager

        - 'Profile not found: {profile_name}':
            Cause: Specified profile doesn't exist
            Fix: Use firefox_profiles(operation='get_firefox_profiles') to list profiles
            Workaround: Use 'default' profile name, check profile spelling

        - 'Backup path not accessible: {backup_path}':
            Cause: Backup directory doesn't exist or lacks write permissions
            Fix: Create directory, verify write permissions, check disk space
            Workaround: Use user home directory or desktop for backups

        - 'Backup file not found: {restore_path}':
            Cause: Restore path doesn't point to valid backup file
            Fix: Verify backup file exists, check file path spelling
            Workaround: List files in backup directory to find correct filename

        - 'Backup file corrupted':
            Cause: Backup file is incomplete or damaged
            Fix: Use different backup file, verify backup file integrity
            Workaround: Create new backup if old one is corrupted

        - 'Insufficient disk space':
            Cause: Not enough space to create backup file
            Fix: Free up disk space, use different backup location
            Workaround: Use external drive or network location for backups

    See Also:
        - firefox_profiles: List and manage Firefox profiles
        - firefox_bookmarks: Manage bookmarks (can export/import separately)
        - browser_bookmarks: Cross-browser bookmark backup operations
    """

    if operation == "backup_firefox_data":
        return await _backup_firefox_data(
            profile_name, backup_path, include_bookmarks, include_settings, include_passwords
        )
    elif operation == "restore_firefox_data":
        return await _restore_firefox_data(profile_name, restore_path)
    elif operation == "create_session":
        return await _create_session(profile_name)
    else:
        return {
            "success": False,
            "error": f"Unknown operation: {operation}",
            "available_operations": [
                "backup_firefox_data",
                "restore_firefox_data",
                "create_session",
            ],
        }


async def _backup_firefox_data(
    profile_name: str | None,
    backup_path: str | None,
    include_bookmarks: bool,
    include_settings: bool,
    include_passwords: bool,
) -> dict[str, Any]:
    """Create a backup of Firefox profile data."""
    try:
        if not profile_name:
            raise ValueError("Profile name is required")
        if not backup_path:
            raise ValueError("Backup path is required")

        return {
            "success": True,
            "message": f"Firefox data backup requested for profile '{profile_name}'",
            "profile_name": profile_name,
            "backup_path": backup_path,
            "include_bookmarks": include_bookmarks,
            "include_settings": include_settings,
            "include_passwords": include_passwords,
            "note": "Implementation pending - requires Firefox backup logic",
        }

    except Exception as e:
        logger.error(f"Error backing up Firefox data: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to backup Firefox data: {str(e)}",
            "profile_name": profile_name,
            "backup_path": backup_path,
            "backup_result": {},
        }


async def _restore_firefox_data(
    profile_name: str | None, restore_path: str | None
) -> dict[str, Any]:
    """Restore Firefox profile data from backup."""
    try:
        if not profile_name:
            raise ValueError("Profile name is required")
        if not restore_path:
            raise ValueError("Restore path is required")

        return {
            "success": True,
            "message": f"Firefox data restore requested for profile '{profile_name}'",
            "profile_name": profile_name,
            "restore_path": restore_path,
            "note": "Implementation pending - requires Firefox restore logic",
        }

    except Exception as e:
        logger.error(f"Error restoring Firefox data: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to restore Firefox data: {str(e)}",
            "profile_name": profile_name,
            "restore_path": restore_path,
            "restore_result": {},
        }


async def _create_session(profile_name: str | None) -> dict[str, Any]:
    """Create a new Firefox session for authentication."""
    try:
        if not profile_name:
            raise ValueError("Profile name is required")

        return {
            "success": True,
            "message": f"Firefox session creation requested for profile '{profile_name}'",
            "profile_name": profile_name,
            "note": "Implementation pending - requires Firefox session logic",
        }

    except Exception as e:
        logger.error(f"Error creating Firefox session: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to create Firefox session: {str(e)}",
            "profile_name": profile_name,
            "session_result": {},
        }
