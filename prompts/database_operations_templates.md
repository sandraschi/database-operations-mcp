# Database Query Templates

These templates help you interact effectively with the Database Operations MCP Server.

## Basic Database Operations

### Connect to Database
```
I need to connect to a database. The database type is {database_type} and the connection string is {connection_string}. Please establish the connection and confirm it's working.
```

### Execute Query
```
Execute this SQL query and return the results:

{database_type}: {sql_query}

Please format the results in a readable way and explain what the query does.
```

### Schema Information
```
Show me the schema information for the {table_name} table in the {database_name} database. Include column names, types, constraints, and indexes.
```

## Advanced Operations

### Performance Analysis
```
Analyze the performance of this query and suggest optimizations:

{database_type}: {sql_query}

Consider execution time, resource usage, and index utilization.
```

### Data Migration
```
Help me migrate data from {source_table} to {target_table}. The source is {source_database} and target is {target_database}. Handle any data type conversions and constraints.
```

### Backup and Recovery
```
Create a backup strategy for the {database_name} database. Include:
- Backup frequency and retention
- Recovery time objectives
- Storage requirements
- Testing procedures
```

## Troubleshooting Templates

### Connection Issues
```
I'm having trouble connecting to my {database_type} database with this connection string: {connection_string}

Error message: {error_message}

Please help diagnose and fix the connection issue.
```

### Query Performance
```
This query is running slowly:

{database_type}: {sql_query}

Current execution time: {execution_time}

Please identify bottlenecks and suggest improvements.
```

### Data Integrity
```
I suspect data integrity issues in the {table_name} table. Please:
1. Check for constraint violations
2. Look for orphaned records
3. Verify referential integrity
4. Suggest cleanup procedures
```

## Best Practices Prompts

### Security Audit
```
Perform a security audit of the {database_name} database. Check for:
- Weak passwords and authentication
- Excessive permissions
- Unencrypted sensitive data
- SQL injection vulnerabilities
- Audit logging configuration
```

### Maintenance Tasks
```
What routine maintenance tasks should I perform on my {database_type} database? Include:
- Index maintenance
- Statistics updates
- Log file management
- Performance monitoring setup
```

## Windows-Specific Operations

### File System Integration
```
I need to integrate database operations with Windows file system. The database contains file paths in {table_name} and I need to:
1. Verify all paths exist
2. Check file permissions
3. Update any broken paths
4. Synchronize with actual file system
```

### Windows Service Management
```
Help me manage Windows services related to the database:
- Check service status for {service_name}
- Start/stop/restart services as needed
- Monitor service logs
- Configure automatic startup
```

## Media Library Management

### Calibre Integration
```
I need to manage my Calibre ebook library through the database:
- Scan for new books in {directory}
- Update metadata for existing books
- Check for duplicate entries
- Generate reading statistics
```

### Plex Media Server
```
Help me manage my Plex media library:
- Scan media folders for new content
- Update metadata and artwork
- Check library health
- Optimize database performance
```

## Firefox Integration

### Bookmark Management
```
I need to manage my Firefox bookmarks through the database:
- Export bookmarks to {format}
- Import bookmarks from {file}
- Clean up duplicate bookmarks
- Organize bookmarks by {criteria}
```

## Error Handling Prompts

### Database Errors
```
I'm getting this database error:

Database: {database_type}
Error Code: {error_code}
Error Message: {error_message}
SQL Statement: {sql_statement}

Please explain what this error means and how to fix it.
```

### Connection Timeouts
```
My database connections are timing out:

Database: {database_type}
Timeout Value: {timeout_seconds}
Error: {error_message}

Please help troubleshoot and optimize the connection settings.
```

## Reporting and Analytics

### Usage Statistics
```
Generate usage statistics for the {database_name} database:
- Most frequently accessed tables
- Query performance trends
- Storage growth patterns
- User activity summary
```

### Performance Reports
```
Create a performance report for the {database_name} database including:
- Slow query analysis
- Index usage statistics
- Resource utilization trends
- Optimization recommendations
```

---

**Note**: Replace placeholders like {database_type}, {table_name}, etc. with your specific values when using these templates.

**Version**: 1.0.0
**Last Updated**: 2025-01-01
