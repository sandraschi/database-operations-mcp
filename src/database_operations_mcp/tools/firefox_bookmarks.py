# Firefox bookmark helper functions.
# Used by browser_bookmarks portmanteau tool.

import logging
from typing import Any

from database_operations_mcp.tools.firefox.age_analyzer import (
    find_old_bookmarks,
    get_bookmark_stats,
)
from database_operations_mcp.tools.firefox.bookmark_manager import BookmarkManager
from database_operations_mcp.tools.firefox.bulk_operations import BulkOperations
from database_operations_mcp.tools.firefox.core import FirefoxDatabaseUnlocker
from database_operations_mcp.tools.firefox.link_checker import LinkChecker
from database_operations_mcp.tools.firefox.search_tools import BookmarkSearcher
from database_operations_mcp.tools.firefox.status import FirefoxStatusChecker
from database_operations_mcp.tools.firefox.tag_manager import TagManager
from database_operations_mcp.tools.firefox.utils import get_profile_directory
from database_operations_mcp.tools.help_tools import HelpSystem

logger = logging.getLogger(__name__)

# Write operations that require Firefox to be closed
WRITE_OPERATIONS = {
    "add_bookmark",
    "batch_update_tags",
    "remove_unused_tags",
    "merge_tags",
    "clean_up_tags",
}


def _check_firefox_for_write(operation: str) -> dict[str, Any] | None:
    """Check if Firefox is running before write operations.
    
    Returns error dict if Firefox is running, None if safe to proceed.
    """
    if operation not in WRITE_OPERATIONS:
        return None
    
    status = FirefoxStatusChecker.is_firefox_running()
    if status.get("is_running"):
        return {
            "success": False,
            "error": "Firefox is running - cannot write to bookmark database",
            "operation": operation,
            "firefox_status": status,
            "solution": "Please close Firefox completely and try again",
            "details": (
                "Firefox locks its places.sqlite database while running. "
                "Write operations require exclusive access. "
                "Close all Firefox windows and wait a few seconds for the "
                "process to fully exit before retrying."
            ),
            "hint_for_mcp_client": "Tell the user to close Firefox browser before proceeding",
        }
    return None


def _get_bruteforce_connection(profile_name: str | None):
    """Get database connection using brute force methods (bypasses Firefox lock)."""
    profile_path = get_profile_directory(profile_name)
    if not profile_path:
        return None, "Profile not found"

    db_path = profile_path / "places.sqlite"
    if not db_path.exists():
        return None, "places.sqlite not found"

    return FirefoxDatabaseUnlocker.get_database_connection_bruteforce(db_path)


