import sqlite3
import os

# Check the FTS database structure in detail
fts_path = r'L:\Multimedia Files\Written Word\Calibre-Bibliothek Deutsch\full-text-search.db'
if os.path.exists(fts_path):
    try:
        conn = sqlite3.connect(fts_path)
        cursor = conn.cursor()

        # Check books_text table content
        cursor.execute('SELECT book, format, text_size, substr(searchable_text, 1, 200) as preview FROM books_text WHERE searchable_text IS NOT NULL AND length(searchable_text) > 0 LIMIT 5')
        rows = cursor.fetchall()
        print('Sample books_text entries:')
        for row in rows:
            print(f'  Book: {row[0]}, Format: {row[1]}, Size: {row[2]} chars')
            print(f'  Preview: {row[3][:100]}...')
            print()

        # Try to understand the FTS setup
        try:
            cursor.execute("SELECT * FROM books_fts_config")
            config = cursor.fetchall()
            print(f'FTS config: {config}')
        except Exception as e:
            print(f'Cannot access FTS config: {e}')

        # Check if we can do basic text search on books_text
        search_term = 'python'
        cursor.execute('SELECT book, format, substr(searchable_text, 1, 200) as preview FROM books_text WHERE searchable_text LIKE ? LIMIT 5', (f'%{search_term}%',))
        results = cursor.fetchall()
        print(f'\nBasic LIKE search for "{search_term}": {len(results)} results')
        for row in results:
            print(f'  Book: {row[0]}, Format: {row[1]}')
            print(f'  Preview: {row[2][:100]}...')
            print()

        conn.close()
    except Exception as e:
        print(f'Error examining FTS database: {e}')
        import traceback
        traceback.print_exc()
else:
    print(f'FTS database not found at: {fts_path}')
