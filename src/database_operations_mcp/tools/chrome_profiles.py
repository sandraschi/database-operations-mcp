"""
Chrome profile management portmanteau tool.

This module provides comprehensive Chrome profile management, consolidating all
profile operations into a single interface. Chrome uses User Data folders
instead of SQLite-based profiles like Firefox.
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Any

from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.operation_types import ChromeProfilesOperation
from database_operations_mcp.tool_responses import mcp_error, unknown_operation_response
from database_operations_mcp.services.browser.chrome_core import ChromeManager

_chrome_manager = ChromeManager()


@mcp.tool()
async def chrome_profiles(
    operation: ChromeProfilesOperation,
    profile_name: str | None = None,
    check_access: bool = True,
    include_info: bool = True,
    backup_destination: str | None = None,
    backup_file: str | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Chrome profile management portmanteau tool.

    connection_name is not used; Chrome profiles are identified by `profile_name`
    (e.g. Default, Profile 1).

    Operations:
        get_chrome_profiles, get_profile_info, validate_profile, is_chrome_running,
        get_profile_directory, get_bookmarks_db_path, get_chrome_platform,
        get_database_info, check_chrome_status, backup_profile, restore_profile,
        create_profile, delete_profile, switch_profile.

    Parameters:
        profile_name: Chrome profile folder name (default for many ops: 'Default').
        check_access: Reserved for future access checks (default True).
        include_info: Reserved for extended diagnostics (default True).
        backup_destination: Directory for backup_profile ZIP output (default: system temp).
        backup_file: Path to a backup ZIP for restore_profile.
        overwrite: When True, restore_profile may replace an existing profile directory.

    Returns:
        success=True responses include operation-specific keys (profiles, info, paths, etc.).
        success=False includes error, error_type, recovery_options where applicable.

    Errors:
        Missing Chrome installation: user_fixable — install Chrome or fix User Data path.
        Chrome running during restore: close Chrome and retry (retryable).
    """

    pn = profile_name or "Default"

    try:
        if operation == "get_chrome_profiles":
            profiles = await _chrome_manager.get_profiles()
            return {
                "success": True,
                "operation": operation,
                "profiles": profiles,
                "count": len(profiles),
                "message": f"Found {len(profiles)} Chrome profile(s)",
            }

        if operation == "get_profile_info":
            info = await _chrome_manager.get_profile_info(pn)
            return {
                "success": True,
                "operation": operation,
                "profile_name": pn,
                "info": info,
                "message": f"Profile info retrieved for {pn}",
            }

        if operation == "validate_profile":
            is_valid = await _chrome_manager.validate_profile(pn)
            return {
                "success": True,
                "operation": operation,
                "profile_name": pn,
                "is_valid": is_valid,
                "message": f"Profile {pn} is {'valid' if is_valid else 'invalid'}",
            }

        if operation == "is_chrome_running":
            is_running = await _chrome_manager.is_database_locked(pn)
            return {
                "success": True,
                "operation": operation,
                "is_running": is_running,
                "message": "Chrome appears to be running" if is_running else "Chrome appears closed",
                "note": "Detection uses process scan; close Chrome before bookmark file writes.",
            }

        if operation == "get_profile_directory":
            profile_path = await _chrome_manager.get_profile_path(pn)
            return {
                "success": True,
                "operation": operation,
                "profile_name": pn,
                "profile_directory": profile_path,
                "message": f"Profile directory path for {pn}",
            }

        if operation == "get_bookmarks_db_path":
            db_path = _chrome_manager.get_database_path(pn)
            return {
                "success": True,
                "operation": operation,
                "profile_name": pn,
                "bookmarks_path": db_path,
                "message": f"Bookmarks file path for {pn}",
            }

        if operation == "get_chrome_platform":
            return {
                "success": True,
                "operation": operation,
                "platform": sys.platform,
                "message": f"Python platform tag: {sys.platform}",
            }

        if operation == "get_database_info":
            info = await _chrome_manager.get_profile_info(pn)
            bp = Path(_chrome_manager.get_database_path(pn))
            size_b = bp.stat().st_size if bp.exists() else 0
            return {
                "success": True,
                "operation": operation,
                "profile_name": pn,
                "bookmarks_path": str(bp),
                "file_size_bytes": size_b,
                "profile_info": info,
                "message": f"Bookmarks file size {size_b} bytes for profile {pn}",
            }

        if operation == "check_chrome_status":
            data_dir = _chrome_manager.chrome_data_dir
            profiles = await _chrome_manager.get_profiles() if data_dir else []
            running = await _chrome_manager.is_database_locked(pn)
            return {
                "success": True,
                "operation": operation,
                "chrome_user_data_found": data_dir is not None and Path(data_dir).exists(),
                "chrome_user_data_dir": str(data_dir) if data_dir else None,
                "profile_count": len(profiles),
                "chrome_running": running,
                "message": "Chrome User Data located" if data_dir else "Chrome User Data not found",
            }

        if operation == "backup_profile":
            dest = backup_destination or tempfile.gettempdir()
            Path(dest).mkdir(parents=True, exist_ok=True)
            out = await _chrome_manager.backup_profile(pn, dest)
            return {
                "success": True,
                "operation": operation,
                "profile_name": pn,
                "backup_path": out,
                "message": f"Backup written to {out}",
            }

        if operation == "restore_profile":
            if not backup_file:
                return mcp_error(
                    message="backup_file is required for restore_profile",
                    error="backup_file is required for restore_profile",
                    error_type="invalid_input",
                    recovery_options=["Pass backup_file pointing to a ZIP from backup_profile."],
                )
            res = await _chrome_manager.restore_profile(pn, backup_file, overwrite=overwrite)
            res["success"] = True
            res["operation"] = operation
            return res

        if operation in ("create_profile", "delete_profile", "switch_profile"):
            return mcp_error(
                message=f"Operation {operation} is not automated in this MCP build",
                error=f"Chrome profile {operation} not supported programmatically here",
                error_type="user_fixable",
                recovery_options=[
                    "Use Chrome's built-in profile manager (chrome://profile-picker or Settings).",
                    "For backups, use backup_profile / restore_profile.",
                ],
                operation=operation,
            )

    except Exception as e:
        return mcp_error(
            message=str(e),
            error=str(e),
            error_type="user_fixable",
            recovery_options=[
                "Ensure Google Chrome is installed and profile_name matches a folder under User Data.",
                "Close Chrome before restore or backup if you see file lock errors.",
            ],
            operation=operation,
            profile_name=profile_name,
        )

    return unknown_operation_response(
        operation,
        [
            "get_chrome_profiles",
            "get_profile_info",
            "validate_profile",
            "is_chrome_running",
            "get_profile_directory",
            "get_bookmarks_db_path",
            "get_chrome_platform",
            "get_database_info",
            "check_chrome_status",
            "backup_profile",
            "restore_profile",
            "create_profile",
            "delete_profile",
            "switch_profile",
        ],
    )
