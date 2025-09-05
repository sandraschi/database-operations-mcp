"""Core Firefox bookmark functionality."""
import os
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional
import psutil
from . import mcp  # Import the mcp instance from __init__

class FirefoxNotClosedError(Exception):
    """Raised when Firefox is running and database access would be unsafe."""
    pass

def is_firefox_running() -> bool:
    """Check if Firefox is running."""
    try:
        return any('firefox' in p.name().lower() for p in psutil.process_iter(['name']))
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return False

def get_default_profile_path() -> Optional[Path]:
    """Get the path to the default Firefox profile."""
    if os.name == 'nt':  # Windows
        path = Path(os.environ.get('APPDATA', '')) / 'Mozilla' / 'Firefox' / 'Profiles'
    else:  # Linux/Mac
        path = Path.home() / '.mozilla' / 'firefox'
    
    if not path.exists():
        return None
        
    profiles_ini = path.parent / 'profiles.ini'
    if not profiles_ini.exists():
        return None
        
    return path  # Simplified for brevity

@mcp.tool
async def get_firefox_profiles() -> Dict[str, Any]:
    """List available Firefox profiles."""
    if is_firefox_running():
        return {
            "status": "error",
            "message": "Firefox must be closed to access profile information"
        }
    
    profile_path = get_default_profile_path()
    if not profile_path:
        return {"status": "error", "message": "No Firefox profiles found"}
    
    return {
        "status": "success",
        "profiles": {
            "default": {
                "path": str(profile_path),
                "bookmarks_file": str(profile_path / "places.sqlite")
            }
        }
    }