async def _bruteforce_read_operation(
    operation: str,
    profile_name: str | None,
    folder_id: int | None,
    bookmark_id: int | None,
    search_query: str | None,
    search_type: str,
    similarity_threshold: float,
    age_days: int,
) -> dict[str, Any]:
    """Execute read operations using brute force database access."""
    conn, method = _get_bruteforce_connection(profile_name)

    if not conn:
        return {
            "success": False,
            "error": f"Brute force access failed: {method}",
            "note": "Close Firefox and try again without force_access=True",
        }

    try:
        cursor = conn.cursor()

        if operation == "list_bookmarks":
            # Query bookmarks directly
            query = """
                SELECT b.id, b.title, p.url, b.dateAdded, b.lastModified
                FROM moz_bookmarks b
                LEFT JOIN moz_places p ON b.fk = p.id
                WHERE b.type = 1
            """
            if folder_id:
                query += f" AND b.parent = {folder_id}"
            query += " ORDER BY b.dateAdded DESC LIMIT 1000"

            cursor.execute(query)
            bookmarks = [
                {
                    "id": row[0],
                    "title": row[1] or "",
                    "url": row[2] or "",
                    "dateAdded": row[3],
                    "lastModified": row[4],
                }
                for row in cursor.fetchall()
            ]

            return {
                "success": True,
                "message": "Bookmarks listed (brute force access)",
                "access_method": method,
                "firefox_was_running": True,
                "profile_name": profile_name,
                "folder_id": folder_id,
                "bookmarks": bookmarks,
                "count": len(bookmarks),
            }

        elif operation == "get_bookmark":
            if not bookmark_id:
                return {"success": False, "error": "bookmark_id required"}

            cursor.execute(
                """
                SELECT b.id, b.title, p.url, b.dateAdded, b.lastModified, b.parent
                FROM moz_bookmarks b
                LEFT JOIN moz_places p ON b.fk = p.id
                WHERE b.id = ?
                """,
                (bookmark_id,),
            )
            row = cursor.fetchone()
            if not row:
                return {"success": False, "error": f"Bookmark {bookmark_id} not found"}

            return {
                "success": True,
                "message": f"Bookmark {bookmark_id} retrieved (brute force)",
                "access_method": method,
                "bookmark": {
                    "id": row[0],
                    "title": row[1] or "",
                    "url": row[2] or "",
                    "dateAdded": row[3],
                    "lastModified": row[4],
                    "parent": row[5],
                },
            }

        elif operation == "search_bookmarks":
            if not search_query:
                return {"success": False, "error": "search_query required"}

            like_query = f"%{search_query}%"
            cursor.execute(
                """
                SELECT b.id, b.title, p.url
                FROM moz_bookmarks b
                LEFT JOIN moz_places p ON b.fk = p.id
                WHERE b.type = 1
                  AND (b.title LIKE ? OR p.url LIKE ?)
                LIMIT 100
                """,
                (like_query, like_query),
            )
            results = [
                {"id": row[0], "title": row[1] or "", "url": row[2] or ""}
                for row in cursor.fetchall()
            ]

            return {
                "success": True,
                "message": f"Search completed (brute force)",
                "access_method": method,
                "search_query": search_query,
                "results": results,
                "count": len(results),
            }

        elif operation == "get_bookmark_stats":
            cursor.execute("SELECT COUNT(*) FROM moz_bookmarks WHERE type = 1")
            bookmark_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM moz_places")
            url_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(DISTINCT parent) FROM moz_bookmarks WHERE type = 1")
            folder_count = cursor.fetchone()[0]

            return {
                "success": True,
                "message": "Stats retrieved (brute force)",
                "access_method": method,
                "stats": {
                    "bookmark_count": bookmark_count,
                    "url_count": url_count,
                    "folder_count": folder_count,
                },
            }

        else:
            # Other read operations - fall back to normal path
            return {
                "success": False,
                "error": f"Brute force not implemented for {operation}",
                "note": "Close Firefox and try without force_access=True",
            }

    except Exception as e:
        logger.error(f"Brute force operation failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Brute force operation failed: {str(e)}",
        }

    finally:
        # Clean up temp file if database was copied
        if hasattr(conn, "temp_db_path"):
            try:
                conn.temp_db_path.unlink(missing_ok=True)
            except Exception:
                pass
        conn.close()


