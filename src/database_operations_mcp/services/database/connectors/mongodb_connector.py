"""
MongoDB database connector implementation.

Handles connections to MongoDB databases, including replica sets and sharded clusters.
Supports document storage, querying, and aggregation operations.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

from pymongo import MongoClient
from pymongo.errors import (
    ConfigurationError,
    ConnectionFailure,
    OperationFailure,
)

from ....database_manager import (
    BaseDatabaseConnector,
    ConnectionError,
    ConnectionStatus,
    DatabaseType,
    QueryError,
)

logger = logging.getLogger(__name__)


class MongoDBConnector(BaseDatabaseConnector):
    """MongoDB database connector."""

    @property
    def database_type(self) -> DatabaseType:
        """Return the database type."""
        return DatabaseType.MONGODB

    def __init__(self, connection_config: Dict[str, Any]):
        """Initialize MongoDB connector.

        Args:
            connection_config: Must contain connection parameters
                - connection_string: MongoDB connection string (preferred)
                OR
                - host: MongoDB server host (default: localhost)
                - port: MongoDB server port (default: 27017)
                - username: Authentication username (optional)
                - password: Authentication password (optional)
                - auth_source: Authentication database (default: admin)
                - auth_mechanism: Authentication mechanism (e.g., SCRAM-SHA-256)
                - tls: Enable TLS/SSL (default: False)
                - tlsCAFile: Path to CA certificate file (optional)
                - replica_set: Replica set name (optional)
                - read_preference: Read preference (e.g., 'primary', 'secondary')
        """
        super().__init__(connection_config)

        # Connection parameters with defaults
        self.connection_string = connection_config.get("connection_string")
        self.host = connection_config.get("host", "localhost")
        self.port = int(connection_config.get("port", 27017))
        self.username = connection_config.get("username")
        self.password = connection_config.get("password")
        self.auth_source = connection_config.get("auth_source", "admin")
        self.auth_mechanism = connection_config.get("auth_mechanism")
        self.tls = connection_config.get("tls", False)
        self.tls_ca_file = connection_config.get("tlsCAFile")
        self.replica_set = connection_config.get("replica_set")
        self.read_preference = connection_config.get("read_preference", "primary")

        # Connection objects
        self.client = None
        self.connection = None

    def connect(self) -> bool:
        """Establish MongoDB connection."""
        try:
            # Close existing connection if any
            if self.client:
                self.client.close()

            # Build connection parameters
            conn_params = {
                "host": self.connection_string or self.host,
                "port": self.port,
                "username": self.username,
                "password": self.password,
                "authSource": self.auth_source,
                "authMechanism": self.auth_mechanism,
                "tls": self.tls,
                "replicaSet": self.replica_set,
                "readPreference": self.read_preference,
                "serverSelectionTimeoutMS": 10000,  # 10 seconds timeout
                "connectTimeoutMS": 10000,
            }

            # Add TLS/SSL options if enabled
            if self.tls and self.tls_ca_file:
                conn_params["tlsCAFile"] = self.tls_ca_file

            # Remove None values
            conn_params = {k: v for k, v in conn_params.items() if v is not None}

            # Connect to MongoDB
            self.client = MongoClient(**conn_params)

            # Test the connection
            self.client.admin.command("ping")

            self.connection = self.client.get_database()
            self.status = ConnectionStatus.CONNECTED
            self.last_error = None

            logger.info(f"Connected to MongoDB at {self.host}:{self.port}")
            return True

        except (ConnectionFailure, ConfigurationError, OperationFailure) as e:
            self.status = ConnectionStatus.ERROR
            self.last_error = str(e)
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False

    def disconnect(self) -> bool:
        """Close MongoDB connection."""
        try:
            if self.client:
                self.client.close()

            self.client = None
            self.connection = None
            self.status = ConnectionStatus.DISCONNECTED
            self.last_error = None

            logger.info("Disconnected from MongoDB")
            return True

        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error disconnecting from MongoDB: {e}")
            return False

    def execute_query(
        self, query: Dict, database_name: str = None, collection_name: str = None, **kwargs
    ) -> Dict[str, Any]:
        """Execute a MongoDB query.

        Args:
            query: MongoDB query document
            database_name: Target database name (optional if specified in connection)
            collection_name: Target collection name
            **kwargs: Additional query options

        Returns:
            Dictionary with query results and metadata
        """
        try:
            if not self.client:
                if not self.connect():
                    raise ConnectionError("Failed to connect to MongoDB")

            db = self.client[database_name] if database_name else self.connection
            collection = db[collection_name] if collection_name else None

            if not collection:
                raise ValueError("Collection name must be provided")

            # Determine operation type from query
            operation = query.get("operation")

            if operation == "find":
                cursor = collection.find(
                    filter=query.get("filter", {}),
                    projection=query.get("projection"),
                    sort=query.get("sort"),
                    limit=query.get("limit"),
                    skip=query.get("skip"),
                    **kwargs,
                )
                results = list(cursor)
                return {"operation": "find", "count": len(results), "results": results}

            elif operation == "aggregate":
                pipeline = query.get("pipeline", [])
                cursor = collection.aggregate(pipeline, **kwargs)
                results = list(cursor)
                return {"operation": "aggregate", "count": len(results), "results": results}

            elif operation == "insert_one":
                result = collection.insert_one(query.get("document", {}), **kwargs)
                return {
                    "operation": "insert_one",
                    "inserted_id": str(result.inserted_id),
                    "acknowledged": result.acknowledged,
                }

            elif operation == "update_one":
                result = collection.update_one(
                    filter=query.get("filter", {}),
                    update=query.get("update", {}),
                    upsert=query.get("upsert", False),
                    **kwargs,
                )
                return {
                    "operation": "update_one",
                    "matched_count": result.matched_count,
                    "modified_count": result.modified_count,
                    "upserted_id": str(result.upserted_id) if result.upserted_id else None,
                }

            elif operation == "delete_one":
                result = collection.delete_one(query.get("filter", {}), **kwargs)
                return {"operation": "delete_one", "deleted_count": result.deleted_count}

            else:
                raise ValueError(f"Unsupported MongoDB operation: {operation}")

        except Exception as e:
            logger.error(f"MongoDB query failed: {e}")
            raise QueryError(f"MongoDB operation failed: {e}")

    def list_databases(self) -> List[Dict[str, Any]]:
        """List all databases on the MongoDB server."""
        try:
            if not self.client:
                if not self.connect():
                    raise ConnectionError("Failed to connect to MongoDB")

            databases = []
            for db_info in self.client.list_databases():
                db_name = db_info["name"]
                db = self.client[db_name]
                stats = db.command("dbstats")

                databases.append(
                    {
                        "name": db_name,
                        "size_on_disk": stats.get("storageSize", 0),
                        "empty": stats.get("empty", False),
                        "collections": db.list_collection_names(),
                        "stats": {
                            "collections": stats.get("collections", 0),
                            "objects": stats.get("objects", 0),
                            "avg_obj_size": stats.get("avgObjSize", 0),
                        },
                    }
                )

            return databases

        except Exception as e:
            logger.error(f"Failed to list MongoDB databases: {e}")
            raise QueryError(f"Failed to list databases: {e}")

    def list_collections(self, database_name: str = None) -> List[Dict[str, Any]]:
        """List collections in a database.

        Args:
            database_name: Name of the database (optional if specified in connection)

        Returns:
            List of collection information dictionaries
        """
        try:
            if not self.client:
                if not self.connect():
                    raise ConnectionError("Failed to connect to MongoDB")

            db = self.client[database_name] if database_name else self.connection
            if not db:
                raise ValueError(
                    "Database name must be provided or connection must specify a database"
                )

            collections = []
            for coll_name in db.list_collection_names():
                coll = db[coll_name]
                stats = db.command("collstats", coll_name)

                collections.append(
                    {
                        "name": coll_name,
                        "type": "collection",
                        "size": stats.get("size", 0),
                        "count": stats.get("count", 0),
                        "storage_size": stats.get("storageSize", 0),
                        "indexes": stats.get("nindexes", 0),
                        "capped": stats.get("capped", False),
                    }
                )

            return collections

        except Exception as e:
            logger.error(f"Failed to list collections in database {database_name}: {e}")
            raise QueryError(f"Failed to list collections: {e}")

    def get_collection_stats(self, database_name: str, collection_name: str) -> Dict[str, Any]:
        """Get statistics for a specific collection."""
        try:
            if not self.client:
                if not self.connect():
                    raise ConnectionError("Failed to connect to MongoDB")

            db = self.client[database_name] if database_name else self.connection
            if not db:
                raise ValueError(
                    "Database name must be provided or connection must specify a database"
                )

            # Get basic collection stats
            stats = db.command("collstats", collection_name)

            # Get index information
            indexes = db[collection_name].list_indexes()

            return {
                "namespace": f"{database_name}.{collection_name}",
                "count": stats.get("count", 0),
                "size": stats.get("size", 0),
                "storage_size": stats.get("storageSize", 0),
                "total_index_size": stats.get("totalIndexSize", 0),
                "index_sizes": stats.get("indexSizes", {}),
                "indexes": [idx for idx in indexes],
                "capped": stats.get("capped", False),
                "sharded": "sharded" in stats,
                "shard_key": stats.get("shardKey", {}) if "sharded" in stats else None,
            }

        except Exception as e:
            logger.error(
                f"Failed to get stats for collection {database_name}.{collection_name}: {e}"
            )
            raise QueryError(f"Failed to get collection stats: {e}")

    def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the MongoDB connection."""
        try:
            if not self.client:
                if not self.connect():
                    return {
                        "status": "error",
                        "message": "Failed to connect to MongoDB",
                        "details": self.last_error,
                    }

            # Get server status
            server_status = self.client.admin.command("serverStatus")

            # Get replica set status if applicable
            rs_status = None
            try:
                rs_status = self.client.admin.command("replSetGetStatus")
            except OperationFailure:
                # Not part of a replica set
                pass

            # Get database list
            db_list = self.client.list_database_names()

            return {
                "status": "ok",
                "server": {
                    "host": self.client.HOST,
                    "port": self.client.PORT,
                    "version": server_status.get("version"),
                    "uptime": server_status.get("uptime"),
                    "connections": server_status.get("connections", {}),
                    "replica_set": {
                        "is_configured": bool(rs_status),
                        "name": rs_status.get("set") if rs_status else None,
                        "members": [
                            {
                                "name": m.get("name"),
                                "state": m.get("stateStr"),
                                "health": m.get("health"),
                                "uptime": m.get("uptime"),
                            }
                            for m in rs_status.get("members", [])
                        ]
                        if rs_status
                        else [],
                    },
                },
                "databases": {"count": len(db_list), "names": db_list},
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"MongoDB health check failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics from MongoDB."""
        try:
            if not self.client:
                if not self.connect():
                    raise ConnectionError("Failed to connect to MongoDB")

            server_status = self.client.admin.command("serverStatus")

            # Extract relevant metrics
            metrics = {
                "opcounters": server_status.get("opcounters", {}),
                "opcountersRepl": server_status.get("opcountersRepl", {}),
                "network": server_status.get("network", {}),
                "connections": server_status.get("connections", {}),
                "mem": server_status.get("mem", {}),
                "wiredTiger": server_status.get("wiredTiger", {}).get("cache", {})
                if "wiredTiger" in server_status
                else {},
                "globalLock": server_status.get("globalLock", {}),
                "metrics": server_status.get("metrics", {}),
            }

            return metrics

        except Exception as e:
            logger.error(f"Failed to get MongoDB performance metrics: {e}")
            raise QueryError(f"Failed to get performance metrics: {e}")

    def test_connection(self) -> Dict[str, Any]:
        """Test the MongoDB connection."""
        start_time = datetime.now()
        try:
            if not self.client:
                if not self.connect():
                    return {
                        "success": False,
                        "error": "Failed to connect to MongoDB",
                        "details": self.last_error,
                        "latency_ms": (datetime.now() - start_time).total_seconds() * 1000,
                    }

            # Test with a simple command
            self.client.admin.command("ping")

            return {
                "success": True,
                "server_info": self.client.server_info(),
                "latency_ms": (datetime.now() - start_time).total_seconds() * 1000,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "latency_ms": (datetime.now() - start_time).total_seconds() * 1000,
            }
