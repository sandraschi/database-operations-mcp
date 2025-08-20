"""
ChromaDB vector database connector implementation.

Handles ChromaDB vector databases for AI embeddings, semantic search, and 
machine learning workflows. Perfect for RAG systems and AI applications.
"""

import logging
import chromadb
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import json

from database_operations.database_manager import (
    BaseDatabaseConnector, 
    DatabaseType, 
    ConnectionStatus,
    ConnectionError,
    QueryError
)

logger = logging.getLogger(__name__)

class ChromaDBConnector(BaseDatabaseConnector):
    """ChromaDB vector database connector."""
    
    @property
    def database_type(self) -> DatabaseType:
        """Return the database type."""
        return DatabaseType.CHROMADB
    
    def __init__(self, connection_config: Dict[str, Any]):
        """Initialize ChromaDB connector."""
        super().__init__(connection_config)
        
        self.persist_directory = connection_config.get("persist_directory")
        self.host = connection_config.get("host")
        self.port = connection_config.get("port", 8000)
        self.collection_name = connection_config.get("collection_name", "default")
        
        if not self.persist_directory and not self.host:
            raise ValueError("ChromaDB connector requires either 'persist_directory' or 'host'")
        
        self.client = None
        self.connection = None
    
    def test_connection(self) -> Dict[str, Any]:
        """Test ChromaDB connectivity."""
        try:
            if self.persist_directory:
                test_client = chromadb.PersistentClient(path=self.persist_directory)
                connection_type = "local_persistent"
                connection_info = {"persist_directory": self.persist_directory}
            else:
                test_client = chromadb.HttpClient(host=self.host, port=self.port)
                connection_type = "remote_server"
                connection_info = {"host": self.host, "port": self.port}
            
            collections = test_client.list_collections()
            
            try:
                heartbeat = test_client.heartbeat()
                version_info = {"heartbeat": heartbeat}
            except Exception:
                version_info = {"heartbeat": "unknown"}
            
            try:
                temp_collection = test_client.create_collection("test_connection_temp")
                test_client.delete_collection("test_connection_temp")
                write_permissions = True
            except Exception:
                write_permissions = False
            
            return {
                "success": True,
                "connection_type": connection_type,
                "connection_info": connection_info,
                "collections_count": len(collections),
                "write_permissions": write_permissions,
                "version_info": version_info,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"ChromaDB connection test failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def connect(self) -> bool:
        """Establish ChromaDB connection."""
        try:
            if self.persist_directory:
                self.client = chromadb.PersistentClient(path=self.persist_directory)
                logger.info(f"Connected to local ChromaDB: {self.persist_directory}")
            else:
                self.client = chromadb.HttpClient(host=self.host, port=self.port)
                logger.info(f"Connected to remote ChromaDB: {self.host}:{self.port}")
            
            self.client.list_collections()
            self.connection = self.client
            self.status = ConnectionStatus.CONNECTED
            self.last_error = None
            return True
            
        except Exception as e:
            self.status = ConnectionStatus.ERROR
            self.last_error = str(e)
            logger.error(f"Failed to connect to ChromaDB: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Close ChromaDB connection."""
        try:
            self.client = None
            self.connection = None
            self.status = ConnectionStatus.DISCONNECTED
            self.last_error = None
            logger.info("Disconnected from ChromaDB")
            return True
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error disconnecting from ChromaDB: {e}")
            return False
    
    def list_databases(self) -> List[Dict[str, Any]]:
        """List databases (ChromaDB instance info)."""
        try:
            if not self.client:
                if not self.connect():
                    raise ConnectionError("Failed to connect to ChromaDB")
            
            return [{
                "name": "chromadb_instance",
                "type": "vector_database",
                "connection_type": "local_persistent" if self.persist_directory else "remote_server",
                "location": self.persist_directory or f"{self.host}:{self.port}"
            }]
            
        except Exception as e:
            logger.error(f"Error listing ChromaDB databases: {e}")
            raise QueryError(f"Failed to list databases: {e}")
    
    def list_tables(self, database: Optional[str] = None) -> List[Dict[str, Any]]:
        """List collections (tables) in ChromaDB."""
        try:
            if not self.client:
                if not self.connect():
                    raise ConnectionError("Failed to connect to ChromaDB")
            
            collections = self.client.list_collections()
            tables = []
            
            for collection in collections:
                col_obj = self.client.get_collection(collection.name)
                count = col_obj.count()
                metadata = getattr(collection, 'metadata', {}) or {}
                
                tables.append({
                    "name": collection.name,
                    "type": "collection",
                    "document_count": count,
                    "metadata": metadata,
                    "id": getattr(collection, 'id', None)
                })
            
            return tables
            
        except Exception as e:
            logger.error(f"Error listing ChromaDB collections: {e}")
            raise QueryError(f"Failed to list collections: {e}")
    
    def describe_table(self, table_name: str, database: Optional[str] = None) -> Dict[str, Any]:
        """Get collection schema and metadata."""
        try:
            if not self.client:
                if not self.connect():
                    raise ConnectionError("Failed to connect to ChromaDB")
            
            try:
                collection = self.client.get_collection(table_name)
            except Exception:
                raise QueryError(f"Collection '{table_name}' not found")
            
            document_count = collection.count()
            
            sample_data = None
            if document_count > 0:
                sample = collection.get(limit=3)
                sample_data = {
                    "sample_ids": sample.get("ids", []),
                    "sample_documents": sample.get("documents", []),
                    "sample_metadatas": sample.get("metadatas", []),
                    "has_embeddings": "embeddings" in sample and sample["embeddings"] is not None
                }
            
            metadata_fields = set()
            if sample_data and sample_data.get("sample_metadatas"):
                for metadata in sample_data["sample_metadatas"]:
                    if metadata:
                        metadata_fields.update(metadata.keys())
            
            return {
                "collection_name": table_name,
                "document_count": document_count,
                "metadata_fields": list(metadata_fields),
                "sample_data": sample_data,
                "embedding_dimension": self._get_embedding_dimension(collection),
                "collection_metadata": getattr(collection, 'metadata', {})
            }
            
        except Exception as e:
            logger.error(f"Error describing ChromaDB collection {table_name}: {e}")
            raise QueryError(f"Failed to describe collection: {e}")
    
    def _get_embedding_dimension(self, collection) -> Optional[int]:
        """Get embedding dimension from collection."""
        try:
            sample = collection.get(limit=1, include=["embeddings"])
            if sample.get("embeddings") and len(sample["embeddings"]) > 0:
                return len(sample["embeddings"][0])
        except Exception:
            pass
        return None
    
    def execute_query(self, query: str, parameters: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute ChromaDB operations (similarity search, etc.)."""
        try:
            if not self.client:
                if not self.connect():
                    raise ConnectionError("Failed to connect to ChromaDB")
            
            # Parse query type - simplified implementation
            query_lower = query.strip().lower()
            
            if query_lower.startswith("search"):
                # Semantic search operation
                return self._execute_search_query(query, parameters)
            elif query_lower.startswith("insert") or query_lower.startswith("add"):
                # Insert documents
                return self._execute_insert_query(query, parameters)
            elif query_lower.startswith("delete"):
                # Delete documents
                return self._execute_delete_query(query, parameters)
            else:
                return {
                    "query_type": "UNSUPPORTED",
                    "error": "ChromaDB supports search, insert, and delete operations",
                    "supported_operations": ["search", "insert", "delete"]
                }
                
        except Exception as e:
            logger.error(f"Error executing ChromaDB query: {e}")
            raise QueryError(f"Query execution failed: {e}")
    
    def _execute_search_query(self, query: str, parameters: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute similarity search."""
        try:
            params = parameters or {}
            collection_name = params.get("collection", self.collection_name)
            query_texts = params.get("query_texts", [])
            n_results = params.get("n_results", 10)
            where = params.get("where")
            
            collection = self.client.get_collection(collection_name)
            
            if query_texts:
                results = collection.query(
                    query_texts=query_texts,
                    n_results=n_results,
                    where=where
                )
            else:
                # Get all documents if no query specified
                results = collection.get(limit=n_results, where=where)
            
            return {
                "query_type": "SEARCH",
                "collection": collection_name,
                "results": results,
                "result_count": len(results.get("ids", [])) if results.get("ids") else 0
            }
            
        except Exception as e:
            raise QueryError(f"Search query failed: {e}")
    
    def _execute_insert_query(self, query: str, parameters: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute document insertion."""
        try:
            params = parameters or {}
            collection_name = params.get("collection", self.collection_name)
            
            # Get or create collection
            try:
                collection = self.client.get_collection(collection_name)
            except Exception:
                collection = self.client.create_collection(collection_name)
            
            documents = params.get("documents", [])
            metadatas = params.get("metadatas")
            ids = params.get("ids")
            
            if not documents:
                raise QueryError("No documents provided for insertion")
            
            # Generate IDs if not provided
            if not ids:
                ids = [f"doc_{i}_{int(datetime.now().timestamp())}" for i in range(len(documents))]
            
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            return {
                "query_type": "INSERT",
                "collection": collection_name,
                "inserted_count": len(documents),
                "inserted_ids": ids
            }
            
        except Exception as e:
            raise QueryError(f"Insert query failed: {e}")
    
    def _execute_delete_query(self, query: str, parameters: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute document deletion."""
        try:
            params = parameters or {}
            collection_name = params.get("collection", self.collection_name)
            
            collection = self.client.get_collection(collection_name)
            
            ids = params.get("ids")
            where = params.get("where")
            
            if ids:
                collection.delete(ids=ids)
                deleted_count = len(ids)
            elif where:
                # Get documents matching where clause first
                matching = collection.get(where=where)
                if matching.get("ids"):
                    collection.delete(ids=matching["ids"])
                    deleted_count = len(matching["ids"])
                else:
                    deleted_count = 0
            else:
                raise QueryError("Must specify either 'ids' or 'where' for deletion")
            
            return {
                "query_type": "DELETE",
                "collection": collection_name,
                "deleted_count": deleted_count
            }
            
        except Exception as e:
            raise QueryError(f"Delete query failed: {e}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get ChromaDB performance metrics."""
        try:
            if not self.client:
                if not self.connect():
                    raise ConnectionError("Failed to connect to ChromaDB")
            
            collections = self.client.list_collections()
            total_documents = 0
            collection_stats = []
            
            for collection in collections:
                col_obj = self.client.get_collection(collection.name)
                doc_count = col_obj.count()
                total_documents += doc_count
                
                collection_stats.append({
                    "name": collection.name,
                    "document_count": doc_count,
                    "metadata": getattr(collection, 'metadata', {})
                })
            
            return {
                "database_metrics": {
                    "total_collections": len(collections),
                    "total_documents": total_documents,
                    "collection_stats": collection_stats,
                    "connection_type": "local_persistent" if self.persist_directory else "remote_server"
                },
                "performance_status": "healthy",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting ChromaDB performance metrics: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform ChromaDB health check."""
        try:
            health_status = "healthy"
            issues = []
            
            connection_test = self.test_connection()
            if not connection_test["success"]:
                health_status = "unhealthy"
                issues.append(f"Connection failed: {connection_test['error']}")
            
            metrics = self.get_performance_metrics()
            
            # Test basic operations if connected
            operation_test = None
            if self.client or self.connect():
                try:
                    self.client.list_collections()
                    operation_test = {"success": True}
                except Exception as e:
                    operation_test = {"success": False, "error": str(e)}
                    health_status = "unhealthy"
                    issues.append(f"Operation test failed: {str(e)}")
            
            return {
                "status": health_status,
                "issues": issues,
                "connection_test": connection_test,
                "operation_test": operation_test,
                "metrics": metrics,
                "connection_info": {
                    "persist_directory": self.persist_directory,
                    "host": self.host,
                    "port": self.port
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error performing ChromaDB health check: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

