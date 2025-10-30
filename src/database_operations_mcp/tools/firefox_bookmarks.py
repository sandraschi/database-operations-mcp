# Firefox bookmark management portmanteau tool.
# Consolidates all Firefox bookmark operations into a single interface.

import logging
from typing import Any

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.tools.firefox.age_analyzer import (
    find_old_bookmarks,
    get_bookmark_stats,
)
from database_operations_mcp.tools.firefox.bookmark_manager import BookmarkManager
from database_operations_mcp.tools.firefox.bulk_operations import BulkOperations
from database_operations_mcp.tools.firefox.link_checker import LinkChecker
from database_operations_mcp.tools.firefox.search_tools import BookmarkSearcher
from database_operations_mcp.tools.firefox.tag_manager import TagManager
from database_operations_mcp.tools.help_tools import HelpSystem

logger = logging.getLogger(__name__)


@mcp.tool()
@HelpSystem.register_tool(category="firefox")
async def firefox_bookmarks(
    operation: str,
    profile_name: str | None = None,
    folder_id: int | None = None,
    bookmark_id: int | None = None,
    url: str | None = None,
    title: str | None = None,
    tags: list[str] | None = None,
    search_query: str | None = None,
    search_type: str = "all",
    export_format: str = "json",
    export_path: str | None = None,
    batch_size: int = 100,
    similarity_threshold: float = 0.85,
    age_days: int = 365,
    check_links: bool = False,
) -> dict[str, Any]:
    """Firefox bookmark management portmanteau tool.

    This tool consolidates all Firefox bookmark operations into a single interface,
    providing unified access to bookmark management functionality.

    Operations:
    - list_bookmarks: List bookmarks from a profile or folder
    - get_bookmark: Get details for a specific bookmark
    - add_bookmark: Add a new bookmark to the profile
    - search_bookmarks: Search bookmarks using various criteria
    - find_duplicates: Find duplicate bookmarks based on URL or content
    - export_bookmarks: Export bookmarks to various formats
    - batch_update_tags: Update tags for multiple bookmarks
    - remove_unused_tags: Remove tags that are no longer used
    - list_tags: List all tags used in bookmarks
    - find_similar_tags: Find tags with similar names
    - merge_tags: Merge similar tags into a single tag
    - clean_up_tags: Clean up and standardize tag names
    - find_old_bookmarks: Find bookmarks older than specified days
    - get_bookmark_stats: Get statistics about bookmark collection
    - find_broken_links: Find bookmarks with broken or inaccessible URLs

    Args:
        operation: The operation to perform (required)
        profile_name: Firefox profile name to operate on
        folder_id: ID of the folder to operate on
        bookmark_id: ID of the specific bookmark
        url: URL for the bookmark
        title: Title for the bookmark
        tags: List of tags to apply
        search_query: Search query string
        search_type: Type of search (all, title, url, tags)
        export_format: Format for export (json, csv, html)
        export_path: Path to save exported data
        batch_size: Number of bookmarks to process per batch
        similarity_threshold: Threshold for duplicate detection
        age_days: Age threshold for old bookmark detection
        check_links: Whether to check link accessibility

    Returns:
        Dictionary with operation results and bookmark data

    Examples:
        List bookmarks:
        firefox_bookmarks(operation='list_bookmarks', profile_name='default')

        Add bookmark:
        firefox_bookmarks(operation='add_bookmark', profile_name='default',
                         url='https://example.com', title='Example', tags=['work'])

        Search bookmarks:
        firefox_bookmarks(operation='search_bookmarks', profile_name='default',
                         search_query='python', search_type='title')

        Find duplicates:
        firefox_bookmarks(operation='find_duplicates', profile_name='default',
                         similarity_threshold=0.9)

        Export bookmarks:
        firefox_bookmarks(operation='export_bookmarks', profile_name='default',
                         export_format='html', export_path='bookmarks.html')

        Find old bookmarks:
        firefox_bookmarks(operation='find_old_bookmarks', profile_name='default',
                         age_days=730)

        Check broken links:
        firefox_bookmarks(operation='find_broken_links', profile_name='default',
                         check_links=True)
    """

    if operation == "list_bookmarks":
        return await _list_bookmarks(profile_name, folder_id)
    elif operation == "get_bookmark":
        return await _get_bookmark(bookmark_id, profile_name)
    elif operation == "add_bookmark":
        return await _add_bookmark(profile_name, url, title, tags)
    elif operation == "search_bookmarks":
        return await _search_bookmarks(profile_name, search_query, search_type)
    elif operation == "find_duplicates":
        return await _find_duplicates(profile_name, similarity_threshold)
    elif operation == "export_bookmarks":
        return await _export_bookmarks(profile_name, export_format, export_path)
    elif operation == "batch_update_tags":
        return await _batch_update_tags(profile_name, tags, batch_size)
    elif operation == "remove_unused_tags":
        return await _remove_unused_tags(profile_name)
    elif operation == "list_tags":
        return await _list_tags(profile_name)
    elif operation == "find_similar_tags":
        return await _find_similar_tags(profile_name)
    elif operation == "merge_tags":
        return await _merge_tags(profile_name, tags)
    elif operation == "clean_up_tags":
        return await _clean_up_tags(profile_name)
    elif operation == "find_old_bookmarks":
        return await _find_old_bookmarks(profile_name, age_days)
    elif operation == "get_bookmark_stats":
        return await _get_bookmark_stats(profile_name)
    elif operation == "find_broken_links":
        return await _find_broken_links(profile_name, check_links)
    else:
        return {
            "success": False,
            "error": f"Unknown operation: {operation}",
            "available_operations": [
                "list_bookmarks",
                "get_bookmark",
                "add_bookmark",
                "search_bookmarks",
                "find_duplicates",
                "export_bookmarks",
                "batch_update_tags",
                "remove_unused_tags",
                "list_tags",
                "find_similar_tags",
                "merge_tags",
                "clean_up_tags",
                "find_old_bookmarks",
                "get_bookmark_stats",
                "find_broken_links",
            ],
        }


