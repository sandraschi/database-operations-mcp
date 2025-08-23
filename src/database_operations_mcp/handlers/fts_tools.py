"""
Full-Text Search (FTS) tools for SQLite databases.

Provides tools for querying and managing SQLite FTS5/4 virtual tables.
"""

import sqlite3
import logging
from typing import Dict, List, Optional, Any
from fastmcp import FastMCP
from .help_tools import HelpSystem

logger = logging.getLogger(__name__)

# This will be set when the tools are registered
DATABASE_CONNECTIONS = None

def register_tools(mcp: FastMCP) -> None:
    """Register FTS tools with the MCP server.
    
    Args:
        mcp: The FastMCP instance to register tools with
    """
    global DATABASE_CONNECTIONS
    from . import init_tools
    DATABASE_CONNECTIONS = init_tools.DATABASE_CONNECTIONS
    
    @mcp.tool()
    @HelpSystem.register_tool
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
    
        try:
            conn = DATABASE_CONNECTIONS[connection_name]['connector'].connection
            
            # Build the SELECT clause
            select_columns = ['*']
            if highlight and columns:
                for col in columns:
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
            logger.exception("Error executing FTS query")
            return {
                'status': 'error',
                'message': f'Error executing FTS query: {str(e)}',
                'query': query
            }
    
    @mcp.tool()
    @HelpSystem.register_tool
    async def fts_tables(
        self,
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
            
        try:
            conn = DATABASE_CONNECTIONS[connection_name]['connector'].connection
            cursor = conn.cursor()
            
            # Query to find all FTS virtual tables
            cursor.execute("""
                SELECT name, sql 
                FROM sqlite_master 
                WHERE type = 'table' 
                AND (sql LIKE '%USING FTS%' OR sql LIKE '%USING FTS3%' OR 
                     sql LIKE '%USING FTS4%' OR sql LIKE '%USING FTS5%')
            """)
            
            tables = []
            for name, sql in cursor.fetchall():
                # Determine FTS version
                if 'USING FTS5' in sql.upper():
                    fts_type = 'FTS5'
                elif 'USING FTS4' in sql.upper():
                    fts_type = 'FTS4'
                elif 'USING FTS3' in sql.upper():
                    fts_type = 'FTS3'
                else:
                    fts_type = 'FTS'  # Default/unknown
                
                tables.append({
                    'name': name,
                    'type': fts_type,
                    'sql': sql
                })
            
            return {
                'status': 'success',
                'tables': tables
            }
            
        except sqlite3.Error as e:
            logger.exception("Error listing FTS tables")
            return {
                'status': 'error',
                'message': f'Error listing FTS tables: {str(e)}'
            }
    
    @mcp.tool()
    @HelpSystem.register_tool
    async def fts_suggest(
        self,
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
        
        try:
            conn = DATABASE_CONNECTIONS[connection_name]['connector'].connection
            cursor = conn.cursor()
            
            # Use FTS5 prefix search if available, otherwise use LIKE
            cursor.execute(f"""
                SELECT DISTINCT {column}
                FROM {table}
                WHERE {column} LIKE ? || '%'
                LIMIT ?
            """, (prefix, limit))
            
            suggestions = [row[0] for row in cursor.fetchall()]
            
            return {
                'status': 'success',
                'suggestions': suggestions,
                'count': len(suggestions)
            }
            
        except sqlite3.Error as e:
            logger.exception("Error getting FTS suggestions")
            return {
                'status': 'error',
                'message': f'Error getting suggestions: {str(e)}'
            }
    
    return mcp
