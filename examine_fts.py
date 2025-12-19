import sqlite3
import os

# Check the FTS database structure
fts_path = r'L:\Multimedia Files\Written Word\Calibre-Bibliothek Deutsch\full-text-search.db'
if os.path.exists(fts_path):
    try:
        conn = sqlite3.connect(fts_path)
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f'FTS Database tables: {tables}')

        # Check for FTS tables
        fts_tables = [t for t in tables if t.startswith('FTS_')]
        print(f'FTS tables: {fts_tables}')

        # Examine structure of first FTS table
        if fts_tables:
            table_name = fts_tables[0]
            cursor.execute(f'PRAGMA table_info("{table_name}")')
            columns = cursor.fetchall()
            print(f'\n{table_name} columns:')
            for col in columns:
                print(f'  {col[1]}: {col[2]}')

            # Sample data
            cursor.execute(f'SELECT * FROM "{table_name}" LIMIT 3')
            rows = cursor.fetchall()
            print(f'\nSample data from {table_name}:')
            for row in rows[:3]:
                print(f'  {row}')

        # Check if there are other important tables
        for table in tables:
            if table not in fts_tables:
                cursor.execute(f'PRAGMA table_info("{table}")')
                columns = cursor.fetchall()
                print(f'\n{table} columns:')
                for col in columns:
                    print(f'  {col[1]}: {col[2]}')

                cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
                count = cursor.fetchone()[0]
                print(f'  Row count: {count}')

        conn.close()
    except Exception as e:
        print(f'Error examining FTS database: {e}')
else:
    print(f'FTS database not found at: {fts_path}')
