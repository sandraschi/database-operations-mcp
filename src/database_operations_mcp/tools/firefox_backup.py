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

    Operations: backup_firefox_data, restore_firefox_data, create_session.
    profile_name: Firefox profile name (default: 'default')
    backup_path: Directory path for backup (required for backup_firefox_data)
    restore_path: Full path to backup zip file (required for restore_firefox_data)
    include_passwords: Include password database in backup (default: False)
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