async def _list_bookmarks(profile_name: str | None, folder_id: int | None) -> dict[str, Any]:
    """List bookmarks from a profile or folder."""
    try:
        manager = BookmarkManager(profile_name)
        bookmarks = await manager.list_bookmarks(folder_id)

        return {
            "success": True,
            "message": "Bookmarks listed successfully",
            "profile_name": profile_name,
            "folder_id": folder_id,
            "bookmarks": bookmarks,
            "count": len(bookmarks),
        }

    except Exception as e:
        logger.error(f"Error listing bookmarks: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to list bookmarks: {str(e)}",
            "profile_name": profile_name,
            "bookmarks": [],
            "count": 0,
        }


async def _get_bookmark(bookmark_id: int | None, profile_name: str | None) -> dict[str, Any]:
    """Get details for a specific bookmark."""
    try:
        if not bookmark_id:
            raise ValueError("Bookmark ID is required")

        manager = BookmarkManager(profile_name)
        bookmark = await manager.get_bookmark(bookmark_id)

        return {
            "success": True,
            "message": f"Bookmark {bookmark_id} retrieved successfully",
            "profile_name": profile_name,
            "bookmark_id": bookmark_id,
            "bookmark": bookmark,
        }

    except Exception as e:
        logger.error(f"Error getting bookmark: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to get bookmark: {str(e)}",
            "profile_name": profile_name,
            "bookmark_id": bookmark_id,
        }


async def _add_bookmark(
    profile_name: str | None, url: str | None, title: str | None, tags: list[str] | None
) -> dict[str, Any]:
    """Add a new bookmark to the profile."""
    try:
        if not url:
            raise ValueError("URL is required")

        manager = BookmarkManager(profile_name)
        bookmark_id = await manager.add_bookmark(url, title, tags)

        return {
            "success": True,
            "message": "Bookmark added successfully",
            "profile_name": profile_name,
            "bookmark_id": bookmark_id,
            "url": url,
            "title": title,
            "tags": tags,
        }

    except Exception as e:
        logger.error(f"Error adding bookmark: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to add bookmark: {str(e)}",
            "profile_name": profile_name,
            "url": url,
        }


