"""Utility functions for Firefox bookmark management."""

import configparser
import os
from pathlib import Path
from typing import Any

from database_operations_mcp.config.mcp_config import mcp


def get_platform() -> str:
    """Get the current platform identifier."""
    if os.name == "nt":
        return "windows"
    elif os.name == "posix":
        if "darwin" in os.uname().sysname.lower():
            return "darwin"
    return "linux"


def get_profiles_ini_path() -> Path | None:
    """Get the path to profiles.ini based on the platform."""
    platform = get_platform()
    if platform == "windows":
        return Path(os.environ.get("APPDATA", "")) / "Mozilla" / "Firefox" / "profiles.ini"
    elif platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Firefox" / "profiles.ini"
    else:  # linux
        return Path.home() / ".mozilla" / "firefox" / "profiles.ini"


def parse_profiles_ini() -> dict[str, dict[str, Any]]:
    """Parse Firefox profiles.ini and return profile information."""
    profiles_ini = get_profiles_ini_path()
    if not profiles_ini or not profiles_ini.exists():
        return {}

    config = configparser.ConfigParser()
    config.read(profiles_ini)

    profiles = {}
    for section in config.sections():
        if section.startswith("Profile"):
            profile = dict(config[section])
            if "Path" in profile:
                profiles[profile.get("Name", profile["Path"])] = profile
    return profiles


def get_profile_directory(profile_name: str | None = None) -> Path | None:
    """Get the directory path for a Firefox profile."""
    profiles = parse_profiles_ini()
    if not profiles:
        return None

    if not profile_name:
        # Try to find default profile
        for name, profile in profiles.items():
            if profile.get("Default", "0") == "1":
                profile_name = name
                break
        else:
            # If no default, use the first profile
            profile_name = next(iter(profiles.keys()), None)

    if profile_name not in profiles:
        return None

    profile = profiles[profile_name]
    if profile.get("IsRelative", "1") == "1":
        base_dir = get_profiles_ini_path().parent
        return base_dir / profile["Path"]
    else:
        return Path(profile["Path"])


def get_places_db_path(profile_name: str | None = None) -> Path | None:
    """Get the path to the places.sqlite file for a profile."""
    profile_dir = get_profile_directory(profile_name)
    if not profile_dir:
        return None
    return profile_dir / "places.sqlite"


@mcp.tool()
def get_firefox_platform() -> dict[str, Any]:
    """
    Get the current platform identifier for Firefox operations.

    Returns:
        Dict containing platform information
    """
    platform = get_platform()
    return {"platform": platform, "os_name": os.name, "message": f"Detected platform: {platform}"}


@mcp.tool()
def get_firefox_profiles() -> dict[str, Any]:
    """
    Get all available Firefox profiles.

    Returns:
        Dict containing profile information and paths
    """
    profiles = parse_profiles_ini()
    profiles_ini_path = get_profiles_ini_path()

    return {
        "profiles": profiles,
        "profiles_ini_path": str(profiles_ini_path) if profiles_ini_path else None,
        "count": len(profiles),
        "message": f"Found {len(profiles)} Firefox profiles",
    }


@mcp.tool()
def get_firefox_profile_directory(profile_name: str | None = None) -> dict[str, Any]:
    """
    Get the directory path for a Firefox profile.

    Args:
        profile_name: Name of the profile (optional, uses default if not provided)

    Returns:
        Dict containing profile directory information
    """
    profile_dir = get_profile_directory(profile_name)

    if not profile_dir:
        return {
            "success": False,
            "message": f"Profile '{profile_name or 'default'}' not found",
            "profile_directory": None,
        }

    return {
        "success": True,
        "profile_name": profile_name,
        "profile_directory": str(profile_dir),
        "message": f"Found profile directory: {profile_dir}",
    }


@mcp.tool()
def get_firefox_places_db_path(profile_name: str | None = None) -> dict[str, Any]:
    """
    Get the path to the places.sqlite file for a Firefox profile.

    Args:
        profile_name: Name of the profile (optional, uses default if not provided)

    Returns:
        Dict containing database path information
    """
    db_path = get_places_db_path(profile_name)

    if not db_path:
        return {
            "success": False,
            "message": f"Could not find places.sqlite for profile '{profile_name or 'default'}'",
            "database_path": None,
        }

    return {
        "success": True,
        "profile_name": profile_name,
        "database_path": str(db_path),
        "exists": db_path.exists(),
        "message": f"Found places.sqlite at: {db_path}",
    }
