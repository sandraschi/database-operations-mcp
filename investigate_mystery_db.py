#!/usr/bin/env python3
"""
Mystery Database Investigator

Quick script to analyze the top-level metadata.db in the Calibre base directory.
Uses the database-operations-mcp SQLite connector for comprehensive analysis.
"""

import sys
import os
from pathlib import Path

# Add the database operations module to path
repo_path = Path(__file__).parent
sys.path.insert(0, str(repo_path))

from database_operations_mcp.connectors.sqlite_connector import SQLiteConnector

def investigate_mystery_database():
    """Investigate the mystery metadata.db file."""
    
    mystery_db_path = r"L:\Multimedia Files\Written Word\metadata.db"
    
    print("🔍 Mystery Database Investigation")
    print("=" * 50)
    print(f"📁 Database Path: {mystery_db_path}")
    print()
    
    if not os.path.exists(mystery_db_path):
        print("❌ Mystery database file does not exist!")
        return
    
    # Create SQLite connector
    config = {"database_path": mystery_db_path}
    connector = SQLiteConnector(config)
    
    try:
        print("🔗 Testing Connection...")
        connection_test = connector.test_connection()
        
        if connection_test["success"]:
            print("✅ Connection successful!")
            print(f"   SQLite Version: {connection_test['sqlite_version']}")
            print(f"   File Size: {connection_test['file_size_bytes']:,} bytes ({connection_test['file_size_bytes']/1024/1024:.2f} MB)")
            print()
        else:
            print(f"❌ Connection failed: {connection_test['error']}")
            return
        
        # Connect and analyze
        if connector.connect():
            print("📊 Database Analysis:")
            print("-" * 30)
            
            # List tables
            tables = connector.list_tables()
            print(f"📋 Tables found: {len(tables)}")
            
            for table in tables:
                print(f"   • {table['name']} ({table['type']}) - {table['row_count']:,} rows")
            print()
            
            # Analyze each table
            for table in tables:
                table_name = table['name']
                print(f"🔍 Analyzing table: {table_name}")
                
                try:
                    schema = connector.describe_table(table_name)
                    print(f"   Columns: {schema['column_count']}")
                    print(f"   Rows: {schema['row_count']:,}")
                    
                    # Show column structure
                    for col in schema['columns'][:5]:  # First 5 columns
                        pk_indicator = " (PK)" if col['primary_key'] else ""
                        print(f"     - {col['name']}: {col['type']}{pk_indicator}")
                    
                    if len(schema['columns']) > 5:
                        print(f"     ... and {len(schema['columns']) - 5} more columns")
                    
                    # Sample data
                    if schema['row_count'] > 0:
                        sample_result = connector.execute_query(f"SELECT * FROM [{table_name}] LIMIT 3")
                        if sample_result['rows']:
                            print(f"   Sample data (first row):")
                            for i, col_name in enumerate(sample_result['columns'][:3]):
                                value = sample_result['rows'][0][i] if len(sample_result['rows'][0]) > i else None
                                print(f"     {col_name}: {value}")
                    print()
                    
                except Exception as e:
                    print(f"   ❌ Error analyzing table: {e}")
                    print()
            
            # Performance metrics
            print("⚡ Performance Metrics:")
            print("-" * 25)
            metrics = connector.get_performance_metrics()
            db_metrics = metrics.get("database_metrics", {})
            
            print(f"   File Size: {db_metrics.get('file_size_mb', 0):.2f} MB")
            print(f"   Page Count: {db_metrics.get('page_count', 0):,}")
            print(f"   Page Size: {db_metrics.get('page_size', 0):,} bytes")
            print(f"   Journal Mode: {db_metrics.get('journal_mode', 'unknown')}")
            print()
            
            # Health check
            print("🏥 Health Check:")
            print("-" * 15)
            health = connector.health_check()
            print(f"   Status: {health['status'].upper()}")
            
            if health.get('issues'):
                print("   Issues:")
                for issue in health['issues']:
                    print(f"     ⚠️  {issue}")
            else:
                print("   ✅ No issues detected")
            
        else:
            print("❌ Failed to connect to database")
    
    except Exception as e:
        print(f"❌ Investigation failed: {e}")
    
    finally:
        connector.disconnect()

if __name__ == "__main__":
    investigate_mystery_database()
