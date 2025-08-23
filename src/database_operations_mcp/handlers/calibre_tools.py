"""
Calibre Library Search Tools

Provides specialized search functionality for Calibre ebook libraries,
including full-text search within book content.
"""

import sqlite3
import logging
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union, TypeVar, Callable
from .help_tools import HelpSystem
from .init_tools import DATABASE_CONNECTIONS

# Type variable for function type
F = TypeVar('F', bound=Callable[..., Any])

logger = logging.getLogger(__name__)

def _get_fts_db_path(library_path: Union[str, Path]) -> Path:
    """Get the path to the full-text search database."""
    lib_path = Path(library_path)
    return lib_path / 'full-text-search.db'

def register_tools(mcp: 'FastMCP') -> None:
    """Register all Calibre tools with the MCP server.
    
    Args:
        mcp: The FastMCP instance to register tools with
    """
    @mcp.tool()
    @HelpSystem.register_tool
    async def search_calibre_library(
        query: str,
        library_path: str,
        search_fields: Optional[List[str]] = None,
        limit: int = 20,
        offset: int = 0,
        highlight: bool = True
    ) -> Dict[str, Any]:
        """
        Search for text in a Calibre library.
        
        Args:
            query: The search query (supports FTS5 syntax)
            library_path: Path to the Calibre library directory
            search_fields: Fields to search in ['title', 'authors', 'tags', 'comments', 'series', 'publisher']
            limit: Maximum number of results to return
            offset: Number of results to skip (for pagination)
            highlight: Whether to include highlighted snippets
            
        Returns:
            Dictionary containing search results and metadata
        """
        if search_fields is None:
            search_fields = ['title', 'authors', 'tags', 'comments', 'series', 'publisher']
            
        # Convert library path to Path object and find metadata.db
        lib_path = Path(library_path)
        db_path = lib_path / 'metadata.db'
        
        if not db_path.exists():
            return {
                'status': 'error',
                'message': f'Calibre library not found at {db_path}'
            }
            
        try:
            # Connect to the database
            conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Build the query
            fields = []
            params = []
            
            # Search in specified fields
            for field in search_fields:
                if field == 'title':
                    fields.append("b.title LIKE ?")
                    params.append(f'%{query}%')
                elif field == 'authors':
                    fields.append("a.name LIKE ?")
                    params.append(f'%{query}%')
                elif field == 'tags':
                    fields.append("t.name LIKE ?")
                    params.append(f'%{query}%')
                elif field == 'comments':
                    fields.append("b.comments LIKE ?")
                    params.append(f'%{query}%')
                elif field == 'series':
                    fields.append("s.name LIKE ?")
                    params.append(f'%{query}%')
                elif field == 'publisher':
                    fields.append("b.publisher LIKE ?")
                    params.append(f'%{query}%')
            
            # Build the SQL query
            sql = """
            SELECT DISTINCT b.id, b.title, b.sort, b.timestamp, b.pubdate, b.series_index,
                   b.author_sort, b.isbn, b.lccn, b.path, b.flags, b.uuid,
                   b.has_cover, b.last_modified
            FROM books b
            LEFT JOIN books_authors_link bal ON b.id = bal.book
            LEFT JOIN authors a ON bal.author = a.id
            LEFT JOIN books_tags_link btl ON b.id = btl.book
            LEFT JOIN tags t ON btl.tag = t.id
            LEFT JOIN books_series_link bsl ON b.id = bsl.book
            LEFT JOIN series s ON bsl.series = s.id
            """
            
            if fields:
                sql += " WHERE (" + " OR ".join(fields) + ")"
            
            # Add ordering and limiting
            sql += " ORDER BY b.sort"
            sql += f" LIMIT {limit} OFFSET {offset}"
            
            # Execute the query
            cursor.execute(sql, params)
            results = [dict(row) for row in cursor.fetchall()]
            
            # Get total count for pagination
            count_sql = "SELECT COUNT(DISTINCT b.id) as count FROM books b"
            if fields:
                count_sql += " LEFT JOIN books_authors_link bal ON b.id = bal.book"
                count_sql += " LEFT JOIN authors a ON bal.author = a.id"
                count_sql += " LEFT JOIN books_tags_link btl ON b.id = btl.book"
                count_sql += " LEFT JOIN tags t ON btl.tag = t.id"
                count_sql += " LEFT JOIN books_series_link bsl ON b.id = bsl.book"
                count_sql += " LEFT JOIN series s ON bsl.series = s.id"
                count_sql += " WHERE (" + " OR ".join(fields) + ")"
            
            cursor.execute(count_sql, params)
            total_count = cursor.fetchone()[0]
            
            # Close the connection
            conn.close()
            
            # Format the results
            formatted_results = []
            for result in results:
                # Add the book path
                result['path'] = str(lib_path / result['path'])
                
                # Add the cover path if it exists
                cover_path = lib_path / result['path'] / 'cover.jpg'
                if cover_path.exists():
                    result['cover_path'] = str(cover_path)
                
                formatted_results.append(result)
            
            return {
                'status': 'success',
                'query': query,
                'results': formatted_results,
                'total_count': total_count,
                'offset': offset,
                'limit': limit
            }
            
        except Exception as e:
            logger.error(f"Error searching Calibre library: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error searching Calibre library: {str(e)}'
            }

    @mcp.tool()
    @HelpSystem.register_tool
    async def get_calibre_book(
        book_id: int,
        library_path: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific book in the Calibre library.
        
        Args:
            book_id: The ID of the book to retrieve
            library_path: Path to the Calibre library directory
            
        Returns:
            Dictionary containing book details
        """
        lib_path = Path(library_path)
        db_path = lib_path / 'metadata.db'
        
        if not db_path.exists():
            return {
                'status': 'error',
                'message': f'Calibre library not found at {db_path}'
            }
            
        try:
            # Connect to the database
            conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get book details
            cursor.execute("""
                SELECT * FROM books WHERE id = ?
            """, (book_id,))
            
            book = cursor.fetchone()
            
            if not book:
                return {
                    'status': 'error',
                    'message': f'Book with ID {book_id} not found'
                }
            
            # Convert to dict
            book_data = dict(book)
            
            # Get authors
            cursor.execute("""
                SELECT a.id, a.name, a.sort, a.link
                FROM authors a
                JOIN books_authors_link bal ON a.id = bal.author
                WHERE bal.book = ?
                ORDER BY bal.id
            """, (book_id,))
            
            authors = [dict(row) for row in cursor.fetchall()]
            book_data['authors'] = authors
            
            # Get tags
            cursor.execute("""
                SELECT t.id, t.name
                FROM tags t
                JOIN books_tags_link btl ON t.id = btl.tag
                WHERE btl.book = ?
                ORDER BY t.name
            """, (book_id,))
            
            tags = [dict(row) for row in cursor.fetchall()]
            book_data['tags'] = tags
            
            # Get series
            cursor.execute("""
                SELECT s.id, s.name, bsl.series_index
                FROM series s
                JOIN books_series_link bsl ON s.id = bsl.series
                WHERE bsl.book = ?
            """, (book_id,))
            
            series = cursor.fetchone()
            if series:
                book_data['series'] = dict(series)
            
            # Get formats
            cursor.execute("""
                SELECT format, name, uncompressed_size
                FROM data
                WHERE book = ?
            """, (book_id,))
            
            formats = [dict(row) for row in cursor.fetchall()]
            book_data['formats'] = formats
            
            # Get identifiers
            cursor.execute("""
                SELECT type, val
                FROM identifiers
                WHERE book = ?
            """, (book_id,))
            
            identifiers = {row['type']: row['val'] for row in cursor.fetchall()}
            book_data['identifiers'] = identifiers
            
            # Get comments
            cursor.execute("""
                SELECT text FROM comments WHERE book = ?
            """, (book_id,))
            
            comments = cursor.fetchone()
            if comments:
                book_data['comments'] = comments[0]
            
            # Get custom columns
            cursor.execute("""
                SELECT label, name, datatype, is_multiple, normalized,
                       display, is_custom, is_multiple2
                FROM custom_columns
            """)
            
            custom_columns = {}
            for row in cursor.fetchall():
                col = dict(row)
                cursor.execute(f"""
                    SELECT value FROM books_custom_column_{col['id']}_link
                    WHERE book = ?
                """, (book_id,))
                
                values = [r[0] for r in cursor.fetchall()]
                
                if col['datatype'] in ('int', 'float'):
                    values = [float(v) if '.' in v else int(v) for v in values]
                
                if not col['is_multiple'] and values:
                    values = values[0]
                
                custom_columns[col['label']] = values
            
            book_data['custom_columns'] = custom_columns
            
            # Add the book path
            book_path = lib_path / book_data['path']
            book_data['path'] = str(book_path)
            
            # Add the cover path if it exists
            cover_path = book_path / 'cover.jpg'
            if cover_path.exists():
                book_data['cover_path'] = str(cover_path)
            
            # Add the format file paths
            for fmt in book_data['formats']:
                fmt_path = book_path / f"{book_id}.{fmt['format'].lower()}"
                if fmt_path.exists():
                    fmt['path'] = str(fmt_path)
            
            # Close the connection
            conn.close()
            
            return {
                'status': 'success',
                'book': book_data
            }
            
        except Exception as e:
            logger.error(f"Error getting Calibre book details: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error getting book details: {str(e)}'
            }
    
    logger.info("Registered Calibre tools")
