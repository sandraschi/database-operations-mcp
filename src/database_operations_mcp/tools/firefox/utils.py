"""Utility functions for Firefox bookmark management."""

import configparser
import os
from pathlib import Path
from typing import Any, Dict, Optional


def get_platform() -> str:
    """Get the current platform identifier."""
    if os.name == "nt":
        return "windows"
    elif os.name == "posix":
        if "darwin" in os.uname().sysname.lower():
            return "darwin"
    return "linux"


def get_profiles_ini_path() -> Optional[Path]:
    """Get the path to profiles.ini based on the platform."""
    platform = get_platform()
    if platform == "windows":
        return Path(os.environ.get("APPDATA", "")) / "Mozilla" / "Firefox" / "profiles.ini"
    elif platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Firefox" / "profiles.ini"
    else:  # linux
        return Path.home() / ".mozilla" / "firefox" / "profiles.ini"


def parse_profiles_ini() -> Dict[str, Dict[str, Any]]:
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


def get_profile_directory(profile_name: Optional[str] = None) -> Optional[Path]:
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


def get_places_db_path(profile_name: Optional[str] = None) -> Optional[Path]:
    """Get the path to the places.sqlite file for a profile."""
    profile_dir = get_profile_directory(profile_name)
    if not profile_dir:
        return None
    return profile_dir / "places.sqlite"
