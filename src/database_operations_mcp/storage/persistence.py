"""
FastMCP 2.13+ Persistent Storage Integration

Uses FastMCP's built-in storage backends for persistent state management.

IMPORTANT: This implementation uses DiskStore to ensure data persists across
Claude Desktop restarts. Storage is saved to platform-appropriate directories:
- Windows: %APPDATA%\database-operations-mcp
- macOS: ~/Library/Application Support/database-operations-mcp
- Linux: ~/.local/share/database-operations-mcp

DEV MODE: Set ENABLE_PASSWORD_STORAGE=1 to save passwords (INSECURE).
          Only use during development phase. NEVER enable in production.
"""

import json
import logging
import os
import platform
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

logger = logging.getLogger(__name__)

# Dev-only: Allow saving passwords (INSECURE - dev only!)
# Set environment variable: ENABLE_PASSWORD_STORAGE=1
ENABLE_PASSWORD_STORAGE = os.getenv("ENABLE_PASSWORD_STORAGE", "0").lower() in ("1", "true", "yes")

# Storage keys (use prefix for this app)
STORAGE_PREFIX = "dbops:"
CONNECTIONS_KEY = f"{STORAGE_PREFIX}connections"
ACTIVE_CONNECTION_KEY = f"{STORAGE_PREFIX}active_connection"
USER_PREFS_KEY = f"{STORAGE_PREFIX}user_preferences"
SEARCH_HISTORY_KEY = f"{STORAGE_PREFIX}search_history"
BOOKMARK_SYNC_STATE_KEY = f"{STORAGE_PREFIX}bookmark_sync_state"
WINDOWS_DB_PATHS_KEY = f"{STORAGE_PREFIX}windows_db_paths"
QUERY_TEMPLATES_KEY = f"{STORAGE_PREFIX}query_templates"
BACKUP_LOCATIONS_KEY = f"{STORAGE_PREFIX}backup_locations"
SCHEMA_CACHE_PREFIX = f"{STORAGE_PREFIX}schema_cache:"


