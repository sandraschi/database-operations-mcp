"""
Central FastMCP Configuration

This module provides a centralized FastMCP instance for the application.
All tools should import the MCP instance from this module to ensure
consistent registration and configuration.
"""

import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastmcp import FastMCP
from fastmcp.server import create_proxy

logger = logging.getLogger(__name__)

# Global storage instance (will be initialized in lifespan)
_storage_instance = None


@asynccontextmanager
async def server_lifespan(mcp_instance: FastMCP) -> AsyncIterator[None]:
    """
    FastMCP 2.13+ server lifespan for initialization and cleanup.

    This follows FastMCP 2.13+ persistence pattern:
    - Initialize persistent storage during startup
    - Restore saved state (connections, preferences)
    - Cleanup on shutdown

    Storage persists across:
    - Claude Desktop restarts
    - OS reboots (Windows/macOS/Linux)
    """
    global _storage_instance

    # Startup: Initialize persistent storage
    try:
        from database_operations_mcp.storage.persistence import (
            DatabaseOperationsStorage,
            set_storage,
        )

        # Initialize FastMCP 2.13+ persistent storage using DiskStore backend
        storage_instance = DatabaseOperationsStorage(mcp_instance, use_disk_storage=True)
        await storage_instance.initialize()
        set_storage(storage_instance)
        _storage_instance = storage_instance
        logger.info("FastMCP 2.13+ persistent storage initialized")

        # Restore saved connections from persistent storage
        saved_connections = await storage_instance.get_all_connections()
        if saved_connections:
            logger.info(
                f"Restored {len(saved_connections)} saved connections from persistent storage"
            )

        # Restore active connection preference
        active_conn = await storage_instance.get_active_connection()
        if active_conn:
            logger.info(f"Restored active connection preference: {active_conn}")

        # Restore user preferences
        prefs = await storage_instance.get_user_preferences()
        if prefs:
            logger.info(f"Restored {len(prefs)} user preferences")

        yield  # Server runs here - storage is available during this time

    finally:
        # Shutdown: Final cleanup
        if _storage_instance:
            try:
                logger.info("FastMCP 2.13+ persistent storage: Saving final state...")
                # Storage operations auto-save on each write
                # DiskStore persists automatically - no explicit flush needed
                logger.info("Persistent storage cleanup complete")
            except Exception as e:
                logger.warning(f"Error during storage cleanup (non-fatal): {e}")


# Create a single FastMCP instance with lifespan for persistent storage
# Persistent storage is enabled following FastMCP 3.0 standards
mcp = FastMCP(name="database-operations-mcp", lifespan=server_lifespan)

# MCP Bridge: proxy upstream servers via MCP_BRIDGE_URLS (comma-separated)
_bridge_proxies = []
bridge_urls = os.getenv("MCP_BRIDGE_URLS", "")
if bridge_urls:
    for url in bridge_urls.split(","):
        url = url.strip()
        if url:
            try:
                mcp.add_provider(create_proxy(url))
                _bridge_proxies.append(url)
            except Exception:
                logger.warning("Failed to create proxy for %s", url)

# Expose bundled skills as MCP resources (skill://database-expert/SKILL.md)
try:
    from pathlib import Path

    from fastmcp.server.providers.skills import SkillsDirectoryProvider

    _skills_dir = Path(__file__).resolve().parent.parent / "skills"
    if _skills_dir.is_dir():
        mcp.add_provider(SkillsDirectoryProvider(roots=[_skills_dir]))
        logger.info("Skills provider registered: bundled database-expert skill available")
except ImportError:
    pass  # FastMCP 3.1+ skills provider optional

# Flag to control individual tool registration
# Set to False to ensure only portmanteau tools are surfaced
# This maintains the "unified gateway" design requested by the user
ENABLE_INDIVIDUAL_TOOLS = os.getenv("ENABLE_INDIVIDUAL_TOOLS", "false").lower() == "true"


# Check if we're being imported by a portmanteau module
def is_portmanteau_import():
    """Check if the current import is from a portmanteau module."""
    import inspect

    frame = inspect.currentframe()
    try:
        # Go up the call stack to find the importing module
        for _i in range(10):  # Check up to 10 frames up
            frame = frame.f_back
            if frame is None:
                break
            filename = frame.f_code.co_filename
            if (
                "portmanteau" in filename.lower()
                or "db_connection" in filename
            ):
                return True
    finally:
        del frame
    return False


def get_mcp() -> FastMCP:
    """Get the global MCP instance."""
    return mcp


def get_storage():
    """Get the global storage instance (if initialized)."""
    return _storage_instance
