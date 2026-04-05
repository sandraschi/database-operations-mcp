# Firefox curated sources portmanteau tool.
# Consolidates Firefox curated sources operations into a single interface.

import logging
from typing import Any

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.operation_types import FirefoxCuratedOperation
from database_operations_mcp.tool_responses import unknown_operation_response
from database_operations_mcp.tools.firefox.curated_sources import (
    get_curated_source,
    list_curated_sources,
)
from database_operations_mcp.tools.help_tools import HelpSystem

logger = logging.getLogger(__name__)


@mcp.tool()
@HelpSystem.register_tool(category="firefox")
async def firefox_curated(
    operation: FirefoxCuratedOperation,
    source_name: str | None = None,
    category: str | None = None,
    include_metadata: bool = True,
    limit: int = 100,
) -> dict[str, Any]:
    """Firefox curated sources portmanteau tool.

    Operations: get_curated_source, list_curated_sources, list_curated_bookmark_sources.
    source_name: Curated source identifier (required for get_curated_source)
    category: Filter sources by category (e.g. 'development', 'data-science')
    limit: Max results (default: 100)
    """

    limit = max(1, min(limit, 10_000))

    if operation == "get_curated_source":
        return await _get_curated_source(source_name, include_metadata)
    elif operation == "list_curated_sources":
        return await _list_curated_sources(category, include_metadata, limit)
    elif operation == "list_curated_bookmark_sources":
        return await _list_curated_bookmark_sources(category, include_metadata, limit)
    else:
        return unknown_operation_response(
            operation,
            [
                "get_curated_source",
                "list_curated_sources",
                "list_curated_bookmark_sources",
            ],
        )


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
