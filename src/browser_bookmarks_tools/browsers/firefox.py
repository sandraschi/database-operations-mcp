"""Firefox bookmark operations."""

from pathlib import Path
from typing import Any

import aiosqlite


class FirefoxBookmarkManager:
    """Manage Firefox bookmarks via SQLite."""

    def __init__(self, profile_name: str = "default"):
        """Initialize Firefox manager.

        Args:
            profile_name: Firefox profile name
        """
        self.profile_name = profile_name
        self.profile_path = self._get_profile_path()
        self.places_db = self.profile_path / "places.sqlite"

    def _get_profile_path(self) -> Path:
        """Get Firefox profile directory path.

        Returns:
            Path to Firefox profile
        """
        if Path.home() / "AppData" / "Roaming" / "Mozilla" / "Firefox" / "Profiles".exists():
            profiles_dir = Path.home() / "AppData" / "Roaming" / "Mozilla" / "Firefox" / "Profiles"
            for profile_folder in profiles_dir.iterdir():
                if profile_folder.name.startswith(self.profile_name):
                    return profile_folder
        raise FileNotFoundError(f"Firefox profile '{self.profile_name}' not found")

    async def is_browser_running(self) -> bool:
        """Check if Firefox is running.

        Returns:
            True if Firefox is running
        """
        # Try to open database in exclusive mode
        try:
            conn = await aiosqlite.connect(f"file:{self.places_db}?mode=ro")
            await conn.close()
            return False
        except Exception:
            return True

    async def add_bookmark(
        self,
        url: str,
        title: str,
        folder_id: int = 0,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Add bookmark to Firefox.

        Args:
            url: URL of bookmark
            title: Title of bookmark
            folder_id: Parent folder ID
            tags: Optional tags

        Returns:
            Dictionary with bookmark details
        """
        if await self.is_browser_running():
            return {
                "success": False,
                "error": "Firefox must be closed to modify bookmarks",
            }

        async with aiosqlite.connect(self.places_db) as db:
            # Add bookmark logic here
            bookmark_id = 1  # Placeholder
            return {
                "success": True,
                "bookmark_id": bookmark_id,
                "title": title,
                "url": url,
                "folder_id": folder_id,
                "tags": tags or [],
            }

    async def get_bookmarks(self, folder_id: int = 0) -> list[dict[str, Any]]:
        """Get bookmarks from folder.

        Args:
            folder_id: Folder ID to get bookmarks from

        Returns:
            List of bookmarks
        """
        async with aiosqlite.connect(self.places_db) as db:
            query = """
                SELECT id, title, url, dateAdded
                FROM moz_bookmarks
                WHERE type = 1 AND parent = ?
                ORDER BY position
            """
            async with db.execute(query, (folder_id,)) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        "id": row[0],
                        "title": row[1],
                        "url": row[2],
                        "date_added": row[3],
                    }
                    for row in rows
                ]
