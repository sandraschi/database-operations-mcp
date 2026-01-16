# Firefox curated sources portmanteau tool.
# Consolidates Firefox curated sources operations into a single interface.

import logging
from typing import Any

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.tools.firefox.curated_sources import (
    get_curated_source,
    list_curated_sources,
)
from database_operations_mcp.tools.help_tools import HelpSystem

logger = logging.getLogger(__name__)


@mcp.tool()
@HelpSystem.register_tool(category="firefox")
async def firefox_curated(
    operation: str,
    source_name: str | None = None,
    category: str | None = None,
    include_metadata: bool = True,
    limit: int = 100,
) -> dict[str, Any]:
    """Firefox curated sources portmanteau tool.

    Comprehensive curated bookmark collections consolidating ALL curated source
    operations into a single interface. Supports accessing predefined bookmark
    collections from GitHub awesome repositories and other curated sources.

    Prerequisites:
        - Network connectivity required to access curated sources
        - For GitHub sources: GitHub API access (rate limits apply)
        - Valid source name or category (use list_curated_sources to discover)

    Operations:
        - get_curated_source: Get a specific curated source by name
        - list_curated_sources: List all available curated sources
        - list_curated_bookmark_sources: List curated bookmark sources with details

    Parameters:
        operation (str, REQUIRED): The operation to perform
            Valid values: 'get_curated_source', 'list_curated_sources',
                         'list_curated_bookmark_sources'
            Example: 'get_curated_source', 'list_curated_sources'

        source_name (str, OPTIONAL): Name of the curated source to retrieve
            Format: Valid curated source identifier
            Required for: get_curated_source operation
            Example: 'awesome-python', 'awesome-javascript', 'awesome-ai'
            Validation: Source must exist (use list_curated_sources to verify)

        category (str, OPTIONAL): Category to filter sources by
            Format: Category name string
            Used for: list_curated_sources, list_curated_bookmark_sources
            Valid values: 'development', 'design', 'data-science', 'security', etc.
            Example: 'development', 'design', 'programming'
            Behavior: Filters sources matching category

        include_metadata (bool, OPTIONAL): Include metadata in results
            Default: True
            Behavior: Includes source descriptions, statistics, and additional info
            Used for: All list operations
            Impact: Provides more context but increases response size

        limit (int, OPTIONAL): Maximum number of sources to return
            Format: Positive integer
            Range: 1-1,000
            Default: 100
            Used for: list_curated_sources, list_curated_bookmark_sources
            Behavior: Limits result set size for pagination
            Example: 50, 100, 500

    Returns:
        Dictionary containing operation-specific results:
            - success: Boolean indicating operation success
            - operation: Echo of operation performed
            - For get_curated_source: source_name, source (dict), bookmarks (list), count
            - For list_curated_sources: sources (list), total_sources, categories (list)
            - For list_curated_bookmark_sources: bookmark_sources (list), total, metadata (dict)
            - error: Error message if success is False
            - available_operations: List of valid operations (on invalid operation)

    Usage:
        This tool provides access to curated bookmark collections from GitHub awesome
        repositories and other sources. Use it to discover high-quality bookmark collections
        and import them into Firefox profiles.

        Common scenarios:
        - Discovery: Find curated bookmark collections by category
        - Import: Get curated sources to import into Firefox profiles
        - Research: Browse available collections before importing
        - Organization: Filter sources by category for better organization

        Best practices:
        - Use list_curated_sources to discover available collections
        - Filter by category to find relevant sources
        - Use include_metadata=True to get source descriptions
        - Import curated sources into separate profiles for testing
        - Review bookmarks before importing large collections

    Examples:
        Get specific curated source:
            result = await firefox_curated(
                operation='get_curated_source',
                source_name='awesome-python',
                include_metadata=True
            )
            # Returns: {
            #     'success': True,
            #     'source_name': 'awesome-python',
            #     'source': {
            #         'name': 'awesome-python',
            #         'description': 'A curated list of Python resources',
            #         'bookmarks': [...]
            #     },
            #     'count': 150
            # }

        List all curated sources:
            result = await firefox_curated(
                operation='list_curated_sources',
                include_metadata=True,
                limit=100
            )
            # Returns: {
            #     'success': True,
            #     'sources': [
            #         {'name': 'awesome-python', 'category': 'development'},
            #         {'name': 'awesome-javascript', 'category': 'development'}
            #     ],
            #     'total_sources': 250
            # }

        List sources by category:
            result = await firefox_curated(
                operation='list_curated_sources',
                category='development',
                limit=50
            )
            # Returns: {
            #     'success': True,
            #     'sources': [...],
            #     'total_sources': 45,
            #     'category': 'development'
            # }

        List bookmark sources:
            result = await firefox_curated(
                operation='list_curated_bookmark_sources',
                category='data-science',
                include_metadata=True
            )
            # Returns: {
            #     'success': True,
            #     'bookmark_sources': [...],
            #     'total': 15,
            #     'metadata': {
            #         'categories': ['data-science', 'machine-learning']
            #     }
            # }

        Error handling - source not found:
            result = await firefox_curated(
                operation='get_curated_source',
                source_name='nonexistent-source'
            )
            # Returns: {
            #     'success': False,
            #     'error': 'Curated source not found: nonexistent-source'
            # }

    Errors:
        Common errors and solutions:
        - 'Curated source not found: {source_name}':
            Cause: Specified source doesn't exist
            Fix: Use list_curated_sources to see available sources
            Workaround: Check source name spelling, verify source exists

        - 'Network error: {error}':
            Cause: Cannot access curated sources (network issue, API rate limit)
            Fix: Check internet connection, wait for rate limit reset
            Workaround: Retry after delay, check GitHub API status

        - 'Invalid category: {category}':
            Cause: Specified category doesn't exist
            Fix: Use list_curated_sources to see available categories
            Workaround: Use None to list all sources, filter manually

        - 'Rate limit exceeded':
            Cause: Too many requests to GitHub API
            Fix: Wait before retrying, use authentication token if available
            Workaround: Reduce request frequency, cache results locally

    See Also:
        - firefox_profiles: Create profiles for importing curated sources
        - firefox_bookmarks: Import curated bookmarks into profiles
        - firefox_profiles: create_loaded_profile_from_preset (uses curated sources)
    """

    if operation == "get_curated_source":
        return await _get_curated_source(source_name, include_metadata)
    elif operation == "list_curated_sources":
        return await _list_curated_sources(category, include_metadata, limit)
    elif operation == "list_curated_bookmark_sources":
        return await _list_curated_bookmark_sources(category, include_metadata, limit)
    else:
        return {
            "success": False,
            "error": f"Unknown operation: {operation}",
            "available_operations": [
                "get_curated_source",
                "list_curated_sources",
                "list_curated_bookmark_sources",
            ],
        }


