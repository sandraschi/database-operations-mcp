"""
Test script for MongoDB connector.

This script demonstrates how to use the MongoDB connector with the database-operations-mcp package.
"""

import os
import sys
import json
import logging
from typing import Dict, Any

# Add parent directory to path to import from database_operations_mcp
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from database_operations_mcp.connectors.mongodb_connector import MongoDBConnector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_mongodb_connection(connection_config: Dict[str, Any]) -> None:
    """Test MongoDB connection and basic operations."""
    connector = None
    try:
        # Initialize connector
        connector = MongoDBConnector(connection_config)
        
        # Test connection
        logger.info("Testing MongoDB connection...")
        if not connector.connect():
            logger.error("Failed to connect to MongoDB")
            return
        
        logger.info("✓ Connected to MongoDB")
        
        # Test listing databases
        logger.info("\nListing databases:")
        dbs = connector.list_databases()
        for db in dbs[:5]:  # Show first 5 databases to avoid too much output
            logger.info(f"- {db['name']} (collections: {len(db.get('collections', []))}, size: {db.get('size_on_disk', 0) / (1024*1024):.2f} MB)")
        
        # Get the first available database with collections
        test_db = next((db for db in dbs if db.get('collections')), None)
        
        if test_db and test_db['collections']:
            db_name = test_db['name']
            collection_name = test_db['collections'][0]
            
            logger.info(f"\nTesting operations on {db_name}.{collection_name}")
            
            # Test collection stats
            stats = connector.get_collection_stats(db_name, collection_name)
            logger.info(f"Collection stats: {json.dumps(stats, indent=2, default=str)}")
            
            # Test a simple find query
            logger.info("\nTesting find query (limit 1):")
            query = {
                'operation': 'find',
                'filter': {},
                'limit': 1
            }
            result = connector.execute_query(query, db_name, collection_name)
            logger.info(f"Found {result.get('count', 0)} documents")
            if result.get('results'):
                logger.info(f"Sample document: {json.dumps(result['results'][0], indent=2, default=str)}")
            
            # Test insert one
            test_doc = {
                'test_field': 'test_value',
                'timestamp': '2025-08-21T00:00:00',
                'metadata': {
                    'source': 'test_script',
                    'version': '1.0'
                }
            }
            
            logger.info("\nTesting insert_one:")
            insert_result = connector.execute_query(
                {
                    'operation': 'insert_one',
                    'document': test_doc
                },
                db_name,
                collection_name
            )
            logger.info(f"Insert result: {json.dumps(insert_result, indent=2)}")
            
            # Test health check
            logger.info("\nRunning health check:")
            health = connector.health_check()
            logger.info(f"Health check: {json.dumps(health, indent=2, default=str)}")
            
            # Test performance metrics
            logger.info("\nGetting performance metrics:")
            metrics = connector.get_performance_metrics()
            logger.info(f"Performance metrics: {json.dumps(metrics, indent=2, default=str)}")
            
        else:
            logger.warning("No databases with collections found for testing")
            
    except Exception as e:
        logger.error(f"Error during MongoDB test: {e}", exc_info=True)
    finally:
        if connector:
            connector.disconnect()
            logger.info("Disconnected from MongoDB")

if __name__ == "__main__":
    # Default connection configuration - update these values as needed
    connection_config = {
        'host': 'localhost',
        'port': 27017,
        'username': None,  # Optional
        'password': None,  # Optional
        'auth_source': 'admin',  # Default authentication database
        'tls': False,  # Set to True for TLS/SSL
        'replica_set': None  # Set to replica set name if using replica sets
    }
    
    # You can also use a connection string
    # connection_config = {
    #     'connection_string': 'mongodb://username:password@host:27017/?authSource=admin'
    # }
    
    test_mongodb_connection(connection_config)
