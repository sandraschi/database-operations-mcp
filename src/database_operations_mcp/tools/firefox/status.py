"""Firefox status checking utilities."""

from pathlib import Path
from typing import Any, Dict, Optional

import psutil

from database_operations_mcp.config.mcp_config import mcp


class FirefoxStatusChecker:
    """Comprehensive Firefox status checking and profile management."""

    @staticmethod
    def is_firefox_running() -> Dict[str, Any]:
        """Check if Firefox is running with detailed status."""
        try:
            firefox_processes = []
            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    if "firefox" in proc.info["name"].lower():
                        firefox_processes.append(
                            {
                                "pid": proc.info["pid"],
                                "name": proc.info["name"],
                                "cmdline": proc.info["cmdline"][:3]
                                if proc.info["cmdline"]
                                else [],  # First 3 args only
                            }
                        )
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue

            is_running = len(firefox_processes) > 0
            return {
                "is_running": is_running,
                "process_count": len(firefox_processes),
                "processes": firefox_processes,
                "message": (
                    f"Firefox is {'running' if is_running else 'not running'} "
                    f"({len(firefox_processes)} processes)"
                ),
            }
        except Exception as e:
            return {
                "is_running": False,
                "error": f"Could not check Firefox status: {str(e)}",
                "message": "Unable to determine Firefox status",
            }

    @staticmethod
    def check_database_access_safe(profile_path: Optional[Path] = None) -> Dict[str, Any]:
        """Check if it's safe to access Firefox databases."""
        status = FirefoxStatusChecker.is_firefox_running()

        if status.get("error"):
            return {
                "safe": False,
                "reason": "status_check_failed",
                "message": status["message"],
                "details": status,
            }

        if status["is_running"]:
            return {
                "safe": False,
                "reason": "firefox_running",
                "message": (
                    "Firefox is currently running. Close Firefox before accessing "
                    "bookmark databases to prevent data corruption."
                ),
                "details": status,
            }

        # Check if profile path exists and is accessible
        if profile_path:
            if not profile_path.exists():
                return {
                    "safe": False,
                    "reason": "profile_not_found",
                    "message": f"Firefox profile not found at: {profile_path}",
                    "details": {"profile_path": str(profile_path)},
                }

            places_db = profile_path / "places.sqlite"
            if not places_db.exists():
                return {
                    "safe": False,
                    "reason": "database_not_found",
                    "message": f"Firefox places.sqlite database not found at: {places_db}",
                    "details": {"database_path": str(places_db)},
                }

        return {"safe": True, "message": "Safe to access Firefox databases", "details": status}


@mcp.tool()
def is_firefox_running() -> Dict[str, Any]:
    """
    Check if Firefox is currently running.
    
    Returns detailed status information about Firefox processes.
    
    Returns:
        Dict containing Firefox running status, process count, and details
    """
    return FirefoxStatusChecker.is_firefox_running()


@mcp.tool()
def check_firefox_database_access_safe(profile_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Check if it's safe to access Firefox bookmark databases.
    
    Args:
        profile_path: Optional path to Firefox profile directory
        
    Returns:
        Dict containing safety status and recommendations
    """
    path_obj = Path(profile_path) if profile_path else None
    return FirefoxStatusChecker.check_database_access_safe(path_obj)
