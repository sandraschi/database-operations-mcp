"""Tag management functionality for Firefox bookmarks."""

import re
from pathlib import Path
from typing import Any

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.tools.help_tools import HelpSystem

from .db import FirefoxDB


class TagManager:
    """Handles tag operations for Firefox bookmarks."""

    def __init__(self, profile_path: Path | None = None):
        self.db = FirefoxDB(profile_path)

    def get_tag_stats(self) -> dict[str, Any]:
        """Get statistics about tags."""
        query = """
            SELECT t.title as tag, COUNT(*) as count
            FROM moz_bookmarks t
            JOIN moz_bookmarks b ON b.id = +t.parent
            WHERE t.type = 2  # Tag folder
            GROUP BY t.title
            ORDER BY count DESC
        """
        cursor = self.db.execute(query)
        return [dict(row) for row in cursor.fetchall()]


@mcp.tool()
@HelpSystem.register_tool(category="firefox")
async def list_tags(
    profile_path: str | None = None, min_count: int = 0, max_count: int = 1000
) -> dict[str, Any]:
    """List all tags in the Firefox bookmarks database.

    Args:
        profile_path: Path to the Firefox profile directory
        min_count: Minimum number of bookmarks a tag must have to be included
        max_count: Maximum number of tags to return

    Returns:
        Dictionary with tag statistics
    """
    manager = TagManager(Path(profile_path) if profile_path else None)
    tags = manager.get_tag_stats()

    # Filter tags by min_count
    filtered_tags = [tag for tag in tags if tag["count"] >= min_count]

    # Limit number of results
    limited_tags = filtered_tags[:max_count]

    return {
        "tags": limited_tags,
        "total_tags": len(filtered_tags),
        "min_count": min_count,
        "max_count": max_count,
    }


@mcp.tool()
@HelpSystem.register_tool(category="firefox")
async def find_similar_tags(
    search_pattern: str, profile_path: str | None = None
) -> dict[str, Any]:
    """Find tags similar to the search pattern.

    Args:
        search_pattern: Pattern to search for in tag names
        profile_path: Path to the Firefox profile directory

    Returns:
        Dictionary with matching tags and their statistics
    """
    manager = TagManager(Path(profile_path) if profile_path else None)
    tags = manager.get_tag_stats()

    # Simple pattern matching (can be enhanced with fuzzy matching)
    pattern = re.compile(search_pattern, re.IGNORECASE)
    matches = [tag for tag in tags if pattern.search(tag["tag"])]

    return {"search_pattern": search_pattern, "matches": matches, "match_count": len(matches)}


@mcp.tool()
@HelpSystem.register_tool(category="firefox")
async def merge_tags(
    source_tags: list[str],
    target_tag: str,
    profile_path: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Merge multiple tags into a single tag.

    Args:
        source_tags: List of tag names to merge
        target_tag: Name of the target tag
        profile_path: Path to the Firefox profile directory
        dry_run: If True, only show what would be changed

    Returns:
        Dictionary with merge results
    """
    db = FirefoxDB(Path(profile_path) if profile_path else None)
    changes = []

    # Get all bookmarks with source tags
    bookmarks_to_update = set()
    for tag in source_tags:
        async for bookmark in db.get_bookmarks_by_tag(tag):
            bookmarks_to_update.add(bookmark["id"])

    # Apply changes
    if not dry_run:
        for bookmark_id in bookmarks_to_update:
            # Get current tags
            current_tags = await db.get_bookmark_tags(bookmark_id)
            # Remove source tags and add target tag
            new_tags = [t for t in current_tags if t not in source_tags]
            if target_tag not in new_tags:
                new_tags.append(target_tag)

            # Update tags if changed
            if set(new_tags) != set(current_tags):
                await db.update_bookmark_tags(bookmark_id, new_tags)
                changes.append(
                    {"bookmark_id": bookmark_id, "old_tags": current_tags, "new_tags": new_tags}
                )

    return {
        "status": "success" if not dry_run else "dry_run",
        "changes": changes,
        "change_count": len(changes),
        "dry_run": dry_run,
    }


@mcp.tool()
@HelpSystem.register_tool(category="firefox")
async def clean_up_tags(
    min_count: int = 1, profile_path: str | None = None, dry_run: bool = True
) -> dict[str, Any]:
    """Clean up rarely used tags.

    Args:
        min_count: Minimum number of bookmarks a tag must have
        profile_path: Path to the Firefox profile directory
        dry_run: If True, only show what would be changed

    Returns:
        Dictionary with cleanup results
    """
    manager = TagManager(Path(profile_path) if profile_path else None)
    stats = manager.get_tag_stats()

    tags_to_remove = [tag["tag"] for tag in stats if tag["count"] < min_count]

    changes = []
    if not dry_run:
        # Implementation for actual tag removal
        pass

    return {
        "status": "success" if not dry_run else "dry_run",
        "removed_tags": tags_to_remove,
        "changes": changes,
        "dry_run": dry_run,
    }
