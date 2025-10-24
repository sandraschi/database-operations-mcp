# Firefox curated sources portmanteau tool.
# Consolidates Firefox curated sources operations into a single interface.

import logging
from typing import Any, Dict, List, Optional

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.tools.help_tools import HelpSystem
from database_operations_mcp.tools.firefox.curated_sources import (
    get_curated_source,
    list_curated_sources,
)

logger = logging.getLogger(__name__)


@mcp.tool()
@HelpSystem.register_tool(category="firefox")
async def firefox_curated(
    operation: str,
    source_name: Optional[str] = None,
    category: Optional[str] = None,
    include_metadata: bool = True,
    limit: int = 100,
) -> Dict[str, Any]:
    """Firefox curated sources portmanteau tool.

    This tool consolidates all Firefox curated sources operations into a single interface,
    providing unified access to curated bookmark collections functionality.

    Operations:
    - get_curated_source: Get a specific curated source by name
    - list_curated_sources: List all available curated sources
    - list_curated_bookmark_sources: List curated bookmark sources with details

    Args:
        operation: The operation to perform (required)
        source_name: Name of the curated source to retrieve
        category: Category to filter sources by
        include_metadata: Whether to include metadata in results
        limit: Maximum number of sources to return

    Returns:
        Dictionary with operation results and curated source information

    Examples:
        Get specific source:
        firefox_curated(operation='get_curated_source', source_name='awesome-python')

        List all sources:
        firefox_curated(operation='list_curated_sources', include_metadata=True)

        List bookmark sources:
        firefox_curated(operation='list_curated_bookmark_sources', category='development')

        List with limit:
        firefox_curated(operation='list_curated_sources', limit=50)
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


async def _get_curated_source(source_name: Optional[str], include_metadata: bool) -> Dict[str, Any]:
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
    category: Optional[str], include_metadata: bool, limit: int
) -> Dict[str, Any]:
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
    category: Optional[str], include_metadata: bool, limit: int
) -> Dict[str, Any]:
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
