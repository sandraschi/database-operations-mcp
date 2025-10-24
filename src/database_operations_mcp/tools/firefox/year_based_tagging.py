"""
Year-based tagging for Firefox bookmarks.
Adds creation/edit years as tags for time-based organization.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp

from database_operations_mcp.tools.help_tools import HelpSystem
from .db import FirefoxDB


@mcp.tool()
@HelpSystem.register_tool(category="firefox")
async def batch_tag_from_year(
    profile_path: Optional[str] = None,
    use_last_modified: bool = False,
    prefix: str = "year:",
    batch_size: int = 100,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """
    Batch process bookmarks to add year-based tags.

    Args:
        profile_path: Path to Firefox profile
        use_last_modified: If True, use last modified date instead of creation date
        prefix: Prefix to use for year tags
        batch_size: Number of bookmarks to process in each batch
        dry_run: If True, only show what would be changed
    """
    db = FirefoxDB(Path(profile_path) if profile_path else None)
    all_changes = []
    year_counts = {}
    total_processed = 0

    # Get all bookmarks first to calculate progress
    all_bookmarks = [b async for b in db.get_all_bookmarks()]
    total_bookmarks = len(all_bookmarks)

    # Process in batches
    for i in range(0, total_bookmarks, batch_size):
        batch = all_bookmarks[i : i + batch_size]
        batch_changes = []

        for bookmark in batch:
            timestamp = bookmark.get("last_modified" if use_last_modified else "date_added")
            if not timestamp:
                continue

            try:
                dt = datetime.fromtimestamp(timestamp / 1000000)
                year = str(dt.year)
                year_tag = f"{prefix}{year}"
            except (ValueError, TypeError):
                continue

            year_counts[year] = year_counts.get(year, 0) + 1
            current_tags = set(await db.get_bookmark_tags(bookmark["id"]))

            if year_tag not in current_tags:
                new_tags = current_tags | {year_tag}
                batch_changes.append(
                    (
                        bookmark["id"],
                        list(new_tags),
                        {
                            "bookmark_id": bookmark["id"],
                            "title": bookmark.get("title", "Untitled"),
                            "date": dt.isoformat(),
                            "year_tag": year_tag,
                            "current_tags": list(current_tags),
                            "new_tags": list(new_tags),
                        },
                    )
                )

        # Apply batch updates
        if not dry_run and batch_changes:
            for bookmark_id, tags, _ in batch_changes:
                await db.update_bookmark_tags(bookmark_id, tags)

        all_changes.extend(change[2] for change in batch_changes)
        total_processed += len(batch)

        # Yield progress
        yield {
            "status": "in_progress",
            "processed": total_processed,
            "total": total_bookmarks,
            "progress": (total_processed / total_bookmarks) * 100,
            "changes_in_batch": len(batch_changes),
            "current_batch": i // batch_size + 1,
            "total_batches": (total_bookmarks + batch_size - 1) // batch_size,
        }

    # Final result
    yield {
        "status": "dry_run" if dry_run else "success",
        "total_processed": total_processed,
        "bookmarks_updated": len(all_changes),
        "year_counts": year_counts,
        "changes": all_changes,
        "dry_run": dry_run,
    }


@mcp.tool
@HelpSystem.register_tool(category="firefox")
async def tag_from_year(
    profile_path: Optional[str] = None,
    use_last_modified: bool = False,
    prefix: str = "year:",
    dry_run: bool = True,
) -> Dict[str, Any]:
    """
    Add year-based tags to bookmarks.

    Args:
        profile_path: Path to Firefox profile
        use_last_modified: If True, use last modified date instead of creation date
        prefix: Prefix to use for year tags (e.g., 'year:' results in 'year:2023')
        dry_run: If True, only show what would be changed
    """
    db = FirefoxDB(Path(profile_path) if profile_path else None)
    changes = []
    year_counts = {}

    async for bookmark in db.get_all_bookmarks():
        # Get the appropriate timestamp
        timestamp = bookmark.get("last_modified" if use_last_modified else "date_added")
        if not timestamp:
            continue

        # Convert to year
        try:
            dt = datetime.fromtimestamp(timestamp / 1000000)  # Firefox uses microseconds
            year = str(dt.year)
            year_tag = f"{prefix}{year}"
        except (ValueError, TypeError):
            continue

        # Track year counts
        year_counts[year] = year_counts.get(year, 0) + 1

        # Get current tags
        current_tags = set(await db.get_bookmark_tags(bookmark["id"]))
        new_tags = set(current_tags)

        # Add year tag if not already present
        if year_tag not in current_tags:
            new_tags.add(year_tag)

            changes.append(
                {
                    "bookmark_id": bookmark["id"],
                    "title": bookmark.get("title", "Untitled"),
                    "date": dt.isoformat(),
                    "year_tag": year_tag,
                    "current_tags": list(current_tags),
                    "new_tags": list(new_tags),
                }
            )

    # Apply changes if not dry run
    if not dry_run:
        for change in changes:
            await db.update_bookmark_tags(change["bookmark_id"], change["new_tags"])

    return {
        "status": "dry_run" if dry_run else "success",
        "year_counts": year_counts,
        "bookmarks_updated": len(changes),
        "dry_run": dry_run,
    }
