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
from typing import Dict, List, Optional, Any, Tuple, Union
from fastmcp import mcp_tool
from .help_tools import HelpSystem
from .init_tools import DATABASE_CONNECTIONS

logger = logging.getLogger(__name__)

def _get_fts_db_path(library_path: Union[str, Path]) -> Path:
    """Get the path to the full-text search database."""
    lib_path = Path(library_path)
    return lib_path / 'full-text-search.db'

@HelpSystem.register_tool(category='calibre')
@mcp_tool()
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
    if not search_fields:
        search_fields = ['title', 'authors', 'tags', 'comments']
    
    # Convert library path to Path object and find metadata.db
    lib_path = Path(library_path)
    db_path = lib_path / 'metadata.db'
    
    if not db_path.exists():
        return {
            'status': 'error',
            'message': f'No metadata.db found in {library_path}'
        }
    
    try:
        # Connect to the Calibre database
        conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
        conn.row_factory = sqlite3.Row
        
        # Build the search conditions
        conditions = []
        params = []
        
        # Handle different search fields
        if 'title' in search_fields:
            conditions.append("books.title LIKE ?")
            params.append(f'%{query}%')
            
        if 'authors' in search_fields:
            conditions.append("""
                EXISTS (
                    SELECT 1 FROM authors, books_authors_link 
                    WHERE authors.id = books_authors_link.author 
                    AND books_authors_link.book = books.id
                    AND authors.name LIKE ?
                )""")
            params.append(f'%{query}%')
            
        if 'tags' in search_fields:
            conditions.append("""
                EXISTS (
                    SELECT 1 FROM tags, books_tags_link 
                    WHERE tags.id = books_tags_link.tag 
                    AND books_tags_link.book = books.id
                    AND tags.name LIKE ?
                )""")
            params.append(f'%{query}%')
            
        if 'comments' in search_fields:
            conditions.append("comments.text LIKE ?")
            params.append(f'%{query}%')
            
        if 'series' in search_fields:
            conditions.append("""
                series.name LIKE ? AND
                books.series_index IS NOT NULL""")
            params.append(f'%{query}%')
            
        if 'publisher' in search_fields:
            conditions.append("publishers.name LIKE ?")
            params.append(f'%{query}%')
        
        if not conditions:
            return {
                'status': 'error',
                'message': 'No valid search fields specified'
            }
        
        where_clause = ' OR '.join(conditions)
        
        # Build the query
        sql = f"""
        SELECT 
            books.id,
            books.title,
            (SELECT GROUP_CONCAT(authors.name, ', ') 
             FROM authors, books_authors_link 
             WHERE authors.id = books_authors_link.author 
             AND books_authors_link.book = books.id) as authors,
            (SELECT GROUP_CONCAT(tags.name, ', ') 
             FROM tags, books_tags_link 
             WHERE tags.id = books_tags_link.tag 
             AND books_tags_link.book = books.id) as tags,
            series.name as series,
            books.series_index,
            publishers.name as publisher,
            books.pubdate,
            comments.text as comments,
            data.format,
            data.name as filename
        FROM books
        LEFT JOIN comments ON comments.book = books.id
        LEFT JOIN books_series_link ON books_series_link.book = books.id
        LEFT JOIN series ON series.id = books_series_link.series
        LEFT JOIN books_publishers_link ON books_publishers_link.book = books.id
        LEFT JOIN publishers ON publishers.id = books_publishers_link.publisher
        LEFT JOIN data ON data.book = books.id
        WHERE {where_clause}
        GROUP BY books.id
        ORDER BY books.sort
        LIMIT ? OFFSET ?
        """
        
        # Add limit and offset to params
        params.extend([limit, offset])
        
        # Execute the query
        cursor = conn.cursor()
        cursor.execute(sql, params)
        
        # Get total count for pagination
        count_sql = f"""
        SELECT COUNT(DISTINCT books.id) as total
        FROM books
        LEFT JOIN comments ON comments.book = books.id
        LEFT JOIN books_series_link ON books_series_link.book = books.id
        LEFT JOIN series ON series.id = books_series_link.series
        LEFT JOIN books_publishers_link ON books_publishers_link.book = books.id
        LEFT JOIN publishers ON publishers.id = books_publishers_link.publisher
        WHERE {where_clause}
        """
        
        cursor.execute(count_sql, params[:-2])  # Exclude limit and offset
        total = cursor.fetchone()[0]
        
        # Process results
        results = []
        for row in cursor.fetchall():
            book = dict(row)
            
            # Format the path to the book files
            author = book.get('authors', 'Unknown').split(',')[0].strip()
            title = book.get('title', 'Unknown')
            book_path = lib_path / author / title / f"{title} - {author}.{book['format']}"
            
            book['path'] = str(book_path)
            
            # Add highlights if requested
            if highlight:
                book['highlights'] = {}
                for field in search_fields:
                    if field in ['title', 'comments'] and book.get(field):
                        book['highlights'][field] = book[field].replace(
                            query, f'<b>{query}</b>'
                        )
            
            results.append(book)
        
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
            'message': f'Database error: {str(e)}'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error searching Calibre library: {str(e)}'
        }
    finally:
        conn.close()

