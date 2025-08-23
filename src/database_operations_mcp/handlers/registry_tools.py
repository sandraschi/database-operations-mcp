"""
Windows Registry Tools

Provides tools for interacting with the Windows Registry as a hierarchical database,
including monitoring, backup, and restore functionality.
"""

import winreg
import logging
from typing import Dict, List, Any, Optional, Callable, TypeVar, Tuple, cast
import json
import os
import threading
import time
import uuid
from dataclasses import dataclass, field

from fastmcp import FastMCP as FastMCPType
from .help_tools import HelpSystem

# Type variable for function type
F = TypeVar('F', bound=Callable[..., Any])

logger = logging.getLogger(__name__)

# Map registry hives to their corresponding winreg constants
HIVE_MAP = {
    'HKEY_CLASSES_ROOT': winreg.HKEY_CLASSES_ROOT,
    'HKCU': winreg.HKEY_CURRENT_USER,
    'HKEY_CURRENT_USER': winreg.HKEY_CURRENT_USER,
    'HKLM': winreg.HKEY_LOCAL_MACHINE,
    'HKEY_LOCAL_MACHINE': winreg.HKEY_LOCAL_MACHINE,
    'HKU': winreg.HKEY_USERS,
    'HKEY_USERS': winreg.HKEY_USERS,
    'HKCC': winreg.HKEY_CURRENT_CONFIG,
    'HKEY_CURRENT_CONFIG': winreg.HKEY_CURRENT_CONFIG,
    'HKDD': winreg.HKEY_DYN_DATA,
    'HKEY_DYN_DATA': winreg.HKEY_DYN_DATA
}

# Map value types to human-readable names
VALUE_TYPES = {
    winreg.REG_NONE: 'REG_NONE',
    winreg.REG_SZ: 'REG_SZ',
    winreg.REG_EXPAND_SZ: 'REG_EXPAND_SZ',
    winreg.REG_BINARY: 'REG_BINARY',
    winreg.REG_DWORD: 'REG_DWORD',
    winreg.REG_DWORD_BIG_ENDIAN: 'REG_DWORD_BIG_ENDIAN',
    winreg.REG_LINK: 'REG_LINK',
    winreg.REG_MULTI_SZ: 'REG_MULTI_SZ',
    winreg.REG_RESOURCE_LIST: 'REG_RESOURCE_LIST',
    winreg.REG_FULL_RESOURCE_DESCRIPTOR: 'REG_FULL_RESOURCE_DESCRIPTOR',
    winreg.REG_RESOURCE_REQUIREMENTS_LIST: 'REG_RESOURCE_REQUIREMENTS_LIST',
    winreg.REG_QWORD: 'REG_QWORD'
}

def _parse_registry_path(path: str) -> Tuple[int, str]:
    """Parse a registry path into hive and subkey."""
    if '\\' not in path:
        raise ValueError("Invalid registry path format. Use 'HKLM\\Path\\To\\Key' format.")
    
    hive_name, _, subkey = path.partition('\\')
    hive = HIVE_MAP.get(hive_name.upper())
    
    if hive is None:
        raise ValueError(f"Unknown registry hive: {hive_name}")
    
    return hive, subkey

# Active monitors
_active_monitors: Dict[str, 'RegistryMonitor'] = {}

