"""
Bulk operations for Firefox bookmarks.
Provides tools for batch processing of bookmarks.
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from ..help_tools import HelpSystem
from . import mcp  # Import the mcp instance from __init__
from .db import FirefoxDB


class BulkOperations:
    """Handles batch operations on Firefox bookmarks."""

    def __init__(self, profile_path: Optional[Path] = None):
        self.db = FirefoxDB(profile_path)

    async def process_in_batches(self, operation: str, batch_size: int = 50, **kwargs):
        """Process bookmarks in batches to avoid memory issues."""
        offset = 0
        while True:
            bookmarks = await self.db.get_bookmarks(limit=batch_size, offset=offset)
            if not bookmarks:
                break

            for bookmark in bookmarks:
                if operation == "export":
                    yield await self._export_bookmark(bookmark, **kwargs)
                # Add other operations as needed

            offset += batch_size

    async def _export_bookmark(
        self, bookmark: Dict[str, Any], format: str = "json"
    ) -> Dict[str, Any]:
        """Export a single bookmark in specified format."""
        if format == "json":
            return {
                "id": bookmark["id"],
                "title": bookmark["title"],
                "url": bookmark["url"],
                "tags": await self.db.get_bookmark_tags(bookmark["id"]),
                "date_added": bookmark["date_added"],
                "last_modified": bookmark["last_modified"],
            }
        # Add other formats as needed


@mcp.tool()
@HelpSystem.register_tool(category="firefox")
async def export_bookmarks(
    output_format: str = "json",
    output_file: Optional[str] = None,
    profile_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Export bookmarks to a file.

    Args:
        output_format: Output format ('json' or 'csv')
        output_file: Path to the output file (defaults to bookmarks_<timestamp>.<format>)
        profile_path: Path to the Firefox profile directory

    Returns:
        Dictionary with export results
    """
    db = FirefoxDB(Path(profile_path) if profile_path else None)
    bookmarks = db.get_all_bookmarks()

    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"bookmarks_{timestamp}.{output_format}"

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_format == "json":
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(bookmarks, f, indent=2, default=str)
    elif output_format == "csv":
        if bookmarks:
            fieldnames = bookmarks[0].keys()
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(bookmarks)
    else:
        return {"status": "error", "message": f"Unsupported format: {output_format}"}

    return {"status": "success", "output_file": str(output_path), "bookmark_count": len(bookmarks)}


@mcp.tool()
@HelpSystem.register_tool(category="firefox")
async def batch_update_tags(
    tag_mapping: Dict[str, str], dry_run: bool = True, profile_path: Optional[str] = None
) -> Dict[str, Any]:
    """Batch update tags in bookmarks.

    Args:
        tag_mapping: Dictionary mapping old tag names to new tag names
        dry_run: If True, only show what would be changed
        profile_path: Path to the Firefox profile directory

    Returns:
        Dictionary with update results
    """
    db = FirefoxDB(Path(profile_path) if profile_path else None)
    changes = []
    total_affected = 0

    try:
        # Get all bookmarks with their current tags
        bookmarks = await db.get_all_bookmarks()
        
        for bookmark in bookmarks:
            bookmark_id = bookmark["id"]
            current_tags = await db.get_bookmark_tags(bookmark_id)
            
            # Check if any tags need updating
            updated_tags = []
            bookmark_changed = False
            
            for tag in current_tags:
                if tag in tag_mapping:
                    new_tag = tag_mapping[tag]
                    updated_tags.append(new_tag)
                    bookmark_changed = True
                    changes.append({
                        "bookmark_id": bookmark_id,
                        "bookmark_title": bookmark["title"],
                        "old_tag": tag,
                        "new_tag": new_tag
                    })
                else:
                    updated_tags.append(tag)
            
            # Update the bookmark if changes were made
            if bookmark_changed and not dry_run:
                await db.update_bookmark_tags(bookmark_id, updated_tags)
                total_affected += 1
            elif bookmark_changed and dry_run:
                total_affected += 1

        return {
            "status": "success" if not dry_run else "dry_run",
            "changes": changes,
            "change_count": len(changes),
            "affected_bookmarks": total_affected,
            "dry_run": dry_run,
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "changes": changes,
            "change_count": len(changes),
            "affected_bookmarks": total_affected,
            "dry_run": dry_run,
        }


@mcp.tool()
@HelpSystem.register_tool(category="firefox")
async def remove_unused_tags(
    dry_run: bool = True, profile_path: Optional[str] = None
) -> Dict[str, Any]:
    """Remove tags that are not associated with any bookmarks.

    Args:
        dry_run: If True, only show what would be removed
        profile_path: Path to the Firefox profile directory

    Returns:
        Dictionary with removal results
    """
    db = FirefoxDB(Path(profile_path) if profile_path else None)
    removed_tags = []
    
    try:
        # Get all tags
        all_tags = await db.get_all_tags()
        
        # Get all bookmarks with their tags
        bookmarks = await db.get_all_bookmarks()
        used_tags = set()
        
        for bookmark in bookmarks:
            bookmark_tags = await db.get_bookmark_tags(bookmark["id"])
            used_tags.update(bookmark_tags)
        
        # Find unused tags
        unused_tags = [tag for tag in all_tags if tag not in used_tags]
        
        # Remove unused tags if not dry run
        if not dry_run:
            for tag in unused_tags:
                await db.delete_tag(tag)
                removed_tags.append(tag)
        
        return {
            "status": "success" if not dry_run else "dry_run",
            "unused_tags": unused_tags,
            "removed_tags": removed_tags,
            "unused_count": len(unused_tags),
            "removed_count": len(removed_tags),
            "dry_run": dry_run,
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "unused_tags": [],
            "removed_tags": removed_tags,
            "unused_count": 0,
            "removed_count": len(removed_tags),
            "dry_run": dry_run,
        }
