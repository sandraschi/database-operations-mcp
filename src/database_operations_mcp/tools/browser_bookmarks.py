"""
Universal browser bookmark management portmanteau tool.

This module provides a unified interface for bookmark management across all
supported browsers with full CRUD and advanced operations.
"""

from typing import Any

from database_operations_mcp.tools.help_system import HelpSystem
from database_operations_mcp.config.mcp_config import mcp


@mcp.tool()
@HelpSystem.register_tool
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
    # Sync parameters
    target_browser: str | None = None,
    # Firefox lock bypass
    force_access: bool = False,
) -> dict[str, Any]:
    """Universal browser bookmark management portmanteau tool.

    Browsers: firefox, chrome, edge, brave.
    Core ops (all): list_bookmarks, add_bookmark, edit_bookmark, delete_bookmark,
    get_bookmark, search/search_bookmarks, sync_bookmarks.
    Firefox-only: find_duplicates, export_bookmarks, batch_update_tags,
    remove_unused_tags, list_tags, find_similar_tags, merge_tags, clean_up_tags,
    find_old_bookmarks, get_bookmark_stats, find_broken_links.
    For full docs call help_system.
    """
    browser_lower = browser.lower()

    # Special handling for sync_bookmarks (cross-browser operation)
    if operation == "sync_bookmarks":
        if not target_browser:
            return {
                "success": False,
                "error": "sync_bookmarks operation requires 'target_browser' parameter",
            }
        from database_operations_mcp.tools.sync_tools import sync_bookmarks

        return await sync_bookmarks(
            source_browser=browser,
            target_browser=target_browser,
            dry_run=dry_run,
            limit=limit,
        )

    # Firefox - delegate to firefox_bookmarks helper (supports all operations)
    if browser_lower == "firefox":
        from database_operations_mcp.tools.firefox_bookmarks import (
            firefox_bookmarks as ff_bookmarks,
        )

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
                b
                for b in bookmarks
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
                    "list_bookmarks",
                    "add_bookmark",
                    "edit_bookmark",
                    "delete_bookmark",
                    "get_bookmark",
                    "search",
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
