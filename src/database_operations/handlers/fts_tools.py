"""
Full-Text Search (FTS) tools for SQLite databases.

Provides tools for querying and managing SQLite FTS5/4 virtual tables.
"""

import sqlite3
import logging
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
from fastmcp import mcp_tool
from .help_tools import HelpSystem
from .init_tools import DATABASE_CONNECTIONS

logger = logging.getLogger(__name__)

@HelpSystem.register_tool
@mcp_tool()
async def fts_search(
    query: str,
    connection_name: str = "default",
    table: str = "fts_index",
    columns: Optional[List[str]] = None,
    limit: int = 20,
    offset: int = 0,
    highlight: bool = True,
    snippet_size: int = 3
) -> Dict[str, Any]:
    """Execute a full-text search query on an SQLite FTS table.
    
    Args:
        query: The search query (supports FTS5 query syntax)
        connection_name: Name of the database connection
        table: Name of the FTS virtual table
        columns: List of columns to search (default: all columns)
        limit: Maximum number of results to return
        offset: Number of results to skip
        highlight: Whether to include highlighted snippets
        snippet_size: Number of context words around each match
        
    Returns:
        Dictionary containing search results and metadata
    """
    if connection_name not in DATABASE_CONNECTIONS:
        return {
            'status': 'error',
            'message': f'No such connection: {connection_name}'
        }
    
    conn = DATABASE_CONNECTIONS[connection_name]['connector'].connection
    
    try:
        # Build the SELECT clause
        select_columns = ['*']
        if highlight:
            highlight_cols = columns or ['*']
            for col in highlight_cols:
                if col == '*':
                    continue
                select_columns.extend([
                    f'highlight({table}, {col}, "<b>", "</b>") as {col}_highlight',
                    f'snippet({table}, {col}, "... ", " ...", "...", {snippet_size}) as {col}_snippet'
                ])
        
        # Build the WHERE clause
        where_parts = [f"{table} MATCH ?"]
        params = [query]
        
        # Build the query
        sql = f"""
        SELECT {', '.join(select_columns)}
        FROM {table}
        WHERE {' AND '.join(where_parts)}
        ORDER BY rank
        LIMIT ? OFFSET ?
        """
        
        # Execute the query
        cursor = conn.cursor()
        cursor.execute(sql, [*params, limit, offset])
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Fetch results
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        # Get total count for pagination
        count_sql = f"""
        SELECT COUNT(*) as total
        FROM {table}
        WHERE {' AND '.join(where_parts)}
        """
        cursor.execute(count_sql, params)
        total = cursor.fetchone()[0]
        
        return {
            'status': 'success',
            'results': results,
            'total': total,
            'limit': limit,
            'offset': offset,
            'query': query
        }
        
    except sqlite3.Error as e:
        return {
            'status': 'error',
            'message': f'Error executing FTS query: {str(e)}',
            'query': query
        }

@HelpSystem.register_tool
@mcp_tool()
async def fts_tables(
    connection_name: str = "default"
) -> Dict[str, Any]:
    """List all FTS virtual tables in the database.
    
    Args:
        connection_name: Name of the database connection
        
    Returns:
        List of FTS virtual tables with their types (FTS3/4/5)
    """
    if connection_name not in DATABASE_CONNECTIONS:
        return {
            'status': 'error',
            'message': f'No such connection: {connection_name}'
        }
    
    conn = DATABASE_CONNECTIONS[connection_name]['connector'].connection
    
    try:
        cursor = conn.cursor()
        
        # Find all virtual tables that are FTS tables
        cursor.execute("""
        SELECT name, sql 
        FROM sqlite_master 
        WHERE type = 'table' 
        AND sql LIKE '%VIRTUAL TABLE%USING FTS%'
        """)
        
        tables = []
        for name, sql in cursor.fetchall():
            # Determine FTS version
            if 'USING FTS5' in sql.upper():
                version = 'FTS5'
            elif 'USING FTS4' in sql.upper():
                version = 'FTS4'
            else:
                version = 'FTS3'
                
            # Get column info
            cursor.execute(f"PRAGMA table_info({name})")
            columns = [row[1] for row in cursor.fetchall()]
            
            tables.append({
                'name': name,
                'version': version,
                'columns': columns,
                'sql': sql
            })
        
        return {
            'status': 'success',
            'tables': tables
        }
        
    except sqlite3.Error as e:
        return {
            'status': 'error',
            'message': f'Error listing FTS tables: {str(e)}'
        }

@HelpSystem.register_tool
@mcp_tool()
async def fts_suggest(
    prefix: str,
    connection_name: str = "default",
    table: str = "fts_index",
    column: str = "content",
    limit: int = 10
) -> Dict[str, Any]:
    """Get search suggestions based on a prefix (for autocomplete).
    
    Args:
        prefix: The prefix to get suggestions for
        connection_name: Name of the database connection
        table: FTS table name
        column: Column to get suggestions from
        limit: Maximum number of suggestions to return
        
    Returns:
        List of suggested completions
    """
    if connection_name not in DATABASE_CONNECTIONS:
        return {
            'status': 'error',
            'message': f'No such connection: {connection_name}'
        }
    
    conn = DATABASE_CONNECTIONS[connection_name]['connector'].connection
    
    try:
        cursor = conn.cursor()
        
        # Use FTS5 prefix search if available
        cursor.execute(f"""
        SELECT DISTINCT {column}
        FROM {table}
        WHERE {column} MATCH ?
        LIMIT ?
        """, [f"{prefix}*"])
        
        suggestions = [row[0] for row in cursor.fetchall()]
        
        return {
            'status': 'success',
            'suggestions': suggestions,
            'count': len(suggestions)
        }
        
    except sqlite3.Error as e:
        return {
            'status': 'error',
            'message': f'Error getting suggestions: {str(e)}'
        }
