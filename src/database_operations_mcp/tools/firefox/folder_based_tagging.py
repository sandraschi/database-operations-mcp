"""
Folder-based tagging for Firefox bookmarks.
Adds tags based on the bookmark's position in the folder hierarchy.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.tools.help_tools import HelpSystem

from .db import FirefoxDB


async def get_folder_path(db: FirefoxDB, folder_id: int) -> List[Dict[str, Any]]:
    """Get the full path of a folder as a list of folder names."""
    path = []
    current_id = folder_id

    while current_id:
        folder = await db.get_folder_by_id(current_id)
        if not folder:
            break
        path.insert(0, {"id": folder["id"], "title": folder.get("title", "Untitled")})
        current_id = folder.get("parent_id")

    return path


@mcp.tool()
@HelpSystem.register_tool(category="firefox")
async def batch_tag_from_folder(
    profile_path: Optional[str] = None,
    include_ancestors: bool = True,
    exclude_folders: Optional[List[str]] = None,
    batch_size: int = 100,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """
    Batch process bookmarks to add tags based on folder hierarchy.

    Args:
        profile_path: Path to Firefox profile
        include_ancestors: If True, include all parent folders as tags
        exclude_folders: List of folder names to exclude from tagging
        batch_size: Number of bookmarks to process in each batch
        dry_run: If True, only show what would be changed
    """
    db = FirefoxDB(Path(profile_path) if profile_path else None)
    exclude_set = set(exclude_folders or [])
    all_changes = []
    total_processed = 0

    # Get all bookmarks first to calculate progress
    all_bookmarks = [b async for b in db.get_all_bookmarks()]
    total_bookmarks = len(all_bookmarks)

    # Process in batches
    for i in range(0, total_bookmarks, batch_size):
        batch = all_bookmarks[i : i + batch_size]
        batch_changes = []

        for bookmark in batch:
            if not bookmark.get("parent_id"):
                continue

            folder_path = await get_folder_path(db, bookmark["parent_id"])
            if not folder_path:
                continue

            current_tags = set(await db.get_bookmark_tags(bookmark["id"]))
            new_tags = set(current_tags)

            # Add folder-based tags
            for folder in folder_path:
                folder_name = folder["title"].strip()
                if not folder_name or folder_name in exclude_set:
                    continue

                new_tags.add(folder_name)

                if len(folder_path) == 1:
                    new_tags.add(f"!{folder_name}")

                if include_ancestors:
                    path_tags = [
                        f["title"].strip() for f in folder_path[: folder_path.index(folder) + 1]
                    ]
                    new_tags.add(" ".join(path_tags))

            if new_tags != current_tags:
                batch_changes.append(
                    (
                        bookmark["id"],
                        list(new_tags),
                        {
                            "bookmark_id": bookmark["id"],
                            "title": bookmark.get("title", "Untitled"),
                            "folder_path": [f["title"] for f in folder_path],
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
        "changes": all_changes,
        "dry_run": dry_run,
    }


@mcp.tool
@HelpSystem.register_tool(category="firefox")
async def tag_from_folder(
    profile_path: Optional[str] = None,
    include_ancestors: bool = True,
    exclude_folders: Optional[List[str]] = None,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """
    Add tags based on bookmark folder hierarchy.

    Args:
        profile_path: Path to Firefox profile
        include_ancestors: If True, include all parent folders as tags
        exclude_folders: List of folder names to exclude from tagging
        dry_run: If True, only show what would be changed
    """
    db = FirefoxDB(Path(profile_path) if profile_path else None)
    exclude_set = set(exclude_folders or [])
    changes = []

    async for bookmark in db.get_all_bookmarks():
        if not bookmark.get("parent_id"):
            continue

        folder_path = await get_folder_path(db, bookmark["parent_id"])
        if not folder_path:
            continue

        # Get current tags
        current_tags = set(await db.get_bookmark_tags(bookmark["id"]))
        new_tags = set(current_tags)

        # Add folder-based tags
        for folder in folder_path:
            folder_name = folder["title"].strip()
            if not folder_name or folder_name in exclude_set:
                continue

            # Add folder name as tag
            new_tags.add(folder_name)

            # Add ! prefixed version for top-level folders
            if len(folder_path) == 1:
                new_tags.add(f"!{folder_name}")

            # Add path-based tags if enabled
            if include_ancestors:
                path_tags = [
                    f["title"].strip() for f in folder_path[: folder_path.index(folder) + 1]
                ]
                new_tags.add(" ".join(path_tags))

        # Only include if tags changed
        if new_tags != current_tags:
            changes.append(
                {
                    "bookmark_id": bookmark["id"],
                    "title": bookmark.get("title", "Untitled"),
                    "folder_path": [f["title"] for f in folder_path],
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
        "changes": changes,
        "bookmarks_updated": len(changes),
        "dry_run": dry_run,
    }
