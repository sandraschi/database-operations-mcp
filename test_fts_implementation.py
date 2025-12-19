#!/usr/bin/env python3
"""Test the Calibre FTS database search implementation."""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database_operations_mcp.tools.media_library import _search_calibre_fts_db

async def test_fts_search():
    """Test FTS search on the user's Calibre library."""
    library_path = r'L:\Multimedia Files\Written Word\Calibre-Bibliothek Deutsch'
    search_queries = ['python', 'programmierung', 'code', 'algorithmus']

    for search_query in search_queries:
        print(f"\n{'='*60}")
        print(f"Testing FTS search on: {library_path}")
        print(f"Search query: '{search_query}'")
        print(f"{'='*60}")

        result = await _search_calibre_fts_db(library_path, search_query, include_metadata=True)

        print(f"Success: {result['success']}")
        if result['success']:
            print(f"Found {result['count']} results")
            print(f"FTS database: {result['fts_db_path']}")

            for i, book in enumerate(result['results'][:3]):  # Show first 3 results
                print(f"\nResult {i+1}:")
                print(f"  Book ID: {book['book_id']}")
                print(f"  Title: {book.get('title', 'Unknown')}")
                print(f"  Author: {book.get('author', 'Unknown')}")
                print(f"  Format: {book['format']}")
                print(f"  Text size: {book['text_size']}")
                preview = book['text_preview']
                # Find the search term in preview and highlight it
                if search_query.lower() in preview.lower():
                    idx = preview.lower().find(search_query.lower())
                    start = max(0, idx - 50)
                    end = min(len(preview), idx + len(search_query) + 50)
                    highlighted = preview[start:end]
                    print(f"  Preview: ...{highlighted}...")
                else:
                    print(f"  Preview: {preview[:200]}...")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(test_fts_search())