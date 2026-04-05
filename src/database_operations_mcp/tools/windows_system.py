import logging
import os
import shutil
import sqlite3
import threading
import time
import winreg
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Callable

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp
from database_operations_mcp.operation_types import WindowsSystemOperation
from database_operations_mcp.tool_responses import unknown_operation_response
from database_operations_mcp.tools.help_tools import HelpSystem

logger = logging.getLogger(__name__)

# Global dictionary to track active monitors
_active_monitors: Dict[str, "RegistryMonitor"] = {}

# Map registry hives to their corresponding winreg constants
HIVE_MAP = {
    "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
    "HKCU": winreg.HKEY_CURRENT_USER,
    "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
    "HKLM": winreg.HKEY_LOCAL_MACHINE,
    "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
    "HKU": winreg.HKEY_USERS,
    "HKEY_USERS": winreg.HKEY_USERS,
    "HKCC": winreg.HKEY_CURRENT_CONFIG,
    "HKEY_CURRENT_CONFIG": winreg.HKEY_CURRENT_CONFIG,
}

# Map value types to their string representations
VALUE_TYPES = {
    winreg.REG_SZ: "REG_SZ",
    winreg.REG_EXPAND_SZ: "REG_EXPAND_SZ",
    winreg.REG_BINARY: "REG_BINARY",
    winreg.REG_DWORD: "REG_DWORD",
    winreg.REG_DWORD_LITTLE_ENDIAN: "REG_DWORD_LITTLE_ENDIAN",
    winreg.REG_DWORD_BIG_ENDIAN: "REG_DWORD_BIG_ENDIAN",
    winreg.REG_LINK: "REG_LINK",
    winreg.REG_MULTI_SZ: "REG_MULTI_SZ",
    winreg.REG_RESOURCE_LIST: "REG_RESOURCE_LIST",
    winreg.REG_FULL_RESOURCE_DESCRIPTOR: "REG_FULL_RESOURCE_DESCRIPTOR",
    winreg.REG_RESOURCE_REQUIREMENTS_LIST: "REG_RESOURCE_REQUIREMENTS_LIST",
    winreg.REG_QWORD: "REG_QWORD",
    winreg.REG_QWORD_LITTLE_ENDIAN: "REG_QWORD_LITTLE_ENDIAN",
}

# Common Windows database locations
WINDOWS_DB_PATHS = {
    "chrome_history": [
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\History"),
        os.path.expandvars(
            r"%USERPROFILE%\AppData\Local\Google\Chrome\User Data\Default\History"
        ),
    ],
    "firefox_history": [
        os.path.expandvars(r"%APPDATA%\Mozilla\Firefox\Profiles"),
    ],
    "edge_history": [
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\History"),
        os.path.expandvars(
            r"%USERPROFILE%\AppData\Local\Microsoft\Edge\User Data\Default\History"
        ),
    ],
    "brave_history": [
        os.path.expandvars(
            r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\History"
        ),
        os.path.expandvars(
            r"%USERPROFILE%\AppData\Local\BraveSoftware\Brave-Browser\\"
            r"User Data\Default\History"
        ),
    ],
    "outlook": [
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Outlook"),
        os.path.expandvars(r"%USERPROFILE%\AppData\Local\Microsoft\Outlook"),
    ],
    "windows_thumbnails": [
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Explorer")
    ],
}


