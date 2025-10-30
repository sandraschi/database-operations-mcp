"""
Universal browser bookmark management portmanteau tool.

This module provides a unified interface for bookmark management across all
supported browsers. Automatically detects browser type and routes to the
appropriate browser-specific manager.
"""

from typing import Any

from database_operations_mcp.config.mcp_config import mcp


@mcp.tool()
async def browser_bookmarks(
    operation: str,
    browser: str,
    profile_name: str | None = None,
    folder_id: int | None = None,
    bookmark_id: int | None = None,
    url: str | None = None,
    title: str | None = None,
    tags: list[str] | None = None,
    search_query: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    """Universal browser bookmark management portmanteau tool.

    Provides a unified interface for bookmark management across ALL supported
    browsers. Automatically detects browser type and routes to the appropriate
    browser-specific implementation. This tool eliminates the need to know
    which browser you're working with, making bookmark operations seamless.

    Supported Browsers:
        - 'firefox': Firefox (uses SQLite database)
        - 'chrome': Google Chrome (uses JSON file)
        - 'edge': Microsoft Edge (uses JSON file, same as Chrome)
        - 'brave': Brave Browser (uses JSON file, same as Chrome)
        - 'safari': Safari (uses SQLite database with different schema)

    Parameters:
        operation: Bookmark operation to perform
            # Core bookmark operations
            - 'list_bookmarks': List bookmarks with filtering and pagination
            - 'get_bookmark': Get specific bookmark by ID
            - 'search': Advanced bookmark search with multiple criteria
            - 'find_duplicates': Find duplicate bookmarks by URL or content
            - 'find_broken_links': Check bookmarks for broken URLs
            - 'export': Export bookmarks to various formats
            - 'import': Import bookmarks from external sources

            # Tagging operations
            - 'list_tags': List all tags used in profile
            - 'tag_from_folder': Generate tags from folder structure
            - 'merge_tags': Merge similar or duplicate tags
            - 'clean_up_tags': Remove unused or redundant tags

            # Backup operations
            - 'backup_browser_data': Create complete profile backup
            - 'restore_browser_data': Restore from backup
            - 'list_backups': List available backup files

        browser: Browser type (required)
            - Must be one of: 'firefox', 'chrome', 'edge', 'brave', 'safari'
            - Determines which browser implementation to use
            - Auto-routes to browser-specific handler

        profile_name: Browser profile name (optional)
            - Firefox: 'default', 'work', 'personal', etc.
            - Chrome/Edge: 'Default', 'Profile 1', 'Profile 2', etc.
            - Safari: Profile identifiers
            - If not provided, uses default profile for browser type

        folder_id: Folder ID for folder-based operations (optional)
            - Used for some bookmark operations
            - Browser-specific implementation

        bookmark_id: Bookmark ID for specific bookmark operations (optional)
            - Retrieve or modify specific bookmark
            - Browser-specific implementation

        url: Bookmark URL (optional, required for add operations)
            - Full URL including protocol
            - Must be valid URL format
            - Example: 'https://example.com/page'

        title: Bookmark title (optional, required for add operations)
            - Human-readable bookmark title
            - Example: 'Example Website'

        tags: List of tags for bookmark (optional)
            - Tags for categorization
            - Example: ['work', 'reference']
            - Used for organization and filtering

        search_query: Search query string (optional, required for search)
            - Searches bookmark titles and URLs
            - Case-insensitive partial matching
            - Example: 'python' or 'https://docs.python.org'

        limit: Maximum number of results to return (default: 100)
            - Controls result set size
            - Range: 1-1000
            - Used for pagination and performance

    Returns:
        Dictionary containing the result of the operation, including status,
        message, browser type, and relevant data.

        Example response structure:
            {
                'success': bool,
                'operation': str,
                'browser': str,
                'profile_name': str,
                'data': {...},       # Bookmarks, tags, etc.
                'message': str,
                'warnings': List[str]
            }

    Usage:
        Universal browser bookmark management covering all browsers in single
        interface. Essential for cross-browser bookmark operations without
        needing to specify browser-specific tools. Auto-detects browser type
        and routes to appropriate implementation.

        Common scenarios:
        - List bookmarks from any browser:
                browser_bookmarks(
                    operation='list_bookmarks',
                    browser='chrome',
                    profile_name='Default',
                    limit=50
                )

        - Search across browser:
                browser_bookmarks(
                    operation='search',
                    browser='firefox',
                    search_query='python',
                    limit=100
                )

        - Find duplicates:
                browser_bookmarks(
                    operation='find_duplicates',
                    browser='chrome'
                )

        - Export bookmarks:
                browser_bookmarks(
                    operation='export',
                    browser='firefox',
                    profile_name='work'
                )

    Examples:
        List Chrome bookmarks:
            result = await browser_bookmarks(
                operation='list_bookmarks',
                browser='chrome',
                profile_name='Default',
                limit=50
            )
            # Returns: List of bookmarks from Chrome default profile

        Search Firefox bookmarks:
            result = await browser_bookmarks(
                operation='search',
                browser='firefox',
                profile_name='default',
                search_query='python',
                tags=['programming'],
                limit=100
            )
            # Returns: Matching bookmarks from Firefox

        Get tags from any browser:
            result = await browser_bookmarks(
                operation='list_tags',
                browser='chrome',
                profile_name='Default'
            )
            # Returns: List of all tags used in Chrome profile

    Notes:
        - Browser must be completely closed before using bookmark operations
        - Profile names vary by browser type
        - Some operations may not be supported for all browsers yet
        - Safari support is limited (different database structure)
        - Chrome/Edge/Brave share same JSON format
        - Firefox uses SQLite with different schema

    See Also:
        - firefox_bookmarks: Firefox-specific bookmark management
        - chrome_bookmarks: Chrome-specific bookmark management
        - firefox_profiles: Firefox profile management
        - chrome_profiles: Chrome profile management
    """
    # Route to appropriate browser handler based on browser type
    if browser.lower() == "firefox":
        # Import and use Firefox bookmark handler
        from database_operations_mcp.tools.firefox_bookmarks import (
            firefox_bookmarks,
        )

        return await firefox_bookmarks(
            operation=operation,
            profile_name=profile_name,
            folder_id=folder_id,
            bookmark_id=bookmark_id,
            url=url,
            title=title,
            tags=tags,
            search_query=search_query,
            limit=limit,
        )

    elif browser.lower() in ["chrome", "edge", "brave"]:
        # Import and use Chrome/Edge/Brave bookmark handler (same format)
        from database_operations_mcp.tools.chrome_bookmarks import chrome_bookmarks

        result = await chrome_bookmarks(
            operation=operation,
            profile_name=profile_name,
            folder_id=folder_id,
            bookmark_id=bookmark_id,
            url=url,
            title=title,
            tags=tags,
            search_query=search_query,
            limit=limit,
        )
        # Update browser field to reflect actual browser
        result["browser"] = browser.lower()
        return result

    elif browser.lower() == "safari":
        # Safari support coming soon
        return {
            "success": False,
            "operation": operation,
            "browser": "safari",
            "error": "Safari support is not yet implemented",
            "message": "Safari bookmark management coming soon",
            "note": "Safari uses SQLite but with different schema than Firefox",
        }

    else:
        return {
            "success": False,
            "operation": operation,
            "browser": browser,
            "error": f"Unknown browser type: {browser}",
            "message": f"Browser '{browser}' is not supported",
            "supported_browsers": ["firefox", "chrome", "edge", "brave", "safari"],
        }
