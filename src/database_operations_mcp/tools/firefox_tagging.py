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

    Comprehensive automated tagging operations consolidating ALL Firefox tagging
    functionality into a single interface. Supports folder-based tagging, year-based
    tagging, batch processing, and preview modes for efficient bookmark organization.

    Prerequisites:
        - Firefox must be completely closed before tagging operations
        - Valid Firefox profile name (use firefox_profiles to list available profiles)
        - For folder operations: Valid folder path in bookmark structure
        - For year operations: Bookmarks must have creation dates

    Operations:
        - tag_from_folder: Tag bookmarks based on their folder structure
        - batch_tag_from_folder: Tag multiple bookmarks from folder structure in batches
        - tag_from_year: Tag bookmarks based on their creation year
        - batch_tag_from_year: Tag multiple bookmarks from year in batches

    Parameters:
        operation (str, REQUIRED): The operation to perform
            Valid values: 'tag_from_folder', 'batch_tag_from_folder',
                         'tag_from_year', 'batch_tag_from_year'
            Example: 'tag_from_folder', 'batch_tag_from_folder'

        profile_name (str, OPTIONAL): Firefox profile name to operate on
            Format: Valid Firefox profile name
            Required for: All operations
            Default: 'default' (if not specified)
            Validation: Profile must exist (use firefox_profiles to verify)
            Example: 'default', 'work', 'personal'

        folder_path (str, OPTIONAL): Path of the folder to tag from
            Format: Folder path in bookmark structure (e.g., 'Work/Projects')
            Required for: tag_from_folder, batch_tag_from_folder operations
            Validation: Folder must exist in bookmark structure
            Example: 'Work/Projects', 'Research/Papers', 'Personal/Reading'

        year (int, OPTIONAL): Year to tag bookmarks from
            Format: Four-digit year
            Required for: tag_from_year, batch_tag_from_year operations
            Range: 1990-2100
            Validation: Year must be valid
            Example: 2023, 2024, 2020

        tag_prefix (str, OPTIONAL): Prefix to add to generated tags
            Format: String prefix for tags
            Default: None (no prefix)
            Behavior: Prepended to all generated tags
            Example: 'work', 'archive', 'project'
            Result: 'work-projects', 'archive-2023', 'project-research'

        batch_size (int, OPTIONAL): Number of bookmarks to process per batch
            Format: Positive integer
            Range: 1-10,000
            Default: 100
            Used for: batch_tag_from_folder, batch_tag_from_year operations
            Impact: Larger batches faster but use more memory
            Example: 50, 100, 500

        dry_run (bool, OPTIONAL): Preview changes without applying them
            Default: False
            Behavior: Shows what tags would be added without modifying bookmarks
            Used for: All operations
            Best practice: Use True first to preview changes
            Example: True for testing, False to apply changes

        include_subfolders (bool, OPTIONAL): Include subfolders in folder-based tagging
            Default: True
            Behavior: Tags bookmarks in folder and all subfolders
            Used for: tag_from_folder, batch_tag_from_folder operations
            Impact: Processes nested folder structure recursively
            Example: True for recursive tagging, False for single folder only

    Returns:
        Dictionary containing operation-specific results:
            - success: Boolean indicating operation success
            - operation: Echo of operation performed
            - profile_name: Echo of profile name used
            - For tag_from_folder: tags_applied (list), bookmarks_tagged (int), folder_path
            - For batch_tag_from_folder: batches_processed (int), total_tagged,
              tags_generated (list)
            - For tag_from_year: tags_applied (list), bookmarks_tagged (int), year
            - For batch_tag_from_year: batches_processed (int), total_tagged, year
            - dry_run: Echo of dry_run setting
            - preview: Preview of changes (if dry_run=True)
            - error: Error message if success is False
            - available_operations: List of valid operations (on invalid operation)

    Usage:
        This tool provides automated tagging for Firefox bookmarks. Use it to organize
        bookmarks by folder structure or creation date, making them easier to find and search.

        Common scenarios:
        - Folder organization: Tag bookmarks based on folder structure
        - Year-based organization: Tag bookmarks by creation year
        - Batch processing: Process large bookmark collections efficiently
        - Preview changes: Use dry_run to see what tags would be applied

        Best practices:
        - Always use dry_run=True first to preview changes
        - Use tag_prefix to avoid conflicts with existing tags
        - Process in batches for large bookmark collections
        - Use include_subfolders=True for recursive folder tagging
        - Review generated tags before applying

    Examples:
        Tag from folder:
            result = await firefox_tagging(
                operation='tag_from_folder',
                profile_name='work',
                folder_path='Work/Projects',
                tag_prefix='work',
                include_subfolders=True,
                dry_run=False
            )
            # Returns: {
            #     'success': True,
            #     'tags_applied': ['work-projects', 'work-projects-web'],
            #     'bookmarks_tagged': 45,
            #     'folder_path': 'Work/Projects'
            # }

        Preview folder tagging (dry run):
            result = await firefox_tagging(
                operation='tag_from_folder',
                profile_name='default',
                folder_path='Research',
                tag_prefix='research',
                dry_run=True
            )
            # Returns: {
            #     'success': True,
            #     'dry_run': True,
            #     'preview': {
            #         'tags_to_apply': ['research', 'research-papers'],
            #         'bookmarks_affected': 23
            #     }
            # }

        Batch tag from folder:
            result = await firefox_tagging(
                operation='batch_tag_from_folder',
                profile_name='default',
                folder_path='Personal',
                tag_prefix='personal',
                batch_size=50,
                include_subfolders=True
            )
            # Returns: {
            #     'success': True,
            #     'batches_processed': 3,
            #     'total_tagged': 125,
            #     'tags_generated': ['personal', 'personal-reading', 'personal-videos']
            # }

        Tag from year:
            result = await firefox_tagging(
                operation='tag_from_year',
                profile_name='default',
                year=2023,
                tag_prefix='archive'
            )
            # Returns: {
            #     'success': True,
            #     'tags_applied': ['archive-2023'],
            #     'bookmarks_tagged': 67,
            #     'year': 2023
            # }

        Batch tag from year:
            result = await firefox_tagging(
                operation='batch_tag_from_year',
                profile_name='default',
                year=2022,
                tag_prefix='archive',
                batch_size=100
            )
            # Returns: {
            #     'success': True,
            #     'batches_processed': 2,
            #     'total_tagged': 180,
            #     'year': 2022
            # }

        Error handling - Firefox running:
            result = await firefox_tagging(
                operation='tag_from_folder',
                profile_name='default',
                folder_path='Work'
            )
            # Returns: {
            #     'success': False,
            #     'error': 'Firefox is running. Close Firefox before operations.'
            # }

    Errors:
        Common errors and solutions:
        - 'Firefox is running. Close Firefox before operations':
            Cause: Firefox browser is currently running
            Fix: Completely close all Firefox windows and processes
            Workaround: Wait for Firefox to close, check Task Manager

        - 'Profile not found: {profile_name}':
            Cause: Specified profile doesn't exist
            Fix: Use firefox_profiles(operation='get_firefox_profiles') to list profiles
            Workaround: Use 'default' profile name, check profile spelling

        - 'Folder not found: {folder_path}':
            Cause: Specified folder doesn't exist in bookmark structure
            Fix: Use firefox_bookmarks(operation='list_bookmarks') to see folder structure
            Workaround: Check folder path spelling, verify folder exists

        - 'No bookmarks found in folder: {folder_path}':
            Cause: Folder exists but contains no bookmarks
            Fix: Verify folder has bookmarks, check include_subfolders setting
            Workaround: Use different folder or check bookmark structure

        - 'Invalid year: {year}':
            Cause: Year is outside valid range or invalid format
            Fix: Use valid year between 1990-2100
            Example: year=2023 not year=23

        - 'No bookmarks found for year: {year}':
            Cause: No bookmarks have creation dates matching specified year
            Fix: Verify bookmarks have creation dates, check year value
            Workaround: Use different year or check bookmark metadata

    See Also:
        - firefox_bookmarks: List bookmarks and view folder structure
        - firefox_profiles: Manage Firefox profiles
        - firefox_bookmarks: tag operations (list_tags, merge_tags, etc.)
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
