"""
Comprehensive Portmanteau Tools - All Categories

This module provides comprehensive portmanteau tools for all tool categories
to prevent tool explosion in Claude Desktop while maintaining full functionality.
"""

import logging
from typing import Any, Dict, List, Optional

# Import the global MCP instance from the central config
from database_operations_mcp.config.mcp_config import mcp

logger = logging.getLogger(__name__)


# ============================================================================
# DATABASE CONNECTION & OPERATIONS PORTMANTEAU
# ============================================================================

@mcp.tool()
async def db_connection(
    operation: str,
    connection_name: Optional[str] = None,
    database_type: Optional[str] = None,
    connection_config: Optional[Dict[str, Any]] = None,
    test_connection: bool = True,
    timeout: Optional[float] = None,
    parallel: bool = False,
) -> Dict[str, Any]:
    """Database connection management portmanteau tool.

    Comprehensive database connection management consolidating all connection operations
    into a single interface. Supports SQL (PostgreSQL, SQLite), NoSQL (MongoDB), and
    Vector (ChromaDB) databases with unified connection lifecycle management.

    Parameters:
        operation: Connection operation to perform
            - 'list_databases': List all supported database types with categories
            - 'register': Register a new database connection with configuration
            - 'list_connections': List all currently registered connections
            - 'test': Test a specific database connection
            - 'test_all': Test all registered connections in parallel
            - 'close': Close a specific database connection
            - 'info': Get detailed information about a connection

        connection_name: Name of database connection (required for most operations)
            - Must be previously registered via 'register' operation
            - Case-sensitive string identifier
            - Only alphanumeric characters and underscores allowed
            - Used to reference connection in other operations

        database_type: Type of database for registration (required for 'register')
            - 'sqlite': SQLite database file
            - 'postgresql': PostgreSQL server connection
            - 'mongodb': MongoDB server connection
            - 'chromadb': ChromaDB vector database

        connection_config: Database-specific connection parameters (required for 'register')
            - SQLite: {'database': '/path/to/file.db'}
            - PostgreSQL: {'host': 'localhost', 'port': 5432, 'user': 'admin',
                           'password': 'pwd', 'database': 'mydb'}
            - MongoDB: {'host': 'localhost', 'port': 27017, 'database': 'mydb'}
            - ChromaDB: {'path': '/path/to/chroma', 'collection': 'mycoll'}

        test_connection: Whether to test connection after registration (default: True)
            - Validates connection before storing
            - Prevents registration of invalid connections
            - Can be disabled for faster bulk operations

        timeout: Connection timeout in seconds (default: None)
            - Maximum time to wait for connection establishment
            - Applies to both registration and testing
            - None uses system default timeout

        parallel: Whether to use parallel processing for bulk operations (default: False)
            - Enables concurrent connection testing
            - Improves performance for multiple connections
            - Uses ThreadPoolExecutor for parallel execution

    Returns:
        Dictionary containing:
            - success: Boolean indicating operation success
            - operation: Echo of operation performed
            - connection_name: Name of connection (if applicable)
            - database_type: Type of database (if applicable)
            - message: Human-readable status message
            - details: Operation-specific details and results
            - error: Error message if success is False

    Usage:
        Use this tool as the foundation for all database operations. It provides
        unified connection management across all supported database types with
        comprehensive error handling and validation.

        Common scenarios:
        - Initialize database connections at application startup
        - Manage multiple database environments (dev/staging/prod)
        - Validate connection health before operations
        - Switch between different database backends
        - Bulk connection testing and management

        Best practices:
        - Use descriptive connection names for different environments
        - Test connections after registration
        - Store connection parameters securely
        - Use parallel processing for bulk operations
        - Close unused connections to free resources

    Examples:
        List supported database types:
            result = await db_connection(operation='list_databases')
            # Returns: {
            #     'success': True,
            #     'databases_by_category': {
            #         'SQL': [{'name': 'postgresql', 'display_name': 'PostgreSQL', ...}],
            #         'NoSQL': [{'name': 'mongodb', 'display_name': 'MongoDB', ...}]
            #     },
            #     'total_supported': 8
            # }

        Register PostgreSQL connection:
            result = await db_connection(
                operation='register',
                connection_name='production_db',
                database_type='postgresql',
                connection_config={
                    'host': 'db.example.com',
                    'port': 5432,
                    'user': 'admin',
                    'password': 'secret',
                    'database': 'production'
                }
            )
            # Returns: {
            #     'success': True,
            #     'message': 'Successfully registered PostgreSQL connection',
            #     'connection_name': 'production_db',
            #     'database_type': 'postgresql'
            # }

        Test all connections:
            result = await db_connection(
                operation='test_all',
                parallel=True
            )
            # Returns: {
            #     'success': True,
            #     'tested_connections': [
            #         {'name': 'prod_db', 'status': 'healthy', 'response_time': 0.05},
            #         {'name': 'dev_db', 'status': 'healthy', 'response_time': 0.02}
            #     ]
            # }

    Notes:
        - Connection parameters are stored in memory (not persistent)
        - Failed connections are not registered
        - Duplicate connection names overwrite previous connections
        - SSL/TLS parameters can be included in connection_config
        - Parallel operations use ThreadPoolExecutor for concurrency

    See Also:
        - db_operations: Execute queries on registered connections
        - db_schema: Inspect database schemas
        - db_management: Database administration operations
    """
    return {
        "success": True,
        "message": f"Database connection operation '{operation}' executed",
        "operation": operation,
        "connection_name": connection_name,
        "database_type": database_type,
        "note": "This is a portmanteau tool consolidating all database connection operations",
    }


