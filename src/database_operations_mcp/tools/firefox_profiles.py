# Firefox profile management portmanteau tool.
# Consolidates all Firefox profile operations into a single interface.

import logging
from typing import Any, Dict, List, Optional

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.tools.help_tools import HelpSystem
from database_operations_mcp.tools.firefox.db import FirefoxDB
from database_operations_mcp.tools.firefox.status import FirefoxStatusChecker

logger = logging.getLogger(__name__)


@mcp.tool()
@HelpSystem.register_tool(category="firefox")
async def firefox_profiles(
    operation: str,
    profile_name: Optional[str] = None,
    source_profiles: Optional[List[str]] = None,
    preset_name: Optional[str] = None,
    profile_config: Optional[Dict[str, Any]] = None,
    check_status: bool = True,
    include_bookmarks: bool = True,
    include_settings: bool = True,
) -> Dict[str, Any]:
    """Firefox profile management portmanteau tool.

    This tool consolidates all Firefox profile operations into a single interface,
    providing unified access to profile management functionality.

    Operations:
    - get_firefox_profiles: List all available Firefox profiles
    - create_firefox_profile: Create a new Firefox profile
    - delete_firefox_profile: Delete an existing Firefox profile
    - create_loaded_profile: Create a profile with specific bookmarks loaded
    - create_portmanteau_profile: Create a hybrid profile from multiple sources
    - suggest_portmanteau_profiles: Get AI suggestions for profile combinations
    - create_loaded_profile_from_preset: Create profile from predefined preset
    - check_firefox_status: Check if Firefox is running and accessible

    Args:
        operation: The operation to perform (required)
        profile_name: Name of the Firefox profile
        source_profiles: List of source profiles for portmanteau creation
        preset_name: Name of the preset to use
        profile_config: Configuration for the new profile
        check_status: Whether to check Firefox status during operations
        include_bookmarks: Whether to include bookmarks in profile operations
        include_settings: Whether to include settings in profile operations

    Returns:
        Dictionary with operation results and profile information

    Examples:
        List profiles:
        firefox_profiles(operation='get_firefox_profiles')

        Create profile:
        firefox_profiles(operation='create_firefox_profile', profile_name='work')

        Delete profile:
        firefox_profiles(operation='delete_firefox_profile', profile_name='old_profile')

        Create loaded profile:
        firefox_profiles(operation='create_loaded_profile', profile_name='dev',
                        source_profiles=['work', 'personal'])

        Create portmanteau profile:
        firefox_profiles(operation='create_portmanteau_profile', profile_name='hybrid',
                        source_profiles=['work', 'research', 'personal'])

        Get suggestions:
        firefox_profiles(operation='suggest_portmanteau_profiles', profile_name='new_profile')

        Create from preset:
        firefox_profiles(operation='create_loaded_profile_from_preset',
                        profile_name='developer', preset_name='dev_tools')

        Check status:
        firefox_profiles(operation='check_firefox_status')
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


async def _get_firefox_profiles() -> Dict[str, Any]:
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
    profile_name: Optional[str], profile_config: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
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


async def _delete_firefox_profile(profile_name: Optional[str]) -> Dict[str, Any]:
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
    profile_name: Optional[str],
    source_profiles: Optional[List[str]],
    include_bookmarks: bool,
    include_settings: bool,
) -> Dict[str, Any]:
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
    profile_name: Optional[str], source_profiles: Optional[List[str]]
) -> Dict[str, Any]:
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


async def _suggest_portmanteau_profiles(profile_name: Optional[str]) -> Dict[str, Any]:
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
    profile_name: Optional[str], preset_name: Optional[str]
) -> Dict[str, Any]:
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


async def _check_firefox_status() -> Dict[str, Any]:
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
