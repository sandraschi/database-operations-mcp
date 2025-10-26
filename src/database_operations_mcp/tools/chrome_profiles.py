"""
Chrome profile management portmanteau tool.

This module provides comprehensive Chrome profile management, consolidating all
profile operations into a single interface. Chrome uses User Data folders
instead of SQLite-based profiles like Firefox.
"""

from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP

from database_operations_mcp.services.browser.chrome_core import ChromeManager

mcp = FastMCP()

# Initialize Chrome manager
_chrome_manager = ChromeManager()


@mcp.tool()
async def chrome_profiles(
    operation: str,
    profile_name: Optional[str] = None,
    check_access: bool = True,
    include_info: bool = True,
) -> Dict[str, Any]:
    """Chrome profile management portmanteau tool.

    Comprehensive Chrome profile management consolidating ALL profile-related
    operations into a single interface. Includes profile management, utilities,
    and system operations for complete Chrome administration. Chrome uses a different
    profile system than Firefox, based on User Data folders rather than SQLite.

    Parameters:
        operation: Profile operation to perform
            # Core profile operations
            - 'get_chrome_profiles': List all available Chrome profiles
            - 'get_profile_info': Get detailed information about a specific profile
            - 'create_profile': Create a new Chrome profile
            - 'delete_profile': Delete a Chrome profile (use with caution)
            - 'switch_profile': Switch to a different profile as default
            - 'backup_profile': Backup profile data and settings
            - 'restore_profile': Restore profile from backup

            # Utility operations
            - 'is_chrome_running': Check if Chrome is currently running
            - 'get_chrome_platform': Get Chrome platform information
            - 'get_profile_directory': Get profile directory path
            - 'get_bookmarks_db_path': Get Bookmarks file path
            - 'get_database_info': Get database information and statistics
            - 'check_chrome_status': Comprehensive Chrome status check
            - 'validate_profile': Validate profile exists and is accessible

        profile_name: Chrome profile name (default: 'Default')
            - Target Chrome profile for operations
            - Must be valid Chrome profile name
            - Example: 'Default', 'Profile 1', 'Profile 2'
            - Case-sensitive but common variations handled

        check_access: Whether to check database access (default: True)
            - Verify bookmark database accessibility
            - Prevents operations on locked databases
            - Essential for safe operations
            - May impact operation speed

        include_info: Whether to include detailed information (default: True)
            - Include comprehensive profile information
            - Provides additional context and diagnostics
            - May impact response time
            - Useful for troubleshooting

    Returns:
        Dictionary containing the result of the operation, including status,
        message, and relevant data (profiles, info, diagnostics, etc.).

        Example response structure:
            {
                'success': bool,
                'operation': str,
                'profile_name': str,
                'data': {...},       # Profile info, status, etc.
                'message': str,
                'warnings': List[str]
            }

    Usage:
        Chrome profile management tool covering all profile lifecycle operations.
        Essential for managing multiple Chrome profiles, organizing bookmarks,
        and configuring Chrome behavior. Chrome profiles are stored in User Data
        folders, not SQLite databases.

        Common scenarios:
        - List Chrome profiles: chrome_profiles(operation='get_chrome_profiles')
        - Get profile info: chrome_profiles(
                operation='get_profile_info', profile_name='Default')
        - Check if Chrome is running: chrome_profiles(operation='is_chrome_running')
        - Validate profile: chrome_profiles(
                operation='validate_profile', profile_name='Default')

    Examples:
        List all Chrome profiles:
            result = await chrome_profiles(operation='get_chrome_profiles')
            # Returns: {
            #     'success': True,
            #     'profiles': ['Default', 'Profile 1', 'Profile 2'],
            #     'count': 3
            # }

        Get detailed profile information:
            result = await chrome_profiles(
                operation='get_profile_info',
                profile_name='Default',
                include_info=True
            )
            # Returns: {
            #     'success': True,
            #     'profile_name': 'Default',
            #     'profile_path': '...',
            #     'bookmark_count': 1543,
            #     'browser_version': 'chrome',
            #     'last_accessed': None
            # }

    Notes:
        - Chrome must be completely closed before using profile operations
        - Chrome profiles are stored in User Data folders
        - Default profile is always named 'Default'
        - Additional profiles are named 'Profile 1', 'Profile 2', etc.
        - Profile names are case-sensitive
        - Chrome syncs with Google account (may affect data accessibility)
        - Backing up profiles includes bookmarks, settings, and extensions

    See Also:
        - chrome_bookmarks: Chrome bookmark management
        - firefox_profiles: Firefox profile management
        - browser_bookmarks: Universal browser bookmarks
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
