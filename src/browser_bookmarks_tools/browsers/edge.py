"""Edge browser bookmark handling."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class EdgeBrowser:
    """Edge browser bookmark manager."""

    def __init__(self) -> None:
        """Initialize Edge browser handler."""
        self.bookmark_file = self._find_bookmark_file()

    def _find_bookmark_file(self) -> Path | None:
        """Find Edge bookmarks file."""
        import os

        if os.name == "nt":  # Windows
            appdata = os.getenv("LOCALAPPDATA")
            if appdata:
                return (
                    Path(appdata)
                    / "Microsoft"
                    / "Edge"
                    / "User Data"
                    / "Default"
                    / "Bookmarks"
                )
        else:
            home = Path.home()
            return home / ".config" / "microsoft-edge" / "Default" / "Bookmarks"
        return None

    async def get_bookmarks(self, folder: str | None = None) -> list[dict[str, Any]]:
        """Get bookmarks from Edge (uses Chrome format)."""
        if not self.bookmark_file or not self.bookmark_file.exists():
            logger.error("Edge bookmarks file not found")
            return []

        try:
            with open(self.bookmark_file, encoding="utf-8") as f:
                data = json.load(f)

            def extract_bookmarks(node: dict[str, Any], target_folder: str | None = None) -> list[dict[str, Any]]:
                bookmarks = []
                if node.get("type") == "bookmark":
                    bookmarks.append(
                        {
                            "id": node.get("id"),
                            "url": node.get("url"),
                            "title": node.get("name"),
                            "date_added": node.get("date_added"),
                            "folder": target_folder,
                        }
                    )
                elif node.get("type") == "folder":
                    children = node.get("children", [])
                    current_folder = node.get("name")
                    if target_folder is None or current_folder == target_folder:
                        for child in children:
                            bookmarks.extend(extract_bookmarks(child, current_folder))
                    else:
                        for child in children:
                            bookmarks.extend(extract_bookmarks(child, target_folder))
                return bookmarks

            all_bookmarks = []
            roots = data.get("roots", {})
            for root_name in roots:
                all_bookmarks.extend(extract_bookmarks(roots[root_name], folder))

            return all_bookmarks
        except Exception as e:
            logger.error(f"Error reading Edge bookmarks: {e}", exc_info=True)
            return []

    async def add_bookmark(self, url: str, title: str, folder: str | None = None) -> dict[str, Any]:
        """Add bookmark to Edge."""
        return {"success": False, "error": "Not implemented - requires browser to be closed"}


async def get_edge_bookmarks() -> list[dict[str, Any]]:
    """Get Edge bookmarks."""
    browser = EdgeBrowser()
    return await browser.get_bookmarks()


async def add_edge_bookmark(url: str, title: str, folder: str | None = None) -> dict[str, Any]:
    """Add bookmark to Edge."""
    browser = EdgeBrowser()
    return await browser.add_bookmark(url, title, folder)





