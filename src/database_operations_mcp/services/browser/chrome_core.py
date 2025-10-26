"""
Chrome browser bookmark management implementation.

This module provides Chrome-specific bookmark management functionality.
Chrome uses JSON format for bookmarks stored in the Bookmarks file, unlike
Firefox which uses SQLite. This module handles parsing and operations for
Chrome's bookmark format.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from database_operations_mcp.services.browser.base_browser import BaseBrowserManager


class ChromeManager(BaseBrowserManager):
    """Chrome browser bookmark manager implementation.

    Manages Chrome bookmarks by parsing the JSON-based Bookmarks file.
    Supports multiple Chrome profiles and handles Chrome-specific features
    like sync and profile management.

    Chrome Bookmark Storage:
    - Location: %LOCALAPPDATA%/Google/Chrome/User Data/[Profile]/Bookmarks
    - Format: JSON with specific structure
    - Profiles: Stored in User Data folders (Default, Profile 1, Profile 2, etc.)

    Differences from Firefox:
    - Single Bookmarks file (not SQLite database)
    - No explicit folder IDs (folders are nodes with children)
    - Simpler hierarchy (roots.bookmark_bar, roots.other, roots.synced)
    - Synchronization with Google account
    """

    def __init__(self):
        """Initialize Chrome manager."""
        self.chrome_data_dir = self._find_chrome_data_directory()
        self.browser_type = "chrome"

    def _find_chrome_data_directory(self) -> Optional[Path]:
        """Find Chrome User Data directory on this system.

        Searches standard Chrome installation locations across platforms.
        Supports Windows, macOS, and Linux.

        Returns:
            Path to Chrome User Data directory if found
            None if Chrome is not installed

        Platform-specific locations:
        - Windows: %LOCALAPPDATA%/Google/Chrome/User Data
        - macOS: ~/Library/Application Support/Google/Chrome
        - Linux: ~/.config/google-chrome
        """
        import os

        # Try Windows location
        appdata = os.getenv("LOCALAPPDATA")
        if appdata:
            chrome_dir = Path(appdata) / "Google" / "Chrome" / "User Data"
            if chrome_dir.exists():
                return chrome_dir

        # Try macOS location
        home = Path.home()
        chrome_dir = home / "Library" / "Application Support" / "Google" / "Chrome"
        if chrome_dir.exists():
            return chrome_dir

        # Try Linux location
        chrome_dir = home / ".config" / "google-chrome"
        if chrome_dir.exists():
            return chrome_dir

        return None

    async def get_profiles(self) -> List[str]:
        """Get list of available Chrome profiles.

        Chrome stores profiles in the User Data directory. The default profile
        is 'Default', and additional profiles are named 'Profile 1', 'Profile 2', etc.

        Returns:
            List of Chrome profile names

        Raises:
            BrowserNotInstalledError: If Chrome is not installed
        """
        if not self.chrome_data_dir:
            raise RuntimeError("Chrome is not installed or User Data directory not found")

        profiles = []
        if self.chrome_data_dir.exists():
            # Default profile always exists
            if (self.chrome_data_dir / "Default").exists():
                profiles.append("Default")

            # Look for other profiles (Profile 1, Profile 2, etc.)
            for item in self.chrome_data_dir.iterdir():
                if item.is_dir() and item.name.startswith("Profile "):
                    if (item / "Bookmarks").exists():
                        profiles.append(item.name)

        return sorted(profiles)

    async def get_profile_path(self, profile_name: str) -> str:
        """Get filesystem path for Chrome profile.

        Args:
            profile_name: Name of the Chrome profile (e.g., 'Default', 'Profile 1')

        Returns:
            Full path to Chrome profile directory

        Raises:
            ProfileNotFoundError: If profile does not exist
        """
        if not self.chrome_data_dir:
            raise RuntimeError("Chrome is not installed")

        profile_path = self.chrome_data_dir / profile_name

        if not profile_path.exists():
            raise RuntimeError(f'Chrome profile "{profile_name}" not found')

        return str(profile_path)

    async def parse_bookmarks(self, profile_name: str) -> List[Dict[str, Any]]:
        """Parse Chrome bookmarks from JSON format.

        Chrome stores bookmarks in a JSON file with the following structure:
        {
            'roots': {
                'bookmark_bar': {...},
                'other': {...},
                'synced': {...}
            },
            'version': 1,
            'checksum': '...'
        }

        Each root contains nested bookmark and folder nodes.

        Args:
            profile_name: Name of Chrome profile

        Returns:
            List of bookmarks in standardized format

        Raises:
            ProfileNotFoundError: If profile does not exist
            CorruptBookmarkError: If Bookmarks file is corrupted
            PermissionError: If access is denied
        """
        db_path = self.get_database_path(profile_name)
        bookmarks_file = Path(db_path)

        if not bookmarks_file.exists():
            raise RuntimeError(f"Chrome Bookmarks file not found: {db_path}")

        try:
            with open(bookmarks_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            bookmarks = []
            roots = data.get("roots", {})

            # Parse all root folders
            for root_name in ["bookmark_bar", "other", "synced"]:
                if root_name in roots:
                    bookmarks.extend(self._parse_bookmark_node(roots[root_name], root_name, ""))

            return bookmarks

        except json.JSONDecodeError as e:
            raise RuntimeError(f"Corrupted Chrome Bookmarks file: {e}") from e
        except PermissionError:
            raise RuntimeError("Permission denied accessing Chrome Bookmarks") from None
        except Exception as e:
            raise RuntimeError(f"Error parsing Chrome Bookmarks: {e}") from e

    def _parse_bookmark_node(
        self, node: Dict[str, Any], root_name: str, folder_path: str
    ) -> List[Dict[str, Any]]:
        """Recursively parse bookmark nodes from Chrome structure.

        Chrome nodes can be either 'url' (bookmark) or 'folder' types.
        This method recursively processes all nodes to extract bookmarks.

        Args:
            node: Chrome bookmark node dictionary
            root_name: Name of the root (bookmark_bar, other, synced)
            folder_path: Current folder path for hierarchy

        Returns:
            List of parsed bookmarks
        """
        bookmarks = []
        node_type = node.get("type", "unknown")

        if node_type == "url":
            # This is a bookmark
            bookmark = {
                "id": node.get("id", 0),
                "title": node.get("name", ""),
                "url": node.get("url", ""),
                "folder_path": folder_path,
                "added_date": node.get("date_added", "0"),
                "last_modified": node.get("date_modified", "0"),
                "tags": node.get("tags", []),
                "root": root_name,
            }
            bookmarks.append(bookmark)

        elif node_type == "folder":
            # This is a folder - recursively process children
            folder_name = node.get("name", "Unknown")
            new_folder_path = f"{folder_path}/{folder_name}" if folder_path else folder_name

            children = node.get("children", [])
            for child in children:
                bookmarks.extend(self._parse_bookmark_node(child, root_name, new_folder_path))

        return bookmarks

    async def list_tags(self, profile_name: str) -> List[str]:
        """List all tags used in Chrome bookmarks.

        Chrome doesn't have built-in tag support like Firefox, but we can
        extract tags from custom fields or detect patterns in bookmark
        titles and folders.

        Args:
            profile_name: Name of Chrome profile

        Returns:
            List of unique tags (if any exist in custom fields)
        """
        bookmarks = await self.parse_bookmarks(profile_name)
        tags = set()

        for bookmark in bookmarks:
            bookmark_tags = bookmark.get("tags", [])
            if isinstance(bookmark_tags, list):
                tags.update(bookmark_tags)
            elif bookmark_tags:
                tags.add(bookmark_tags)

        return sorted(list(tags))

    async def search_bookmarks(
        self,
        profile_name: str,
        query: str,
        tags: Optional[List[str]] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Search Chrome bookmarks with flexible criteria.

        Performs case-insensitive search on bookmark titles and URLs,
        with optional tag filtering.

        Args:
            profile_name: Name of Chrome profile
            query: Search query string
            tags: Optional list of tags to filter by
            limit: Maximum results (default: 100)

        Returns:
            List of matching bookmarks
        """
        bookmarks = await self.parse_bookmarks(profile_name)
        query_lower = query.lower()
        results = []

        for bookmark in bookmarks:
            # Check title and URL match
            title = bookmark.get("title", "").lower()
            url = bookmark.get("url", "").lower()

            if query_lower not in title and query_lower not in url:
                continue

            # Check tag filter
            if tags:
                bookmark_tags = bookmark.get("tags", [])
                bookmark_tags = [bookmark_tags] if isinstance(bookmark_tags, str) else bookmark_tags
                if not any(tag in bookmark_tags for tag in tags):
                    continue

            results.append(bookmark)
            if len(results) >= limit:
                break

        return results

    def get_database_path(self, profile_name: str) -> str:
        """Get path to Chrome Bookmarks file.

        Chrome stores bookmarks in a JSON file named 'Bookmarks' in each
        profile's directory.

        Args:
            profile_name: Name of Chrome profile

        Returns:
            Full path to Bookmarks file

        Raises:
            ProfileNotFoundError: If profile does not exist
        """
        profile_path = self.chrome_data_dir / profile_name
        bookmarks_file = profile_path / "Bookmarks"

        return str(bookmarks_file)

    async def is_database_locked(self, profile_name: str) -> bool:
        """Check if Chrome database is locked.

        Chrome locks the Bookmarks file while running. We detect this by
        checking if Chrome processes are running.

        Args:
            profile_name: Name of Chrome profile

        Returns:
            True if Chrome is running (database locked)
            False if Chrome is closed (database unlocked)
        """
        import psutil

        # Check for Chrome processes
        for proc in psutil.process_iter(["name"]):
            try:
                name = proc.info["name"].lower()
                if "chrome" in name and "chrome.exe" in name:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return False

    async def backup_profile(self, profile_name: str, backup_path: str) -> str:
        """Create backup of Chrome profile.

        Backs up the Bookmarks file and other profile data.

        Args:
            profile_name: Name of profile to backup
            backup_path: Destination path for backup

        Returns:
            Path to created backup file
        """
        import shutil
        from datetime import datetime

        profile_path = Path(await self.get_profile_path(profile_name))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"chrome_{profile_name}_{timestamp}.zip"
        backup_file = Path(backup_path) / backup_name

        # Create backup ZIP
        shutil.make_archive(str(backup_file.with_suffix("")), "zip", str(profile_path))

        return str(backup_file)

    async def restore_profile(
        self, profile_name: str, backup_file: str, overwrite: bool = False
    ) -> Dict[str, Any]:
        """Restore Chrome profile from backup.

        Args:
            profile_name: Name of profile to restore to
            backup_file: Path to backup file
            overwrite: Whether to overwrite existing profile

        Returns:
            Restore results dictionary
        """
        import zipfile

        backup_path = Path(backup_file)
        if not backup_path.exists():
            raise RuntimeError(f"Backup file not found: {backup_file}")

        profile_path = Path(await self.get_profile_path(profile_name))

        if profile_path.exists() and not overwrite:
            raise RuntimeError(
                f"Profile {profile_name} already exists. Use overwrite=True to replace."
            )

        # Extract backup
        with zipfile.ZipFile(backup_file, "r") as zip_ref:
            zip_ref.extractall(profile_path)

        return {
            "success": True,
            "profile_name": profile_name,
            "items_restored": {"bookmarks": 0, "settings": 0},
            "warnings": [],
        }

    def get_browser_type(self) -> str:
        """Get Chrome browser type identifier.

        Returns:
            'chrome'
        """
        return "chrome"
