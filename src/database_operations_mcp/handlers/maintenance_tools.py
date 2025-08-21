"""
Database Maintenance Tools

Provides tools for maintaining and repairing database integrity,
optimizing performance, and managing database files.
"""

import sqlite3
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from fastmcp import mcp_tool
from .help_tools import HelpSystem
from .init_tools import DATABASE_CONNECTIONS

logger = logging.getLogger(__name__)

@HelpSystem.register_tool(category='admin')
@mcp_tool()
async def optimize_database(
    connection_name: str = None,
    vacuum: bool = True,
    analyze: bool = True,
    reindex: bool = False,
    backup: bool = True,
    backup_path: str = None
) -> Dict[str, Any]:
    """Optimize and maintain a database.
    
    Args:
        connection_name: Name of the database connection to optimize
        vacuum: Whether to run VACUUM to rebuild the database file
        analyze: Whether to update query planner statistics
        reindex: Whether to rebuild all indexes
        backup: Whether to create a backup before optimization
        backup_path: Custom backup path (defaults to same directory with .bak extension)
        
    Returns:
        Dictionary with optimization results and statistics
    """
    if not connection_name and not DATABASE_CONNECTIONS:
        return {
            'status': 'error',
            'message': 'No active database connections'
        }
    
    results = {}
    
    # If no specific connection, optimize all
    connections = [connection_name] if connection_name else list(DATABASE_CONNECTIONS.keys())
    
    for conn_name in connections:
        if conn_name not in DATABASE_CONNECTIONS:
            results[conn_name] = {'status': 'error', 'message': 'Connection not found'}
            continue
            
        conn_info = DATABASE_CONNECTIONS[conn_name]
        db_path = conn_info.get('path')
        
        if not db_path:
            results[conn_name] = {'status': 'error', 'message': 'No file path for this connection'}
            continue
            
        try:
            # Create backup if requested
            backup_file = None
            if backup and db_path:
                backup_file = _create_backup(db_path, backup_path)
            
            # Connect to the database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Run maintenance commands
            stats = {
                'original_size': Path(db_path).stat().st_size if db_path else None,
                'operations': []
            }
            
            if analyze:
                cursor.execute("ANALYZE")
                stats['operations'].append('analyze')
            
            if reindex:
                cursor.execute("REINDEX")
                stats['operations'].append('reindex')
            
            if vacuum:
                cursor.execute("VACUUM")
                stats['operations'].append('vacuum')
            
            # Get final size
            if db_path:
                stats['final_size'] = Path(db_path).stat().st_size
                if 'original_size' in stats and stats['original_size']:
                    stats['space_saved'] = stats['original_size'] - stats['final_size']
            
            conn.close()
            
            results[conn_name] = {
                'status': 'success',
                'backup': str(backup_file) if backup_file else None,
                **stats
            }
            
        except Exception as e:
            results[conn_name] = {
                'status': 'error',
                'message': str(e),
                'backup': str(backup_file) if 'backup_file' in locals() else None
            }
    
    return {
        'status': 'partial' if any(r.get('status') == 'error' for r in results.values()) else 'success',
        'results': results
    }

