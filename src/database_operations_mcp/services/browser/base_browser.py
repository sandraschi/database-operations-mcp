"""
Base browser bookmark management interface.

This module provides the abstract base class for browser-specific bookmark
managers. All browser implementations (Firefox, Chrome, Edge, etc.) inherit
from this class to ensure consistent interfaces.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseBrowserManager(ABC):
    """Base class for browser bookmark management.

    This abstract base class defines the interface that all browser-specific
    bookmark managers must implement. It provides a consistent API for
    bookmark operations across different browsers.

    All browser managers should inherit from this class and implement the
    abstract methods to provide browser-specific functionality while
    maintaining a consistent interface for the MCP tools.
    """

    @abstractmethod
    async def get_profiles(self) -> list[str]:
        """Get list of available browser profiles.

        Returns a list of profile names or identifiers that can be used
        in subsequent operations. The exact format depends on the browser.

        Returns:
            List of profile names/identifiers:
                - Firefox: ['default', 'work', 'personal']
                - Chrome: ['Default', 'Profile 1', 'Profile 2']
                - Edge: ['Default', 'Profile 1']

        Raises:
            BrowserNotInstalledError: If browser is not installed
            PermissionError: If access to browser data is denied
        """
        pass

    @abstractmethod
    async def get_profile_path(self, profile_name: str) -> str:
        """Get filesystem path for a specific profile.

        Args:
            profile_name: Name or identifier of the profile

        Returns:
            Full filesystem path to the profile directory

        Raises:
            ProfileNotFoundError: If profile does not exist
        """
        pass

    @abstractmethod
    async def parse_bookmarks(self, profile_name: str) -> list[dict[str, Any]]:
        """Parse bookmarks from browser-specific format.

        Extracts bookmarks from the browser's storage format and converts
        them to a standardized format for MCP tools.

        Args:
            profile_name: Name or identifier of the profile

        Returns:
            List of bookmark dictionaries with standardized structure:
                [
                    {
                        'id': int,           # Unique bookmark ID
                        'title': str,         # Bookmark title
                        'url': str,          # Bookmark URL
                        'folder_id': int,    # Parent folder ID
                        'folder_path': str,  # Full folder path
                        'added_date': int,   # Timestamp (Unix epoch)
                        'last_modified': int, # Last modified timestamp
                        'tags': List[str],   # Bookmarks tags (if any)
                    },
                    ...
                ]

        Raises:
            ProfileNotFoundError: If profile does not exist
            CorruptBookmarkError: If bookmark data is corrupted
            PermissionError: If access to bookmark data is denied
        """
        pass

    @abstractmethod
    async def list_tags(self, profile_name: str) -> list[str]:
        """List all tags used in bookmarks.

        Returns all unique tags found across all bookmarks in the profile.

        Args:
            profile_name: Name or identifier of the profile

        Returns:
            List of unique tag strings sorted alphabetically

        Raises:
            ProfileNotFoundError: If profile does not exist
        """
        pass

    @abstractmethod
    async def search_bookmarks(
        self,
        profile_name: str,
        query: str,
        tags: list[str] | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Search bookmarks with flexible criteria.

        Performs full-text search on bookmark titles and URLs, with optional
        filtering by tags. Supports fuzzy matching and relevance ranking.

        Args:
            profile_name: Name or identifier of the profile
            query: Search query string (searches title and URL)
            tags: Optional list of tags to filter by (AND logic)
            limit: Maximum number of results to return (default: 100)

        Returns:
            List of matching bookmarks sorted by relevance

        Raises:
            ProfileNotFoundError: If profile does not exist
        """
        pass

    @abstractmethod
    def get_database_path(self, profile_name: str) -> str:
        """Get path to browser's bookmark database file.

        Returns the full path to the browser's bookmark storage file.
        Format varies by browser:
        - Firefox: places.sqlite (SQLite database)
        - Chrome: Bookmarks (JSON file)
        - Edge: Bookmarks (JSON file, same as Chrome)

        Args:
            profile_name: Name or identifier of the profile

        Returns:
            Full path to bookmark database file

        Raises:
            ProfileNotFoundError: If profile does not exist
        """
        pass

    @abstractmethod
    async def is_database_locked(self, profile_name: str) -> bool:
        """Check if browser database is currently locked.

        Browsers lock their database files while running to prevent corruption.
        This method checks if it's safe to access the database.

        Args:
            profile_name: Name or identifier of the profile

        Returns:
            True if database is locked (browser running)
            False if database is unlocked (browser closed)

        Raises:
            ProfileNotFoundError: If profile does not exist
            PermissionError: If access check fails
        """
        pass

    @abstractmethod
    async def backup_profile(self, profile_name: str, backup_path: str) -> str:
        """Create backup of browser profile.

        Creates a complete backup of the browser profile including bookmarks,
        settings, and other data. Returns path to backup file.

        Args:
            profile_name: Name or identifier of the profile to backup
            backup_path: Destination path for backup file

        Returns:
            Full path to created backup file

        Raises:
            ProfileNotFoundError: If profile does not exist
            BackupError: If backup creation fails
        """
        pass

    @abstractmethod
    async def restore_profile(
        self, profile_name: str, backup_file: str, overwrite: bool = False
    ) -> dict[str, Any]:
        """Restore browser profile from backup.

        Restores a profile from a previously created backup. Can optionally
        overwrite existing profile data.

        Args:
            profile_name: Name of profile to restore to
            backup_file: Path to backup file created by backup_profile
            overwrite: Whether to overwrite existing profile data
                     (default: False, creates new profile)

        Returns:
            Dictionary with restore results:
                {
                    'success': bool,
                    'profile_name': str,
                    'items_restored': Dict[str, int],
                    'warnings': List[str],
                }

        Raises:
            ProfileNotFoundError: If target profile exists and overwrite=False
            BackupError: If restore fails
            CorruptBackupError: If backup file is invalid
        """
        pass

    async def get_profile_info(self, profile_name: str) -> dict[str, Any]:
        """Get information about a profile.

        Returns metadata and statistics about the profile including bookmark
        counts, installation paths, and browser version.

        Args:
            profile_name: Name or identifier of the profile

        Returns:
            Dictionary with profile information:
                {
                    'profile_name': str,
                    'profile_path': str,
                    'database_path': str,
                    'bookmark_count': int,
                    'folder_count': int,
                    'last_accessed': str,
                    'browser_version': str,
                    'is_default': bool,
                }

        Raises:
            ProfileNotFoundError: If profile does not exist
        """
        bookmarks = await self.parse_bookmarks(profile_name)
        db_path = self.get_database_path(profile_name)

        # Calculate bookmark count
        bookmark_count = len([b for b in bookmarks if b.get("url")])

        # Calculate folder count
        folders = set()
        for bookmark in bookmarks:
            folder_path = bookmark.get("folder_path", "")
            if folder_path:
                folders.add(folder_path)
        folder_count = len(folders)

        profile_path = await self.get_profile_path(profile_name)

        return {
            "profile_name": profile_name,
            "profile_path": profile_path,
            "database_path": db_path,
            "bookmark_count": bookmark_count,
            "folder_count": folder_count,
            "last_accessed": None,  # Browser-specific implementation
            "browser_version": self.get_browser_type(),
            "is_default": profile_name == "Default",
        }

    @abstractmethod
    def get_browser_type(self) -> str:
        """Get browser type identifier.

        Returns a string identifying the browser type for use in UI and
        error messages. Should be lowercase (e.g., 'firefox', 'chrome').

        Returns:
            Browser type identifier (e.g., 'firefox', 'chrome', 'edge')
        """
        pass

    async def validate_profile(self, profile_name: str) -> bool:
        """Validate that a profile exists and is accessible.

        Checks if the profile exists and the bookmark database is accessible.
        This is a quick validation without full parsing.

        Args:
            profile_name: Name or identifier of the profile

        Returns:
            True if profile is valid and accessible
            False if profile doesn't exist or is locked

        Raises:
            BrowserNotInstalledError: If browser is not installed
        """
        try:
            db_path = self.get_database_path(profile_name)
            return Path(db_path).exists() and not await self.is_database_locked(profile_name)
        except Exception:
            return False

    def format_bookmark_path(self, bookmark: dict[str, Any]) -> str:
        """Format bookmark for display with full path.

        Creates a human-readable path string for a bookmark including its
        folder hierarchy.

        Args:
            bookmark: Bookmark dictionary from parse_bookmarks

        Returns:
            Formatted path string like "Work > Projects > Project X > Bookmark Title"
        """
        folder_path = bookmark.get("folder_path", "")
        title = bookmark.get("title", "Unknown")

        if folder_path:
            return f"{folder_path} > {title}"
        return title
