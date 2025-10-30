"""
Windows Registry Tools

Provides tools for interacting with the Windows Registry as a hierarchical database,
including monitoring, backup, and restore functionality.
"""

import logging
import threading
import time
import winreg
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

# Import the global MCP instance
from database_operations_mcp.config.mcp_config import mcp

from .help_tools import HelpSystem

# Type variable for function type
F = TypeVar("F", bound=Callable[..., Any])

logger = logging.getLogger(__name__)

# Global dictionary to track active monitors
_active_monitors: dict[str, "RegistryMonitor"] = {}

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


def _parse_registry_path(path: str) -> tuple[int, str]:
    """Parse a registry path into hive and subkey."""
    path_parts = path.replace("\\", "/").split("/", 1)
    hive_name = path_parts[0].upper()

    if hive_name not in HIVE_MAP:
        raise ValueError(f"Unsupported registry hive: {hive_name}")

    hive = HIVE_MAP[hive_name]
    subkey = path_parts[1] if len(path_parts) > 1 else ""

    return hive, subkey


# Active monitors
_active_monitors: dict[str, "RegistryMonitor"] = {}


@dataclass
class RegistryMonitor:
    """Monitor registry changes in real-time."""

    path: str
    callback: Callable[[dict], None]
    running: bool = False
    thread: threading.Thread = field(init=False)
    last_values: dict = field(default_factory=dict)

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
        if hasattr(self, "thread") and self.thread.is_alive():
            self.thread.join(timeout=1.0)

    def _monitor(self):
        """Monitor the registry key for changes."""
        hive, subkey = _parse_registry_path(self.path)

        while self.running:
            try:
                current_values = self._get_key_values(hive, subkey)
                changes = self._find_changes(current_values)

                if changes:
                    self.callback({"path": self.path, "timestamp": time.time(), "changes": changes})

                self.last_values = current_values
                time.sleep(1.0)  # Check every second

            except Exception as e:
                logger.error(f"Error monitoring registry key {self.path}: {e}")
                time.sleep(5.0)  # Wait longer on error

    def _get_key_values(self, hive, subkey):
        """Get all values from a registry key."""
        values = {}

        try:
            with winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ) as key:
                i = 0
                while True:
                    try:
                        name, value, value_type = winreg.EnumValue(key, i)
                        values[name] = {
                            "value": value,
                            "type": value_type,
                            "type_name": VALUE_TYPES.get(value_type, f"UNKNOWN (0x{value_type:X})"),
                        }
                        i += 1
                    except OSError as e:
                        if e.winerror == 259:  # No more data
                            break
                        raise
        except FileNotFoundError:
            pass  # Key doesn't exist (anymore)

        return values

    def _find_changes(self, current: dict) -> list[dict]:
        """Find changes between current and last known values."""
        if not self.last_values:
            return []

        changes = []

        # Check for new or modified values
        for name, value_info in current.items():
            if name not in self.last_values:
                changes.append({"type": "value_added", "name": name, "new_value": value_info})
            elif (
                self.last_values[name]["value"] != value_info["value"]
                or self.last_values[name]["type"] != value_info["type"]
            ):
                changes.append(
                    {
                        "type": "value_modified",
                        "name": name,
                        "old_value": self.last_values[name],
                        "new_value": value_info,
                    }
                )

        # Check for removed values
        for name in set(self.last_values) - set(current):
            changes.append(
                {"type": "value_removed", "name": name, "old_value": self.last_values[name]}
            )

        return changes


# Register tools using the @mcp.tool decorator
# The mcp instance is imported from the centralized config


