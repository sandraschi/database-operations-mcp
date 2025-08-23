"""
Unit tests for the export_calibre_library function in maintenance_tools.py
"""
import os
import tempfile
import shutil
import sqlite3
import json
import csv
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the function to test
from database_operations_mcp.handlers.maintenance_tools import export_calibre_library

# Test data
SAMPLE_LIBRARY = {
    'metadata.db': {
        'tables': {
            'books': [
                (1, 'Book 1', 'sort1', 'Author 1', '2023-01-01', '2022-01-01', '2023-01-02', 'uuid1', 1, 1.0, 'path1', '1234567890', 'lccn1'),
                (2, 'Book 2', 'sort2', 'Author 2', '2023-01-02', '2022-01-02', '2023-01-03', 'uuid2', 0, 2.0, 'path2', None, None)
            ],
            'authors': [
                (1, 'Author 1', 'Author 1', ''),
                (2, 'Author 2', 'Author 2', '')
            ],
            'books_authors_link': [(1, 1), (2, 2)],
            'books_plugin_data': [
                (1, 'format1', 'key1', 'value1'),
                (2, 'format2', 'key2', 'value2')
            ],
            'identifiers': [
                (1, 'isbn', '1234567890'),
                (1, 'asin', 'B0ABCDE123')
            ],
            'tags': [(1, 'Fiction'), (2, 'Non-Fiction')],
            'books_tags_link': [(1, 1), (2, 2)],
            'series': [(1, 'Series 1'), (2, 'Series 2')],
            'books_series_link': [(1, 1, 1), (2, 2, 2)],
            'ratings': [(1, 5), (2, 4)],
            'books_ratings_link': [(1, 1), (2, 2)],
            'comments': [(1, 'Comment 1'), (2, 'Comment 2')],
            'publishers': [(1, 'Publisher 1'), (2, 'Publisher 2')],
            'books_publishers_link': [(1, 1), (2, 2)]
        }
    }
}

@pytest.fixture
def temp_calibre_library():
    """Create a temporary Calibre library for testing."""
    temp_dir = tempfile.mkdtemp()
    library_path = Path(temp_dir) / 'test_library'
    library_path.mkdir()
    
    # Create metadata.db
    db_path = library_path / 'metadata.db'
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Create tables and insert test data
    cursor.executescript("""
        CREATE TABLE books (
            id INTEGER PRIMARY KEY,
            title TEXT,
            sort TEXT,
            author_sort TEXT,
            timestamp TEXT,
            pubdate TEXT,
            last_modified TEXT,
            uuid TEXT,
            has_cover INTEGER,
            series_index REAL,
            path TEXT,
            isbn TEXT,
            lccn TEXT
        );
        
        CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT, sort TEXT, link TEXT);
        CREATE TABLE books_authors_link (book INTEGER, author INTEGER);
        CREATE TABLE books_plugin_data (book INTEGER, format TEXT, name TEXT, val TEXT);
        CREATE TABLE identifiers (book INTEGER, type TEXT, val TEXT);
        CREATE TABLE tags (id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE books_tags_link (book INTEGER, tag INTEGER);
        CREATE TABLE series (id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE books_series_link (book INTEGER, series INTEGER, value REAL);
        CREATE TABLE ratings (id INTEGER PRIMARY KEY, rating INTEGER);
        CREATE TABLE books_ratings_link (book INTEGER, rating INTEGER);
        CREATE TABLE comments (book INTEGER, text TEXT);
        CREATE TABLE publishers (id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE books_publishers_link (book INTEGER, publisher INTEGER);
    """)
    
    # Insert test data
    for table, rows in SAMPLE_LIBRARY['metadata.db']['tables'].items():
        if rows:  # Only insert if there are rows
            cursor.executemany(f'INSERT INTO {table} VALUES ({",".join(["?"]*len(rows[0]))})', rows)
    
    conn.commit()
    conn.close()
    
    yield library_path
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def temp_output_file():
    """Create a temporary output file for testing."""
    temp_dir = tempfile.mkdtemp()
    output_file = Path(temp_dir) / 'output'
    
    yield output_file
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)

