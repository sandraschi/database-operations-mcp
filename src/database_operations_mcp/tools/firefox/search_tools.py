"""Advanced search functionality for bookmarks with smart profile detection."""

from pathlib import Path
from typing import Any, Dict, List, Optional

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp

from database_operations_mcp.tools.help_tools import HelpSystem
from .db import FirefoxDB
from .exceptions import FirefoxNotClosedError
from .status import FirefoxStatusChecker
from .utils import get_profile_directory, parse_profiles_ini


class SmartProfileDetector:
    """Smart profile detection based on search terms and context."""

    @staticmethod
    def detect_profile_from_query(query: str) -> Optional[str]:
        """Detect which profile to use based on search query.

        Examples:
        - "immich bookmarks" -> looks for profile containing "immich"
        - "work bookmarks" -> looks for profile named "work" or containing "work"
        - "dev profile bookmarks" -> looks for profile named "dev"
        """
        query_lower = query.lower().strip()

        # Common profile indicators
        profile_keywords = {
            "work": ["work", "business", "office", "job"],
            "personal": ["personal", "home", "private"],
            "dev": ["dev", "development", "coding", "programming"],
            "afterwork": ["afterwork", "after-work", "evening", "leisure"],
            "default": ["default", "main"],
        }

        # Check for explicit profile mentions
        for profile_name, keywords in profile_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return profile_name

        # Check for application-specific searches that might indicate profile usage
        app_indicators = {
            "immich": "immich",
            "plex": "media",
            "jellyfin": "media",
            "nextcloud": "cloud",
            "gitlab": "dev",
            "github": "dev",
            "stackoverflow": "dev",
        }

        for app, profile_hint in app_indicators.items():
            if app in query_lower:
                return profile_hint

        return None

    @staticmethod
    def find_matching_profile(detected_name: str) -> Optional[str]:
        """Find an actual profile that matches the detected name."""
        try:
            profiles = parse_profiles_ini()
            if not profiles:
                return None

            # Exact match first
            if detected_name in profiles:
                return detected_name

            # Partial match in profile names
            for profile_name in profiles.keys():
                if detected_name.lower() in profile_name.lower():
                    return profile_name

            # Fuzzy matching for common patterns
            detected_lower = detected_name.lower()
            for profile_name in profiles.keys():
                profile_lower = profile_name.lower()
                # Check if detected name is contained in profile name or vice versa
                if detected_lower in profile_lower or profile_lower in detected_lower:
                    return profile_name

        except Exception:
            pass

        return None