class RegistryMonitor:
    """Monitor registry changes in real-time."""

    def __init__(self, path: str, callback: Callable[[dict], None]):
        self.path = path
        self.callback = callback
        self.running = False
        self.last_values = {}
        self.thread = None

    def start(self):
        """Start monitoring the registry key."""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._monitor, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop monitoring."""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)

    def _monitor(self):
        """Monitor the registry key for changes."""
        try:
            hive, subkey = _parse_registry_path(self.path)
            while self.running:
                current_values = self._get_key_values(hive, subkey)
                changes = self._find_changes(current_values)
                if changes:
                    self.callback(
                        {
                            "path": self.path,
                            "timestamp": time.time(),
                            "changes": changes,
                        }
                    )
                self.last_values = current_values
                time.sleep(1.0)
        except Exception as e:
            logger.error(f"Error monitoring registry key {self.path}: {e}")

    def _get_key_values(self, hive, subkey):
        values = {}
        try:
            with winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ) as key:
                i = 0
                while True:
                    try:
                        name, value, value_type = winreg.EnumValue(key, i)
                        values[name or "(Default)"] = {
                            "value": value,
                            "type": VALUE_TYPES.get(value_type, f"TYPE_{value_type}"),
                        }
                        i += 1
                    except OSError:
                        break
        except FileNotFoundError:
            pass
        return values

    def _find_changes(self, current: dict) -> list[dict]:
        if not self.last_values:
            return []
        changes = []
        for name, info in current.items():
            if name not in self.last_values:
                changes.append({"type": "added", "name": name, "new": info})
            elif self.last_values[name]["value"] != info["value"]:
                changes.append(
                    {
                        "type": "modified",
                        "name": name,
                        "old": self.last_values[name],
                        "new": info,
                    }
                )
        for name in set(self.last_values) - set(current):
            changes.append(
                {"type": "removed", "name": name, "old": self.last_values[name]}
            )
        return changes


def _parse_registry_path(path: str) -> tuple[int, str]:
    """Parse a registry path into hive and subkey."""
    path = path.replace("/", "\\")
    path_parts = path.split("\\", 1)
    hive_name = path_parts[0].upper()
    if hive_name not in HIVE_MAP:
        raise ValueError(f"Unsupported registry hive: {hive_name}")
    hive = HIVE_MAP[hive_name]
    subkey = path_parts[1] if len(path_parts) > 1 else ""
    return hive, subkey


def _find_windows_db(db_type: str) -> Path | None:
    """Find a Windows database file by type."""
    for path in WINDOWS_DB_PATHS.get(db_type, []):
        try:
            if db_type == "firefox_history":
                profiles_path = Path(path)
                if profiles_path.exists() and profiles_path.is_dir():
                    profile_candidates = []
                    for profile_dir in profiles_path.iterdir():
                        if profile_dir.is_dir():
                            places_db = profile_dir / "places.sqlite"
                            if places_db.exists():
                                priority = 0
                                if profile_dir.name.endswith(".default-release"):
                                    priority = 2
                                elif profile_dir.name.endswith(".default"):
                                    priority = 1
                                profile_candidates.append((priority, places_db))
                    if profile_candidates:
                        profile_candidates.sort(key=lambda x: x[0], reverse=True)
                        return profile_candidates[0][1]
            else:
                db_path = Path(path)
                if db_path.exists():
                    return db_path
        except (PermissionError, OSError) as e:
            logger.debug(f"Skipping {db_type} path {path} due to error: {e}")
            continue
    return None


@mcp.tool()
@HelpSystem.register_tool(category="windows")
async def windows_system(
    operation: WindowsSystemOperation,
    registry_key: Optional[str] = None,
    registry_value: Optional[str] = None,
    value_data: Optional[Any] = None,
    value_type: Optional[str] = None,
    database_path: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = 100,
    clean_database: bool = False,
    backup: bool = True,
    bruteforce_firefox: bool = False,
    action: Optional[str] = "analyze",
) -> Dict[str, Any]:
    """Windows system management portmanteau tool.

    Comprehensive Windows system operations consolidating ALL registry, Plex, and
    Windows-specific database operations into a single interface.
    """
    limit = max(1, min(limit, 50_000))

    try:
        if operation == "list_windows_databases":
            return await _list_windows_databases(bruteforce_firefox)
        elif operation == "query_windows_database":
            return await _query_windows_database(
                database_path, query, limit, bruteforce_firefox
            )
        elif operation == "clean_windows_database":
            return await _clean_windows_database(
                database_path,
                "vacuum" if clean_database else "analyze",
                backup,
                bruteforce_firefox,
            )
        elif operation == "read_registry_value":
            return await _read_registry_value(registry_key, registry_value)
        elif operation == "write_registry_value":
            return await _write_registry_value(
                registry_key, registry_value, value_data, value_type
            )
        elif operation == "list_registry_keys":
            return await _list_registry_keys(registry_key)
        elif operation == "list_registry_values":
            return await _list_registry_values(registry_key)
        elif operation == "monitor_registry":
            return await _monitor_registry(registry_key, action)
        elif operation == "delete_registry_value":
            return await _delete_registry_value(registry_key, registry_value)
        elif operation == "delete_registry_key":
            return await _delete_registry_key(registry_key)
        elif operation == "registry_key_exists":
            return await _registry_key_exists(registry_key)
        else:
            return unknown_operation_response(
                operation,
                [
                    "list_windows_databases",
                    "query_windows_database",
                    "clean_windows_database",
                    "read_registry_value",
                    "write_registry_value",
                    "delete_registry_value",
                    "delete_registry_key",
                    "registry_key_exists",
                    "list_registry_keys",
                    "list_registry_values",
                    "monitor_registry",
                ],
            )
    except Exception as e:
        logger.exception(f"Error in windows_system operation {operation}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "fatal",
            "retryable": False,
            "recovery_options": [
                "Verify registry_key paths and that you have permission.",
                "For database paths, ensure the file exists and is not exclusively locked.",
            ],
        }


async def _list_windows_databases(bruteforce: bool = False) -> Dict[str, Any]:
    """List discoverable Windows databases."""
    result = {}
    for db_type in WINDOWS_DB_PATHS:
        db_path = _find_windows_db(db_type)
        if db_path and db_path.exists():
            size_mb = os.path.getsize(db_path) / (1024 * 1024)
            result[db_type] = {
                "path": str(db_path),
                "size_mb": round(size_mb, 2),
                "exists": True,
            }
        else:
            result[db_type] = {"exists": False}
    return {"success": True, "databases": result}


async def _query_windows_database(
    target: Optional[str],
    query: Optional[str],
    limit: int = 100,
    bruteforce: bool = False,
) -> Dict[str, Any]:
    """Execute query against Windows database."""
    if not target or not query:
        return {"success": False, "error": "Target and query are required"}

    db_path = _find_windows_db(target) or Path(target)
    if not db_path.exists():
        return {"success": False, "error": f"Database not found: {target}"}

    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if "LIMIT" not in query.upper() and limit > 0:
            query = query.rstrip(";") + f" LIMIT {limit}"

        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        return {
            "success": True,
            "database": target,
            "columns": columns,
            "results": [dict(row) for row in rows],
            "count": len(rows),
        }
    finally:
        if "conn" in locals():
            conn.close()


async def _clean_windows_database(
    target: Optional[str],
    action: str = "vacuum",
    backup: bool = True,
    bruteforce: bool = False,
) -> Dict[str, Any]:
    """Clean/Optimize Windows database."""
    if not target:
        return {"success": False, "error": "Target database is required"}

    db_path = _find_windows_db(target) or Path(target)
    if not db_path.exists():
        return {"success": False, "error": f"Database not found: {target}"}

    if backup:
        backup_path = db_path.with_suffix(
            f".bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        shutil.copy2(db_path, backup_path)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("VACUUM" if action == "vacuum" else "ANALYZE")
        conn.commit()
        return {
            "success": True,
            "message": f"Database {action} completed",
            "backup": str(backup_path) if backup else None,
        }
    finally:
        if "conn" in locals():
            conn.close()


async def _read_registry_value(
    key_path: Optional[str], value_name: Optional[str]
) -> Dict[str, Any]:
    """Read value from Windows Registry."""
    if not key_path:
        return {"success": False, "error": "Registry key path is required"}
    try:
        hive, subkey = _parse_registry_path(key_path)
        with winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ) as key:
            value, vtype = winreg.QueryValueEx(key, value_name or "")
            return {
                "success": True,
                "path": key_path,
                "value": value,
                "type": VALUE_TYPES.get(vtype, f"TYPE_{vtype}"),
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


async def _write_registry_value(
    key_path: Optional[str],
    value_name: Optional[str],
    data: Any,
    vtype_str: Optional[str] = None,
) -> Dict[str, Any]:
    """Write value to Windows Registry."""
    if not key_path:
        return {"success": False, "error": "Registry key path is required"}
    try:
        hive, subkey = _parse_registry_path(key_path)
        reg_type = winreg.REG_SZ
        if vtype_str:
            type_map = {v: k for k, v in VALUE_TYPES.items()}
            reg_type = type_map.get(vtype_str, winreg.REG_SZ)
        elif isinstance(data, int):
            reg_type = winreg.REG_DWORD
        with winreg.CreateKey(hive, subkey) as key:
            winreg.SetValueEx(key, value_name or "", 0, reg_type, data)
        return {"success": True, "message": "Value written successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def _list_registry_keys(key_path: Optional[str]) -> Dict[str, Any]:
    """List subkeys in a registry path."""
    if not key_path:
        return {"success": False, "error": "Registry key path is required"}
    try:
        hive, subkey = _parse_registry_path(key_path)
        subkeys = []
        with winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ) as key:
            i = 0
            while True:
                try:
                    subkeys.append(winreg.EnumKey(key, i))
                    i += 1
                except OSError:
                    break
        return {"success": True, "subkeys": subkeys}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def _list_registry_values(key_path: Optional[str]) -> Dict[str, Any]:
    """List values in a registry key."""
    if not key_path:
        return {"success": False, "error": "Registry key path is required"}
    try:
        hive, subkey = _parse_registry_path(key_path)
        values = {}
        with winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ) as key:
            i = 0
            while True:
                try:
                    name, data, vtype = winreg.EnumValue(key, i)
                    values[name or "(Default)"] = {
                        "value": data,
                        "type": VALUE_TYPES.get(vtype, f"TYPE_{vtype}"),
                    }
                    i += 1
                except OSError:
                    break
        return {"success": True, "values": values}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def _delete_registry_value(
    key_path: Optional[str], value_name: Optional[str]
) -> Dict[str, Any]:
    """Delete a value from the Windows Registry."""
    if not key_path:
        return {"success": False, "error": "Registry key path is required"}
    try:
        hive, subkey = _parse_registry_path(key_path)
        with winreg.OpenKey(hive, subkey, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, value_name or "")
        return {"success": True, "message": f"Value {value_name} deleted successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def _delete_registry_key(key_path: Optional[str]) -> Dict[str, Any]:
    """Delete a key from the Windows Registry."""
    if not key_path:
        return {"success": False, "error": "Registry key path is required"}
    try:
        hive, subkey = _parse_registry_path(key_path)
        winreg.DeleteKey(hive, subkey)
        return {"success": True, "message": f"Key {key_path} deleted successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def _registry_key_exists(key_path: Optional[str]) -> Dict[str, Any]:
    """Check if a registry key exists."""
    if not key_path:
        return {"success": False, "error": "Registry key path is required"}
    try:
        hive, subkey = _parse_registry_path(key_path)
        with winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ):
            return {"success": True, "exists": True}
    except FileNotFoundError:
        return {"success": True, "exists": False}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def _monitor_registry(
    key_path: Optional[str], action: Optional[str] = "start"
) -> Dict[str, Any]:
    """Manage registry monitoring."""
    if not key_path:
        return {"success": False, "error": "Registry key path is required"}

    if action == "start":
        if key_path in _active_monitors:
            return {
                "success": True,
                "message": f"Monitor already active for {key_path}",
            }

        def on_change(change_data):
            logger.info(f"Registry change detected: {change_data}")
            # In a real agentic scenario, we might use notifications here

        monitor = RegistryMonitor(key_path, on_change)
        monitor.start()
        _active_monitors[key_path] = monitor
        return {"success": True, "message": f"Registry monitor started for {key_path}"}

    elif action == "stop":
        if key_path in _active_monitors:
            _active_monitors[key_path].stop()
            del _active_monitors[key_path]
            return {
                "success": True,
                "message": f"Registry monitor stopped for {key_path}",
            }
        return {"success": False, "error": f"No active monitor for {key_path}"}

    elif action == "status":
        return {"success": True, "active": key_path in _active_monitors}

    return {"success": False, "error": f"Unsupported monitor action: {action}"}
