"""
Link checking functionality for Firefox bookmarks.
Identifies broken or redirected URLs.

DEPRECATED: Individual tools deprecated. Use firefox_bookmarks portmanteau instead.
- find_broken_links() → firefox_bookmarks(operation='find_broken_links')
"""

from pathlib import Path
from typing import Any

import aiohttp

# NOTE: @mcp.tool decorators removed - functionality moved to firefox_bookmarks portmanteau
from .db import FirefoxDB


class LinkChecker:
    """Handles link validation and checking."""

    def __init__(self, profile_path: Path | None = None):
        self.db = FirefoxDB(profile_path)
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.session:
            await self.session.close()

    async def check_link(self, url: str) -> dict[str, Any]:
        """Check if a URL is accessible."""
        if not self.session:
            raise RuntimeError("LinkChecker must be used as a context manager")

        try:
            async with self.session.head(url, allow_redirects=True, timeout=10) as response:
                return {
                    "url": str(response.url),
                    "status": response.status,
                    "is_redirected": str(response.url) != url,
                    "is_broken": response.status >= 400,
                }
        except Exception as e:
            return {"url": url, "error": str(e), "is_broken": True}


# DEPRECATED: Use firefox_bookmarks(operation='find_broken_links') instead
async def find_broken_links(
    profile_path: str | None = None, timeout: int = 10, concurrent_requests: int = 10
) -> dict[str, Any]:
    """Find broken or redirected links in bookmarks.

    Args:
        profile_path: Path to Firefox profile
        timeout: Request timeout in seconds
        concurrent_requests: Maximum number of concurrent HTTP requests

    Returns:
        Dictionary with broken links and their status
    """
    results = []
    db = FirefoxDB(Path(profile_path) if profile_path else None)

    async with LinkChecker() as checker:
        async for bookmark in db.get_all_bookmarks():
            if not bookmark.get("url"):
                continue

            result = await checker.check_link(bookmark["url"])
            if result.get("is_broken") or result.get("is_redirected"):
                results.append(
                    {"bookmark_id": bookmark["id"], "title": bookmark["title"], **result}
                )

    return {
        "status": "success",
        "checked": len(results),
        "broken_links": [r for r in results if r.get("is_broken")],
        "redirected_links": [
            r for r in results if r.get("is_redirected") and not r.get("is_broken")
        ],
    }
