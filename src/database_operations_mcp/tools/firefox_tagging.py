# Firefox tagging system portmanteau tool.
# Consolidates Firefox tagging operations into a single interface.

import logging
from typing import Any

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.tools.firefox.folder_based_tagging import (
    batch_tag_from_folder,
    tag_from_folder,
)
from database_operations_mcp.tools.firefox.year_based_tagging import (
    batch_tag_from_year,
    tag_from_year,
)
from database_operations_mcp.tools.help_tools import HelpSystem

logger = logging.getLogger(__name__)


@mcp.tool()
@HelpSystem.register_tool(category="firefox")
async def firefox_tagging(
    operation: str,
    profile_name: str | None = None,
    folder_path: str | None = None,
    year: int | None = None,
    tag_prefix: str | None = None,
    batch_size: int = 100,
    dry_run: bool = False,
    include_subfolders: bool = True,
) -> dict[str, Any]:
    """Firefox tagging system portmanteau tool.

    Operations: tag_from_folder, batch_tag_from_folder, tag_from_year, batch_tag_from_year.
    Requires Firefox to be closed before operations.

    Args:
        operation: Operation to perform (required)
        profile_name: Firefox profile name. Default: 'default'
        dry_run: Preview changes without applying. Default: False
        batch_size: Items per batch. Default: 100
        tag_prefix: Prefix for generated tags. Default: None
        folder_path: Folder path for folder-based tagging
        year: Year for year-based tagging
    """

    if operation == "tag_from_folder":
        return await _tag_from_folder(
            profile_name, folder_path, tag_prefix, include_subfolders, dry_run
        )
    elif operation == "batch_tag_from_folder":
        return await _batch_tag_from_folder(
            profile_name, folder_path, tag_prefix, batch_size, include_subfolders, dry_run
        )
    elif operation == "tag_from_year":
        return await _tag_from_year(profile_name, year, tag_prefix, dry_run)
    elif operation == "batch_tag_from_year":
        return await _batch_tag_from_year(profile_name, year, tag_prefix, batch_size, dry_run)
    else:
        return {
            "success": False,
            "error": f"Unknown operation: {operation}",
            "available_operations": [
                "tag_from_folder",
                "batch_tag_from_folder",
                "tag_from_year",
                "batch_tag_from_year",
            ],
        }


async def _tag_from_folder(
    profile_name: str | None,
    folder_path: str | None,
    tag_prefix: str | None,
    include_subfolders: bool,
    dry_run: bool,
) -> dict[str, Any]:
    """Tag bookmarks based on their folder structure."""
    try:
        if not folder_path:
            raise ValueError("Folder path is required")

        result = await tag_from_folder(
            profile_name, folder_path, tag_prefix, include_subfolders, dry_run
        )

        return {
            "success": True,
            "message": f"Folder-based tagging completed for '{folder_path}'",
            "profile_name": profile_name,
            "folder_path": folder_path,
            "tag_prefix": tag_prefix,
            "include_subfolders": include_subfolders,
            "dry_run": dry_run,
            "tagging_result": result,
        }

    except Exception as e:
        logger.error(f"Error tagging from folder: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to tag from folder: {str(e)}",
            "profile_name": profile_name,
            "folder_path": folder_path,
            "tagging_result": {},
        }


async def _batch_tag_from_folder(
    profile_name: str | None,
    folder_path: str | None,
    tag_prefix: str | None,
    batch_size: int,
    include_subfolders: bool,
    dry_run: bool,
) -> dict[str, Any]:
    """Tag multiple bookmarks from folder structure in batches."""
    try:
        if not folder_path:
            raise ValueError("Folder path is required")

        result = await batch_tag_from_folder(
            profile_name, folder_path, tag_prefix, batch_size, include_subfolders, dry_run
        )

        return {
            "success": True,
            "message": f"Batch folder-based tagging completed for '{folder_path}'",
            "profile_name": profile_name,
            "folder_path": folder_path,
            "tag_prefix": tag_prefix,
            "batch_size": batch_size,
            "include_subfolders": include_subfolders,
            "dry_run": dry_run,
            "batch_result": result,
        }

    except Exception as e:
        logger.error(f"Error batch tagging from folder: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to batch tag from folder: {str(e)}",
            "profile_name": profile_name,
            "folder_path": folder_path,
            "batch_result": {},
        }


async def _tag_from_year(
    profile_name: str | None, year: int | None, tag_prefix: str | None, dry_run: bool
) -> dict[str, Any]:
    """Tag bookmarks based on their creation year."""
    try:
        if not year:
            raise ValueError("Year is required")

        result = await tag_from_year(profile_name, year, tag_prefix, dry_run)

        return {
            "success": True,
            "message": f"Year-based tagging completed for year {year}",
            "profile_name": profile_name,
            "year": year,
            "tag_prefix": tag_prefix,
            "dry_run": dry_run,
            "tagging_result": result,
        }

    except Exception as e:
        logger.error(f"Error tagging from year: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to tag from year: {str(e)}",
            "profile_name": profile_name,
            "year": year,
            "tagging_result": {},
        }


async def _batch_tag_from_year(
    profile_name: str | None,
    year: int | None,
    tag_prefix: str | None,
    batch_size: int,
    dry_run: bool,
) -> dict[str, Any]:
    """Tag multiple bookmarks from year in batches."""
    try:
        if not year:
            raise ValueError("Year is required")

        result = await batch_tag_from_year(profile_name, year, tag_prefix, batch_size, dry_run)

        return {
            "success": True,
            "message": f"Batch year-based tagging completed for year {year}",
            "profile_name": profile_name,
            "year": year,
            "tag_prefix": tag_prefix,
            "batch_size": batch_size,
            "dry_run": dry_run,
            "batch_result": result,
        }

    except Exception as e:
        logger.error(f"Error batch tagging from year: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to batch tag from year: {str(e)}",
            "profile_name": profile_name,
            "year": year,
            "batch_result": {},
        }
