"""
Windows Registry Tools

Provides tools for interacting with the Windows Registry as a hierarchical database,
including monitoring, backup, and restore functionality.
"""

import winreg
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
import json
import tempfile
import time
import threading
import queue
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from pathlib import Path
import winreg
import logging
from fastmcp import mcp_tool
from .help_tools import HelpSystem

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

def _get_value(hkey: int, subkey: str, value_name: str = None) -> Any:
    """Get a registry value with proper type handling."""
    try:
        with winreg.OpenKey(hkey, subkey, 0, winreg.KEY_READ) as key:
            if value_name is None:
                # Default value
                value, value_type = winreg.QueryValueEx(key, '')
            else:
                value, value_type = winreg.QueryValueEx(key, value_name)
            
            # Convert to appropriate Python types
            if value_type == winreg.REG_DWORD:
                return int(value)
            elif value_type == winreg.REG_QWORD:
                return int(value)
            elif value_type == winreg.REG_MULTI_SZ:
                return list(value) if value else []
            elif value_type == winreg.REG_BINARY:
                return value.hex() if value else ''
            return value
    except WindowsError as e:
        if e.winerror == 2:  # Key not found
            return None
        raise

@HelpSystem.register_tool(category='windows')
@mcp_tool()
async def get_registry_value(
    path: str,
    value_name: str = None
) -> Dict[str, Any]:
    """
    Get a value from the Windows Registry.
    
    Args:
        path: Registry key path (e.g., 'HKLM\\SOFTWARE\\Microsoft\\Windows')
        value_name: Name of the value to retrieve (defaults to default value)
        
    Returns:
        Dictionary containing the value and metadata
    """
    try:
        hive, subkey = _parse_registry_path(path)
        
        with winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ) as key:
            try:
                value, value_type = winreg.QueryValueEx(key, value_name) if value_name is not None else winreg.QueryValueEx(key, '')
                
                # Format the value based on type
                formatted_value = value
                if value_type == winreg.REG_MULTI_SZ:
                    formatted_value = list(value) if value else []
                elif value_type == winreg.REG_BINARY:
                    formatted_value = value.hex()
                
                return {
                    'status': 'success',
                    'path': path,
                    'value_name': value_name or '(Default)',
                    'value': formatted_value,
                    'type': VALUE_TYPES.get(value_type, f'UNKNOWN (0x{value_type:X})'),
                    'type_code': value_type
                }
            except FileNotFoundError:
                return {
                    'status': 'not_found',
                    'path': path,
                    'value_name': value_name or '(Default)',
                    'message': 'Value not found'
                }
    
    except Exception as e:
        return {
            'status': 'error',
            'path': path,
            'value_name': value_name or '(Default)',
            'message': str(e)
        }

@HelpSystem.register_tool(category='windows')
@mcp_tool()
async def list_registry_key(
    path: str,
    recursive: bool = False,
    max_depth: int = 1,
    current_depth: int = 0
) -> Dict[str, Any]:
    """
    List contents of a registry key.
    
    Args:
        path: Registry key path (e.g., 'HKLM\\SOFTWARE\\Microsoft')
        recursive: Whether to list subkeys recursively
        max_depth: Maximum recursion depth (if recursive=True)
        current_depth: Current recursion depth (internal use)
        
    Returns:
        Dictionary containing the key's subkeys and values
    """
    try:
        hive, subkey = _parse_registry_path(path)
        
        with winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ) as key:
            result = {
                'path': path,
                'values': {},
                'subkeys': {}
            }
            
            # Enumerate values
            try:
                i = 0
                while True:
                    try:
                        value_name, value_data, value_type = winreg.EnumValue(key, i)
                        result['values'][value_name or '(Default)'] = {
                            'value': value_data.hex() if value_type == winreg.REG_BINARY and value_data else value_data,
                            'type': VALUE_TYPES.get(value_type, f'UNKNOWN (0x{value_type:X})'),
                            'type_code': value_type
                        }
                        i += 1
                    except OSError as e:
                        if e.winerror == 259:  # No more data
                            break
                        raise
            except WindowsError:
                pass  # No values
            
            # Enumerate subkeys
            if recursive and current_depth < max_depth:
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        subkey_path = f"{path}\\{subkey_name}" if path else subkey_name
                        result['subkeys'][subkey_name] = await list_registry_key(
                            path=subkey_path,
                            recursive=recursive,
                            max_depth=max_depth,
                            current_depth=current_depth + 1
                        )
                        i += 1
                    except OSError as e:
                        if e.winerror == 259:  # No more data
                            break
                        raise
            
            return {
                'status': 'success',
                **result
            }
    
    except Exception as e:
        return {
            'status': 'error',
            'path': path,
            'message': str(e)
        }

