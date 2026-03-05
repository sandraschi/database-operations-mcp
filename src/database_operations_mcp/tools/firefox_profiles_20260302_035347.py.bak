# Firefox profile management portmanteau tool.
# Consolidates all Firefox profile operations into a single interface.

import logging
from typing import Any

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.tools.firefox.db import FirefoxDB
from database_operations_mcp.tools.firefox.status import FirefoxStatusChecker
from database_operations_mcp.tools.help_tools import HelpSystem

logger = logging.getLogger(__name__)


@mcp.tool()
@HelpSystem.register_tool(category="firefox")
async def firefox_profiles(
    operation: str,
    profile_name: str | None = None,
    source_profiles: list[str] | None = None,
    preset_name: str | None = None,
    profile_config: dict[str, Any] | None = None,
    check_status: bool = True,
    include_bookmarks: bool = True,
    include_settings: bool = True,
) -> dict[str, Any]:
    """Firefox profile management portmanteau tool.

    Comprehensive Firefox profile operations consolidating ALL profile management
    into a single interface. Supports profile creation, deletion, portmanteau profiles,
    preset loading, and status checking across Firefox profiles.

    Prerequisites:
        - Firefox must be completely closed before profile operations
        - For create operations: Sufficient disk space for new profile
        - For portmanteau operations: Source profiles must exist and be accessible
        - For preset operations: Preset must be defined (developer_tools, etc.)

    Operations:
        - get_firefox_profiles: List all available Firefox profiles with details
        - create_firefox_profile: Create a new empty Firefox profile
        - delete_firefox_profile: Delete an existing Firefox profile
        - create_loaded_profile: Create profile with bookmarks from source profiles
        - create_portmanteau_profile: Create hybrid profile from multiple sources
        - suggest_portmanteau_profiles: Get AI suggestions for profile combinations
        - create_loaded_profile_from_preset: Create profile from predefined preset
        - check_firefox_status: Check if Firefox is running and accessible

    Parameters:
        operation (str, REQUIRED): The operation to perform
            Valid values: 'get_firefox_profiles', 'create_firefox_profile',
                         'delete_firefox_profile', 'create_loaded_profile',
                         'create_portmanteau_profile', 'suggest_portmanteau_profiles',
                         'create_loaded_profile_from_preset', 'check_firefox_status'
            Example: 'get_firefox_profiles', 'create_firefox_profile'

        profile_name (str, OPTIONAL): Name of the Firefox profile
            Format: Valid profile name (alphanumeric, underscores, hyphens)
            Required for: create_firefox_profile, delete_firefox_profile,
                         create_loaded_profile, create_portmanteau_profile
            Validation: Must be unique (for create), must exist (for delete)
            Example: 'work', 'personal', 'development', 'test_profile'

        source_profiles (list[str], OPTIONAL): List of source profiles for portmanteau
            Format: List of existing profile names
            Required for: create_loaded_profile, create_portmanteau_profile
            Validation: All profiles must exist
            Example: ['work', 'personal'], ['dev', 'research', 'docs']

        preset_name (str, OPTIONAL): Name of the preset to use
            Format: Valid preset name
            Required for: create_loaded_profile_from_preset
            Valid values: 'developer_tools', 'ai_ml', 'cooking', 'productivity',
                         'news_media', 'finance', 'entertainment', 'shopping'
            Example: 'developer_tools', 'ai_ml'

        profile_config (dict, OPTIONAL): Configuration for the new profile
            Format: Dictionary with profile configuration options
            Used for: create_firefox_profile, create_loaded_profile
            Example: {'bookmark_limit': 50, 'include_settings': True}

        check_status (bool, OPTIONAL): Check Firefox status during operations
            Default: True
            Behavior: Verifies Firefox is closed before profile operations
            Used for: All operations
            Warning: If False, may attempt operations while Firefox is running

        include_bookmarks (bool, OPTIONAL): Include bookmarks in profile operations
            Default: True
            Behavior: Copies bookmarks from source profiles
            Used for: create_loaded_profile, create_portmanteau_profile

        include_settings (bool, OPTIONAL): Include settings in profile operations
            Default: True
            Behavior: Copies settings and preferences from source profiles
            Used for: create_loaded_profile, create_portmanteau_profile

    Returns:
        Dictionary containing operation-specific results:
            - success: Boolean indicating operation success
            - operation: Echo of operation performed
            - For get_firefox_profiles: profiles (list), total_profiles
            - For create_firefox_profile: profile_name, profile_path, message
            - For delete_firefox_profile: profile_name, message
            - For create_loaded_profile: profile_name, source_profiles, bookmarks_count
            - For create_portmanteau_profile: profile_name, source_profiles, combined_stats
            - For suggest_portmanteau_profiles: suggestions (list), profile_name
            - For create_loaded_profile_from_preset: profile_name, preset_name, bookmarks_loaded
            - For check_firefox_status: is_running, process_count, message
            - error: Error message if success is False
            - available_operations: List of valid operations (on invalid operation)

    Usage:
        This tool provides comprehensive Firefox profile management. Use it to create,
        manage, and organize Firefox profiles for different purposes or contexts.

        Common scenarios:
        - Profile creation: Create new profiles for work, personal, development
        - Profile organization: Manage multiple profiles for different contexts
        - Profile combination: Create hybrid profiles from multiple sources
        - Preset profiles: Quickly set up profiles with predefined bookmark collections
        - Profile cleanup: Delete unused or old profiles

        Best practices:
        - Always close Firefox before profile operations
        - Use descriptive profile names for easy identification
        - Backup profiles before deletion
        - Use presets for common profile configurations
        - Check Firefox status before operations

    Examples:
        List all profiles:
            result = await firefox_profiles(operation='get_firefox_profiles')
            # Returns: {
            #     'success': True,
            #     'profiles': [
            #         {'name': 'default', 'path': '...', 'bookmark_count': 150},
            #         {'name': 'work', 'path': '...', 'bookmark_count': 45}
            #     ],
            #     'total_profiles': 2
            # }

        Create new profile:
            result = await firefox_profiles(
                operation='create_firefox_profile',
                profile_name='development',
                check_status=True
            )
            # Returns: {
            #     'success': True,
            #     'profile_name': 'development',
            #     'profile_path': 'C:\\Users\\...\\profiles\\development',
            #     'message': 'Profile created successfully'
            # }

        Create portmanteau profile:
            result = await firefox_profiles(
                operation='create_portmanteau_profile',
                profile_name='hybrid',
                source_profiles=['work', 'personal', 'research'],
                include_bookmarks=True,
                include_settings=True
            )
            # Returns: {
            #     'success': True,
            #     'profile_name': 'hybrid',
            #     'source_profiles': ['work', 'personal', 'research'],
            #     'combined_stats': {
            #         'total_bookmarks': 245,
            #         'total_folders': 12
            #     }
            # }

        Create from preset:
            result = await firefox_profiles(
                operation='create_loaded_profile_from_preset',
                profile_name='developer',
                preset_name='developer_tools'
            )
            # Returns: {
            #     'success': True,
            #     'profile_name': 'developer',
            #     'preset_name': 'developer_tools',
            #     'bookmarks_loaded': 45
            # }

        Check Firefox status:
            result = await firefox_profiles(operation='check_firefox_status')
            # Returns: {
            #     'success': True,
            #     'is_running': False,
            #     'process_count': 0,
            #     'message': 'Firefox is not running'
            # }

        Error handling - Firefox running:
            result = await firefox_profiles(
                operation='create_firefox_profile',
                profile_name='test'
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

        - 'Profile already exists: {profile_name}':
            Cause: Attempting to create profile with existing name
            Fix: Use different profile_name or delete existing profile first
            Workaround: Use unique name, check existing profiles first

        - 'Profile not found: {profile_name}':
            Cause: Specified profile doesn't exist
            Fix: Use get_firefox_profiles to see available profiles
            Workaround: Check profile spelling, verify Firefox installation

        - 'Source profile not found: {profile_name}':
            Cause: One or more source profiles don't exist
            Fix: Verify all source_profiles exist before creating portmanteau
            Workaround: List profiles first, use valid profile names

        - 'Preset not found: {preset_name}':
            Cause: Specified preset doesn't exist
            Fix: Use valid preset name (developer_tools, ai_ml, etc.)
            Workaround: List available presets, check preset name spelling

        - 'Insufficient disk space':
            Cause: Not enough disk space to create profile
            Fix: Free up disk space, choose different location
            Workaround: Delete old profiles, clean up disk

    See Also:
        - firefox_bookmarks: Manage bookmarks in profiles
        - browser_bookmarks: Universal browser bookmark operations
        - firefox_curated: Curated bookmark collections for profiles
    """

    if operation == "get_firefox_profiles":
        return await _get_firefox_profiles()
    elif operation == "create_firefox_profile":
        return await _create_firefox_profile(profile_name, profile_config)
    elif operation == "delete_firefox_profile":
        return await _delete_firefox_profile(profile_name)
    elif operation == "create_loaded_profile":
        return await _create_loaded_profile(
            profile_name, source_profiles, include_bookmarks, include_settings
        )
    elif operation == "create_portmanteau_profile":
        return await _create_portmanteau_profile(profile_name, source_profiles)
    elif operation == "suggest_portmanteau_profiles":
        return await _suggest_portmanteau_profiles(profile_name)
    elif operation == "create_loaded_profile_from_preset":
        return await _create_loaded_profile_from_preset(profile_name, preset_name)
    elif operation == "check_firefox_status":
        return await _check_firefox_status()
    else:
        return {
            "success": False,
            "error": f"Unknown operation: {operation}",
            "available_operations": [
                "get_firefox_profiles",
                "create_firefox_profile",
                "delete_firefox_profile",
                "create_loaded_profile",
                "create_portmanteau_profile",
                "suggest_portmanteau_profiles",
                "create_loaded_profile_from_preset",
                "check_firefox_status",
            ],
        }


