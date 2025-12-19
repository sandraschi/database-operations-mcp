#!/usr/bin/env python3
import sqlite3

db_path = r"L:\Multimedia Files\Written Word\metadata.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Tables found: {tables}")

    for table in tables:
        cursor.execute(f'PRAGMA table_info("{table}")')
        columns = cursor.fetchall()
        print(f"Table '{table}': {len(columns)} columns")

    conn.close()
    print("Database analysis successful")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