class DatabaseOperationsStorage:
    """
    Wrapper around FastMCP storage for persistent state.

    Uses DiskStore to ensure data persists across Claude Desktop and OS restarts.
    Storage location is in AppData\Roaming on Windows, which persists across reboots.
    """

    def __init__(self, mcp: FastMCP, use_disk_storage: bool = True):
        """
        Initialize storage with FastMCP instance.

        Args:
            mcp: FastMCP server instance
            use_disk_storage: If True (default), use DiskStore for persistence.
                            If False, use default in-memory storage (won't persist).
        """
        self.mcp = mcp
        self._storage = None
        self._initialized = False
        self._use_disk_storage = use_disk_storage

        # Platform-appropriate storage directory that survives OS restarts
        if use_disk_storage:
            if os.name == "nt":  # Windows
                appdata = os.getenv("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))
                self._storage_dir = Path(appdata) / "database-operations-mcp"
            else:  # macOS/Linux
                home = Path.home()
                if platform.system() == "Darwin":  # macOS
                    self._storage_dir = (
                        home / "Library" / "Application Support" / "database-operations-mcp"
                    )
                else:  # Linux
                    self._storage_dir = home / ".local" / "share" / "database-operations-mcp"

            # Create directory if it doesn't exist
            self._storage_dir.mkdir(parents=True, exist_ok=True)
        else:
            self._storage_dir = None

    async def initialize(self) -> None:
        """
        Initialize the storage backend using FastMCP 2.13+ persistent storage pattern.

        For persistence across Claude Desktop restarts, we use DiskStore which is
        compatible with FastMCP 2.13+ storage backends. This ensures data persists
        across both Claude Desktop restarts and OS reboots.

        FastMCP 2.13+ Pattern:
        1. Use DiskStore for guaranteed persistence
        2. Storage is initialized in server_lifespan startup
        3. Data survives application and OS restarts
        """
        if self._initialized:
            return

        try:
            # FastMCP 2.13+ Pattern: Use DiskStore for persistent storage
            # This is the recommended approach for cross-session persistence
            if self._use_disk_storage and self._storage_dir:
                try:
                    from key_value.aio.stores.disk import DiskStore

                    # Create persistent disk storage (FastMCP 2.13+ compatible)
                    # DiskStore provides the storage backend interface that FastMCP expects
                    self._storage = DiskStore(directory=str(self._storage_dir))
                    self._initialized = True
                    logger.info(
                        f"FastMCP 2.13 persistent storage initialized at {self._storage_dir}"
                    )
                    return
                except ImportError as e:
                    # py-key-value-aio[disk] should be available via fastmcp dependency
                    logger.warning(
                        f"DiskStore not available: {e}. Falling back to FastMCP's default storage."
                    )

            # Fallback: Try to use FastMCP's storage backend (may be in-memory)
            # FastMCP 2.13+ should provide storage via mcp.storage attribute
            if hasattr(self.mcp, "storage") and self.mcp.storage:
                self._storage = self.mcp.storage
                self._initialized = True
                logger.info("Using FastMCP's provided storage backend")
                return

            # If we get here, storage is not available - graceful degradation
            logger.warning(
                "Persistent storage not available - using in-memory fallback. "
                "Data will not persist across restarts."
            )
            self._initialized = False

        except Exception as e:
            # Storage might not be available yet - that's ok
            logger.debug(f"Storage initialization error (non-fatal): {e}")
            self._initialized = False

    # ==================== DATABASE CONNECTIONS ====================

    async def save_connection(
        self, connection_name: str, db_type: str, connection_params: Dict[str, Any]
    ) -> None:
        """
        Save database connection configuration.

        DEV MODE: If ENABLE_PASSWORD_STORAGE=1, passwords are saved (INSECURE!).
                  Only use during development. Passwords saved in plaintext!
        """
        await self.initialize()
        if not self._storage:
            return

        try:
            # Get existing connections
            connections = await self.get_all_connections()

            # DEV MODE: Optionally save password (INSECURE - dev only!)
            if ENABLE_PASSWORD_STORAGE:
                # Save ALL params including password (dev only!)
                safe_params = connection_params.copy()
                logger.warning(
                    f"DEV MODE: Saving password for '{connection_name}' "
                    "(ENABLE_PASSWORD_STORAGE=1 is active - INSECURE!)"
                )
            else:
                # Remove password for security (production-safe)
                safe_params = {k: v for k, v in connection_params.items() if k != "password"}

            # Save connection config
            connections[connection_name] = {
                "name": connection_name,
                "type": db_type,
                "params": safe_params,
                "last_used": time.time(),
            }

            await self._storage.set(CONNECTIONS_KEY, connections)
        except Exception:
            pass  # Graceful degradation

    async def get_all_connections(self) -> Dict[str, Dict[str, Any]]:
        """Get all saved database connection configurations."""
        await self.initialize()
        if not self._storage:
            return {}

        try:
            value = await self._storage.get(CONNECTIONS_KEY)
            if isinstance(value, dict):
                return value
            elif isinstance(value, str):
                return json.loads(value)
            return {}
        except Exception:
            return {}

    async def delete_connection(self, connection_name: str) -> None:
        """Delete a saved connection configuration."""
        await self.initialize()
        if not self._storage:
            return

        try:
            connections = await self.get_all_connections()
            if connection_name in connections:
                del connections[connection_name]
                await self._storage.set(CONNECTIONS_KEY, connections)
        except Exception:
            pass  # Graceful degradation

    async def set_active_connection(self, connection_name: str) -> None:
        """Set the active/default database connection."""
        await self.initialize()
        if not self._storage:
            return

        try:
            await self._storage.set(ACTIVE_CONNECTION_KEY, connection_name)
        except Exception:
            pass  # Graceful degradation

    async def get_active_connection(self) -> Optional[str]:
        """Get the active/default database connection name."""
        await self.initialize()
        if not self._storage:
            return None

        try:
            value = await self._storage.get(ACTIVE_CONNECTION_KEY)
            return value if isinstance(value, str) else None
        except Exception:
            return None

    # ==================== USER PREFERENCES ====================

    async def get_user_preferences(self) -> Dict[str, Any]:
        """Get user preferences from persistent storage."""
        await self.initialize()
        if not self._storage:
            return {}

        try:
            value = await self._storage.get(USER_PREFS_KEY)
            if isinstance(value, dict):
                return value
            elif isinstance(value, str):
                return json.loads(value)
            return {}
        except Exception:
            return {}

    async def set_user_preferences(self, prefs: Dict[str, Any]) -> None:
        """Store user preferences persistently."""
        await self.initialize()
        if not self._storage:
            return

        try:
            # Merge with existing preferences
            existing = await self.get_user_preferences()
            existing.update(prefs)
            await self._storage.set(USER_PREFS_KEY, existing)
        except Exception:
            pass  # Graceful degradation

    async def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a specific user preference."""
        prefs = await self.get_user_preferences()
        return prefs.get(key, default)

    async def set_preference(self, key: str, value: Any) -> None:
        """Set a specific user preference."""
        prefs = await self.get_user_preferences()
        prefs[key] = value
        await self.set_user_preferences(prefs)

    # ==================== SEARCH HISTORY ====================

    async def add_search_to_history(
        self, query: str, filters: Optional[Dict[str, Any]] = None, max_history: int = 50
    ) -> None:
        """Add a search query to history."""
        await self.initialize()
        if not self._storage:
            return

        try:
            history = await self.get_search_history(max_history=max_history * 2)
            entry = {
                "query": query,
                "filters": filters or {},
                "timestamp": time.time(),
            }
            history.insert(0, entry)
            history = history[:max_history]
            await self._storage.set(SEARCH_HISTORY_KEY, history)
        except Exception:
            pass  # Graceful degradation

    async def get_search_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent search history."""
        await self.initialize()
        if not self._storage:
            return []

        try:
            value = await self._storage.get(SEARCH_HISTORY_KEY)
            if isinstance(value, list):
                return value[:limit]
            elif isinstance(value, str):
                parsed = json.loads(value)
                return parsed[:limit] if isinstance(parsed, list) else []
            return []
        except Exception:
            return []

    async def clear_search_history(self) -> None:
        """Clear all search history."""
        await self.initialize()
        if not self._storage:
            return

        try:
            await self._storage.set(SEARCH_HISTORY_KEY, [])
        except Exception:
            pass  # Graceful degradation

    # ==================== BOOKMARK SYNC STATE ====================

    async def get_bookmark_sync_state(self) -> Dict[str, Any]:
        """Get bookmark sync state (last sync times, preferences)."""
        await self.initialize()
        if not self._storage:
            return {}

        try:
            value = await self._storage.get(BOOKMARK_SYNC_STATE_KEY)
            if isinstance(value, dict):
                return value
            elif isinstance(value, str):
                return json.loads(value)
            return {}
        except Exception:
            return {}

    async def set_bookmark_sync_state(self, state: Dict[str, Any]) -> None:
        """Store bookmark sync state."""
        await self.initialize()
        if not self._storage:
            return

        try:
            await self._storage.set(BOOKMARK_SYNC_STATE_KEY, state)
        except Exception:
            pass  # Graceful degradation

    async def update_sync_time(self, source_browser: str, target_browser: str) -> None:
        """Update last sync time for a browser pair."""
        state = await self.get_bookmark_sync_state()
        sync_key = f"{source_browser}->{target_browser}"
        if "sync_times" not in state:
            state["sync_times"] = {}
        state["sync_times"][sync_key] = time.time()
        await self.set_bookmark_sync_state(state)

    # ==================== WINDOWS APP DATABASE PATHS ====================

    async def add_windows_db_path(self, app_name: str, db_path: str) -> None:
        """Add a remembered Windows app database path."""
        await self.initialize()
        if not self._storage:
            return

        try:
            paths = await self.get_windows_db_paths()
            paths[app_name] = {"path": db_path, "last_used": time.time()}
            await self._storage.set(WINDOWS_DB_PATHS_KEY, paths)
        except Exception:
            pass  # Graceful degradation

    async def get_windows_db_paths(self) -> Dict[str, Dict[str, Any]]:
        """Get all remembered Windows app database paths."""
        await self.initialize()
        if not self._storage:
            return {}

        try:
            value = await self._storage.get(WINDOWS_DB_PATHS_KEY)
            if isinstance(value, dict):
                return value
            elif isinstance(value, str):
                return json.loads(value)
            return {}
        except Exception:
            return {}

    # ==================== QUERY TEMPLATES ====================

    async def save_query_template(
        self, template_name: str, query: str, description: str = ""
    ) -> None:
        """Save a query template."""
        await self.initialize()
        if not self._storage:
            return

        try:
            templates = await self.get_query_templates()
            templates[template_name] = {
                "query": query,
                "description": description,
                "created": time.time(),
            }
            await self._storage.set(QUERY_TEMPLATES_KEY, templates)
        except Exception:
            pass  # Graceful degradation

    async def get_query_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get all saved query templates."""
        await self.initialize()
        if not self._storage:
            return {}

        try:
            value = await self._storage.get(QUERY_TEMPLATES_KEY)
            if isinstance(value, dict):
                return value
            elif isinstance(value, str):
                return json.loads(value)
            return {}
        except Exception:
            return {}

    async def delete_query_template(self, template_name: str) -> None:
        """Delete a query template."""
        await self.initialize()
        if not self._storage:
            return

        try:
            templates = await self.get_query_templates()
            if template_name in templates:
                del templates[template_name]
                await self._storage.set(QUERY_TEMPLATES_KEY, templates)
        except Exception:
            pass  # Graceful degradation

    # ==================== BACKUP LOCATIONS ====================

    async def add_backup_location(self, location: str, description: str = "") -> None:
        """Add a recent backup location."""
        await self.initialize()
        if not self._storage:
            return

        try:
            locations = await self.get_backup_locations()
            locations[location] = {
                "description": description,
                "last_used": time.time(),
            }
            await self._storage.set(BACKUP_LOCATIONS_KEY, locations)
        except Exception:
            pass  # Graceful degradation

    async def get_backup_locations(self) -> Dict[str, Dict[str, Any]]:
        """Get all recent backup locations."""
        await self.initialize()
        if not self._storage:
            return {}

        try:
            value = await self._storage.get(BACKUP_LOCATIONS_KEY)
            if isinstance(value, dict):
                return value
            elif isinstance(value, str):
                return json.loads(value)
            return {}
        except Exception:
            return {}

    # ==================== SCHEMA CACHE ====================

    async def cache_schema(
        self, connection_name: str, db_name: str, schema: Dict[str, Any], ttl: int = 3600
    ) -> None:
        """Cache database schema with TTL (default 1 hour)."""
        await self.initialize()
        if not self._storage:
            return

        try:
            cache_key = f"{SCHEMA_CACHE_PREFIX}{connection_name}:{db_name}"
            await self._storage.set(cache_key, schema, ttl=ttl)
        except Exception:
            pass  # Graceful degradation

    async def get_cached_schema(
        self, connection_name: str, db_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached schema if available and not expired."""
        await self.initialize()
        if not self._storage:
            return None

        try:
            cache_key = f"{SCHEMA_CACHE_PREFIX}{connection_name}:{db_name}"
            value = await self._storage.get(cache_key)
            if isinstance(value, dict):
                return value
            elif isinstance(value, str):
                return json.loads(value)
            return None
        except Exception:
            return None


# Global storage instance (initialized in server startup)
_storage_instance: Optional[DatabaseOperationsStorage] = None


def get_storage() -> Optional[DatabaseOperationsStorage]:
    """Get the singleton storage instance."""
    return _storage_instance


def set_storage(storage: DatabaseOperationsStorage) -> None:
    """Set the singleton storage instance."""
    global _storage_instance
    _storage_instance = storage