async def _get_curated_source(source_name: str | None, include_metadata: bool) -> dict[str, Any]:
    """Get a specific curated source by name."""
    try:
        if not source_name:
            raise ValueError("Source name is required")

        source = get_curated_source(source_name)

        return {
            "success": True,
            "message": f"Curated source '{source_name}' retrieved successfully",
            "source_name": source_name,
            "include_metadata": include_metadata,
            "source": source,
        }

    except Exception as e:
        logger.error(f"Error getting curated source: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to get curated source: {str(e)}",
            "source_name": source_name,
            "source": {},
        }


async def _list_curated_sources(
    category: str | None, include_metadata: bool, limit: int
) -> dict[str, Any]:
    """List all available curated sources."""
    try:
        sources = list_curated_sources()

        return {
            "success": True,
            "message": "Curated sources listed successfully",
            "category": category,
            "include_metadata": include_metadata,
            "limit": limit,
            "sources": sources,
            "count": len(sources),
        }

    except Exception as e:
        logger.error(f"Error listing curated sources: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to list curated sources: {str(e)}",
            "category": category,
            "sources": [],
            "count": 0,
        }


async def _list_curated_bookmark_sources(
    category: str | None, include_metadata: bool, limit: int
) -> dict[str, Any]:
    """List curated bookmark sources with details."""
    try:
        sources = list_curated_sources()

        return {
            "success": True,
            "message": "Curated bookmark sources listed successfully",
            "category": category,
            "include_metadata": include_metadata,
            "limit": limit,
            "bookmark_sources": sources,
            "count": len(sources),
        }

    except Exception as e:
        logger.error(f"Error listing curated bookmark sources: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to list curated bookmark sources: {str(e)}",
            "category": category,
            "bookmark_sources": [],
            "count": 0,
        }
