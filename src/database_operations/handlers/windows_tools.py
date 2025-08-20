"""
Windows-Specific Database Tools

Provides tools for managing Windows-specific databases and Plex Media Server.
"""

import sqlite3
import json
import logging
import os
import re
import shutil
import winreg
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
from fastmcp import mcp_tool
from .help_tools import HelpSystem

logger = logging.getLogger(__name__)

# Common Windows database locations
WINDOWS_DB_PATHS = {
    'chrome_history': [
        os.path.expandvars(r'%LOCALAPPDATA%\\Google\\Chrome\\User Data\\Default\\History'),
        os.path.expandvars(r'%USERPROFILE%\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History')
    ],
    'firefox_history': [
        os.path.expandvars(r'%APPDATA%\\Mozilla\\Firefox\\Profiles\\'),
    ],
    'edge_history': [
        os.path.expandvars(r'%LOCALAPPDATA%\\Microsoft\\Edge\\User Data\\Default\\History'),
    ],
    'outlook': [
        os.path.expandvars(r'%LOCALAPPDATA%\\Microsoft\\Outlook'),
        os.path.expandvars(r'%USERPROFILE%\\AppData\\Local\\Microsoft\\Outlook')
    ],
    'windows_thumbnails': [
        os.path.expandvars(r'%LOCALAPPDATA%\\Microsoft\\Windows\\Explorer')
    ],
    'windows_search': [
        r'C:\\ProgramData\\Microsoft\\Search\\Data\\Applications\\Windows'
    ]
}

# Plex-specific paths
PLEX_PATHS = {
    'metadata': [
        os.path.expandvars(r'%LOCALAPPDATA%\\Plex Media Server\\Metadata'),
        r'C:\\Plex\\Plex Media Server\\Metadata'
    ],
    'cache': [
        os.path.expandvars(r'%LOCALAPPDATA%\\Plex Media Server\\Cache'),
        r'C:\\Plex\\Plex Media Server\\Cache'
    ],
    'logs': [
        os.path.expandvars(r'%LOCALAPPDATA%\\Plex Media Server\\Logs'),
        r'C:\\Plex\\Plex Media Server\\Logs'
    ]
}

def _find_windows_db(db_type: str) -> Optional[Path]:
    """Find a Windows database file by type."""
    for path in WINDOWS_DB_PATHS.get(db_type, []):
        if db_type == 'firefox_history':
            # Special handling for Firefox profiles
            profiles_path = Path(path)
            if profiles_path.exists():
                for profile in profiles_path.iterdir():
                    if profile.is_dir() and 'release' in profile.name.lower():
                        db_path = profile / 'places.sqlite'
                        if db_path.exists():
                            return db_path
        else:
            db_path = Path(path)
            if db_path.exists():
                return db_path
    return None

@HelpSystem.register_tool(category='windows')
@mcp_tool()
async def list_windows_databases() -> Dict[str, Any]:
    """
    List all discoverable Windows databases with their locations and sizes.
    
    Returns:
        Dictionary containing database information
    """
    result = {}
    
    for db_type, paths in WINDOWS_DB_PATHS.items():
        found = False
        for path in paths:
            expanded_path = Path(os.path.expandvars(path))
            
            if db_type == 'firefox_history':
                # Handle Firefox profiles
                if expanded_path.exists():
                    profiles = [p for p in expanded_path.iterdir() 
                              if p.is_dir() and 'release' in p.name.lower()]
                    for profile in profiles:
                        db_path = profile / 'places.sqlite'
                        if db_path.exists():
                            result[f"{db_type}_{profile.name}"] = {
                                'path': str(db_path),
                                'size_mb': db_path.stat().st_size / (1024 * 1024),
                                'last_modified': datetime.fromtimestamp(db_path.stat().st_mtime).isoformat()
                            }
                            found = True
            else:
                # Handle regular files
                if expanded_path.exists():
                    if expanded_path.is_file():
                        result[db_type] = {
                            'path': str(expanded_path),
                            'size_mb': expanded_path.stat().st_size / (1024 * 1024),
                            'last_modified': datetime.fromtimestamp(expanded_path.stat().st_mtime).isoformat()
                        }
                        found = True
                    elif expanded_path.is_dir():
                        # For directories, list all files
                        for db_file in expanded_path.glob('*'):
                            if db_file.suffix.lower() in ('.db', '.sqlite', '.sqlite3', '.sql'):
                                result[f"{db_type}_{db_file.name}"] = {
                                    'path': str(db_file),
                                    'size_mb': db_file.stat().st_size / (1024 * 1024),
                                    'last_modified': datetime.fromtimestamp(db_file.stat().st_mtime).isoformat()
                                }
                                found = True
        
        if not found:
            result[db_type] = {
                'status': 'not_found',
                'message': f'No {db_type} database found in common locations'
            }
    
    return {'status': 'success', 'databases': result}