async def _search_bookmarks(
    profile_name: str | None, search_query: str | None, search_type: str
) -> dict[str, Any]:
    """Search bookmarks using various criteria."""
    try:
        if not search_query:
            raise ValueError("Search query is required")

        searcher = BookmarkSearcher(profile_name)
        results = await searcher.search_bookmarks(search_query, search_type)

        return {
            "success": True,
            "message": f"Search completed for '{search_query}'",
            "profile_name": profile_name,
            "search_query": search_query,
            "search_type": search_type,
            "results": results,
            "count": len(results),
        }

    except Exception as e:
        logger.error(f"Error searching bookmarks: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to search bookmarks: {str(e)}",
            "profile_name": profile_name,
            "search_query": search_query,
            "results": [],
            "count": 0,
        }


async def _find_duplicates(
    profile_name: str | None, similarity_threshold: float
) -> dict[str, Any]:
    """Find duplicate bookmarks based on URL or content."""
    try:
        searcher = BookmarkSearcher(profile_name)
        duplicates = await searcher.find_duplicates(similarity_threshold)

        return {
            "success": True,
            "message": "Duplicate search completed",
            "profile_name": profile_name,
            "similarity_threshold": similarity_threshold,
            "duplicates": duplicates,
            "duplicate_groups": len(duplicates),
        }

    except Exception as e:
        logger.error(f"Error finding duplicates: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to find duplicates: {str(e)}",
            "profile_name": profile_name,
            "duplicates": [],
            "duplicate_groups": 0,
        }


async def _export_bookmarks(
    profile_name: str | None, export_format: str, export_path: str | None
) -> dict[str, Any]:
    """Export bookmarks to various formats."""
    try:
        bulk_ops = BulkOperations(profile_name)
        result = await bulk_ops.export_bookmarks(export_format, export_path)

        return {
            "success": True,
            "message": f"Bookmarks exported to {export_format}",
            "profile_name": profile_name,
            "export_format": export_format,
            "export_path": export_path,
            "export_result": result,
        }

    except Exception as e:
        logger.error(f"Error exporting bookmarks: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to export bookmarks: {str(e)}",
            "profile_name": profile_name,
            "export_format": export_format,
        }


async def _batch_update_tags(
    profile_name: str | None, tags: list[str] | None, batch_size: int
) -> dict[str, Any]:
    """Update tags for multiple bookmarks."""
    try:
        if not tags:
            raise ValueError("Tags are required")

        bulk_ops = BulkOperations(profile_name)
        result = await bulk_ops.batch_update_tags(tags, batch_size)

        return {
            "success": True,
            "message": "Batch tag update completed",
            "profile_name": profile_name,
            "tags": tags,
            "batch_size": batch_size,
            "update_result": result,
        }

    except Exception as e:
        logger.error(f"Error updating tags: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to update tags: {str(e)}",
            "profile_name": profile_name,
            "tags": tags,
        }


async def _remove_unused_tags(profile_name: str | None) -> dict[str, Any]:
    """Remove tags that are no longer used."""
    try:
        bulk_ops = BulkOperations(profile_name)
        result = await bulk_ops.remove_unused_tags()

        return {
            "success": True,
            "message": "Unused tags removed",
            "profile_name": profile_name,
            "removal_result": result,
        }

    except Exception as e:
        logger.error(f"Error removing unused tags: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to remove unused tags: {str(e)}",
            "profile_name": profile_name,
        }