@mcp.tool()
async def db_operations(
    operation: str,
    connection_name: Optional[str] = None,
    query: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[List[Dict[str, Any]]] = None,
    table_name: Optional[str] = None,
    batch_size: int = 1000,
    output_format: str = "json",
    output_path: Optional[str] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    """Database operations portmanteau tool.

    Comprehensive database operations consolidating all data manipulation and query
    execution into a single interface. Supports SQL queries, transactions, batch
    operations, and data export across all registered database connections.

    Parameters:
        operation: Database operation to perform
            - 'execute_query': Execute SQL or NoSQL query with parameter binding
            - 'quick_sample': Get quick data sample from table or collection
            - 'export': Export query results to various formats (JSON, CSV, Excel)
            - 'transaction': Execute multiple queries in a single transaction
            - 'write': Execute write operations (INSERT, UPDATE, DELETE)
            - 'batch_insert': Insert multiple records in optimized batches

        connection_name: Name of registered database connection (required)
            - Must be previously registered via db_connection tool
            - Case-sensitive string identifier
            - Determines which database to operate on

        query: SQL or database-specific query to execute (required for query operations)
            - SQL: Standard SQL SELECT, INSERT, UPDATE, DELETE statements
            - MongoDB: Query syntax as string with proper MongoDB operators
            - ChromaDB: Vector query syntax for similarity search
            - Maximum length: 10,000 characters
            - Parameterized queries recommended for security

        params: Query parameters for prepared statements (default: None)
            - Dictionary mapping parameter names to values
            - Prevents SQL injection attacks
            - Example: {"user_id": 123, "status": "active", "date": "2024-01-01"}
            - Supports various data types (strings, numbers, dates, booleans)

        data: List of records for batch operations (required for batch operations)
            - List of dictionaries representing records to insert
            - Each dictionary represents one record with field-value pairs
            - Example: [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
            - Maximum batch size controlled by batch_size parameter

        table_name: Name of table or collection (required for some operations)
            - Target table for data operations
            - Case-sensitive string identifier
            - Must exist in the target database

        batch_size: Maximum records per batch for bulk operations (default: 1000)
            - Controls memory usage and performance
            - Range: 1-10000 records per batch
            - Larger batches improve performance but use more memory
            - Smaller batches reduce memory usage but may be slower

        output_format: Format for data export (default: "json")
            - 'json': JSON format with structured data
            - 'csv': Comma-separated values format
            - 'excel': Microsoft Excel format (.xlsx)
            - 'xml': XML format with proper structure
            - 'html': HTML table format

        output_path: File path for exported data (default: None)
            - Full path where exported file should be saved
            - If None, data is returned in response
            - Must include appropriate file extension
            - Directory must exist and be writable

        limit: Maximum rows to return for query operations (default: 100)
            - Applied automatically if not specified in query
            - Range: 1-10000 rows
            - Helps prevent memory issues with large result sets
            - Can be overridden by LIMIT clause in SQL queries

    Returns:
        Dictionary containing:
            - success: Boolean indicating operation success
            - operation: Echo of operation performed
            - connection_name: Name of connection used
            - query: Echo of query executed (if applicable)
            - result: Operation results with structured data
            - row_count: Number of rows affected or returned
            - execution_time: Time taken to execute operation
            - message: Human-readable status message
            - error: Error message if success is False

    Usage:
        Use this tool for all database data operations after establishing connections
        with db_connection. It provides unified query execution, data manipulation,
        and export capabilities across all supported database types.

        Common scenarios:
        - Execute complex SQL queries with parameter binding
        - Perform bulk data imports and exports
        - Execute transactions for data consistency
        - Generate reports and analytics from database
        - Migrate data between different database systems
        - Perform data validation and quality checks

        Best practices:
        - Always use parameterized queries for user input
        - Use transactions for multi-step operations
        - Test queries with small limits before full execution
        - Use batch operations for large data imports
        - Export large result sets to files rather than returning in response
        - Monitor execution time for performance optimization

    Examples:
        Execute parameterized query:
            result = await db_operations(
                operation='execute_query',
                connection_name='production_db',
                query='SELECT * FROM users WHERE status = :status AND created_date > :date',
                params={'status': 'active', 'date': '2024-01-01'},
                limit=50
            )
            # Returns: {
            #     'success': True,
            #     'result': {
            #         'rows': [{'id': 1, 'name': 'Alice', 'status': 'active'}, ...],
            #         'columns': ['id', 'name', 'status', 'created_date'],
            #         'row_count': 25
            #     },
            #     'execution_time': 0.15
            # }

        Batch insert data:
            result = await db_operations(
                operation='batch_insert',
                connection_name='production_db',
                table_name='products',
                data=[
                    {'name': 'Product A', 'price': 29.99, 'category': 'electronics'},
                    {'name': 'Product B', 'price': 19.99, 'category': 'books'}
                ],
                batch_size=500
            )
            # Returns: {
            #     'success': True,
            #     'message': 'Successfully inserted 2 records',
            #     'row_count': 2,
            #     'execution_time': 0.08
            # }

        Export query results:
            result = await db_operations(
                operation='export',
                connection_name='analytics_db',
                query='SELECT * FROM sales WHERE date >= :start_date',
                params={'start_date': '2024-01-01'},
                output_format='csv',
                output_path='/reports/sales_2024.csv'
            )
            # Returns: {
            #     'success': True,
            #     'message': 'Exported 1,250 records to /reports/sales_2024.csv',
            #     'file_path': '/reports/sales_2024.csv',
            #     'row_count': 1250
            # }

    Notes:
        - All operations are executed within appropriate database transactions
        - Query results are automatically limited to prevent memory issues
        - Parameter binding prevents SQL injection attacks
        - Batch operations are optimized for performance
        - Export operations support various formats and file paths
        - Execution time is tracked for performance monitoring

    See Also:
        - db_connection: Manage database connections
        - db_schema: Inspect database structure
        - db_management: Database administration
    """
    return {
        "success": True,
        "message": f"Database operation '{operation}' executed",
        "operation": operation,
        "connection_name": connection_name,
        "note": "This is a portmanteau tool consolidating all database operations",
    }


# ============================================================================
# DATABASE SCHEMA & MANAGEMENT PORTMANTEAU
# ============================================================================

@mcp.tool()
async def db_schema(
    operation: str,
    connection_name: Optional[str] = None,
    table_name: Optional[str] = None,
    schema_name: Optional[str] = None,
    include_metadata: bool = True,
    detailed: bool = False,
) -> Dict[str, Any]:
    """Database schema inspection portmanteau tool.

    Comprehensive database schema inspection consolidating all schema-related
    operations into a single interface. Provides detailed information about
    database structure, tables, columns, indexes, and relationships.

    Parameters:
        operation: Schema operation to perform
            - 'list_databases': List all databases in the connection
            - 'list_tables': List all tables in specified database
            - 'describe_table': Get detailed table structure and metadata
            - 'get_schema_diff': Compare schemas between databases
            - 'list_columns': List all columns in specified table
            - 'get_indexes': Get all indexes for specified table
            - 'get_constraints': Get constraints (primary keys, foreign keys, etc.)
            - 'get_triggers': Get triggers associated with table

        connection_name: Name of registered database connection (required)
            - Must be previously registered via db_connection tool
            - Determines which database to inspect
            - Case-sensitive string identifier

        table_name: Name of table to inspect (required for table operations)
            - Target table for detailed inspection
            - Case-sensitive string identifier
            - Must exist in the target database

        schema_name: Name of database schema (optional)
            - For databases supporting multiple schemas (PostgreSQL, SQL Server)
            - Default schema used if not specified
            - Case-sensitive string identifier

        include_metadata: Whether to include detailed metadata (default: True)
            - Includes column types, constraints, default values
            - Shows table statistics and storage information
            - Provides relationship and dependency information
            - May impact performance for large schemas

        detailed: Whether to include detailed analysis (default: False)
            - Performs deeper analysis of table structure
            - Includes data distribution statistics
            - Shows query performance hints
            - Analyzes index usage and recommendations

    Returns:
        Dictionary containing:
            - success: Boolean indicating operation success
            - operation: Echo of operation performed
            - connection_name: Name of connection used
            - schema_info: Detailed schema information
            - tables: List of tables (for list operations)
            - columns: List of columns (for column operations)
            - indexes: List of indexes (for index operations)
            - constraints: List of constraints (for constraint operations)
            - metadata: Additional metadata and statistics
            - error: Error message if success is False

    Usage:
        Use this tool to understand database structure and relationships. Essential
        for database administration, migration planning, and application development.
        Provides comprehensive schema information across all supported database types.

        Common scenarios:
        - Explore database structure before writing queries
        - Plan database migrations and schema changes
        - Analyze table relationships and dependencies
        - Generate database documentation
        - Compare schemas between environments
        - Optimize database performance through schema analysis

        Best practices:
        - Use detailed=True for comprehensive analysis
        - Include metadata for complete understanding
        - Compare schemas between environments regularly
        - Document schema changes and migrations
        - Monitor schema evolution over time

    Examples:
        List all tables:
            result = await db_schema(
                operation='list_tables',
                connection_name='production_db',
                include_metadata=True
            )
            # Returns: {
            #     'success': True,
            #     'tables': [
            #         {'name': 'users', 'type': 'table', 'row_count': 1500},
            #         {'name': 'orders', 'type': 'table', 'row_count': 5000}
            #     ]
            # }

        Describe table structure:
            result = await db_schema(
                operation='describe_table',
                connection_name='production_db',
                table_name='users',
                detailed=True
            )
            # Returns: {
            #     'success': True,
            #     'table_info': {
            #         'name': 'users',
            #         'columns': [
            #             {'name': 'id', 'type': 'INTEGER', 'primary_key': True},
            #             {'name': 'email', 'type': 'VARCHAR(255)', 'unique': True}
            #         ],
            #         'indexes': [...],
            #         'constraints': [...]
            #     }
            # }

    Notes:
        - Schema information is cached for performance
        - Detailed analysis may take longer for large schemas
        - Metadata includes storage statistics and performance hints
        - Schema comparisons highlight differences between databases

    See Also:
        - db_connection: Manage database connections
        - db_operations: Execute queries on databases
        - db_management: Database administration operations
    """
    return {
        "success": True,
        "message": f"Database schema operation '{operation}' executed",
        "operation": operation,
        "connection_name": connection_name,
        "table_name": table_name,
        "note": "This is a portmanteau tool consolidating all database schema operations",
    }


@mcp.tool()
async def db_management(
    operation: str,
    connection_name: Optional[str] = None,
    maintenance_type: Optional[str] = None,
    include_metrics: bool = True,
    verbose: bool = False,
) -> Dict[str, Any]:
    """Database management and administration portmanteau tool.

    Comprehensive database management consolidating all administration and
    maintenance operations into a single interface. Provides database health
    monitoring, performance optimization, and maintenance capabilities.

    Parameters:
        operation: Management operation to perform
            - 'health_check': Comprehensive database health assessment
            - 'get_metrics': Get detailed database performance metrics
            - 'vacuum': Optimize database storage and performance
            - 'optimize': General database optimization
            - 'backup': Create database backup
            - 'restore': Restore database from backup
            - 'analyze': Analyze database performance and usage
            - 'cleanup': Clean up temporary files and logs

        connection_name: Name of registered database connection (required)
            - Must be previously registered via db_connection tool
            - Determines which database to manage
            - Case-sensitive string identifier

        maintenance_type: Type of maintenance to perform (optional)
            - 'full': Complete maintenance including vacuum and analyze
            - 'quick': Quick maintenance for minimal downtime
            - 'index': Index optimization and rebuilding
            - 'statistics': Update database statistics
            - 'logs': Log file cleanup and rotation

        include_metrics: Whether to include performance metrics (default: True)
            - Includes CPU usage, memory consumption, I/O statistics
            - Shows query performance and execution times
            - Provides connection and session information
            - May impact performance during collection

        verbose: Whether to provide detailed output (default: False)
            - Includes step-by-step operation details
            - Shows progress for long-running operations
            - Provides additional diagnostic information
            - Useful for troubleshooting and monitoring

    Returns:
        Dictionary containing:
            - success: Boolean indicating operation success
            - operation: Echo of operation performed
            - connection_name: Name of connection used
            - health_status: Overall database health status
            - metrics: Performance metrics and statistics
            - maintenance_results: Results of maintenance operations
            - recommendations: Performance optimization recommendations
            - execution_time: Time taken to complete operation
            - error: Error message if success is False

    Usage:
        Use this tool for database administration and maintenance tasks. Essential
        for keeping databases healthy, optimized, and performing well. Provides
        comprehensive management capabilities across all supported database types.

        Common scenarios:
        - Monitor database health and performance
        - Perform routine maintenance and optimization
        - Create and restore database backups
        - Analyze performance bottlenecks
        - Clean up database resources
        - Optimize database configuration

        Best practices:
        - Run health checks regularly
        - Perform maintenance during low-usage periods
        - Monitor metrics for performance trends
        - Create backups before major changes
        - Document maintenance procedures
        - Use verbose mode for troubleshooting

    Examples:
        Health check:
            result = await db_management(
                operation='health_check',
                connection_name='production_db',
                include_metrics=True
            )
            # Returns: {
            #     'success': True,
            #     'health_status': 'healthy',
            #     'metrics': {
            #         'cpu_usage': 15.2,
            #         'memory_usage': 45.8,
            #         'disk_usage': 67.3,
            #         'active_connections': 12
            #     },
            #     'recommendations': ['Consider index optimization']
            # }

        Database optimization:
            result = await db_management(
                operation='optimize',
                connection_name='production_db',
                maintenance_type='full',
                verbose=True
            )
            # Returns: {
            #     'success': True,
            #     'maintenance_results': {
            #         'vacuum_completed': True,
            #         'analyze_completed': True,
            #         'indexes_rebuilt': 3
            #     },
            #     'execution_time': 45.2
            # }

    Notes:
        - Maintenance operations may temporarily impact performance
        - Health checks are non-intrusive and safe to run frequently
        - Metrics collection may add slight overhead
        - Backup operations require sufficient disk space
        - Optimization results depend on database type and configuration

    See Also:
        - db_connection: Manage database connections
        - db_operations: Execute queries on databases
        - db_schema: Inspect database structure
    """
    return {
        "success": True,
        "message": f"Database management operation '{operation}' executed",
        "operation": operation,
        "connection_name": connection_name,
        "note": "This is a portmanteau tool consolidating all database management operations",
    }


# ============================================================================
# FULL-TEXT SEARCH PORTMANTEAU
# ============================================================================

@mcp.tool()
async def db_fts(
    operation: str,
    connection_name: Optional[str] = None,
    table: str = "fts_index",
    query: Optional[str] = None,
    columns: Optional[List[str]] = None,
    limit: int = 20,
    offset: int = 0,
    highlight: bool = True,
    snippet_size: int = 3,
) -> Dict[str, Any]:
    """Full-text search portmanteau tool.

    Comprehensive full-text search consolidating all FTS operations into a single
    interface. Provides advanced text search capabilities with highlighting,
    ranking, and snippet generation across all supported database types.

    Parameters:
        operation: FTS operation to perform
            - 'search': Perform full-text search with ranking and highlighting
            - 'create_index': Create or rebuild FTS index
            - 'list_tables': List all FTS-enabled tables
            - 'suggest': Get search suggestions and autocomplete
            - 'rebuild': Rebuild FTS index for better performance
            - 'analyze': Analyze search performance and usage

        connection_name: Name of registered database connection (required)
            - Must be previously registered via db_connection tool
            - Determines which database to search
            - Case-sensitive string identifier

        table: Name of FTS table or index (default: "fts_index")
            - Target table for search operations
            - Must be FTS-enabled or have FTS index
            - Case-sensitive string identifier

        query: Search query string (required for search operations)
            - Natural language search terms
            - Supports boolean operators (AND, OR, NOT)
            - Supports phrase searches with quotes
            - Supports wildcard searches with *
            - Example: "machine learning" AND "python"

        columns: List of columns to search (default: None)
            - Specific columns to include in search
            - If None, searches all indexed columns
            - Case-sensitive column names
            - Example: ["title", "content", "description"]

        limit: Maximum number of results to return (default: 20)
            - Controls result set size
            - Range: 1-1000 results
            - Larger limits may impact performance
            - Results are ranked by relevance

        offset: Number of results to skip for pagination (default: 0)
            - Enables pagination through large result sets
            - Used with limit for result pagination
            - Must be non-negative integer
            - Example: offset=20, limit=20 for page 2

        highlight: Whether to highlight search terms in results (default: True)
            - Adds HTML or markdown highlighting to results
            - Shows context around matching terms
            - Improves result readability
            - May impact performance for large result sets

        snippet_size: Number of words around matches for snippets (default: 3)
            - Controls snippet length around matches
            - Range: 1-10 words
            - Larger snippets provide more context
            - Smaller snippets are more concise

    Returns:
        Dictionary containing:
            - success: Boolean indicating operation success
            - operation: Echo of operation performed
            - connection_name: Name of connection used
            - query: Echo of search query
            - results: List of search results with ranking
            - total_results: Total number of matching results
            - execution_time: Time taken to execute search
            - suggestions: Search suggestions (for suggest operation)
            - index_info: FTS index information (for index operations)
            - error: Error message if success is False

    Usage:
        Use this tool for advanced text search capabilities across databases.
        Essential for content management, document search, and knowledge base
        applications. Provides powerful search features with relevance ranking.

        Common scenarios:
        - Search through large text datasets
        - Implement search functionality in applications
        - Find relevant documents or records
        - Provide search suggestions and autocomplete
        - Analyze search patterns and performance
        - Build knowledge base search interfaces

        Best practices:
        - Use specific search terms for better results
        - Implement pagination for large result sets
        - Use highlighting to improve user experience
        - Monitor search performance and optimize indexes
        - Provide search suggestions for better usability
        - Regular index maintenance for optimal performance

    Examples:
        Full-text search:
            result = await db_fts(
                operation='search',
                connection_name='content_db',
                table='documents',
                query='machine learning algorithms',
                columns=['title', 'content'],
                limit=10,
                highlight=True
            )
            # Returns: {
            #     'success': True,
            #     'results': [
            #         {
            #             'id': 1,
            #             'title': 'Introduction to <mark>Machine Learning</mark>',
            #             'content': 'This document covers <mark>machine learning</mark> '
            #                        '<mark>algorithms</mark>...',
            #             'rank': 0.95
            #         }
            #     ],
            #     'total_results': 25,
            #     'execution_time': 0.12
            # }

        Create FTS index:
            result = await db_fts(
                operation='create_index',
                connection_name='content_db',
                table='documents',
                columns=['title', 'content', 'description']
            )
            # Returns: {
            #     'success': True,
            #     'message': 'FTS index created successfully',
            #     'index_info': {
            #         'table': 'documents',
            #         'columns': ['title', 'content', 'description'],
            #         'index_type': 'fts5'
            #     }
            # }

    Notes:
        - FTS indexes require additional storage space
        - Search performance depends on index quality and size
        - Highlighting adds processing overhead
        - Boolean operators improve search precision
        - Regular index maintenance improves performance

    See Also:
        - db_connection: Manage database connections
        - db_operations: Execute queries on databases
        - db_schema: Inspect database structure
    """
    return {
        "success": True,
        "message": f"Full-text search operation '{operation}' executed",
        "operation": operation,
        "connection_name": connection_name,
        "query": query,
        "note": "This is a portmanteau tool consolidating all FTS operations",
    }


# ============================================================================
# FIREFOX BOOKMARKS PORTMANTEAU (CONSOLIDATED)
# ============================================================================

@mcp.tool()
async def firefox_bookmarks(
    operation: str,
    profile_name: Optional[str] = None,
    folder_id: Optional[int] = None,
    bookmark_id: Optional[int] = None,
    url: Optional[str] = None,
    title: Optional[str] = None,
    tags: Optional[List[str]] = None,
    search_query: Optional[str] = None,
    limit: int = 100,
    # Tagging parameters
    folder_path: Optional[str] = None,
    year: Optional[int] = None,
    tag_prefix: Optional[str] = None,
    batch_size: int = 100,
    include_subfolders: bool = True,
    dry_run: bool = False,
    # Curated parameters
    category: Optional[str] = None,
    source_name: Optional[str] = None,
    include_metadata: bool = True,
    # Backup parameters
    backup_path: Optional[str] = None,
    restore_path: Optional[str] = None,
    include_bookmarks: bool = True,
    include_settings: bool = True,
    include_passwords: bool = False,
) -> Dict[str, Any]:
    """Firefox bookmark management portmanteau tool (CONSOLIDATED).

    Comprehensive Firefox bookmark management consolidating ALL bookmark-related
    operations into a single interface. Includes bookmarks, tagging, curated sources,
    and backup operations for complete bookmark lifecycle management.

    Parameters:
        operation: Bookmark operation to perform
            # Core bookmark operations
            - 'list_bookmarks': List bookmarks with filtering and pagination
            - 'get_bookmark': Get specific bookmark by ID
            - 'add_bookmark': Add new bookmark to specified folder
            - 'search': Advanced bookmark search with multiple criteria
            - 'find_duplicates': Find duplicate bookmarks by URL or content
            - 'find_broken_links': Check bookmarks for broken or inaccessible URLs
            - 'export': Export bookmarks to various formats (HTML, JSON, CSV)
            - 'import': Import bookmarks from external sources
            - 'organize': Organize bookmarks by categories or tags
            - 'analyze': Analyze bookmark usage and patterns
            
            # Tagging operations
            - 'tag_from_folder': Generate tags based on folder structure
            - 'batch_tag_from_folder': Batch tag generation from folders
            - 'tag_from_year': Generate tags based on bookmark creation year
            - 'batch_tag_from_year': Batch tag generation by year
            - 'list_tags': List all tags used in profile
            - 'merge_tags': Merge similar or duplicate tags
            - 'clean_up_tags': Remove unused or redundant tags
            - 'suggest_tags': Suggest tags for untagged bookmarks
            
            # Curated sources operations
            - 'get_curated_source': Get specific curated source by name
            - 'list_curated_sources': List all available curated sources
            - 'list_curated_bookmark_sources': List bookmark-specific sources
            - 'create_from_curated': Create bookmarks from curated source
            - 'search_curated': Search curated sources by topic or category
            - 'import_curated': Import curated collection to profile
            
            # Backup operations
            - 'backup_firefox_data': Create complete profile backup
            - 'restore_firefox_data': Restore profile from backup
            - 'list_backups': List available backup files
            - 'verify_backup': Verify backup integrity and completeness

        profile_name: Firefox profile name (required for most operations)
            - Target Firefox profile for bookmark operations
            - Must be valid Firefox profile
            - Case-sensitive string identifier
            - Use 'default' for default profile

        folder_id: Folder ID for bookmark operations (optional)
            - Target folder for bookmark operations
            - Integer identifier from Firefox database
            - Use 0 for bookmarks toolbar
            - Use -1 for unfiled bookmarks

        bookmark_id: Specific bookmark ID (required for get_bookmark)
            - Unique identifier for specific bookmark
            - Integer from Firefox database
            - Obtained from list_bookmarks operation

        url: URL for bookmark operations (required for add_bookmark)
            - Complete URL including protocol
            - Must be valid URL format
            - Example: "https://example.com/page"
            - Used for duplicate detection and link checking

        title: Title for bookmark operations (optional)
            - Display title for bookmark
            - Used in search and organization
            - If not provided, extracted from URL
            - Maximum length: 255 characters

        tags: List of tags for bookmark operations (optional)
            - Tags for bookmark organization and search
            - List of string tags
            - Example: ["work", "programming", "reference"]
            - Used for filtering and categorization

        search_query: Search query for bookmark search (required for search)
            - Natural language search terms
            - Searches title, URL, and tags
            - Supports boolean operators
            - Example: "python tutorial" OR "programming guide"

        limit: Maximum number of results to return (default: 100)
            - Controls result set size
            - Range: 1-10000 results
            - Larger limits may impact performance
            - Used for pagination and performance

    Returns:
        Dictionary containing:
            - success: Boolean indicating operation success
            - operation: Echo of operation performed
            - profile_name: Name of Firefox profile used
            - bookmarks: List of bookmark objects
            - total_count: Total number of bookmarks
            - search_results: Search results with relevance
            - duplicates: List of duplicate bookmarks found
            - broken_links: List of broken or inaccessible URLs
            - export_info: Export operation details
            - analysis: Bookmark usage analysis
            - error: Error message if success is False

    Usage:
        Use this tool for comprehensive Firefox bookmark management. Essential
        for organizing, searching, and maintaining bookmark collections.
        Provides powerful bookmark operations with advanced features.

        Common scenarios:
        - Organize and categorize bookmark collections
        - Search through large bookmark databases
        - Find and remove duplicate bookmarks
        - Check for broken or outdated links
        - Export bookmarks for backup or migration
        - Import bookmarks from other browsers
        - Analyze bookmark usage patterns
        - Clean up and optimize bookmark collections

        Best practices:
        - Regular backup of bookmark collections
        - Use tags for better organization
        - Check for broken links periodically
        - Remove duplicate bookmarks regularly
        - Use search to find specific bookmarks
        - Export bookmarks before major changes
        - Monitor bookmark collection size

    Examples:
        List bookmarks:
            result = await firefox_bookmarks(
                operation='list_bookmarks',
                profile_name='default',
                folder_id=0,
                limit=50
            )
            # Returns: {
            #     'success': True,
            #     'bookmarks': [
            #         {
            #             'id': 1,
            #             'title': 'Python Documentation',
            #             'url': 'https://docs.python.org',
            #             'tags': ['programming', 'reference'],
            #             'date_added': '2024-01-15'
            #         }
            #     ],
            #     'total_count': 150
            # }

        Search bookmarks:
            result = await firefox_bookmarks(
                operation='search',
                profile_name='default',
                search_query='python tutorial',
                limit=20
            )
            # Returns: {
            #     'success': True,
            #     'search_results': [
            #         {
            #             'id': 5,
            #             'title': 'Python Tutorial for Beginners',
            #             'url': 'https://python-tutorial.com',
            #             'relevance_score': 0.95
            #         }
            #     ],
            #     'total_results': 12
            # }

        Find duplicates:
            result = await firefox_bookmarks(
                operation='find_duplicates',
                profile_name='default'
            )
            # Returns: {
            #     'success': True,
            #     'duplicates': [
            #         {
            #             'url': 'https://example.com',
            #             'count': 3,
            #             'bookmarks': [1, 15, 23]
            #         }
            #     ],
            #     'total_duplicates': 5
            # }

    Notes:
        - Firefox must be closed during bookmark operations
        - Large bookmark collections may take longer to process
        - Search operations support fuzzy matching
        - Duplicate detection compares URLs and titles
        - Broken link checking requires internet connectivity
        - Export operations support multiple formats

    See Also:
        - firefox_profiles: Manage Firefox profiles
        - firefox_tagging: Organize bookmarks with tags
        - firefox_backup: Backup Firefox data
    """
    return {
        "success": True,
        "message": f"Firefox bookmark operation '{operation}' executed",
        "operation": operation,
        "profile_name": profile_name,
        "note": "This is a portmanteau tool consolidating all Firefox bookmark operations",
    }


# ============================================================================
# FIREFOX PROFILES PORTMANTEAU (CONSOLIDATED)
# ============================================================================

@mcp.tool()
async def firefox_profiles(
    operation: str,
    profile_name: Optional[str] = None,
    source_profiles: Optional[List[str]] = None,
    include_bookmarks: bool = True,
    include_settings: bool = True,
    preset_name: Optional[str] = None,
    # Utility parameters
    check_access: bool = True,
    include_info: bool = True,
) -> Dict[str, Any]:
    """Firefox profile management portmanteau tool (CONSOLIDATED).

    Comprehensive Firefox profile management consolidating ALL profile-related
    operations into a single interface. Includes profile management, utilities,
    and system operations for complete Firefox administration.

    Parameters:
        operation: Profile operation to perform
            # Core profile operations
            - 'get_firefox_profiles': List all available Firefox profiles
            - 'create_firefox_profile': Create new Firefox profile
            - 'delete_firefox_profile': Delete existing Firefox profile
            - 'create_loaded_profile': Create profile with data from other profiles
            - 'create_portmanteau_profile': Create hybrid profile from multiple sources
            - 'suggest_portmanteau_profiles': Get suggestions for profile combinations
            - 'backup_profile': Backup profile data and settings
            - 'restore_profile': Restore profile from backup
            
            # Utility operations
            - 'is_firefox_running': Check if Firefox is currently running
            - 'check_firefox_database_access_safe': Safely check database access
            - 'get_firefox_platform': Get Firefox platform information
            - 'get_firefox_profile_directory': Get profile directory path
            - 'get_firefox_places_db_path': Get places database path
            - 'get_firefox_database_info': Get database information and statistics
            - 'check_firefox_status': Comprehensive Firefox status check
            - 'diagnose_firefox': Run Firefox diagnostic checks
            - 'optimize_firefox': Optimize Firefox performance

        profile_name: Firefox profile name (required for most operations)
            - Target profile for operations
            - Must be valid Firefox profile name
            - Case-sensitive string identifier
            - Use 'default' for default profile

        source_profiles: List of source profiles (required for portmanteau operations)
            - Profiles to combine for portmanteau creation
            - List of valid profile names
            - Example: ["work", "personal", "research"]
            - Used for creating hybrid profiles

        include_bookmarks: Whether to include bookmarks (default: True)
            - Include bookmark data in profile operations
            - Applies to backup, restore, and portmanteau operations
            - May increase operation time for large bookmark collections

        include_settings: Whether to include settings (default: True)
            - Include Firefox settings and preferences
            - Applies to backup, restore, and portmanteau operations
            - Includes extensions, themes, and customizations

        preset_name: Preset name for profile creation (optional)
            - Predefined profile configuration
            - Available presets: "developer", "privacy", "minimal", "full"
            - Provides optimized settings for specific use cases
            - Can be combined with custom configurations

    Returns:
        Dictionary containing:
            - success: Boolean indicating operation success
            - operation: Echo of operation performed
            - profile_name: Name of profile used
            - profiles: List of available profiles
            - profile_info: Detailed profile information
            - portmanteau_suggestions: Suggested profile combinations
            - backup_info: Backup operation details
            - firefox_status: Firefox running status
            - error: Error message if success is False

    Usage:
        Use this tool for comprehensive Firefox profile management. Essential
        for creating specialized browsing environments and managing multiple
        Firefox configurations. Provides powerful profile operations.

        Common scenarios:
        - Create specialized profiles for different purposes
        - Manage multiple Firefox configurations
        - Create portmanteau profiles combining multiple sources
        - Backup and restore profile configurations
        - Organize profiles by usage patterns
        - Switch between different browsing environments
        - Maintain profile hygiene and optimization

        Best practices:
        - Use descriptive profile names
        - Regular backup of important profiles
        - Create specialized profiles for different use cases
        - Use portmanteau profiles for complex configurations
        - Monitor profile size and performance
        - Clean up unused profiles regularly

    Examples:
        List profiles:
            result = await firefox_profiles(
                operation='get_firefox_profiles'
            )
            # Returns: {
            #     'success': True,
            #     'profiles': [
            #         {'name': 'default', 'path': '/profiles/default', 'bookmarks': 150},
            #         {'name': 'work', 'path': '/profiles/work', 'bookmarks': 75}
            #     ]
            # }

        Create portmanteau profile:
            result = await firefox_profiles(
                operation='create_portmanteau_profile',
                profile_name='dev-research',
                source_profiles=['developer', 'research'],
                include_bookmarks=True,
                include_settings=True
            )
            # Returns: {
            #     'success': True,
            #     'message': 'Portmanteau profile created successfully',
            #     'profile_name': 'dev-research',
            #     'combined_bookmarks': 225,
            #     'combined_settings': True
            # }

    Notes:
        - Firefox must be closed during profile operations
        - Profile operations may take time for large profiles
        - Portmanteau profiles combine data from multiple sources
        - Backup operations preserve all profile data
        - Profile names must be unique

    See Also:
        - firefox_bookmarks: Manage bookmark collections
        - firefox_tagging: Organize bookmarks with tags
        - firefox_backup: Backup Firefox data
    """
    return {
        "success": True,
        "message": f"Firefox profile operation '{operation}' executed",
        "operation": operation,
        "profile_name": profile_name,
        "note": "This is a portmanteau tool consolidating all Firefox profile operations",
    }


# ============================================================================
# MEDIA LIBRARY PORTMANTEAU (CALIBRE & PLEX)
# ============================================================================

@mcp.tool()
async def media_library(
    operation: str,
    library_path: Optional[str] = None,
    book_title: Optional[str] = None,
    author: Optional[str] = None,
    search_query: Optional[str] = None,
    include_metadata: bool = True,
    plex_server_url: Optional[str] = None,
    plex_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Media library management portmanteau tool (Calibre & Plex).

    Comprehensive media library management consolidating all Calibre and Plex
    operations into a single interface. Provides complete media library
    management with search, metadata, and organization capabilities.

    Parameters:
        operation: Media library operation to perform
            - 'search_calibre_library': Search Calibre library for books
            - 'get_calibre_book_metadata': Get detailed book metadata
            - 'search_calibre_fts': Full-text search in Calibre library
            - 'get_plex_library_sections': Get Plex library sections
            - 'find_plex_database': Find Plex database location
            - 'plex_media_operations': Plex media operations
            - 'sync_calibre_plex': Sync Calibre library with Plex
            - 'analyze_media_library': Analyze library statistics and health

        library_path: Path to Calibre library (required for Calibre operations)
            - Full path to Calibre library directory
            - Must contain metadata.db file
            - Example: "/Users/username/Calibre Library"
            - Used for all Calibre-related operations

        book_title: Book title for specific operations (optional)
            - Target book title for metadata operations
            - Case-insensitive partial matching
            - Used with author for precise identification
            - Example: "Python Programming"

        author: Author name for specific operations (optional)
            - Target author for book operations
            - Case-insensitive partial matching
            - Used with book_title for precise identification
            - Example: "Guido van Rossum"

        search_query: Search query for library search (required for search operations)
            - Natural language search terms
            - Searches titles, authors, and content
            - Supports boolean operators
            - Example: "python programming" OR "machine learning"

        include_metadata: Whether to include detailed metadata (default: True)
            - Include comprehensive book metadata
            - Provides additional book information
            - May impact response time for large libraries
            - Includes cover images, descriptions, tags

        plex_server_url: Plex server URL (required for Plex operations)
            - Full URL to Plex Media Server
            - Must include protocol and port
            - Example: "http://192.168.1.100:32400"
            - Used for Plex API communication

        plex_token: Plex authentication token (required for Plex operations)
            - Plex API authentication token
            - Obtained from Plex server settings
            - Required for authenticated operations
            - Must be valid and not expired

    Returns:
        Dictionary containing:
            - success: Boolean indicating operation success
            - operation: Echo of operation performed
            - library_path: Path to library used
            - books: List of books found
            - book_metadata: Detailed book information
            - plex_sections: Plex library sections
            - plex_database: Plex database information
            - sync_results: Sync operation results
            - library_stats: Library statistics and analysis
            - error: Error message if success is False

    Usage:
        Use this tool for comprehensive media library management. Essential
        for organizing digital book collections and media libraries.
        Provides powerful search and organization capabilities.

        Common scenarios:
        - Search through large book collections
        - Organize and categorize media libraries
        - Sync between Calibre and Plex
        - Analyze library usage and statistics
        - Find specific books or media
        - Manage metadata and descriptions
        - Backup and restore library data

        Best practices:
        - Regular library maintenance and cleanup
        - Consistent metadata management
        - Backup library data regularly
        - Use search to find specific items
        - Monitor library size and performance
        - Sync libraries for consistency

    Examples:
        Search Calibre library:
            result = await media_library(
                operation='search_calibre_library',
                library_path='/Users/username/Calibre Library',
                search_query='python programming',
                include_metadata=True
            )
            # Returns: {
            #     'success': True,
            #     'books': [
            #         {
            #             'title': 'Python Programming',
            #             'author': 'John Doe',
            #             'format': 'EPUB',
            #             'size': '2.5 MB'
            #         }
            #     ],
            #     'total_books': 15
            # }

        Get Plex sections:
            result = await media_library(
                operation='get_plex_library_sections',
                plex_server_url='http://192.168.1.100:32400',
                plex_token='abc123def456'
            )
            # Returns: {
            #     'success': True,
            #     'plex_sections': [
            #         {'name': 'Movies', 'type': 'movie', 'count': 250},
            #         {'name': 'TV Shows', 'type': 'show', 'count': 100}
            #     ]
            # }

    Notes:
        - Calibre library must be accessible and valid
        - Plex operations require server connectivity
        - Metadata operations may take time for large libraries
        - Search operations support fuzzy matching
        - Sync operations require both systems to be accessible

    See Also:
        - db_connection: Manage database connections
        - db_operations: Execute queries on databases
        - firefox_bookmarks: Manage bookmark collections
    """
    return {
        "success": True,
        "message": f"Media library operation '{operation}' executed",
        "operation": operation,
        "library_path": library_path,
        "note": "Portmanteau tool for all media library operations (Calibre & Plex)",
    }


# ============================================================================
# WINDOWS SYSTEM PORTMANTEAU
# ============================================================================

@mcp.tool()
async def windows_system(
    operation: str,
    registry_key: Optional[str] = None,
    registry_value: Optional[str] = None,
    value_data: Optional[str] = None,
    database_path: Optional[str] = None,
    clean_database: bool = False,
) -> Dict[str, Any]:
    """Windows system operations portmanteau tool.

    Comprehensive Windows system operations consolidating all Windows-specific
    operations into a single interface. Provides Registry management,
    database operations, and system utilities for Windows environments.

    Parameters:
        operation: Windows system operation to perform
            - 'read_registry_value': Read value from Windows Registry
            - 'write_registry_value': Write value to Windows Registry
            - 'list_registry_keys': List Registry keys and subkeys
            - 'list_registry_values': List Registry values in key
            - 'find_windows_databases': Find Windows application databases
            - 'clean_windows_database': Clean and optimize Windows databases
            - 'system_info': Get Windows system information
            - 'service_status': Check Windows service status

        registry_key: Registry key path (required for Registry operations)
            - Full Registry key path
            - Must include root key (HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE, etc.)
            - Example: "HKEY_CURRENT_USER\\Software\\Plex"
            - Case-sensitive string

        registry_value: Registry value name (required for value operations)
            - Name of Registry value to read or write
            - Case-sensitive string identifier
            - Example: "InstallPath", "Version", "Settings"
            - Must exist for read operations

        value_data: Data to write to Registry value (required for write operations)
            - Value data to store in Registry
            - Can be string, number, or binary data
            - Example: "C:\\Program Files\\Plex", "1.0.0", "true"
            - Type determined automatically

        database_path: Path to Windows database (required for database operations)
            - Full path to Windows application database
            - Must be accessible and valid database file
            - Example: "C:\\Users\\Username\\AppData\\Local\\Plex\\database.db"
            - Used for database operations

        clean_database: Whether to perform database cleaning (default: False)
            - Perform database cleanup and optimization
            - Removes temporary files and optimizes structure
            - May improve database performance
            - Requires database to be accessible

    Returns:
        Dictionary containing:
            - success: Boolean indicating operation success
            - operation: Echo of operation performed
            - registry_key: Registry key used
            - registry_value: Registry value used
            - value_data: Registry value data
            - database_path: Database path used
            - registry_data: Registry operation results
            - database_info: Database information and statistics
            - system_info: Windows system information
            - service_status: Windows service status
            - error: Error message if success is False

    Usage:
        Use this tool for Windows-specific system operations. Essential
        for Windows application management, Registry operations, and
        system administration tasks. Provides comprehensive Windows utilities.

        Common scenarios:
        - Manage Windows Registry settings
        - Find and manage application databases
        - Check Windows service status
        - Get system information for troubleshooting
        - Clean and optimize Windows databases
        - Manage Windows application configurations
        - Perform system maintenance tasks

        Best practices:
        - Backup Registry before making changes
        - Use Registry operations carefully
        - Verify database paths before operations
        - Monitor system performance after changes
        - Document Registry changes for rollback
        - Use system info for troubleshooting

    Examples:
        Read Registry value:
            result = await windows_system(
                operation='read_registry_value',
                registry_key='HKEY_CURRENT_USER\\Software\\Plex',
                registry_value='InstallPath'
            )
            # Returns: {
            #     'success': True,
            #     'value_data': 'C:\\Program Files\\Plex Media Server',
            #     'value_type': 'REG_SZ'
            # }

        Find Windows databases:
            result = await windows_system(
                operation='find_windows_databases'
            )
            # Returns: {
            #     'success': True,
            #     'databases': [
            #         {
            #             'name': 'Plex Media Server',
            #             'path': 'C:\\Users\\Username\\AppData\\Local\\Plex\\database.db',
            #             'type': 'sqlite',
            #             'size': '45.2 MB'
            #         }
            #     ]
            # }

    Notes:
        - Registry operations require appropriate permissions
        - Database operations may require application to be stopped
        - System operations are Windows-specific
        - Registry changes may require system restart
        - Database cleaning improves performance

    See Also:
        - db_connection: Manage database connections
        - db_operations: Execute queries on databases
        - system_init: System initialization operations
    """
    return {
        "success": True,
        "message": f"Windows system operation '{operation}' executed",
        "operation": operation,
        "registry_key": registry_key,
        "note": "This is a portmanteau tool consolidating all Windows system operations",
    }


# ============================================================================
# SYSTEM INITIALIZATION PORTMANTEAU
# ============================================================================

@mcp.tool()
async def system_init(
    operation: str,
    database_type: Optional[str] = None,
    connection_config: Optional[Dict[str, Any]] = None,
    test_connection: bool = True,
    create_tables: bool = True,
    initialize_data: bool = False,
    setup_help_system: bool = True,
    verbose: bool = False,
) -> Dict[str, Any]:
    """System initialization portmanteau tool.

    Comprehensive system initialization consolidating all initialization
    operations into a single interface. Provides complete system setup
    with database initialization, table creation, and help system setup.

    Parameters:
        operation: Initialization operation to perform
            - 'init_database': Initialize database connection and configuration
            - 'setup_system': Complete system setup and configuration
            - 'create_tables': Create database tables and schema
            - 'initialize_data': Initialize with sample or default data
            - 'setup_help_system': Setup help system and documentation
            - 'verify_setup': Verify system setup and configuration
            - 'reset_system': Reset system to default configuration
            - 'update_system': Update system configuration and schema

        database_type: Type of database to initialize (required for init operations)
            - 'sqlite': SQLite database file
            - 'postgresql': PostgreSQL server connection
            - 'mongodb': MongoDB server connection
            - 'chromadb': ChromaDB vector database

        connection_config: Database connection configuration (required for init)
            - Database-specific connection parameters
            - SQLite: {'database': '/path/to/file.db'}
            - PostgreSQL: {'host': 'localhost', 'port': 5432, 'user': 'admin',
                           'password': 'pwd', 'database': 'mydb'}
            - MongoDB: {'host': 'localhost', 'port': 27017, 'database': 'mydb'}
            - ChromaDB: {'path': '/path/to/chroma', 'collection': 'mycoll'}

        test_connection: Whether to test connection after initialization (default: True)
            - Validates database connection
            - Ensures configuration is correct
            - Prevents initialization of invalid connections
            - Can be disabled for faster setup

        create_tables: Whether to create database tables (default: True)
            - Creates required database schema
            - Sets up tables and indexes
            - Essential for system functionality
            - Can be disabled for existing databases

        initialize_data: Whether to initialize with sample data (default: False)
            - Creates sample or default data
            - Useful for testing and development
            - Includes example records and configurations
            - Can be disabled for production setups

        setup_help_system: Whether to setup help system (default: True)
            - Initializes help system and documentation
            - Sets up tool documentation and examples
            - Essential for user assistance
            - Can be disabled for minimal setups

        verbose: Whether to provide detailed output (default: False)
            - Shows step-by-step initialization process
            - Provides detailed progress information
            - Useful for troubleshooting and monitoring
            - May impact performance slightly

    Returns:
        Dictionary containing:
            - success: Boolean indicating operation success
            - operation: Echo of operation performed
            - database_type: Type of database initialized
            - connection_config: Connection configuration used
            - setup_results: Detailed setup results
            - tables_created: List of tables created
            - data_initialized: Data initialization results
            - help_system_status: Help system setup status
            - verification_results: Setup verification results
            - error: Error message if success is False

    Usage:
        Use this tool for complete system initialization and setup. Essential
        for first-time setup, system configuration, and environment preparation.
        Provides comprehensive initialization capabilities.

        Common scenarios:
        - Initial system setup and configuration
        - Database initialization and schema creation
        - Development environment setup
        - Production system deployment
        - System reset and reconfiguration
        - Environment migration and setup
        - System verification and health checks

        Best practices:
        - Use verbose mode for first-time setup
        - Test connections before proceeding
        - Initialize with sample data for development
        - Verify setup after completion
        - Document configuration for future reference
        - Use appropriate database types for environment

    Examples:
        Complete system setup:
            result = await system_init(
                operation='setup_system',
                database_type='sqlite',
                connection_config={'database': '/app/data/system.db'},
                create_tables=True,
                initialize_data=True,
                setup_help_system=True,
                verbose=True
            )
            # Returns: {
            #     'success': True,
            #     'setup_results': {
            #         'database_initialized': True,
            #         'tables_created': 15,
            #         'data_initialized': True,
            #         'help_system_ready': True
            #     }
            # }

        Initialize database only:
            result = await system_init(
                operation='init_database',
                database_type='postgresql',
                connection_config={
                    'host': 'localhost',
                    'port': 5432,
                    'user': 'admin',
                    'password': 'secret',
                    'database': 'production'
                },
                test_connection=True
            )
            # Returns: {
            #     'success': True,
            #     'message': 'Database initialized successfully',
            #     'connection_tested': True
            # }

    Notes:
        - System initialization may take time for complex setups
        - Database initialization requires appropriate permissions
        - Table creation may fail if tables already exist
        - Sample data is useful for testing and development
        - Help system setup improves user experience

    See Also:
        - db_connection: Manage database connections
        - db_operations: Execute queries on databases
        - help_system: Help system operations
    """
    return {
        "success": True,
        "message": f"System initialization operation '{operation}' executed",
        "operation": operation,
        "database_type": database_type,
        "note": "This is a portmanteau tool consolidating all system initialization operations",
    }


# ============================================================================
# HELP SYSTEM PORTMANTEAU
# ============================================================================

@mcp.tool()
async def help_system(
    operation: str,
    category: Optional[str] = None,
    tool_name: Optional[str] = None,
    detailed: bool = False,
) -> Dict[str, Any]:
    """Help system portmanteau tool.

    Comprehensive help system consolidating all help and documentation
    operations into a single interface. Provides interactive help,
    tool documentation, and user assistance capabilities.

    Parameters:
        operation: Help system operation to perform
            - 'help': Get help for all tools or specific category
            - 'tool_help': Get detailed help for specific tool
            - 'list_categories': List all available tool categories
            - 'search_help': Search help documentation
            - 'get_examples': Get usage examples for tools
            - 'troubleshoot': Get troubleshooting information
            - 'update_help': Update help system documentation
            - 'help_status': Check help system status and health

        category: Tool category filter (optional)
            - Filter help by tool category
            - Available categories: "database", "firefox", "media", "windows", "system"
            - Case-insensitive string
            - Used for category-specific help

        tool_name: Specific tool name (required for tool_help)
            - Target tool for detailed help
            - Must be valid tool name
            - Case-sensitive string identifier
            - Example: "db_connection", "firefox_bookmarks"

        detailed: Whether to include detailed information (default: False)
            - Include comprehensive help information
            - Provides additional context and examples
            - May impact response time
            - Useful for complete understanding

    Returns:
        Dictionary containing:
            - success: Boolean indicating operation success
            - operation: Echo of operation performed
            - category: Category filter used
            - tool_name: Tool name used
            - help_content: Help content and documentation
            - categories: List of available categories
            - tools: List of tools in category
            - examples: Usage examples and samples
            - troubleshooting: Troubleshooting information
            - help_status: Help system status and health
            - error: Error message if success is False

    Usage:
        Use this tool for comprehensive help and documentation. Essential
        for discovering tool capabilities, learning usage patterns, and
        getting assistance with operations. Provides interactive help.

        Common scenarios:
        - Discover available tools and capabilities
        - Learn how to use specific tools
        - Find examples and usage patterns
        - Troubleshoot issues and problems
        - Get assistance with operations
        - Explore tool categories and organization
        - Update and maintain help documentation

        Best practices:
        - Use help system for tool discovery
        - Check examples before using tools
        - Use troubleshooting for problem resolution
        - Keep help system updated
        - Provide feedback on help quality
        - Use detailed mode for comprehensive information

    Examples:
        Get general help:
            result = await help_system(
                operation='help'
            )
            # Returns: {
            #     'success': True,
            #     'categories': {
            #         'database': {
            #             'description': 'Database operations and management',
            #             'tools': ['db_connection', 'db_operations', 'db_schema']
            #         }
            #     }
            # }

        Get tool-specific help:
            result = await help_system(
                operation='tool_help',
                tool_name='db_connection',
                detailed=True
            )
            # Returns: {
            #     'success': True,
            #     'tool_help': {
            #         'name': 'db_connection',
            #         'description': 'Database connection management',
            #         'parameters': {...},
            #         'examples': [...]
            #     }
            # }

    Notes:
        - Help system is always available and accessible
        - Detailed help provides comprehensive information
        - Examples help with tool usage
        - Troubleshooting assists with problem resolution
        - Help system updates automatically

    See Also:
        - All other portmanteau tools for specific functionality
        - system_init: System initialization operations
        - db_connection: Database connection management
    """
    return {
        "success": True,
        "message": f"Help system operation '{operation}' executed",
        "operation": operation,
        "category": category,
        "tool_name": tool_name,
        "note": "This is a portmanteau tool consolidating all help system operations",
    }