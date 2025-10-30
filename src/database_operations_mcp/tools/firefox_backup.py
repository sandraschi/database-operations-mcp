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

    This tool consolidates all Firefox backup and authentication operations into a single interface,
    providing unified access to backup and auth functionality.

    Operations:
    - backup_firefox_data: Create a backup of Firefox profile data
    - restore_firefox_data: Restore Firefox profile data from backup
    - create_session: Create a new Firefox session for authentication

    Args:
        operation: The operation to perform (required)
        profile_name: Firefox profile name to operate on
        backup_path: Path to save backup data
        include_bookmarks: Whether to include bookmarks in backup
        include_settings: Whether to include settings in backup
        include_passwords: Whether to include passwords in backup
        restore_path: Path to restore data from
        create_session: Whether to create a new session

    Returns:
        Dictionary with operation results and backup information

    Examples:
        Backup profile:
        firefox_backup(operation='backup_firefox_data', profile_name='default',
                      backup_path='/backups/firefox', include_bookmarks=True)

        Restore profile:
        firefox_backup(operation='restore_firefox_data', profile_name='default',
                      restore_path='/backups/firefox/backup_2023.zip')

        Create session:
        firefox_backup(operation='create_session', profile_name='default')
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