# NOTE: No @mcp.tool() - browser_bookmarks portmanteau handles all browsers
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
    force_access: bool = False,
) -> dict[str, Any]:
    """Firefox bookmark management portmanteau tool.

    Comprehensive Firefox bookmark operations consolidating ALL bookmark management
    into a single interface. Supports CRUD operations, search, deduplication, tagging,
    age analysis, broken link detection, and export across Firefox profiles.

    Prerequisites:
        - Firefox should be closed, OR use force_access=True to bypass lock
        - Valid Firefox profile name (use firefox_profiles to list available profiles)
        - For write operations: Profile must exist and be accessible
        - For broken link detection: Network connectivity required

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

    Parameters:
        operation (str, REQUIRED): The operation to perform
            Valid values: 'list_bookmarks', 'get_bookmark', 'add_bookmark',
                         'search_bookmarks', 'find_duplicates', 'export_bookmarks',
                         'batch_update_tags', 'remove_unused_tags', 'list_tags',
                         'find_similar_tags', 'merge_tags', 'clean_up_tags',
                         'find_old_bookmarks', 'get_bookmark_stats', 'find_broken_links'
            Example: 'list_bookmarks', 'add_bookmark', 'search_bookmarks'

        profile_name (str, OPTIONAL): Firefox profile name to operate on
            Format: Valid Firefox profile name
            Default: 'default' (if not specified)
            Required for: All operations
            Example: 'default', 'work', 'personal'
            Validation: Profile must exist (use firefox_profiles to verify)

        folder_id (int, OPTIONAL): ID of the folder to operate on
            Format: Numeric folder ID from Firefox database
            Used for: list_bookmarks operation (filter by folder)
            Example: 1, 2, 3 (1=Bookmarks Menu, 2=Bookmarks Toolbar, 3=Other Bookmarks)

        bookmark_id (int, OPTIONAL): ID of the specific bookmark
            Format: Numeric bookmark ID from Firefox database
            Required for: get_bookmark operation
            Example: 12345, 67890

        url (str, OPTIONAL): URL for the bookmark
            Format: Full URL including protocol
            Required for: add_bookmark operation
            Validation: Must be valid URL format
            Example: 'https://example.com', 'https://docs.python.org/3/'

        title (str, OPTIONAL): Title for the bookmark
            Format: Human-readable bookmark title
            Required for: add_bookmark operation
            Example: 'Python Documentation', 'Example Website'

        tags (list[str], OPTIONAL): List of tags to apply
            Format: List of tag strings
            Used for: add_bookmark, batch_update_tags operations
            Example: ['work', 'programming'], ['reference', 'docs']

        search_query (str, OPTIONAL): Search query string
            Format: Free-form search text
            Required for: search_bookmarks operation
            Behavior: Searches titles, URLs, and tags based on search_type
            Example: 'python', 'https://docs', 'programming'

        search_type (str, OPTIONAL): Type of search to perform
            Valid values: 'all', 'title', 'url', 'tags'
            Default: 'all'
            Used for: search_bookmarks operation
            'all': Search titles, URLs, and tags
            'title': Search only bookmark titles
            'url': Search only bookmark URLs
            'tags': Search only tags

        export_format (str, OPTIONAL): Format for exported bookmarks
            Valid values: 'json', 'csv', 'html'
            Default: 'json'
            Used for: export_bookmarks operation
            Example: 'json', 'csv', 'html'

        export_path (str, OPTIONAL): Path to save exported data
            Format: Absolute or relative file path
            Required for: export_bookmarks operation
            Validation: Parent directory must exist and be writable
            Example: 'C:/backups/bookmarks.json', './exports/firefox_bookmarks.html'

        batch_size (int, OPTIONAL): Number of bookmarks to process per batch
            Format: Positive integer
            Range: 1-10,000
            Default: 100
            Used for: batch_update_tags, find_duplicates operations
            Impact: Larger batches faster but use more memory

        similarity_threshold (float, OPTIONAL): Threshold for duplicate detection
            Format: Float between 0.0 and 1.0
            Range: 0.0-1.0
            Default: 0.85
            Used for: find_duplicates operation
            Behavior: Higher values require more similarity (0.9=very strict, 0.7=loose)

        age_days (int, OPTIONAL): Age threshold for old bookmark detection
            Format: Positive integer (days)
            Range: 1-36500 (1 day to 100 years)
            Default: 365
            Used for: find_old_bookmarks operation
            Example: 30, 90, 365, 730

        check_links (bool, OPTIONAL): Whether to check link accessibility
            Default: False
            Behavior: If True, tests URL accessibility via HTTP request
            Used for: find_broken_links operation
            Warning: May be slow for large bookmark collections
            Example: True, False

        force_access (bool, OPTIONAL): Bypass Firefox database lock for read operations
            Default: False
            Behavior: If True, uses brute force methods (URI tricks, temp copy) to read
                     the database even when Firefox is running
            Used for: READ operations only (list, search, get, stats)
            Warning: Write operations still require Firefox to be closed
            Note: Read data may be slightly stale if Firefox has pending writes
            Example: True to read while Firefox is open, False for normal operation

    Returns:
        Dictionary containing operation-specific results:
            - success: Boolean indicating operation success
            - operation: Echo of operation performed
            - For list_bookmarks: bookmarks (list), total_count, folder_id
            - For get_bookmark: bookmark (dict with details)
            - For add_bookmark: bookmark_id, message, url, title
            - For search_bookmarks: results (list), count, query
            - For find_duplicates: duplicates (list), total_duplicates
            - For export_bookmarks: export_path, format, record_count
            - For tag operations: tags_processed, tags_affected, changes (list)
            - For find_old_bookmarks: old_bookmarks (list), count, age_days
            - For get_bookmark_stats: stats (dict with collection statistics)
            - For find_broken_links: broken_links (list), count, checked_count
            - error: Error message if success is False
            - available_operations: List of valid operations (on invalid operation)

    Usage:
        This tool provides comprehensive Firefox bookmark management. Use it to organize,
        search, and maintain your bookmark collections across Firefox profiles.

        Common scenarios:
        - Organization: Add bookmarks, apply tags, organize by folders
        - Search: Find bookmarks by title, URL, or tags
        - Maintenance: Remove duplicates, clean up old bookmarks, fix broken links
        - Backup: Export bookmarks for backup or migration
        - Analysis: Get statistics about bookmark usage and age

        Best practices:
        - Always close Firefox before operations to prevent database locks
        - Use tags for better organization and searchability
        - Regularly check for duplicates and broken links
        - Export bookmarks periodically for backup
        - Use profile_name to manage separate bookmark collections

    Examples:
        List all bookmarks:
            result = await firefox_bookmarks(
                operation='list_bookmarks',
                profile_name='default'
            )
            # Returns: {
            #     'success': True,
            #     'bookmarks': [...],
            #     'total_count': 150
            # }

        Add bookmark:
            result = await firefox_bookmarks(
                operation='add_bookmark',
                profile_name='work',
                url='https://docs.python.org/3/',
                title='Python Documentation',
                tags=['programming', 'reference']
            )
            # Returns: {
            #     'success': True,
            #     'bookmark_id': 12345,
            #     'message': 'Bookmark added successfully'
            # }

        Search bookmarks:
            result = await firefox_bookmarks(
                operation='search_bookmarks',
                profile_name='default',
                search_query='python',
                search_type='title'
            )
            # Returns: {
            #     'success': True,
            #     'results': [
            #         {'id': 123, 'title': 'Python.org', 'url': 'https://python.org'}
            #     ],
            #     'count': 5
            # }

        Find duplicates:
            result = await firefox_bookmarks(
                operation='find_duplicates',
                profile_name='default',
                similarity_threshold=0.9
            )
            # Returns: {
            #     'success': True,
            #     'duplicates': [
            #         {'url': 'https://example.com', 'count': 3, 'ids': [1, 2, 3]}
            #     ],
            #     'total_duplicates': 5
            # }

        Export bookmarks:
            result = await firefox_bookmarks(
                operation='export_bookmarks',
                profile_name='default',
                export_format='json',
                export_path='C:/backups/firefox_bookmarks.json'
            )
            # Returns: {
            #     'success': True,
            #     'export_path': 'C:/backups/firefox_bookmarks.json',
            #     'format': 'json',
            #     'record_count': 150
            # }

        Find old bookmarks:
            result = await firefox_bookmarks(
                operation='find_old_bookmarks',
                profile_name='default',
                age_days=365
            )
            # Returns: {
            #     'success': True,
            #     'old_bookmarks': [...],
            #     'count': 25,
            #     'age_days': 365
            # }

        Error handling - Firefox running:
            result = await firefox_bookmarks(
                operation='list_bookmarks',
                profile_name='default'
            )
            # Returns: {
            #     'success': False,
            #     'error': 'Firefox is running. Close Firefox before operations.'
            # }

    Errors:
        Common errors and solutions:
        - 'Firefox is running. Close Firefox before operations':
            Cause: Firefox browser is currently running and has database locked
            Fix: Completely close all Firefox windows and processes
            Workaround: Wait for Firefox to close, check Task Manager for processes

        - 'Profile not found: {profile_name}':
            Cause: Specified profile doesn't exist
            Fix: Use firefox_profiles(operation='get_firefox_profiles') to list profiles
            Workaround: Use 'default' profile name, check profile spelling

        - 'Database locked':
            Cause: Another process is accessing Firefox database
            Fix: Close Firefox, wait a few seconds, check for background processes
            Workaround: Restart computer if Firefox won't release lock

        - 'Bookmark ID not found: {bookmark_id}':
            Cause: Specified bookmark_id doesn't exist in database
            Fix: Use list_bookmarks to find valid bookmark IDs
            Workaround: Search by URL or title instead

        - 'Invalid URL format':
            Cause: URL doesn't match valid URL pattern
            Fix: Ensure URL starts with http:// or https://, check for typos
            Example: 'https://example.com' not 'example.com'

        - 'Export failed: {error}':
            Cause: Export path inaccessible or insufficient permissions
            Fix: Verify path exists, check write permissions, ensure disk space
            Workaround: Export to user home directory or desktop

    See Also:
        - firefox_profiles: List and manage Firefox profiles
        - browser_bookmarks: Universal browser bookmark operations (cross-browser)
        - firefox_tagging: Advanced tag management operations
    """

    # Read operations that support force_access
    read_operations = {
        "list_bookmarks", "get_bookmark", "search_bookmarks", "find_duplicates",
        "list_tags", "find_similar_tags", "find_old_bookmarks", "get_bookmark_stats",
    }

    # Handle force_access for read operations when Firefox is running
    if force_access and operation in read_operations:
        status = FirefoxStatusChecker.is_firefox_running()
        if status.get("is_running"):
            logger.info(f"Firefox running, using brute force for {operation}")
            return await _bruteforce_read_operation(
                operation, profile_name, folder_id, bookmark_id,
                search_query, search_type, similarity_threshold, age_days
            )

    # Block write operations when Firefox is running with explicit error
    firefox_error = _check_firefox_for_write(operation)
    if firefox_error:
        logger.warning(f"Blocking {operation} - Firefox is running")
        return firefox_error

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


async def _find_duplicates(profile_name: str | None, similarity_threshold: float) -> dict[str, Any]:
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