@HelpSystem.register_tool(category='windows')
@mcp_tool()
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
        try:
            i = 0
            while True:
                try:
                    value_name, value_data, _ = winreg.EnumValue(key, i)
                    values[value_name or '(Default)'] = value_data
                    i += 1
                except OSError as e:
                    if e.winerror == 259:  # No more data
                        break
                    raise
        except WindowsError:
            pass
        return values
    
    def _find_changes(self, current: Dict) -> List[Dict]:
        """Find changes between current and last known values."""
        changes = []
        
        # Check for modified or deleted values
        for name, old_value in self.last_values.items():
            if name not in current:
                changes.append({
                    'type': 'deleted',
                    'name': name,
                    'old_value': old_value
                })
            elif current[name] != old_value:
                changes.append({
                    'type': 'modified',
                    'name': name,
                    'old_value': old_value,
                    'new_value': current[name]
                })
        
        # Check for new values
        for name, value in current.items():
            if name not in self.last_values:
                changes.append({
                    'type': 'added',
                    'name': name,
                    'new_value': value
                })
        
        return changes

# Active monitors
_active_monitors: Dict[str, RegistryMonitor] = {}

def register_tools(mcp):
    """Register all registry tools with the MCP server."""
    mcp.tool()(get_registry_value)
    mcp.tool()(list_registry_key)
    mcp.tool()(search_registry)
    mcp.tool()(monitor_registry)
    mcp.tool()(backup_registry)
    mcp.tool()(restore_registry)
    mcp.tool()(export_registry_key)
    
    logger.info("Registered Windows Registry tools")

@HelpSystem.register_tool(category='admin')
@mcp_tool()
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
    global _active_monitors
    
    if action == 'start':
        if path in _active_monitors:
            return {'status': 'error', 'message': f'Already monitoring {path}'}
        
        def on_change(change):
            logger.info(f"Registry change detected: {change}")
            if callback_url:
                try:
                    import requests
                    requests.post(callback_url, json=change, timeout=5)
                except Exception as e:
                    logger.error(f"Error sending webhook: {e}")
        
        monitor = RegistryMonitor(path, on_change)
        monitor.start()
        _active_monitors[path] = monitor
        
        return {
            'status': 'success',
            'action': 'started',
            'path': path,
            'monitor_id': id(monitor)
        }
    
    elif action == 'stop':
        if path not in _active_monitors:
            return {'status': 'error', 'message': f'No active monitor for {path}'}
        
        monitor = _active_monitors.pop(path)
        monitor.stop()
        
        return {
            'status': 'success',
            'action': 'stopped',
            'path': path,
            'monitor_id': id(monitor)
        }
    
    else:
        return {'status': 'error', 'message': 'Invalid action. Use "start" or "stop"'}

@HelpSystem.register_tool(category='admin')
@mcp_tool()
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
        # Get the key name for default output filename
        key_name = path.replace('\\', '_').replace(':', '').strip('_')
        
        if not output_file:
            output_file = f"registry_backup_{key_name}_{int(time.time())}.reg"
        
        output_path = Path(output_file)
        
        # Use reg.exe for reliable backup
        import subprocess
        
        cmd = [
            'reg', 'export', 
            '/y',  # Overwrite without prompt
            path, 
            str(output_path.absolute())
        ]
        
        if not include_subkeys:
            cmd.insert(2, '/reg:32' if 'WOW6432Node' in path else '/reg:64')
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        if result.returncode != 0:
            return {
                'status': 'error',
                'path': path,
                'message': f'Failed to export registry key: {result.stderr}'
            }
        
        return {
            'status': 'success',
            'path': path,
            'backup_file': str(output_path.absolute()),
            'size_kb': output_path.stat().st_size / 1024,
            'included_subkeys': include_subkeys
        }
    
    except Exception as e:
        return {
            'status': 'error',
            'path': path,
            'message': str(e)
        }

