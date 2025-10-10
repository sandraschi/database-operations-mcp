# MCP Server Prompt Templates

These templates help you effectively communicate with MCP (Model Context Protocol) servers.

## Basic Server Interaction

### Get Available Tools
```
Show me all the available tools in this MCP server. List each tool with its name, description, and parameters.
```

### Get Server Status
```
What's the current status of the MCP server? Include version, uptime, active connections, and any recent errors.
```

### Help and Documentation
```
I need help with this MCP server. Show me:
1. Available tools and their purposes
2. How to format requests properly
3. Example usage patterns
4. Common troubleshooting steps
```

## Tool-Specific Templates

### Database Operations
```
I need to work with a database. Please show me:
- How to connect to different database types (SQLite, PostgreSQL, MySQL)
- Available query operations
- Schema inspection capabilities
- Data manipulation tools
```

### File System Operations
```
Help me with file system operations:
- List files and directories
- Search for specific files
- Read file contents
- Write or modify files
- File permissions and metadata
```

### Windows System Tools
```
I need to interact with Windows system:
- Check running processes
- Manage Windows services
- Access registry information
- System information and diagnostics
```

### Media Library Management
```
Help me manage my media libraries:
- Calibre ebook library operations
- Plex media server management
- Media file organization
- Metadata updates and synchronization
```

### Web Browser Integration
```
I need to work with web browsers:
- Firefox bookmark management
- Browser history and cookies
- Extension management
- Web scraping capabilities
```

## Advanced Usage Patterns

### Batch Operations
```
I need to perform multiple related operations:
1. Connect to the database
2. Execute this query: {sql_query}
3. Process the results
4. Export to {format}
5. Save to {location}

Please execute these steps and handle any errors gracefully.
```

### Error Recovery
```
I'm encountering an error with the MCP server:

Error: {error_message}
Operation: {operation_attempted}
Context: {additional_context}

Please help diagnose and resolve this issue.
```

### Performance Optimization
```
The MCP server seems slow. Please:
1. Check current performance metrics
2. Identify bottlenecks
3. Suggest optimizations
4. Implement improvements if possible
```

## Integration Templates

### Claude Desktop Setup
```
Help me set up this MCP server with Claude Desktop:
1. Configuration file setup
2. Server connection parameters
3. Testing the connection
4. Troubleshooting common issues
```

### Development Workflow
```
I'm developing with this MCP server. Show me:
- How to test tools during development
- Debugging techniques
- Logging and monitoring
- Performance profiling
```

## Specialized Use Cases

### Data Analysis
```
I need to analyze data using this MCP server:
- Connect to data sources
- Execute analytical queries
- Generate reports and visualizations
- Export results in various formats
```

### System Administration
```
Help me with system administration tasks:
- Database maintenance and optimization
- Log analysis and monitoring
- Backup and recovery procedures
- Security auditing
```

### Content Management
```
I need to manage content with this server:
- Media file organization
- Metadata extraction and tagging
- Content search and retrieval
- Batch processing operations
```

## Troubleshooting Templates

### Connection Issues
```
I can't connect to the MCP server:

Server: {server_name}
Error: {connection_error}
Environment: {os_info}

Please help diagnose the connection problem.
```

### Tool Execution Errors
```
A specific tool is failing:

Tool: {tool_name}
Parameters: {parameters}
Error: {execution_error}

Please explain why this failed and how to fix it.
```

### Performance Problems
```
The MCP server is performing poorly:

Symptoms: {performance_issues}
Metrics: {current_metrics}
Environment: {system_specs}

Please analyze and suggest improvements.
```

---

**Note**: These templates are designed to work with any MCP server. Customize them based on the specific tools and capabilities available in your server.

**Version**: 1.0.0
**Last Updated**: 2025-01-01
