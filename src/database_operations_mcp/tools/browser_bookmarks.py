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

    Comprehensive cross-browser bookmark operations consolidating ALL bookmark
    management across supported browsers into a single interface. Automatically
    detects browser type and routes to appropriate browser-specific implementation.
    Eliminates need to know which browser you're working with.

    Prerequisites:
        - Target browser must be installed and accessible
        - For Firefox: Firefox must be completely closed (prevents database lock)
        - For Chrome/Edge/Brave: Browser should be closed (recommended, not required)
        - For Safari: Browser should be closed (macOS only)
        - Valid browser profile name (uses default if not specified)

    Supported Browsers:
        - 'firefox': Firefox (uses SQLite database)
        - 'chrome': Google Chrome (uses JSON file)
        - 'edge': Microsoft Edge (uses JSON file, same as Chrome)
        - 'brave': Brave Browser (uses JSON file, same as Chrome)
        - 'safari': Safari (uses SQLite database with different schema)

    Operations:
        Core bookmark operations:
        - list_bookmarks: List bookmarks with filtering and pagination
        - get_bookmark: Get specific bookmark by ID
        - search: Advanced bookmark search with multiple criteria
        - find_duplicates: Find duplicate bookmarks by URL or content
        - find_broken_links: Check bookmarks for broken URLs
        - export: Export bookmarks to various formats
        - import: Import bookmarks from external sources

        Tagging operations:
        - list_tags: List all tags used in profile
        - tag_from_folder: Generate tags from folder structure
        - merge_tags: Merge similar or duplicate tags
        - clean_up_tags: Remove unused or redundant tags

        Backup operations:
        - backup_browser_data: Create complete profile backup
        - restore_browser_data: Restore from backup
        - list_backups: List available backup files

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

        operation (str, REQUIRED): Bookmark operation to perform
            Valid values: See Operations section above
            Example: 'list_bookmarks', 'search', 'find_duplicates'

        browser (str, REQUIRED): Browser type
            Valid values: 'firefox', 'chrome', 'edge', 'brave', 'safari'
            Validation: Browser must be installed
            Behavior: Auto-routes to browser-specific handler
            Example: 'firefox', 'chrome', 'edge'

        profile_name (str, OPTIONAL): Browser profile name
            Format: Browser-specific profile identifier
            Firefox: 'default', 'work', 'personal', etc.
            Chrome/Edge/Brave: 'Default', 'Profile 1', 'Profile 2', etc.
            Safari: Profile identifiers (macOS only)
            Default: Uses default profile for browser type
            Example: 'default', 'work', 'Profile 1'

        folder_id (int, OPTIONAL): Folder ID for folder-based operations
            Format: Numeric folder ID (browser-specific)
            Used for: list_bookmarks operation (filter by folder)
            Example: 1, 2, 3 (varies by browser)

        bookmark_id (int|str, OPTIONAL): Bookmark ID for specific operations
            Format: Browser-specific bookmark identifier
            Required for: get_bookmark operation
            Example: 12345 (Firefox), 'bookmark-uuid' (Chrome)

        url (str, OPTIONAL): Bookmark URL
            Format: Full URL including protocol
            Required for: Add operations
            Validation: Must be valid URL format
            Example: 'https://example.com/page', 'https://docs.python.org/3/'

        title (str, OPTIONAL): Bookmark title
            Format: Human-readable bookmark title
            Required for: Add operations
            Example: 'Python Documentation', 'Example Website'

        tags (list[str], OPTIONAL): List of tags for bookmark
            Format: List of tag strings
            Used for: Tagging operations
            Example: ['work', 'reference'], ['programming', 'docs']

        search_query (str, OPTIONAL): Search query string
            Format: Free-form search text
            Required for: search operation
            Behavior: Searches bookmark titles and URLs (case-insensitive)
            Example: 'python', 'https://docs.python.org', 'machine learning'

        limit (int, OPTIONAL): Maximum number of results to return
            Format: Positive integer
            Range: 1-1,000
            Default: 100
            Used for: list_bookmarks, search operations
            Behavior: Limits result set size for pagination
            Example: 50, 100, 500

    Returns:
        Dictionary containing operation-specific results:
            - success: Boolean indicating operation success
            - operation: Echo of operation performed
            - browser: Echo of browser type used
            - profile_name: Echo of profile name used
            - For list_bookmarks: bookmarks (list), total_count, limit
            - For get_bookmark: bookmark (dict with details)
            - For search: results (list), count, query
            - For find_duplicates: duplicates (list), total_duplicates
            - For find_broken_links: broken_links (list), count
            - For export: export_path, format, record_count
            - For import: imported_count, errors (list)
            - For tag operations: tags (list), count, changes (list)
            - For backup operations: backup_path, backup_info (dict)
            - data: Operation-specific data (varies by operation)
            - message: Human-readable status message
            - warnings: List of warnings (if any)
            - error: Error message if success is False
            - supported_browsers: List of valid browsers (on invalid browser)

    Usage:
        This tool provides universal bookmark management across all supported browsers.
        Use it when you need to work with bookmarks without knowing which browser you're
        using, or when performing cross-browser operations.

        Common scenarios:
        - Cross-browser search: Find bookmarks across different browsers
        - Unified interface: Single API for all browser types
        - Migration: Move bookmarks between browsers
        - Backup: Backup bookmarks from any browser
        - Analysis: Analyze bookmark collections across browsers

        Best practices:
        - Close browsers before operations (especially Firefox)
        - Use correct profile names for each browser type
        - Verify browser is installed before operations
        - Use browser-specific tools for advanced features

    Examples:
        List Chrome bookmarks:
            result = await browser_bookmarks(
                operation='list_bookmarks',
                browser='chrome',
                profile_name='Default',
                limit=50
            )
            # Returns: {
            #     'success': True,
            #     'browser': 'chrome',
            #     'bookmarks': [...],
            #     'total_count': 150
            # }

        Search Firefox bookmarks:
            result = await browser_bookmarks(
                operation='search',
                browser='firefox',
                profile_name='default',
                search_query='python',
                tags=['programming'],
                limit=100
            )
            # Returns: {
            #     'success': True,
            #     'browser': 'firefox',
            #     'results': [...],
            #     'count': 12
            # }

        Find duplicates in Edge:
            result = await browser_bookmarks(
                operation='find_duplicates',
                browser='edge',
                profile_name='Default'
            )
            # Returns: {
            #     'success': True,
            #     'browser': 'edge',
            #     'duplicates': [...],
            #     'total_duplicates': 5
            # }

        Export Chrome bookmarks:
            result = await browser_bookmarks(
                operation='export',
                browser='chrome',
                profile_name='Default'
            )
            # Returns: {
            #     'success': True,
            #     'browser': 'chrome',
            #     'export_path': '...',
            #     'format': 'json',
            #     'record_count': 150
            # }

        Get tags from any browser:
            result = await browser_bookmarks(
                operation='list_tags',
                browser='brave',
                profile_name='Default'
            )
            # Returns: {
            #     'success': True,
            #     'browser': 'brave',
            #     'tags': ['work', 'programming', 'docs'],
            #     'count': 15
            # }

        Error handling - browser not installed:
            result = await browser_bookmarks(
                operation='list_bookmarks',
                browser='safari'
            )
            # Returns: {
            #     'success': False,
            #     'error': 'Safari support is not yet implemented'
            # }

        Error handling - invalid browser:
            result = await browser_bookmarks(
                operation='list_bookmarks',
                browser='invalid_browser'
            )
            # Returns: {
            #     'success': False,
            #     'error': 'Unknown browser type: invalid_browser',
            #     'supported_browsers': ['firefox', 'chrome', 'edge', 'brave', 'safari']
            # }

    Errors:
        Common errors and solutions:
        - 'Browser is running. Close browser before operations':
            Cause: Browser is currently running (especially Firefox)
            Fix: Completely close all browser windows and processes
            Workaround: Wait for browser to close, check Task Manager

        - 'Browser not found: {browser}':
            Cause: Specified browser is not installed
            Fix: Install browser or use different browser type
            Workaround: Use browser_bookmarks(operation='list') to see available browsers

        - 'Profile not found: {profile_name}':
            Cause: Specified profile doesn't exist for browser
            Fix: Use correct profile name for browser type
            Workaround: List profiles first, use default profile

        - 'Safari support is not yet implemented':
            Cause: Safari bookmark management not yet available
            Fix: Use Firefox or Chrome for now, Safari support coming soon
            Workaround: Export Safari bookmarks manually, import to Firefox/Chrome

        - 'Unknown browser type: {browser}':
            Cause: Browser type not in supported list
            Fix: Use one of: firefox, chrome, edge, brave, safari
            Example: browser='firefox' not browser='mozilla'

        - 'Operation not supported for browser: {browser}':
            Cause: Operation not available for specific browser type
            Fix: Check operation compatibility, use browser-specific tool
            Workaround: Use firefox_bookmarks or chrome_bookmarks directly

    See Also:
        - firefox_bookmarks: Firefox-specific bookmark management (more features)
        - chrome_bookmarks: Chrome-specific bookmark management (more features)
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
