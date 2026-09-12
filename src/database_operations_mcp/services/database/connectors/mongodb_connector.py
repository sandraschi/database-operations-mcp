"""
MongoDB database connector implementation.

Handles connections to MongoDB databases, including replica sets and sharded clusters.
Supports document storage, querying, and aggregation operations.
"""

import logging
from datetime import datetime
from typing import Any

try:
    from pymongo import MongoClient
    from pymongo.errors import (
        ConfigurationError,
        ConnectionFailure,
        OperationFailure,
    )
except ImportError:
    MongoClient = None
    ConfigurationError = Exception
    ConnectionFailure = Exception
    OperationFailure = Exception

from ....database_manager import (
    BaseDatabaseConnector,
    ConnectionStatus,
    DatabaseConnectionError,
    DatabaseType,
    QueryError,
    QueryParameters,
    QueryResult,
)

logger = logging.getLogger(__name__)


class MongoDBConnector(BaseDatabaseConnector):
    """MongoDB database connector."""

    @property
    def database_type(self) -> DatabaseType:
        """Return the database type."""
        return DatabaseType.MONGODB

    def __init__(self, connection_config: dict[str, Any]):
        """Initialize MongoDB connector.

        ## Examples
        Create a connector:
            connector = MongoDBConnector({"host": "localhost", "port": 27017})
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
        self.client: Any = None
        self.connection = None

    async def connect(self) -> bool:
        """Establish MongoDB connection."""
        if MongoClient is None:
            self.status = ConnectionStatus.ERROR
            self.last_error = "pymongo package is not installed"
            logger.error("Failed to connect to MongoDB: pymongo package is not installed")
            return False
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

    async def disconnect(self) -> bool:
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

    async def execute_query(
        self,
        query: str | dict[str, Any],
        parameters: QueryParameters = None,
        database_name: str | None = None,
        collection_name: str | None = None,
        **kwargs: Any,
    ) -> QueryResult:
        """Execute a MongoDB query.

        ## Return Format
        Returns a QueryResult whose data holds the operation payload dict.

        ## Examples
        Query a collection:
            result = await connector.execute_query(
                {"operation": "find", "filter": {"status": "active"}},
                database_name="mydb",
                collection_name="users",
            )
        """
        import json as _json

        try:
            if not self.client:
                if not await self.connect():
                    raise DatabaseConnectionError("Failed to connect to MongoDB")

            if isinstance(query, str):
                try:
                    query_doc = _json.loads(query)
                except ValueError:
                    query_doc = {"operation": "find", "filter": {}}
            else:
                query_doc = query
            if not isinstance(query_doc, dict):
                raise ValueError("MongoDB query must be a document or JSON string")
            if isinstance(parameters, dict):
                query_doc = {**query_doc, **parameters}

            db = self.client[database_name] if database_name else self.connection
            if db is None:
                raise DatabaseConnectionError("No database selected and connection has no default database")
            collection = db[collection_name] if collection_name else None

            if collection is None:
                raise ValueError("Collection name must be provided")

            # Determine operation type from query
            operation = query_doc.get("operation")

            if operation == "find":
                cursor = collection.find(
                    filter=query_doc.get("filter", {}),
                    projection=query_doc.get("projection"),
                    sort=query_doc.get("sort"),
                    limit=query_doc.get("limit"),
                    skip=query_doc.get("skip"),
                    **kwargs,
                )
                results = list(cursor)
                payload = {"operation": "find", "count": len(results), "results": results}

            elif operation == "aggregate":
                pipeline = query_doc.get("pipeline", [])
                cursor = collection.aggregate(pipeline, **kwargs)
                results = list(cursor)
                payload = {
                    "operation": "aggregate",
                    "count": len(results),
                    "results": results,
                }

            elif operation == "insert_one":
                result = collection.insert_one(query_doc.get("document", {}), **kwargs)
                payload = {
                    "operation": "insert_one",
                    "inserted_id": str(result.inserted_id),
                    "acknowledged": result.acknowledged,
                }

            elif operation == "update_one":
                result = collection.update_one(
                    filter=query_doc.get("filter", {}),
                    update=query_doc.get("update", {}),
                    upsert=query_doc.get("upsert", False),
                    **kwargs,
                )
                payload = {
                    "operation": "update_one",
                    "matched_count": result.matched_count,
                    "modified_count": result.modified_count,
                    "upserted_id": str(result.upserted_id) if result.upserted_id else None,
                }

            elif operation == "delete_one":
                result = collection.delete_one(query_doc.get("filter", {}), **kwargs)
                payload = {
                    "operation": "delete_one",
                    "deleted_count": result.deleted_count,
                }

            else:
                raise ValueError(f"Unsupported MongoDB operation: {operation}")

            return QueryResult(
                success=True,
                data=[payload],
                rowcount=payload.get("count", payload.get("deleted_count", 1)),
                message=f"MongoDB {payload.get('operation')} completed",
            )

        except Exception as e:
            logger.error(f"MongoDB query failed: {e}")
            raise QueryError(f"MongoDB operation failed: {e}") from e

    async def list_databases(self) -> list[dict[str, Any]]:
        """List all databases on the MongoDB server."""
        try:
            if not self.client:
                if not await self.connect():
                    raise DatabaseConnectionError("Failed to connect to MongoDB")

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
            raise QueryError(f"Failed to list databases: {e}") from e

    async def list_collections(self, database_name: str | None = None) -> list[dict[str, Any]]:
        """List collections in a database.

        ## Return Format
        Returns a list of collection info dicts.

        ## Examples
        List collections:
            collections = await connector.list_collections("mydb")
        """
        try:
            if not self.client:
                if not await self.connect():
                    raise DatabaseConnectionError("Failed to connect to MongoDB")

            db = self.client[database_name] if database_name else self.connection
            if db is None:
                raise ValueError("Database name must be provided or connection must specify a database")

            collections = []
            for coll_name in db.list_collection_names():
                db[coll_name]
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
            raise QueryError(f"Failed to list collections: {e}") from e

    async def get_collection_stats(self, database_name: str, collection_name: str) -> dict[str, Any]:
        """Get statistics for a specific collection."""
        try:
            if not self.client:
                if not await self.connect():
                    raise DatabaseConnectionError("Failed to connect to MongoDB")

            db = self.client[database_name] if database_name else self.connection
            if db is None:
                raise ValueError("Database name must be provided or connection must specify a database")

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
                "indexes": list(indexes),
                "capped": stats.get("capped", False),
                "sharded": "sharded" in stats,
                "shard_key": stats.get("shardKey", {}) if "sharded" in stats else None,
            }

        except Exception as e:
            logger.error(f"Failed to get stats for collection {database_name}.{collection_name}: {e}")
            raise QueryError(f"Failed to get collection stats: {e}") from e

    async def get_schema(self, **kwargs: Any) -> dict[str, Any]:
        """Get database schema (list of collections)."""
        collections = await self.get_tables()
        return {"database": self.connection_config.get("database", "admin"), "collections": collections}

    async def get_tables(self, **kwargs: Any) -> list[str]:
        """Get list of collections in the database."""
        db_name = self.connection_config.get("database", "admin")
        collections = await self.list_collections(db_name)
        return [c["name"] for c in collections]

    async def get_table_schema(self, table_name: str, **kwargs: Any) -> dict[str, Any]:
        """Get schema information (collection stats) for a collection."""
        db_name = self.connection_config.get("database", "admin")
        return await self.get_collection_stats(db_name, table_name)

    async def health_check(self) -> dict[str, Any]:
        """Perform a health check on the MongoDB connection."""
        try:
            if not self.client:
                if not await self.connect():
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

    async def get_performance_metrics(self) -> dict[str, Any]:
        """Get performance metrics from MongoDB."""
        try:
            if not self.client:
                if not await self.connect():
                    raise DatabaseConnectionError("Failed to connect to MongoDB")

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
            raise QueryError(f"Failed to get performance metrics: {e}") from e

    async def test_connection(self) -> dict[str, Any]:
        """Test the MongoDB connection."""
        start_time = datetime.now()
        try:
            if not self.client:
                if not await self.connect():
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
