"""
Chrome profile management portmanteau tool.

This module provides comprehensive Chrome profile management, consolidating all
profile operations into a single interface. Chrome uses User Data folders
instead of SQLite-based profiles like Firefox.
"""

from typing import Any

from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.services.browser.chrome_core import ChromeManager

# Initialize Chrome manager
_chrome_manager = ChromeManager()


@mcp.tool()
async def chrome_profiles(
    operation: str,
    profile_name: str | None = None,
    check_access: bool = True,
    include_info: bool = True,
) -> dict[str, Any]:
    """Chrome profile management portmanteau tool.

    Operations: get_chrome_profiles, get_profile_info, create_profile, delete_profile,
    switch_profile, backup_profile, restore_profile, is_chrome_running, get_chrome_platform,
    get_profile_directory, get_bookmarks_db_path, get_database_info, check_chrome_status,
    validate_profile.

    profile_name: Chrome profile name (default: 'Default')
    check_access: Verify bookmark database accessibility (default: True)
    include_info: Include detailed diagnostics (default: True)
    """
    # Route to appropriate Chrome profile operation handler
    if operation == "get_chrome_profiles":
        profiles = await _chrome_manager.get_profiles()
        return {
            "success": True,
            "operation": operation,
            "profiles": profiles,
            "count": len(profiles),
            "message": f"Found {len(profiles)} Chrome profile(s)",
        }

    elif operation == "get_profile_info" and profile_name:
        info = await _chrome_manager.get_profile_info(profile_name)
        return {
            "success": True,
            "operation": operation,
            "profile_name": profile_name,
            "info": info,
            "message": f"Profile info retrieved for {profile_name}",
        }

    elif operation == "validate_profile" and profile_name:
        is_valid = await _chrome_manager.validate_profile(profile_name)
        return {
            "success": True,
            "operation": operation,
            "profile_name": profile_name,
            "is_valid": is_valid,
            "message": f"Profile {profile_name} is {'valid' if is_valid else 'invalid'}",
        }

    elif operation == "is_chrome_running":
        is_locked = await _chrome_manager.is_database_locked(profile_name or "Default")
        return {
            "success": True,
            "operation": operation,
            "is_running": is_locked,
            "message": "Chrome is running" if is_locked else "Chrome is not running",
            "note": "Database locked = Chrome running; Database unlocked = Chrome closed",
        }

    elif operation == "get_profile_directory" and profile_name:
        profile_path = await _chrome_manager.get_profile_path(profile_name)
        return {
            "success": True,
            "operation": operation,
            "profile_name": profile_name,
            "profile_directory": profile_path,
            "message": f"Profile directory path for {profile_name}",
        }

    elif operation == "get_bookmarks_db_path" and profile_name:
        db_path = _chrome_manager.get_database_path(profile_name)
        return {
            "success": True,
            "operation": operation,
            "profile_name": profile_name,
            "bookmarks_path": db_path,
            "message": f"Bookmarks file path for {profile_name}",
        }

    else:
        return {
            "success": False,
            "operation": operation,
            "error": f'Operation "{operation}" not yet implemented for Chrome profiles',
            "message": "Chrome profile operation not supported yet",
            "note": "This is a placeholder portmanteau tool for Chrome profiles",
        }