class BookmarkSearcher:
    """Handles bookmark search operations with enhanced safety checks."""

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
            if not safety_check["safe"]:
                raise FirefoxNotClosedError(safety_check["message"])
            self.db = FirefoxDB(self.profile_path)
        return self.db

    def search(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search bookmarks by title or URL."""
        db = self._get_db_connection()
        search_term = f"%{query}%"
        query_sql = """
            SELECT b.id, b.title, p.url, b.dateAdded, b.lastModified, b.parent
            FROM moz_bookmarks b
            JOIN moz_places p ON b.fk = p.id
            WHERE b.type = 1
            AND (b.title LIKE ? OR p.url LIKE ?)
            LIMIT ?
        """
        cursor = db.execute(query_sql, (search_term, search_term, limit))
        return [dict(row) for row in cursor.fetchall()]


@mcp.tool()
@HelpSystem.register_tool(category="firefox")
async def search_bookmarks(
    query: str,
    profile_name: Optional[str] = None,
    limit: int = 50,
    auto_detect_profile: bool = True,
) -> Dict[str, Any]:
    """Search bookmarks by title or URL with smart profile detection.

    This tool can automatically detect which Firefox profile to search based on your query.
    For example, searching "immich bookmarks" will look for a profile containing "immich".

    Args:
        query: Search term to find in bookmark titles or URLs
        profile_name: Specific profile name to search (optional)
        limit: Maximum number of results to return
        auto_detect_profile: Whether to automatically detect profile from query

    Examples:
        - "immich bookmarks" -> searches in profile containing "immich"
        - "work gitlab" -> searches in work-related profile
        - "dev stackoverflow" -> searches in dev profile
    """
    try:
        # Determine which profile to use
        actual_profile_name = profile_name
        profile_path = None
        detection_info = None

        if not actual_profile_name and auto_detect_profile:
            # Try smart profile detection
            detected_profile = SmartProfileDetector.detect_profile_from_query(query)
            if detected_profile:
                matched_profile = SmartProfileDetector.find_matching_profile(detected_profile)
                if matched_profile:
                    actual_profile_name = matched_profile
                    detection_info = {
                        "detected_from_query": detected_profile,
                        "matched_profile": matched_profile,
                        "auto_detection": True,
                    }
                else:
                    detection_info = {
                        "detected_from_query": detected_profile,
                        "matched_profile": None,
                        "auto_detection": True,
                        "note": (
                            f"Detected profile '{detected_profile}' but no matching profile found"
                        ),
                    }

        # Get profile path if we have a profile name
        if actual_profile_name:
            profile_path = get_profile_directory(actual_profile_name)
            if not profile_path:
                return {
                    "status": "error",
                    "message": f"Profile '{actual_profile_name}' not found",
                    "available_profiles": list(parse_profiles_ini().keys())
                    if parse_profiles_ini()
                    else [],
                }

        # Perform the search with safety checks
        searcher = BookmarkSearcher(profile_path)
        results = searcher.search(query, limit)

        response = {
            "status": "success",
            "query": query,
            "count": len(results),
            "results": results,
            "profile_used": actual_profile_name or "default",
        }

        if detection_info:
            response["profile_detection"] = detection_info

        if len(results) == 0:
            response["note"] = (
                "No bookmarks found matching your query. Try different keywords "
                "or check if Firefox is closed."
            )

        return response

    except FirefoxNotClosedError as e:
        return {
            "status": "error",
            "message": str(e),
            "firefox_status": FirefoxStatusChecker.is_firefox_running(),
            "solution": "Close Firefox completely and try again",
        }
    except Exception as e:
        return {"status": "error", "message": f"Search failed: {str(e)}"}


@mcp.tool()
@HelpSystem.register_tool(category="firefox")
async def find_duplicates(
    by: str = "url",  # 'url' or 'title'
    profile_name: Optional[str] = None,
    min_duplicates: int = 2,
) -> Dict[str, Any]:
    """Find duplicate bookmarks based on URL or title.

    Args:
        by: Field to check for duplicates ('url' or 'title')
        profile_name: Firefox profile name to search in (optional)
        min_duplicates: Minimum number of duplicates to report

    Returns:
        Dictionary with duplicate bookmarks grouped by the specified field
    """
    if by not in ("url", "title"):
        return {"status": "error", "message": "'by' parameter must be either 'url' or 'title'"}

    try:
        # Get profile path
        profile_path = None
        if profile_name:
            profile_path = get_profile_directory(profile_name)
            if not profile_path:
                return {
                    "status": "error",
                    "message": f"Profile '{profile_name}' not found",
                    "available_profiles": list(parse_profiles_ini().keys())
                    if parse_profiles_ini()
                    else [],
                }

        # Safety check
        safety_check = FirefoxStatusChecker.check_database_access_safe(profile_path)
        if not safety_check["safe"]:
            return {
                "status": "error",
                "message": safety_check["message"],
                "safety_check": safety_check,
            }

        db = FirefoxDB(profile_path)

        # Query to find duplicates
        query = f"""
            SELECT p.{by}, GROUP_CONCAT(b.id) as ids, COUNT(*) as count
            FROM moz_bookmarks b
            JOIN moz_places p ON b.fk = p.id
            WHERE b.type = 1  -- Bookmarks
            GROUP BY p.{by}
            HAVING COUNT(*) >= ?
            ORDER BY count DESC, p.{by}
        """

        cursor = db.execute(query, (min_duplicates,))
        results = []

        for row in cursor.fetchall():
            item = dict(row)
            item["ids"] = [int(id_str) for id_str in item["ids"].split(",")]
            results.append(item)

        return {
            "status": "success",
            "by": by,
            "profile_used": profile_name or "default",
            "min_duplicates": min_duplicates,
            "count": len(results),
            "duplicates": results,
            "safety_check": safety_check,
        }

    except Exception as e:
        return {"status": "error", "message": f"Error finding duplicates: {str(e)}"}
    finally:
        if "db" in locals():
            db.close()