async def _list_tags(profile_name: str | None) -> dict[str, Any]:
    """List all tags used in bookmarks."""
    try:
        tag_manager = TagManager(profile_name)
        tags = await tag_manager.list_tags()

        return {
            "success": True,
            "message": "Tags listed successfully",
            "profile_name": profile_name,
            "tags": tags,
            "count": len(tags),
        }

    except Exception as e:
        logger.error(f"Error listing tags: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to list tags: {str(e)}",
            "profile_name": profile_name,
            "tags": [],
            "count": 0,
        }


async def _find_similar_tags(profile_name: str | None) -> dict[str, Any]:
    """Find tags with similar names."""
    try:
        tag_manager = TagManager(profile_name)
        similar_tags = await tag_manager.find_similar_tags()

        return {
            "success": True,
            "message": "Similar tags found",
            "profile_name": profile_name,
            "similar_tags": similar_tags,
            "groups": len(similar_tags),
        }

    except Exception as e:
        logger.error(f"Error finding similar tags: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to find similar tags: {str(e)}",
            "profile_name": profile_name,
            "similar_tags": [],
            "groups": 0,
        }


async def _merge_tags(profile_name: str | None, tags: list[str] | None) -> dict[str, Any]:
    """Merge similar tags into a single tag."""
    try:
        if not tags or len(tags) < 2:
            raise ValueError("At least 2 tags are required for merging")

        tag_manager = TagManager(profile_name)
        result = await tag_manager.merge_tags(tags)

        return {
            "success": True,
            "message": "Tags merged successfully",
            "profile_name": profile_name,
            "merged_tags": tags,
            "merge_result": result,
        }

    except Exception as e:
        logger.error(f"Error merging tags: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to merge tags: {str(e)}",
            "profile_name": profile_name,
            "merged_tags": tags,
        }


async def _clean_up_tags(profile_name: str | None) -> dict[str, Any]:
    """Clean up and standardize tag names."""
    try:
        tag_manager = TagManager(profile_name)
        result = await tag_manager.clean_up_tags()

        return {
            "success": True,
            "message": "Tags cleaned up successfully",
            "profile_name": profile_name,
            "cleanup_result": result,
        }

    except Exception as e:
        logger.error(f"Error cleaning up tags: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to clean up tags: {str(e)}",
            "profile_name": profile_name,
        }


async def _find_old_bookmarks(profile_name: str | None, age_days: int) -> dict[str, Any]:
    """Find bookmarks older than specified days."""
    try:
        result = await find_old_bookmarks(profile_name, age_days)

        return {
            "success": True,
            "message": f"Old bookmarks found (older than {age_days} days)",
            "profile_name": profile_name,
            "age_days": age_days,
            "old_bookmarks": result.get("old_bookmarks", []),
            "count": result.get("count", 0),
        }

    except Exception as e:
        logger.error(f"Error finding old bookmarks: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to find old bookmarks: {str(e)}",
            "profile_name": profile_name,
            "age_days": age_days,
            "old_bookmarks": [],
            "count": 0,
        }


async def _get_bookmark_stats(profile_name: str | None) -> dict[str, Any]:
    """Get statistics about bookmark collection."""
    try:
        result = await get_bookmark_stats(profile_name)

        return {
            "success": True,
            "message": "Bookmark statistics retrieved",
            "profile_name": profile_name,
            "stats": result,
        }

    except Exception as e:
        logger.error(f"Error getting bookmark stats: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to get bookmark stats: {str(e)}",
            "profile_name": profile_name,
            "stats": {},
        }


async def _find_broken_links(profile_name: str | None, check_links: bool) -> dict[str, Any]:
    """Find bookmarks with broken or inaccessible URLs."""
    try:
        link_checker = LinkChecker(profile_name)
        result = await link_checker.find_broken_links(check_links)

        return {
            "success": True,
            "message": "Broken links check completed",
            "profile_name": profile_name,
            "check_links": check_links,
            "broken_links": result.get("broken_links", []),
            "count": result.get("count", 0),
        }

    except Exception as e:
        logger.error(f"Error finding broken links: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to find broken links: {str(e)}",
            "profile_name": profile_name,
            "broken_links": [],
            "count": 0,
        }