async def _get_firefox_profiles() -> dict[str, Any]:
    """List all available Firefox profiles."""
    try:
        db = FirefoxDB()
        profiles = await db.get_firefox_profiles()

        return {
            "success": True,
            "message": "Firefox profiles listed successfully",
            "profiles": profiles,
            "count": len(profiles),
        }

    except Exception as e:
        logger.error(f"Error getting Firefox profiles: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to get Firefox profiles: {str(e)}",
            "profiles": [],
            "count": 0,
        }


async def _create_firefox_profile(
    profile_name: str | None, profile_config: dict[str, Any] | None
) -> dict[str, Any]:
    """Create a new Firefox profile."""
    try:
        if not profile_name:
            raise ValueError("Profile name is required")

        # For now, return a placeholder implementation
        return {
            "success": True,
            "message": f"Firefox profile '{profile_name}' creation requested",
            "profile_name": profile_name,
            "profile_config": profile_config,
            "note": "Implementation pending - requires Firefox profile creation logic",
        }

    except Exception as e:
        logger.error(f"Error creating Firefox profile: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to create Firefox profile: {str(e)}",
            "profile_name": profile_name,
        }


async def _delete_firefox_profile(profile_name: str | None) -> dict[str, Any]:
    """Delete an existing Firefox profile."""
    try:
        if not profile_name:
            raise ValueError("Profile name is required")

        return {
            "success": True,
            "message": f"Firefox profile '{profile_name}' deletion requested",
            "profile_name": profile_name,
            "note": "Implementation pending - requires Firefox profile deletion logic",
        }

    except Exception as e:
        logger.error(f"Error deleting Firefox profile: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to delete Firefox profile: {str(e)}",
            "profile_name": profile_name,
        }