def test_export_calibre_library_json(temp_calibre_library, temp_output_file):
    """Test exporting Calibre library to JSON format."""
    output_file = temp_output_file.with_suffix('.json')
    
    result = export_calibre_library(
        library_path=str(temp_calibre_library),
        output_path=str(output_file),
        format='json',
        include_metadata=True,
        include_content=False
    )
    
    assert result['status'] == 'success'
    assert output_file.exists()
    assert result['book_count'] == 2
    
    # Verify JSON content
    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        assert 'books' in data
        assert len(data['books']) == 2
        assert data['books'][0]['title'] == 'Book 1'
        assert data['books'][1]['title'] == 'Book 2'

def test_export_calibre_library_csv(temp_calibre_library, temp_output_file):
    """Test exporting Calibre library to CSV format."""
    output_file = temp_output_file.with_suffix('.csv')
    
    result = export_calibre_library(
        library_path=str(temp_calibre_library),
        output_path=str(output_file),
        format='csv',
        include_metadata=True,
        include_content=False
    )
    
    assert result['status'] == 'success'
    assert output_file.exists()
    
    # Verify CSV content
    with open(output_file, 'r', encoding='utf-8-sig') as f:  # Handle BOM
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 2
        assert rows[0]['title'] == 'Book 1'
        assert rows[1]['title'] == 'Book 2'

def test_export_calibre_library_sqlite(temp_calibre_library, temp_output_file):
    """Test exporting Calibre library to SQLite format."""
    output_file = temp_output_file.with_suffix('.db')
    
    result = export_calibre_library(
        library_path=str(temp_calibre_library),
        output_path=str(output_file),
        format='sqlite',
        include_metadata=True,
        include_content=False
    )
    
    assert result['status'] == 'success'
    assert output_file.exists()
    
    # Verify SQLite content
    conn = sqlite3.connect(str(output_file))
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM books')
    assert cursor.fetchone()[0] == 2
    
    cursor.execute('SELECT title FROM books ORDER BY id')
    titles = [row[0] for row in cursor.fetchall()]
    assert titles == ['Book 1', 'Book 2']
    
    conn.close()

def test_export_calibre_library_invalid_format(temp_calibre_library, temp_output_file):
    """Test exporting with an invalid format."""
    output_file = temp_output_file.with_suffix('.invalid')
    
    result = export_calibre_library(
        library_path=str(temp_calibre_library),
        output_path=str(output_file),
        format='invalid',
        include_metadata=True,
        include_content=False
    )
    
    assert result['status'] == 'error'
    assert 'Unsupported export format' in result['message']

def test_export_calibre_library_nonexistent_dir(temp_calibre_library, temp_output_file):
    """Test exporting to a non-existent directory (should create it)."""
    output_file = temp_output_file / 'nonexistent' / 'output.json'
    
    result = export_calibre_library(
        library_path=str(temp_calibre_library),
        output_path=str(output_file),
        format='json',
        include_metadata=True,
        include_content=False
    )
    
    assert result['status'] == 'success'
    assert output_file.exists()

@patch('database_operations_mcp.handlers.maintenance_tools.sqlite3.connect')
def test_export_calibre_library_db_error(mock_connect, temp_output_file):
    """Test error handling when database connection fails."""
    mock_connect.side_effect = sqlite3.Error('Connection failed')
    
    result = export_calibre_library(
        library_path='/nonexistent/path',
        output_path=str(temp_output_file),
        format='json',
        include_metadata=True,
        include_content=False
    )
    
    assert result['status'] == 'error'
    assert 'Error exporting library' in result['message']

def test_export_calibre_library_empty_library(temp_output_file):
    """Test exporting an empty Calibre library."""
    with tempfile.TemporaryDirectory() as temp_dir:
        empty_lib = Path(temp_dir) / 'empty_lib'
        empty_lib.mkdir()
        
        # Create empty database
        db_path = empty_lib / 'metadata.db'
        conn = sqlite3.connect(str(db_path))
        conn.close()
        
        result = export_calibre_library(
            library_path=str(empty_lib),
            output_path=str(temp_output_file),
            format='json',
            include_metadata=True,
            include_content=False
        )
        
        assert result['status'] == 'error'
        assert 'No books found to export' in result['message']