@HelpSystem.register_tool(category='calibre')
@mcp_tool()
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
            'message': f'No metadata.db found in {library_path}'
        }
    
    try:
        conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get book details
        cursor.execute("""
        SELECT 
            books.*,
            comments.text as comments,
            series.name as series_name,
            series.id as series_id,
            publishers.name as publisher_name,
            publishers.id as publisher_id,
            (SELECT GROUP_CONCAT(authors.name, ' & ') 
             FROM authors, books_authors_link 
             WHERE authors.id = books_authors_link.author 
             AND books_authors_link.book = books.id) as authors,
            (SELECT GROUP_CONCAT(authors.id) 
             FROM authors, books_authors_link 
             WHERE authors.id = books_authors_link.author 
             AND books_authors_link.book = books.id) as author_ids
        FROM books
        LEFT JOIN comments ON comments.book = books.id
        LEFT JOIN books_series_link ON books_series_link.book = books.id
        LEFT JOIN series ON series.id = books_series_link.series
        LEFT JOIN books_publishers_link ON books_publishers_link.book = books.id
        LEFT JOIN publishers ON publishers.id = books_publishers_link.publisher
        WHERE books.id = ?
        """, (book_id,))
        
        book = dict(cursor.fetchone())
        
        if not book:
            return {
                'status': 'error',
                'message': f'Book with ID {book_id} not found'
            }
        
        # Get formats
        cursor.execute("""
        SELECT format, name as filename, uncompressed_size as size
        FROM data
        WHERE book = ?
        """, (book_id,))
        
        book['formats'] = [dict(row) for row in cursor.fetchall()]
        
        # Get tags
        cursor.execute("""
        SELECT tags.name, tags.id
        FROM tags, books_tags_link
        WHERE tags.id = books_tags_link.tag
        AND books_tags_link.book = ?
        """, (book_id,))
        
        book['tags'] = [dict(row) for row in cursor.fetchall()]
        
        # Get identifiers (ISBN, etc.)
        cursor.execute("""
        SELECT type, val
        FROM identifiers
        WHERE book = ?
        """, (book_id,))
        
        book['identifiers'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Get custom columns
        cursor.execute("""
        SELECT label, name
        FROM custom_columns
        """)
        
        custom_columns = cursor.fetchall()
        book['custom_columns'] = {}
        
        for col in custom_columns:
            label, name = col
            cursor.execute(f"""
            SELECT value
            FROM custom_column_{label}
            WHERE book = ?
            """, (book_id,))
            
            result = cursor.fetchone()
            if result:
                book['custom_columns'][name] = result[0]
        
        # Generate file paths
        author = book.get('authors', 'Unknown').split('&')[0].strip()
        title = book.get('title', 'Unknown')
        
        book['files'] = {}
        for fmt in book['formats']:
            book['files'][fmt['format']] = str(
                lib_path / author / title / f"{title} - {author}.{fmt['format']}"
            )
        
        # Get cover path
        book['cover_path'] = str(lib_path / author / title / 'cover.jpg')
        
        return {
            'status': 'success',
            'book': book
        }
        
    except sqlite3.Error as e:
        return {
            'status': 'error',
            'message': f'Database error: {str(e)}'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error getting book details: {str(e)}'
        }
    finally:
        conn.close()