@dataclass
class RegistryMonitor:
    """Monitor registry changes in real-time."""
    path: str
    callback: Callable[[Dict], None]
    running: bool = False
    thread: threading.Thread = field(init=False)
    last_values: Dict = field(default_factory=dict)
    
    def start(self):
        """Start monitoring the registry key."""
        self.running = True
        self.thread = threading.Thread(target=self._monitor, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop monitoring."""
        self.running = False
        if hasattr(self, 'thread') and self.thread.is_alive():
            self.thread.join(timeout=2)
    
    def _monitor(self):
        """Monitor the registry key for changes."""
        hive, subkey = _parse_registry_path(self.path)
        
        # Get initial values
        with winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ) as key:
            self.last_values = self._get_key_values(key)
        
        while self.running:
            try:
                with winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ) as key:
                    current_values = self._get_key_values(key)
                    
                    # Check for changes
                    changes = self._find_changes(current_values)
                    if changes:
                        self.callback({
                            'path': self.path,
                            'timestamp': time.time(),
                            'changes': changes
                        })
                    
                    self.last_values = current_values
            except Exception as e:
                logger.error(f"Error monitoring registry: {e}")
            
            time.sleep(1)  # Polling interval
    
    def _get_key_values(self, key) -> Dict:
        """Get all values from a registry key."""
        values = {}
        i = 0
        while True:
            try:
                value_name, value_data, value_type = winreg.EnumValue(key, i)
                value_name = value_name or '(Default)'
                
                # Format the value based on type
                if value_type == winreg.REG_MULTI_SZ:
                    value_data = list(value_data) if value_data else []
                elif value_type == winreg.REG_BINARY:
                    value_data = value_data.hex()
                
                values[value_name] = {
                    'value': value_data,
                    'type': VALUE_TYPES.get(value_type, f'UNKNOWN (0x{value_type:X})'),
                    'type_code': value_type
                }
                i += 1
            except OSError as e:
                if e.winerror == 259:  # No more data
                    break
                raise
        return values
    
    def _find_changes(self, current: Dict) -> List[Dict]:
        """Find changes between current and last known values."""
        changes = []
        
        # Check for added or modified values
        for name, current_value in current.items():
            if name not in self.last_values:
                changes.append({
                    'type': 'value_added',
                    'name': name,
                    'new_value': current_value
                })
            elif current_value != self.last_values[name]:
                changes.append({
                    'type': 'value_modified',
                    'name': name,
                    'old_value': self.last_values[name],
                    'new_value': current_value
                })
        
        # Check for removed values
        for name in set(self.last_values) - set(current):
            changes.append({
                'type': 'value_removed',
                'name': name,
                'old_value': self.last_values[name]
            })
        
        return changes

def register_tools(mcp: 'FastMCP') -> None:
    """Register all registry tools with the MCP server.
    
    Args:
        mcp: The FastMCP instance to register tools with
    """
    @mcp.tool()
    @HelpSystem.register_tool
    async def search_registry(
        search_term: str,
        search_in: str = 'all',  # 'keys', 'values', 'data', 'all'
        hives: List[str] = None,
        max_results: int = 100
    ) -> Dict[str, Any]:
        """
        Search the Windows Registry for keys, values, or data matching a pattern.
        
        Args:
            search_term: Term to search for (case-insensitive)
            search_in: Where to search ('keys', 'values', 'data', or 'all')
            hives: List of hives to search (e.g., ['HKLM', 'HKCU'])
            max_results: Maximum number of results to return
            
        Returns:
            Dictionary containing search results
        """
        if hives is None:
            hives = ['HKLM', 'HKCU', 'HKU', 'HKCR', 'HKCC']
        
        search_in = search_in.lower()
        results = []
        
        def search_key(hive, subkey, path):
            nonlocal results
            if len(results) >= max_results:
                return
                
            try:
                with winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ) as key:
                    # Search in key names
                    if search_in in ['keys', 'all'] and search_term.lower() in path.lower():
                        results.append({
                            'type': 'key',
                            'path': path,
                            'match': 'key_name',
                            'value': path
                        })
                    
                    # Search in value names and data
                    try:
                        i = 0
                        while len(results) < max_results:
                            try:
                                value_name, value_data, value_type = winreg.EnumValue(key, i)
                                value_name = value_name or '(Default)'
                                
                                # Search in value names
                                if search_in in ['values', 'all'] and search_term.lower() in value_name.lower():
                                    results.append({
                                        'type': 'value',
                                        'path': f"{path}\\{value_name}",
                                        'match': 'value_name',
                                        'value': value_name
                                    })
                                
                                # Search in value data
                                if search_in in ['data', 'all']:
                                    search_data = ''
                                    if isinstance(value_data, str):
                                        search_data = value_data.lower()
                                    elif isinstance(value_data, (list, tuple)):
                                        search_data = '\n'.join(map(str, value_data)).lower()
                                    elif value_data is not None:
                                        search_data = str(value_data).lower()
                                    
                                    if search_term.lower() in search_data:
                                        results.append({
                                            'type': 'value_data',
                                            'path': f"{path}\\{value_name}",
                                            'match': 'value_data',
                                            'value': str(value_data)[:200] + ('...' if len(str(value_data)) > 200 else '')
                                        })
                                
                                i += 1
                            except OSError as e:
                                if e.winerror == 259:  # No more data
                                    break
                                raise
                    except WindowsError:
                        pass  # No values
                    
                    # Recursively search subkeys
                    if len(results) < max_results:
                        try:
                            i = 0
                            while True:
                                try:
                                    subkey_name = winreg.EnumKey(key, i)
                                    subkey_path = f"{path}\\{subkey_name}" if path else subkey_name
                                    search_key(hive, f"{subkey}\\{subkey_name}" if subkey else subkey_name, subkey_path)
                                    if len(results) >= max_results:
                                        break
                                    i += 1
                                except OSError as e:
                                    if e.winerror == 259:  # No more data
                                        break
                                    raise
                        except WindowsError:
                            pass  # No subkeys
            except (WindowsError, PermissionError):
                pass  # Skip keys we can't access
        
        # Perform the search
        for hive_name in hives:
            hive = HIVE_MAP.get(hive_name.upper())
            if hive is not None:
                search_key(hive, '', hive_name)
        
        return {
            'status': 'success',
            'search_term': search_term,
            'result_count': len(results),
            'results': results[:max_results]
        }

    @mcp.tool()
    @HelpSystem.register_tool
    async def monitor_registry(
        path: str,
        action: str = 'start',  # 'start' or 'stop'
        callback_url: str = None
    ) -> Dict[str, Any]:
        """
        Monitor a registry key for changes in real-time.
        
        Args:
            path: Registry key path to monitor
            action: 'start' or 'stop' monitoring
            callback_url: Optional webhook URL to receive change notifications
            
        Returns:
            Dictionary with monitoring status
        """
        monitor_id = str(hash(path))
        
        if action.lower() == 'start':
            if monitor_id in _active_monitors:
                return {
                    'status': 'error',
                    'message': f'Already monitoring {path}',
                    'monitor_id': monitor_id
                }
            
            def callback(changes):
                if callback_url:
                    try:
                        import requests
                        requests.post(callback_url, json=changes, timeout=5)
                    except Exception as e:
                        logger.error(f"Error sending callback: {e}")
            
            monitor = RegistryMonitor(path, callback)
            monitor.start()
            _active_monitors[monitor_id] = monitor
            
            return {
                'status': 'success',
                'message': f'Started monitoring {path}',
                'monitor_id': monitor_id
            }
            
        elif action.lower() == 'stop':
            if monitor_id not in _active_monitors:
                return {
                    'status': 'error',
                    'message': f'No active monitor found for {path}',
                    'monitor_id': monitor_id
                }
            
            monitor = _active_monitors.pop(monitor_id)
            monitor.stop()
            
            return {
                'status': 'success',
                'message': f'Stopped monitoring {path}',
                'monitor_id': monitor_id
            }
        
        else:
            return {
                'status': 'error',
                'message': 'Invalid action. Use "start" or "stop"',
                'monitor_id': monitor_id
            }

    @mcp.tool()
    @HelpSystem.register_tool
    async def backup_registry(
        path: str,
        output_file: str = None,
        include_subkeys: bool = True
    ) -> Dict[str, Any]:
        """
        Create a backup of a registry key.
        
        Args:
            path: Registry key path to back up
            output_file: Output file path (defaults to key name with .reg extension)
            include_subkeys: Whether to include subkeys in the backup
            
        Returns:
            Dictionary with backup results
        """
        try:
            import tempfile
            import subprocess
            
            # Default output file if not specified
            if not output_file:
                key_name = path.split('\\')[-1] or 'registry_backup'
                output_file = f"{key_name}.reg"
            
            # Build the reg export command
            cmd = ['reg', 'export', path, output_file]
            if include_subkeys:
                cmd.append('/y')  # Suppress confirmation prompt
            
            # Execute the command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            return {
                'status': 'success',
                'path': path,
                'output_file': output_file,
                'included_subkeys': include_subkeys
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'status': 'error',
                'path': path,
                'message': f'Failed to export registry key: {e.stderr.strip()}',
                'error_code': e.returncode
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'path': path,
                'message': str(e)
            }

    @mcp.tool()
    @HelpSystem.register_tool
    async def restore_registry(
        backup_file: str,
        target_path: str = None,
        create_backup: bool = True
    ) -> Dict[str, Any]:
        """
        Restore a registry key from a backup file.
        
        Args:
            backup_file: Path to the .reg backup file
            target_path: Optional target path (if different from backup)
            create_backup: Whether to create a backup before restoring
            
        Returns:
            Dictionary with restore results
        """
        try:
            import subprocess
            import os.path
            
            if not os.path.exists(backup_file):
                return {
                    'status': 'error',
                    'message': f'Backup file not found: {backup_file}'
                }
            
            # If target path is not specified, try to extract it from the .reg file
            if not target_path:
                with open(backup_file, 'r', encoding='utf-16') as f:
                    first_line = f.readline().strip()
                    if first_line.startswith('Windows Registry Editor') and len(first_line) > 2:
                        target_path = first_line[1:-1]  # Remove brackets
            
            if not target_path:
                return {
                    'status': 'error',
                    'message': 'Target path not specified and could not be determined from backup file'
                }
            
            # Create a backup if requested
            backup_result = None
            if create_backup:
                backup_result = await backup_registry(
                    target_path,
                    f"{target_path.replace('\\', '_')}_backup.reg"
                )
            
            # Build the reg import command
            cmd = ['reg', 'import', backup_file]
            
            # Execute the command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            return {
                'status': 'success',
                'target_path': target_path,
                'backup_file': backup_file,
                'backup_created': backup_result is not None and backup_result.get('status') == 'success',
                'backup_path': backup_result.get('output_file') if backup_result else None
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'status': 'error',
                'target_path': target_path or '',
                'backup_file': backup_file,
                'message': f'Failed to import registry file: {e.stderr.strip()}',
                'error_code': e.returncode,
                'backup_created': backup_result is not None and backup_result.get('status') == 'success' if 'backup_result' in locals() else None,
                'backup_path': backup_result.get('output_file') if 'backup_result' in locals() and backup_result else None
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'target_path': target_path or '',
                'backup_file': backup_file,
                'message': str(e),
                'backup_created': backup_result is not None and backup_result.get('status') == 'success' if 'backup_result' in locals() else None,
                'backup_path': backup_result.get('output_file') if 'backup_result' in locals() and backup_result else None
            }

    @mcp.tool()
    @HelpSystem.register_tool
    async def export_registry_key(
        path: str,
        output_file: str = None,
        format: str = 'json'  # 'json' or 'reg'
    ) -> Dict[str, Any]:
        """
        Export a registry key and its subkeys to a file.
        
        Args:
            path: Registry key path to export
            output_file: Output file path (defaults to key name with .reg or .json extension)
            format: Output format ('json' or 'reg')
            
        Returns:
            Dictionary with export results
        """
        try:
            hive, subkey = _parse_registry_path(path)
            
            # Default output file if not specified
            if not output_file:
                key_name = path.split('\\')[-1] or 'registry_export'
                output_file = f"{key_name}.{format.lower()}"
            
            if format.lower() == 'reg':
                # Use reg export for .reg format
                import subprocess
                
                cmd = ['reg', 'export', path, output_file, '/y']
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
            elif format.lower() == 'json':
                # Custom JSON export
                def export_key(hive, subkey_path):
                    with winreg.OpenKey(hive, subkey_path, 0, winreg.KEY_READ) as key:
                        result = {
                            'values': {},
                            'subkeys': {}
                        }
                        
                        # Export values
                        i = 0
                        while True:
                            try:
                                value_name, value_data, value_type = winreg.EnumValue(key, i)
                                value_name = value_name or '(Default)'
                                
                                # Format the value based on type
                                if value_type == winreg.REG_MULTI_SZ:
                                    value_data = list(value_data) if value_data else []
                                elif value_type == winreg.REG_BINARY:
                                    value_data = value_data.hex()
                                
                                result['values'][value_name] = {
                                    'value': value_data,
                                    'type': VALUE_TYPES.get(value_type, f'UNKNOWN (0x{value_type:X})'),
                                    'type_code': value_type
                                }
                                i += 1
                            except OSError as e:
                                if e.winerror == 259:  # No more data
                                    break
                                raise
                        
                        # Recursively export subkeys
                        i = 0
                        while True:
                            try:
                                subkey_name = winreg.EnumKey(key, i)
                                result['subkeys'][subkey_name] = export_key(hive, f"{subkey_path}\\{subkey_name}" if subkey_path else subkey_name)
                                i += 1
                            except OSError as e:
                                if e.winerror == 259:  # No more data
                                    break
                                raise
                        
                        return result
                
                # Perform the export
                export_data = export_key(hive, subkey)
                
                # Add metadata
                export_data['_metadata'] = {
                    'exported_from': path,
                    'exported_at': time.time(),
                    'exported_by': 'database-operations-mcp',
                    'format_version': '1.0'
                }
                
                # Write to file
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            else:
                return {
                    'status': 'error',
                    'message': f'Unsupported format: {format}. Use "json" or "reg".'
                }
            
            return {
                'status': 'success',
                'path': path,
                'output_file': output_file,
                'format': format
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'path': path,
                'message': str(e)
            }
    
    logger.info("Registered Windows Registry tools")
