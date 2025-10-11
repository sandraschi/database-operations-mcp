"""Core bookmark management functionality with enhanced safety checks."""
from pathlib import Path
from typing import List, Dict, Any, Optional
from . import mcp  # Import the mcp instance from __init__
from .db import FirefoxDB
from .core import FirefoxStatusChecker, FirefoxNotClosedError
from .utils import get_profile_directory

class BookmarkManager:
    """Handles bookmark operations with safety checks."""

    def __init__(self, profile_path: Optional[Path] = None):
        self.profile_path = profile_path
        self.db = None

    def _ensure_safe_access(self) -> Dict[str, Any]:
        """Ensure it's safe to access the database."""
        return FirefoxStatusChecker.check_database_access_safe(self.profile_path)

    def _get_db_connection(self) -> FirefoxDB:
        """Get database connection with safety checks."""
        if self.db is None:
            safety_check = self._ensure_safe_access()
            if not safety_check['safe']:
                raise FirefoxNotClosedError(safety_check['message'])
            self.db = FirefoxDB(self.profile_path)
        return self.db

    def get_bookmarks(self, folder_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve bookmarks, optionally filtered by folder."""
        db = self._get_db_connection()
        query = """
            SELECT b.id, b.title, p.url, b.dateAdded, b.lastModified, b.parent
            FROM moz_bookmarks b
            JOIN moz_places p ON b.fk = p.id
            WHERE b.type = 1
        """
        params = []
        if folder_id is not None:
            query += " AND b.parent = ?"
            params.append(folder_id)

        cursor = db.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

@mcp.tool()
async def list_bookmarks(
    profile_name: Optional[str] = None,
    folder_id: Optional[int] = None
) -> Dict[str, Any]:
    """List bookmarks with optional folder filtering.

    Args:
        profile_name: Firefox profile name to list bookmarks from (optional)
        folder_id: Specific folder ID to list bookmarks from (optional)

    Note: Firefox must be closed to access bookmark databases safely.
    """
    try:
        # Get profile path
        profile_path = None
        if profile_name:
            profile_path = get_profile_directory(profile_name)
            if not profile_path:
                return {
                    "status": "error",
                    "message": f"Profile '{profile_name}' not found"
                }

        manager = BookmarkManager(profile_path)
        bookmarks = manager.get_bookmarks(folder_id)

        response = {
            "status": "success",
            "profile_used": profile_name or "default",
            "count": len(bookmarks),
            "bookmarks": bookmarks
        }

        if len(bookmarks) == 0:
            response["note"] = "No bookmarks found. This could mean the profile is empty or Firefox is running."

        return response

    except FirefoxNotClosedError as e:
        return {
            "status": "error",
            "message": str(e),
            "firefox_status": FirefoxStatusChecker.is_firefox_running(),
            "solution": "Close Firefox completely and try again"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to list bookmarks: {str(e)}"
        }