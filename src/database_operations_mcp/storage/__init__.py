"""
FastMCP 2.13+ Persistent Storage Module

Provides persistent storage for database connections, preferences, and state
that survives Claude Desktop restarts and OS reboots.
"""

from .persistence import DatabaseOperationsStorage, get_storage, set_storage

__all__ = ["DatabaseOperationsStorage", "get_storage", "set_storage"]