@HelpSystem.register_tool(category='admin')
@mcp_tool()
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
        backup_path = Path(backup_file)
        if not backup_path.exists():
            return {'status': 'error', 'message': 'Backup file not found'}
        
        # If no target path specified, try to get it from the .reg file
        if not target_path:
            with open(backup_path, 'r', encoding='utf-16') as f:
                first_line = f.readline().strip()
                if first_line.startswith('Windows Registry Editor') and '\n' in first_line:
                    first_line = first_line.split('\n')[1]
                if first_line.startswith('[') and first_line.endswith(']'):
                    target_path = first_line[1:-1]
                else:
                    return {'status': 'error', 'message': 'Could not determine target path from backup file'}
        
        # Create a backup if requested
        backup_result = None
        if create_backup:
            backup_result = await backup_registry(
                path=target_path,
                output_file=f"pre_restore_backup_{int(time.time())}.reg"
            )
        
        # Import the .reg file
        import subprocess
        
        result = subprocess.run(
            ['reg', 'import', str(backup_path.absolute())],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        if result.returncode != 0:
            return {
                'status': 'error',
                'target_path': target_path,
                'backup_file': str(backup_path),
                'message': f'Failed to import registry file: {result.stderr}',
                'backup_created': bool(backup_result and backup_result.get('status') == 'success'),
                'backup_file_created': backup_result.get('backup_file') if backup_result else None
            }
        
        return {
            'status': 'success',
            'target_path': target_path,
            'backup_file': str(backup_path),
            'backup_created': bool(backup_result and backup_result.get('status') == 'success'),
            'backup_file_created': backup_result.get('backup_file') if backup_result else None
        }
    
    except Exception as e:
        return {
            'status': 'error',
            'target_path': target_path,
            'backup_file': str(backup_path) if 'backup_path' in locals() else None,
            'message': str(e),
            'backup_created': 'backup_result' in locals() and backup_result and backup_result.get('status') == 'success',
            'backup_file_created': backup_result.get('backup_file') if 'backup_result' in locals() and backup_result else None
        }

@HelpSystem.register_tool(category='admin')
@mcp_tool()
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
        if format not in ['json', 'reg']:
            return {'status': 'error', 'message': 'Invalid format. Use "json" or "reg"'}
        
        # Get the key name for default output filename
        key_name = path.split('\\')[-1] or 'export'
        
        if not output_file:
            output_file = f"{key_name}.{format}"
        
        output_path = Path(output_file)
        
        if format == 'json':
            # Export to JSON format
            data = await list_registry_key(path, recursive=True, max_depth=100)
            if data['status'] != 'success':
                return data
                
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
            return {
                'status': 'success',
                'path': path,
                'output_file': str(output_path.absolute()),
                'format': 'json',
                'size_kb': output_path.stat().st_size / 1024
            }
            
        elif format == 'reg':
            # Export to .reg format using reg.exe for better compatibility
            import subprocess
            
            # Create a temporary .reg file
            with tempfile.NamedTemporaryFile(suffix='.reg', delete=False, mode='w') as tmp:
                tmp_reg = tmp.name
            
            try:
                # Use reg.exe to export the key
                result = subprocess.run(
                    ['reg', 'export', path, tmp_reg, '/y'],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                if result.returncode != 0:
                    return {
                        'status': 'error',
                        'path': path,
                        'message': f'Failed to export registry key: {result.stderr}'
                    }
                
                # Move the temporary file to the output location
                shutil.move(tmp_reg, output_path)
                
                return {
                    'status': 'success',
                    'path': path,
                    'output_file': str(output_path.absolute()),
                    'format': 'reg',
                    'size_kb': output_path.stat().st_size / 1024
                }
                
            except Exception as e:
                if Path(tmp_reg).exists():
                    Path(tmp_reg).unlink()
                raise
    
    except Exception as e:
        return {
            'status': 'error',
            'path': path,
            'message': str(e)
        }
