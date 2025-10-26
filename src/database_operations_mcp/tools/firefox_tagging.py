# Firefox tagging system portmanteau tool.
# Consolidates Firefox tagging operations into a single interface.

import logging
from typing import Any, Dict, Optional

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
    profile_name: Optional[str] = None,
    folder_path: Optional[str] = None,
    year: Optional[int] = None,
    tag_prefix: Optional[str] = None,
    batch_size: int = 100,
    dry_run: bool = False,
    include_subfolders: bool = True,
) -> Dict[str, Any]:
    """Firefox tagging system portmanteau tool.

    This tool consolidates all Firefox tagging operations into a single interface,
    providing unified access to automated tagging functionality.

    Operations:
    - tag_from_folder: Tag bookmarks based on their folder structure
    - batch_tag_from_folder: Tag multiple bookmarks from folder structure in batches
    - tag_from_year: Tag bookmarks based on their creation year
    - batch_tag_from_year: Tag multiple bookmarks from year in batches

    Args:
        operation: The operation to perform (required)
        profile_name: Firefox profile name to operate on
        folder_path: Path of the folder to tag from
        year: Year to tag bookmarks from
        tag_prefix: Prefix to add to generated tags
        batch_size: Number of bookmarks to process per batch
        dry_run: If True, preview changes without applying them
        include_subfolders: Whether to include subfolders in folder-based tagging

    Returns:
        Dictionary with operation results and tagging information

    Examples:
        Tag from folder:
        firefox_tagging(operation='tag_from_folder', profile_name='default',
                       folder_path='Work/Projects', tag_prefix='work')

        Batch tag from folder:
        firefox_tagging(operation='batch_tag_from_folder', profile_name='default',
                       folder_path='Research', batch_size=50, dry_run=True)

        Tag from year:
        firefox_tagging(operation='tag_from_year', profile_name='default',
                       year=2023, tag_prefix='archive')

        Batch tag from year:
        firefox_tagging(operation='batch_tag_from_year', profile_name='default',
                       year=2022, batch_size=100, dry_run=False)
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
    profile_name: Optional[str],
    folder_path: Optional[str],
    tag_prefix: Optional[str],
    include_subfolders: bool,
    dry_run: bool,
) -> Dict[str, Any]:
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
    profile_name: Optional[str],
    folder_path: Optional[str],
    tag_prefix: Optional[str],
    batch_size: int,
    include_subfolders: bool,
    dry_run: bool,
) -> Dict[str, Any]:
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
    profile_name: Optional[str], year: Optional[int], tag_prefix: Optional[str], dry_run: bool
) -> Dict[str, Any]:
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
    profile_name: Optional[str],
    year: Optional[int],
    tag_prefix: Optional[str],
    batch_size: int,
    dry_run: bool,
) -> Dict[str, Any]:
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