@HelpSystem.register_tool(category='plex')
@mcp_tool()
async def manage_plex_metadata(
    action: str = 'analyze',
    library_section: Optional[str] = None,
    item_id: Optional[int] = None,
    refresh: bool = False
) -> Dict[str, Any]:
    """
    Manage Plex metadata for media items.
    
    Args:
        action: Action to perform (analyze, refresh, delete, export)
        library_section: Optional library section ID or name
        item_id: Optional specific item ID
        refresh: Whether to refresh metadata from online sources
        
    Returns:
        Dictionary with operation results
    """
    try:
        # Find Plex database
        db_info = await find_plex_database()
        if db_info['status'] != 'success':
            return db_info
        
        db_path = db_info['path']
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cursor = conn.cursor()
        
        results = {}
        
        if action == 'analyze':
            # Get metadata statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_items,
                    COUNT(DISTINCT guid) as unique_guids,
                    COUNT(DISTINCT library_section_id) as sections_covered,
                    SUM(CASE WHEN updated_at > (strftime('%s', 'now') - 86400) THEN 1 ELSE 0 END) as updated_today
                FROM metadata_items
            """)
            
            stats = cursor.fetchone()
            results['statistics'] = {
                'total_items': stats[0],
                'unique_guids': stats[1],
                'sections_covered': stats[2],
                'updated_today': stats[3]
            }
            
            # Get metadata by type
            cursor.execute("""
                SELECT 
                    metadata_type,
                    COUNT(*) as count
                FROM metadata_items
                GROUP BY metadata_type
                ORDER BY count DESC
            """)
            
            results['by_type'] = [
                {'type': row[0], 'count': row[1]} 
                for row in cursor.fetchall()
            ]
            
            # Get largest metadata items
            cursor.execute("""
                SELECT 
                    title,
                    LENGTH(metadata) as metadata_size,
                    updated_at
                FROM metadata_items
                ORDER BY metadata_size DESC
                LIMIT 10
            """)
            
            results['largest_items'] = [
                {'title': row[0], 'size_kb': row[1]/1024, 'updated': row[2]}
                for row in cursor.fetchall()
            ]
        
        elif action == 'export':
            # Export metadata to JSON
            output_dir = Path("plex_metadata_export")
            output_dir.mkdir(exist_ok=True)
            
            # Export metadata items
            cursor.execute("SELECT * FROM metadata_items")
            columns = [desc[0] for desc in cursor.description]
            items = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            output_file = output_dir / 'metadata_items.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(items, f, indent=2, ensure_ascii=False)
            
            results['export'] = {
                'file': str(output_file.absolute()),
                'items_exported': len(items),
                'size_mb': output_file.stat().st_size / (1024 * 1024)
            }
        
        return {
            'status': 'success',
            'action': action,
            **results
        }
    
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'action': action
        }
    
    finally:
        if 'conn' in locals():
            conn.close()

@HelpSystem.register_tool(category='windows')
@mcp_tool()
async def query_windows_database(
    db_type: str,
    query: str,
    params: Optional[dict] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Execute a query against a Windows database.
    
    Args:
        db_type: Type of database (chrome_history, firefox_history, etc.)
        query: SQL query to execute
        params: Optional query parameters
        limit: Maximum number of results to return
        
    Returns:
        Query results and metadata
    """
    try:
        # Find the database
        db_path = _find_windows_db(db_type)
        if not db_path:
            return {
                'status': 'error',
                'message': f'Could not find {db_type} database'
            }
        
        # Connect to the database
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Execute the query with parameters
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Fetch results with limit
        rows = cursor.fetchmany(limit)
        results = [dict(zip(columns, row)) for row in rows]
        
        # Get total count if this was a SELECT query
        total_count = len(rows)
        if query.strip().lower().startswith('select'):
            count_query = f"SELECT COUNT(*) FROM ({query}) AS subquery"
            if params:
                cursor.execute(count_query, params)
            else:
                cursor.execute(count_query)
            total_count = cursor.fetchone()[0]
        
        return {
            'status': 'success',
            'database': str(db_path),
            'query': query,
            'parameters': params or {},
            'result_count': len(results),
            'total_count': total_count,
            'results': results
        }
    
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'database': str(db_path) if 'db_path' in locals() else None,
            'query': query
        }
    
    finally:
        if 'conn' in locals():
            conn.close()

@HelpSystem.register_tool(category='windows')
@mcp_tool()
async def clean_windows_database(
    db_type: str,
    action: str = 'vacuum',
    backup: bool = True
) -> Dict[str, Any]:
    """
    Clean and optimize a Windows database.
    
    Args:
        db_type: Type of database to clean
        action: Action to perform (vacuum, reindex, analyze)
        backup: Whether to create a backup before cleaning
        
    Returns:
        Dictionary with cleaning results
    """
    try:
        # Find the database
        db_path = _find_windows_db(db_type)
        if not db_path:
            return {
                'status': 'error',
                'message': f'Could not find {db_type} database'
            }
        
        # Create backup if requested
        backup_path = None
        if backup:
            backup_dir = Path('db_backups')
            backup_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = backup_dir / f"{db_path.stem}_{timestamp}.bak"
            shutil.copy2(db_path, backup_path)
        
        # Connect to the database
        conn = sqlite3.connect(f"file:{db_path}", uri=True)
        cursor = conn.cursor()
        
        # Get original size
        original_size = db_path.stat().st_size
        
        # Perform the requested action
        if action == 'vacuum':
            cursor.execute("VACUUM")
        elif action == 'reindex':
            cursor.execute("REINDEX")
        elif action == 'analyze':
            cursor.execute("ANALYZE")
        else:
            return {
                'status': 'error',
                'message': f'Unknown action: {action}'
            }
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        
        # Get new size
        new_size = db_path.stat().st_size
        
        return {
            'status': 'success',
            'action': action,
            'database': str(db_path),
            'original_size_mb': original_size / (1024 * 1024),
            'new_size_mb': new_size / (1024 * 1024),
            'space_saved_mb': (original_size - new_size) / (1024 * 1024),
            'backup_created': backup_path is not None,
            'backup_path': str(backup_path) if backup_path else None
        }
    
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'action': action,
            'backup_created': 'backup_path' in locals() and backup_path is not None,
            'backup_path': str(backup_path) if 'backup_path' in locals() else None
        }
    
    finally:
        if 'conn' in locals():
            conn.close()