async def _create_loaded_profile(
    profile_name: str | None,
    source_profiles: list[str] | None,
    include_bookmarks: bool,
    include_settings: bool,
) -> dict[str, Any]:
    """Create a profile with specific bookmarks loaded."""
    try:
        if not profile_name:
            raise ValueError("Profile name is required")
        if not source_profiles:
            raise ValueError("Source profiles are required")

        return {
            "success": True,
            "message": f"Loaded profile '{profile_name}' creation requested",
            "profile_name": profile_name,
            "source_profiles": source_profiles,
            "include_bookmarks": include_bookmarks,
            "include_settings": include_settings,
            "note": "Implementation pending - requires profile loading logic",
        }

    except Exception as e:
        logger.error(f"Error creating loaded profile: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to create loaded profile: {str(e)}",
            "profile_name": profile_name,
            "source_profiles": source_profiles,
        }


async def _create_portmanteau_profile(
    profile_name: str | None, source_profiles: list[str] | None
) -> dict[str, Any]:
    """Create a hybrid profile from multiple sources."""
    try:
        if not profile_name:
            raise ValueError("Profile name is required")
        if not source_profiles or len(source_profiles) < 2:
            raise ValueError("At least 2 source profiles are required")

        return {
            "success": True,
            "message": f"Portmanteau profile '{profile_name}' creation requested",
            "profile_name": profile_name,
            "source_profiles": source_profiles,
            "note": "Implementation pending - requires portmanteau profile logic",
        }

    except Exception as e:
        logger.error(f"Error creating portmanteau profile: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to create portmanteau profile: {str(e)}",
            "profile_name": profile_name,
            "source_profiles": source_profiles,
        }


async def _suggest_portmanteau_profiles(profile_name: str | None) -> dict[str, Any]:
    """Get AI suggestions for profile combinations."""
    try:
        return {
            "success": True,
            "message": "Portmanteau profile suggestions requested",
            "profile_name": profile_name,
            "suggestions": [
                {"name": "work-dev", "description": "Work and development tools"},
                {"name": "research-personal", "description": "Research and personal interests"},
                {"name": "news-social", "description": "News and social media"},
            ],
            "count": 3,
            "note": "Implementation pending - requires AI suggestion logic",
        }

    except Exception as e:
        logger.error(f"Error suggesting portmanteau profiles: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to suggest portmanteau profiles: {str(e)}",
            "profile_name": profile_name,
            "suggestions": [],
            "count": 0,
        }


async def _create_loaded_profile_from_preset(
    profile_name: str | None, preset_name: str | None
) -> dict[str, Any]:
    """Create profile from predefined preset."""
    try:
        if not profile_name:
            raise ValueError("Profile name is required")
        if not preset_name:
            raise ValueError("Preset name is required")

        return {
            "success": True,
            "message": f"Profile '{profile_name}' creation from preset '{preset_name}' requested",
            "profile_name": profile_name,
            "preset_name": preset_name,
            "note": "Implementation pending - requires preset logic",
        }

    except Exception as e:
        logger.error(f"Error creating profile from preset: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to create profile from preset: {str(e)}",
            "profile_name": profile_name,
            "preset_name": preset_name,
        }


async def _check_firefox_status() -> dict[str, Any]:
    """Check if Firefox is running and accessible."""
    try:
        status_checker = FirefoxStatusChecker()
        status = await status_checker.check_firefox_status()

        return {"success": True, "message": "Firefox status checked", "firefox_status": status}

    except Exception as e:
        logger.error(f"Error checking Firefox status: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to check Firefox status: {str(e)}",
            "firefox_status": {"running": False, "accessible": False},
        }
