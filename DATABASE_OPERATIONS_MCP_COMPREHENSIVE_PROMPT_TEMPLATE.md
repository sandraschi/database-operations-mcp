# Comprehensive Database Operations MCP Server Prompt Template

This template provides a complete guide for interacting with the Database Operations MCP Server, covering all available tools, use cases, and best practices.

## 🚀 Quick Start Guide

### Initial Setup
```
I need to start using the Database Operations MCP Server. Please:
1. Show me all available tools and their capabilities
2. Explain how to connect to different database types
3. Provide examples of common operations
4. Show me the current server status and configuration
```

### Get Server Information
```
Show me the current status of the Database Operations MCP Server:
- Server version and uptime
- Available database connections
- Active tools and resources
- System resource usage
- Recent errors or warnings
```

## 🗄️ Database Operations

### Connection Management
```
Help me connect to a database:
- Database type: {sqlite|postgresql|mysql|mongodb}
- Connection parameters: {host|port|database|username|password}
- Connection name: {descriptive_name}
- Test the connection and show available tables/schemas
```

### Query Execution
```
Execute this database query and format the results:
- Database: {database_name}
- Query: {sql_query}
- Result format: {table|json|csv|markdown}
- Include execution time and row count
- Explain what the query does
```

## 🔍 Advanced Database Operations

### Full-Text Search
```
Search for content in the {database_name} database:
- Search terms: {search_query}
- Tables to search: {table1,table2,table3}
- Search type: {exact|partial|fuzzy}
- Return format: {summary|detailed|count_only}
- Sort by: {relevance|date|alphabetical}
```

### Performance Analysis
```
Analyze the performance of this query:
- Database: {database_name}
- Query: {sql_query}
- Execution metrics: {time|cpu|memory|io}
- Optimization suggestions
- Index recommendations
- Alternative query approaches
```

## 🪟 Windows Integration

### Registry Operations
```
I need to work with Windows Registry:
- Registry path: {hkey_current_user\software\app}
- Operation: {read|write|delete|list}
- Value name: {value_name}
- Data type: {string|dword|binary}
- Backup before changes: {true|false}
```

### Windows Service Management
```
Help me manage Windows services through the database:
- Service name: {servicename}
- Operation: {start|stop|restart|status|configure}
- Monitor status: {true|false}
- Log service events: {true|false}
- Auto-restart on failure: {true|false}
```

## 📚 Media Library Management

### Calibre E-book Library
```
Manage my Calibre e-book library:
- Library location: {c:\calibre}
- Operation: {scan|organize|export|import}
- Book format: {epub|mobi|pdf|all}
- Metadata fields: {title|author|series|tags|rating}
- Generate reports: {collection|reading_stats|duplicates}
```

### Plex Media Server
```
Work with my Plex media server:
- Server URL: {http://localhost:32400}
- Library sections: {movies|tv_shows|music|photos}
- Operation: {scan|refresh|analyze|optimize}
- Media types: {video|audio|images}
- Update metadata: {true|false}
```

## 🌐 Web Browser Integration

### Firefox Bookmarks
```
Manage my Firefox bookmarks:
- Profile path: {c:\users\user\appdata\roaming\mozilla\firefox\profiles}
- Operation: {export|import|organize|search|cleanup}
- Bookmark format: {html|json}
- Organize by: {folder|date|domain|frequency}
- Remove duplicates: {true|false}
```

## 🔧 System Administration

### Database Maintenance
```
Perform routine database maintenance:
- Database: {database_name}
- Operations: {optimize|defragment|update_stats|cleanup}
- Schedule: {daily|weekly|monthly}
- Log results: {true|false}
- Send notifications: {email|discord|none}
```

### Backup and Recovery
```
Set up database backup and recovery:
- Database: {database_name}
- Backup type: {full|incremental|differential}
- Schedule: {time|interval}
- Retention: {days_to_keep}
- Storage location: {local|network|cloud}
- Encryption: {true|false}
- Test restore: {true|false}
```

## 📊 Monitoring and Analytics

### Performance Monitoring
```
Monitor database performance:
- Database: {database_name}
- Metrics: {cpu|memory|disk|network|queries}
- Time range: {last_hour|last_day|last_week}
- Alert thresholds: {cpu>80%|memory>90%|disk>85%}
- Report format: {chart|table|summary}
```

### Usage Analytics
```
Analyze database usage patterns:
- Database: {database_name}
- Analysis period: {last_month|last_quarter|last_year}
- Metrics: {query_frequency|table_access|user_activity}
- Generate insights: {trends|bottlenecks|recommendations}
- Export format: {pdf|excel|json}
```

## 🛠️ Troubleshooting

### Connection Issues
```
I'm having trouble connecting to {database_name}:
- Connection string: {connection_details}
- Error message: {error_text}
- Database type: {sqlite|postgresql|mysql|mongodb}
- Network/firewall: {settings}
- Authentication: {credentials}
- Please diagnose and fix the issue
```

### Performance Problems
```
The database is slow or unresponsive:
- Database: {database_name}
- Symptoms: {slow_queries|high_cpu|timeouts}
- Current metrics: {performance_data}
- Recent changes: {schema|data|configuration}
- Please identify bottlenecks and suggest fixes
```

## 🎯 Best Practices

### Security
```
Review database security:
- Database: {database_name}
- Check: {passwords|permissions|encryption|audit_logs}
- Compliance: {gdpr|hipaa|sox|none}
- Generate report: {summary|detailed|action_items}
- Implement recommendations: {true|false}
```

### Optimization
```
Optimize database performance:
- Database: {database_name}
- Areas: {queries|indexes|configuration|hardware}
- Current bottlenecks: {identified_issues}
- Apply optimizations: {true|false}
- Monitor improvements: {true|false}
```

## 📝 Development and Testing

### Development Workflow
```
Help me develop with the Database Operations MCP Server:
- Set up development environment
- Test tools during development
- Debug connection issues
- Performance profiling
- Documentation updates
```

### Testing Templates
```
Test the MCP server functionality:
- Run all available tools
- Test database connections
- Validate error handling
- Performance benchmarking
- Generate test reports
```

## 🚨 Emergency Procedures

### Database Recovery
```
Emergency database recovery needed:
- Database: {database_name}
- Issue: {corruption|crash|data_loss|performance}
- Last backup: {backup_location|date}
- Recovery priority: {critical|high|normal}
- Minimize downtime: {true|false}
- Please execute recovery procedures
```

---

## 📋 Template Variables Reference

Replace these placeholders with your specific values:

- `{database_name}` - Name of your database
- `{table_name}` - Specific table name
- `{sql_query}` - Your SQL query
- `{connection_string}` - Database connection details
- `{file_path}` - File system path
- `{format}` - Output format (json, csv, excel, etc.)
- `{operation}` - Type of operation to perform

## 🔗 Related Documentation

- [CHANGELOG.md](./CHANGELOG.md) - Version history and updates
- [SECURITY.md](./SECURITY.md) - Security policies and procedures
- [CONTRIBUTING.md](./CONTRIBUTING.md) - Development guidelines

---

**Version**: 1.1.0 (Gold Status Certified)
**Last Updated**: 2025-01-01
**MCP Compatibility**: FastMCP 2.12.0
**Glama.ai Status**: Gold Tier (85/100)

This comprehensive template covers all Database Operations MCP Server capabilities and provides ready-to-use prompts for common scenarios, troubleshooting, and advanced operations.