@mcp.tool()
@HelpSystem.register_tool
def read_registry_value(path: str, value_name: str = "") -> dict[str, Any]:
    """Read a value from the Windows Registry.

    Args:
        path: Registry key path (e.g., 'HKLM\\SOFTWARE\\Microsoft\\Windows')
        value_name: Name of the value to read (empty string for default value)

    Returns:
        Dictionary containing the value data and metadata
    """
    try:
        hive, subkey = _parse_registry_path(path)
        with winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ) as key:
            value_data, value_type = winreg.QueryValueEx(key, value_name)

            # Format the value based on type
            if value_type == winreg.REG_MULTI_SZ:
                value_data = list(value_data) if value_data else []
            elif value_type == winreg.REG_BINARY:
                value_data = value_data.hex()

            return {
                "success": True,
                "path": path,
                "value_name": value_name,
                "value": value_data,
                "type": VALUE_TYPES.get(value_type, f"UNKNOWN (0x{value_type:X})"),
                "type_code": value_type,
            }
    except FileNotFoundError:
        return {"success": False, "error": f"Registry key or value not found: {path}\\{value_name}"}
    except Exception as e:
        logger.error(f"Error reading registry value {path}\\{value_name}: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
@HelpSystem.register_tool
def write_registry_value(
    path: str, value_name: str, value: Any, value_type: str | None = None
) -> dict[str, Any]:
    """Write a value to the Windows Registry.

    Args:
        path: Registry key path (e.g., 'HKCU\\Software\\MyApp')
        value_name: Name of the value to write (empty string for default value)
        value: Value to write
        value_type: Type of the value (e.g., 'REG_SZ', 'REG_DWORD')

    Returns:
        Dictionary with operation status
    """
    try:
        hive, subkey = _parse_registry_path(path)

        # Convert value type from string to winreg constant
        if value_type:
            type_map = {v: k for k, v in VALUE_TYPES.items()}
            if value_type not in type_map:
                return {"success": False, "error": f"Unsupported value type: {value_type}"}
            reg_type = type_map[value_type]
        else:
            # Guess type based on Python type
            if isinstance(value, int):
                reg_type = winreg.REG_DWORD
            elif isinstance(value, list):
                reg_type = winreg.REG_MULTI_SZ
                value = [str(v) for v in value]  # Ensure all items are strings
            elif isinstance(value, bytes):
                reg_type = winreg.REG_BINARY
            else:
                reg_type = winreg.REG_SZ
                value = str(value)

        # Create the key if it doesn't exist
        try:
            key = winreg.OpenKey(hive, subkey, 0, winreg.KEY_WRITE)
        except FileNotFoundError:
            key = winreg.CreateKey(hive, subkey)

        with key:
            winreg.SetValueEx(key, value_name, 0, reg_type, value)

        return {
            "success": True,
            "path": path,
            "value_name": value_name,
            "message": "Value written successfully",
        }
    except Exception as e:
        logger.error(f"Error writing registry value {path}\\{value_name}: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
@HelpSystem.register_tool
def list_registry_keys(path: str) -> dict[str, Any]:
    """List all subkeys under a registry key.

    Args:
        path: Registry key path (e.g., 'HKLM\\SOFTWARE\\Microsoft')

    Returns:
        Dictionary containing the list of subkeys
    """
    try:
        hive, subkey = _parse_registry_path(path)
        subkeys = []

        with winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ) as key:
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkeys.append(subkey_name)
                    i += 1
                except OSError as e:
                    if e.winerror == 259:  # No more data
                        break
                    raise

        return {"success": True, "path": path, "subkeys": subkeys, "count": len(subkeys)}
    except Exception as e:
        logger.error(f"Error listing registry keys under {path}: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
@HelpSystem.register_tool
def list_registry_values(path: str) -> dict[str, Any]:
    """List all values under a registry key.

    Args:
        path: Registry key path (e.g., 'HKCU\\Software\\MyApp')

    Returns:
        Dictionary containing the list of values and their data
    """
    try:
        hive, subkey = _parse_registry_path(path)
        values = {}

        with winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ) as key:
            i = 0
            while True:
                try:
                    value_name, value_data, value_type = winreg.EnumValue(key, i)
                    value_name = value_name or "(Default)"

                    # Format the value based on type
                    if value_type == winreg.REG_MULTI_SZ:
                        value_data = list(value_data) if value_data else []
                    elif value_type == winreg.REG_BINARY:
                        value_data = value_data.hex()

                    values[value_name] = {
                        "value": value_data,
                        "type": VALUE_TYPES.get(value_type, f"UNKNOWN (0x{value_type:X})"),
                        "type_code": value_type,
                    }
                    i += 1
                except OSError as e:
                    if e.winerror == 259:  # No more data
                        break
                    raise

        return {"success": True, "path": path, "values": values, "count": len(values)}
    except Exception as e:
        logger.error(f"Error listing registry values under {path}: {e}")
        return {"success": False, "error": str(e)}


# Additional registry tools can be added here following the same pattern
# Each tool should be decorated with @mcp.tool() and @HelpSystem.register_tool
