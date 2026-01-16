"""
Universal browser bookmark management portmanteau tool.

This module provides a unified interface for bookmark management across all
supported browsers with full CRUD and advanced operations.
"""

from typing import Any

from database_operations_mcp.config.mcp_config import mcp


@mcp.tool()
async def browser_bookmarks(
    operation: str,
    browser: str,
    profile_name: str | None = None,
    # Core parameters
    folder_id: int | None = None,
    bookmark_id: str | None = None,
    url: str | None = None,
    title: str | None = None,
    folder: str | None = None,
    # Edit parameters
    new_title: str | None = None,
    new_folder: str | None = None,
    # Search/filter parameters
    tags: list[str] | None = None,
    search_query: str | None = None,
    search_type: str = "all",
    limit: int = 100,
    # Export parameters
    export_format: str = "json",
    export_path: str | None = None,
    # Advanced parameters
    batch_size: int = 100,
    similarity_threshold: float = 0.85,
    age_days: int = 365,
    check_links: bool = False,
    # Options
    allow_duplicates: bool = False,
    create_folders: bool = True,
    dry_run: bool = False,
    # Firefox lock bypass
    force_access: bool = False,
) -> dict[str, Any]:
    """Universal browser bookmark management portmanteau tool.

    Comprehensive cross-browser bookmark operations consolidating ALL bookmark
    management across supported browsers into a single interface. Automatically
    detects browser type and routes to appropriate browser-specific implementation.

    Prerequisites:
        - Target browser must be installed and accessible
        - For Firefox: Firefox should be closed, OR use force_access=True to bypass lock
        - For Chrome/Edge/Brave: Browser should be closed (recommended, not required)
        - Valid browser profile name (uses default if not specified)

    Supported Browsers:
        - 'firefox': Firefox (uses SQLite database, full feature set)
        - 'chrome': Google Chrome (uses JSON file)
        - 'edge': Microsoft Edge (uses JSON file)
        - 'brave': Brave Browser (uses JSON file)

    Operations (all browsers):
        - list_bookmarks: List bookmarks with filtering
        - add_bookmark: Add a new bookmark (requires url, title)
        - edit_bookmark: Edit bookmark title/folder (Chromium only)
        - delete_bookmark: Delete a bookmark (Chromium only)
        - get_bookmark: Get specific bookmark by ID
        - search / search_bookmarks: Search bookmarks by query

    Operations (Firefox only - advanced):
        - find_duplicates: Find duplicate bookmarks
        - export_bookmarks: Export bookmarks to JSON/CSV/HTML
        - batch_update_tags: Update tags for multiple bookmarks
        - remove_unused_tags: Remove orphan tags
        - list_tags: List all tags
        - find_similar_tags: Find similar tag names
        - merge_tags: Merge similar tags
        - clean_up_tags: Standardize tag names
        - find_old_bookmarks: Find bookmarks older than N days
        - get_bookmark_stats: Get collection statistics
        - find_broken_links: Check for broken URLs

    Parameters:
        operation (str, REQUIRED): Bookmark operation to perform
        browser (str, REQUIRED): Browser type ('firefox', 'chrome', 'edge', 'brave')
        profile_name (str, OPTIONAL): Browser profile name
        url (str, OPTIONAL): Bookmark URL
        title (str, OPTIONAL): Bookmark title
        folder (str, OPTIONAL): Target folder for add_bookmark
        bookmark_id (str, OPTIONAL): Bookmark ID for specific operations
        new_title (str, OPTIONAL): New title for edit_bookmark
        new_folder (str, OPTIONAL): New folder for edit_bookmark
        search_query (str, OPTIONAL): Search query string
        search_type (str, OPTIONAL): Search type ('all', 'title', 'url', 'tags')
        tags (list[str], OPTIONAL): Tags for bookmark operations
        limit (int, OPTIONAL): Max results (default: 100)
        export_format (str, OPTIONAL): Export format ('json', 'csv', 'html')
        export_path (str, OPTIONAL): Path for export file
        similarity_threshold (float, OPTIONAL): Duplicate detection threshold
        age_days (int, OPTIONAL): Age threshold for old bookmark detection
        check_links (bool, OPTIONAL): Check URL accessibility
        dry_run (bool, OPTIONAL): Preview changes without applying
        force_access (bool, OPTIONAL): For Firefox - bypass database lock using brute force
            methods (read-only URI tricks, temp copy). Allows reading bookmarks while
            Firefox is running. Default: False

    Returns:
        Dictionary containing operation-specific results

    Examples:
        List Chrome bookmarks:
            browser_bookmarks(operation='list_bookmarks', browser='chrome')

        Add bookmark to Firefox:
            browser_bookmarks(
                operation='add_bookmark',
                browser='firefox',
                url='https://example.com',
                title='Example',
                tags=['work', 'reference']
            )

        Search Edge bookmarks:
            browser_bookmarks(
                operation='search',
                browser='edge',
                search_query='python'
            )

        Find old Firefox bookmarks:
            browser_bookmarks(
                operation='find_old_bookmarks',
                browser='firefox',
                age_days=365
            )

        Export Firefox bookmarks:
            browser_bookmarks(
                operation='export_bookmarks',
                browser='firefox',
                export_format='json',
                export_path='./bookmarks.json'
            )
    """
    browser_lower = browser.lower()

    # Firefox - delegate to firefox_bookmarks helper (supports all operations)
    if browser_lower == "firefox":
        from database_operations_mcp.tools.firefox_bookmarks import firefox_bookmarks as ff_bookmarks

        # Map 'search' to 'search_bookmarks' for Firefox
        ff_operation = "search_bookmarks" if operation == "search" else operation

        result = await ff_bookmarks(
            operation=ff_operation,
            profile_name=profile_name,
            folder_id=folder_id,
            bookmark_id=int(bookmark_id) if bookmark_id and bookmark_id.isdigit() else None,
            url=url,
            title=title,
            tags=tags,
            search_query=search_query,
            search_type=search_type,
            export_format=export_format,
            export_path=export_path,
            batch_size=batch_size,
            similarity_threshold=similarity_threshold,
            age_days=age_days,
            check_links=check_links,
            force_access=force_access,
        )
        result["browser"] = "firefox"
        return result

    # Chrome/Edge/Brave - use chromium helpers directly
    elif browser_lower in ["chrome", "edge", "brave"]:
        # Import the appropriate browser module
        if browser_lower == "chrome":
            from database_operations_mcp.tools.chrome import (
                list_chrome_bookmarks,
                add_chrome_bookmark,
                edit_chrome_bookmark,
                delete_chrome_bookmark,
            )
            list_fn = list_chrome_bookmarks
            add_fn = add_chrome_bookmark
            edit_fn = edit_chrome_bookmark
            delete_fn = delete_chrome_bookmark
        elif browser_lower == "edge":
            from database_operations_mcp.tools.edge import (
                list_edge_bookmarks,
                add_edge_bookmark,
                edit_edge_bookmark,
                delete_edge_bookmark,
            )
            list_fn = list_edge_bookmarks
            add_fn = add_edge_bookmark
            edit_fn = edit_edge_bookmark
            delete_fn = delete_edge_bookmark
        else:  # brave
            from database_operations_mcp.tools.brave import (
                list_brave_bookmarks,
                add_brave_bookmark,
                edit_brave_bookmark,
                delete_brave_bookmark,
            )
            list_fn = list_brave_bookmarks
            add_fn = add_brave_bookmark
            edit_fn = edit_brave_bookmark
            delete_fn = delete_brave_bookmark

        # Route to operation
        if operation == "list_bookmarks":
            result = await list_fn()
            result["browser"] = browser_lower
            result["operation"] = operation
            # Apply limit
            if "bookmarks" in result:
                result["total_count"] = len(result["bookmarks"])
                result["bookmarks"] = result["bookmarks"][:limit]
                result["returned_count"] = len(result["bookmarks"])
            return result

        elif operation == "add_bookmark":
            if not url or not title:
                return {
                    "success": False,
                    "browser": browser_lower,
                    "operation": operation,
                    "error": "add_bookmark requires 'url' and 'title' parameters",
                }
            result = await add_fn(title=title, url=url, folder=folder)
            result["browser"] = browser_lower
            result["operation"] = operation
            return result

        elif operation == "edit_bookmark":
            if not bookmark_id and not url:
                return {
                    "success": False,
                    "browser": browser_lower,
                    "operation": operation,
                    "error": "edit_bookmark requires 'bookmark_id' or 'url' parameter",
                }
            result = await edit_fn(
                id=bookmark_id,
                url=url,
                new_title=new_title,
                new_folder=new_folder,
                allow_duplicates=allow_duplicates,
                create_folders=create_folders,
                dry_run=dry_run,
            )
            result["browser"] = browser_lower
            result["operation"] = operation
            return result

        elif operation == "delete_bookmark":
            if not bookmark_id and not url:
                return {
                    "success": False,
                    "browser": browser_lower,
                    "operation": operation,
                    "error": "delete_bookmark requires 'bookmark_id' or 'url' parameter",
                }
            result = await delete_fn(
                id=bookmark_id,
                url=url,
                dry_run=dry_run,
            )
            result["browser"] = browser_lower
            result["operation"] = operation
            return result

        elif operation in ["search", "search_bookmarks"]:
            if not search_query:
                return {
                    "success": False,
                    "browser": browser_lower,
                    "operation": operation,
                    "error": "search requires 'search_query' parameter",
                }
            # Get all bookmarks and filter
            result = await list_fn()
            bookmarks = result.get("bookmarks", [])
            query_lower = search_query.lower()
            matches = [
                b for b in bookmarks
                if query_lower in (b.get("title", "") or "").lower()
                or query_lower in (b.get("url", "") or "").lower()
            ]
            return {
                "success": True,
                "browser": browser_lower,
                "operation": operation,
                "query": search_query,
                "results": matches[:limit],
                "total_matches": len(matches),
                "returned_count": min(len(matches), limit),
            }

        elif operation == "get_bookmark":
            if not bookmark_id and not url:
                return {
                    "success": False,
                    "browser": browser_lower,
                    "operation": operation,
                    "error": "get_bookmark requires 'bookmark_id' or 'url' parameter",
                }
            # Get all bookmarks and find match
            result = await list_fn()
            bookmarks = result.get("bookmarks", [])
            for b in bookmarks:
                if (bookmark_id and b.get("id") == bookmark_id) or (url and b.get("url") == url):
                    return {
                        "success": True,
                        "browser": browser_lower,
                        "operation": operation,
                        "bookmark": b,
                    }
            return {
                "success": False,
                "browser": browser_lower,
                "operation": operation,
                "error": f"Bookmark not found: {bookmark_id or url}",
            }

        else:
            return {
                "success": False,
                "browser": browser_lower,
                "operation": operation,
                "error": f"Operation '{operation}' not supported for {browser_lower}",
                "supported_operations": [
                    "list_bookmarks", "add_bookmark", "edit_bookmark",
                    "delete_bookmark", "get_bookmark", "search"
                ],
                "note": "For advanced operations (duplicates, tags, export), use browser='firefox'",
            }

    else:
        return {
            "success": False,
            "operation": operation,
            "browser": browser,
            "error": f"Unknown browser type: {browser}",
            "supported_browsers": ["firefox", "chrome", "edge", "brave"],
        }