def _create_backup(db_path: str, custom_path: str = None) -> Path:
    """Create a timestamped backup of a database file."""
    db_path = Path(db_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if custom_path:
        backup_dir = Path(custom_path).parent
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_file = Path(custom_path).with_suffix(f'.{timestamp}.bak')
    else:
        backup_file = db_path.parent / f"{db_path.stem}_{timestamp}.bak"
    
    shutil.copy2(db_path, backup_file)
    return backup_file

@HelpSystem.register_tool(category='admin')
@mcp_tool()
async def check_database_integrity(
    connection_name: str = None,
    quick: bool = False
) -> Dict[str, Any]:
    """Check the integrity of a database.
    
    Args:
        connection_name: Name of the database connection to check
        quick: If True, performs a quick check (less thorough)
        
    Returns:
        Dictionary with integrity check results
    """
    if not connection_name and not DATABASE_CONNECTIONS:
        return {
            'status': 'error',
            'message': 'No active database connections'
        }
    
    results = {}
    connections = [connection_name] if connection_name else list(DATABASE_CONNECTIONS.keys())
    
    for conn_name in connections:
        if conn_name not in DATABASE_CONNECTIONS:
            results[conn_name] = {'status': 'error', 'message': 'Connection not found'}
            continue
            
        conn_info = DATABASE_CONNECTIONS[conn_name]
        
        try:
            conn = conn_info['connector'].connection
            cursor = conn.cursor()
            
            # Run integrity check
            if quick:
                cursor.execute("PRAGMA quick_check")
            else:
                cursor.execute("PRAGMA integrity_check")
            
            result = cursor.fetchall()
            is_ok = len(result) == 1 and result[0][0].lower() == 'ok'
            
            # Get additional stats
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            
            results[conn_name] = {
                'status': 'success' if is_ok else 'warning',
                'integrity_ok': is_ok,
                'details': result,
                'page_count': page_count,
                'page_size': page_size,
                'total_size': page_count * page_size if page_count and page_size else None
            }
            
        except Exception as e:
            results[conn_name] = {
                'status': 'error',
                'message': str(e)
            }
    
    return {
        'status': 'success',
        'results': results
    }

@HelpSystem.register_tool(category='calibre')
@mcp_tool()
async def repair_calibre_library(
    library_path: str,
    rebuild_fts: bool = True,
    rebuild_metadata: bool = False,
    backup: bool = True
) -> Dict[str, Any]:
    """Repair common issues in a Calibre library.
    
    Args:
        library_path: Path to the Calibre library
        rebuild_fts: Whether to rebuild the full-text search index
        rebuild_metadata: Whether to rebuild metadata.opf files
        backup: Whether to create a backup before making changes
        
    Returns:
        Dictionary with repair results
    """
    lib_path = Path(library_path)
    metadata_db = lib_path / 'metadata.db'
    fts_db = lib_path / 'full-text-search.db'
    
    if not metadata_db.exists():
        return {
            'status': 'error',
            'message': 'Not a valid Calibre library (metadata.db not found)'
        }
    
    results = {
        'backup': None,
        'operations': [],
        'warnings': []
    }
    
    try:
        # Create backup if requested
        if backup:
            backup_file = _create_backup(metadata_db)
            results['backup'] = str(backup_file)
        
        # Check database integrity
        integrity = await check_database_integrity()
        if not integrity.get('status') == 'success':
            results['warnings'].append('Database integrity check failed')
        
        # Rebuild FTS if requested
        if rebuild_fts and fts_db.exists():
            try:
                conn = sqlite3.connect(f'file:{fts_db}?mode=rw', uri=True)
                cursor = conn.cursor()
                
                # Get list of FTS tables
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type = 'table' AND name LIKE 'fts%'
                """)
                
                for (table,) in cursor.fetchall():
                    cursor.execute(f"INSERT INTO {table}({table}) VALUES('rebuild')")
                
                conn.commit()
                conn.close()
                results['operations'].append('rebuilt_fts_index')
                
            except Exception as e:
                results['warnings'].append(f'Failed to rebuild FTS: {str(e)}')
        
        # Rebuild metadata.opf files if requested
        if rebuild_metadata:
            # This would require calibredb command-line tool
            results['warnings'].append('Rebuilding metadata.opf files requires calibredb CLI')
        
        # Run VACUUM on the main database
        optimize = await optimize_database(backup=False)
        if optimize.get('status') == 'success':
            results['operations'].append('optimized_database')
        
        return {
            'status': 'success',
            **results
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            **results
        }

@HelpSystem.register_tool(category='calibre')
@mcp_tool()
async def export_calibre_library(
    library_path: str,
    output_path: str,
    format: str = 'csv',
    include_metadata: bool = True,
    include_content: bool = False
) -> Dict[str, Any]:
    """Export Calibre library data to a file.
    
    Args:
        library_path: Path to the Calibre library
        output_path: Path to save the export file
        format: Export format (csv, json, sqlite)
        include_metadata: Whether to include book metadata
        include_content: Whether to include book content (for full-text search)
        
    Returns:
        Dictionary with export results
    """
    # Implementation would go here
    return {
        'status': 'not_implemented',
        'message': 'Export functionality is not yet implemented'
    }
