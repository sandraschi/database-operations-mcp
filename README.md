# Database Operations MCP 🗄️

## Universal Database Operations MCP Server

A comprehensive MCP server supporting SQLite, PostgreSQL, and ChromaDB operations.

[![FastMCP](https://img.shields.io/badge/FastMCP-2.10.1-blue.svg)](https://github.com/jlowin/fastmcp)

## Overview

Database Operations MCP is a comprehensive Model Context Protocol server that provides AI agents with secure, efficient access to multiple database systems. Built with FastMCP 2.10.1, it offers a unified interface for SQLite, PostgreSQL, and ChromaDB operations through 8 specialized tools and 20 guided user prompts.

## Features

- **Multi-Database Support**: PostgreSQL, MongoDB, ChromaDB, and SQLite
- **Unified API**: Consistent interface across different database systems
- **Security First**: Secure credential storage, role-based access control
- **FastMCP 2.10.1**: Modern, efficient MCP implementation
- **Cross-Platform**: Windows, macOS, and Linux support
- **Containerized**: Easy deployment with Docker

## Installation

### Prerequisites

- Python 3.9+
- pip (Python package manager)
- Git
- (Optional) Docker and Docker Compose

### Quick Start

1. Clone the repository
2. Install dependencies
3. Start the MCP server
4. Start using the 20 guided prompts!

## 🛠️ Available Tools

### Registry Tools

Interact with the Windows Registry as a hierarchical database:

- `get_registry_value` - Get a registry value with type information
- `list_registry_key` - List contents of a registry key (values and subkeys)
- `search_registry` - Search across registry keys, values, and data
- `monitor_registry` - Monitor registry keys for changes in real-time
- `backup_registry` - Create backups of registry keys
- `restore_registry` - Restore registry keys from backups
- `export_registry_key` - Export registry data to JSON or .reg format

### Help System

- `list_tools` - List all available MCP tools with descriptions
- `get_tool_help` - Get detailed documentation for a specific tool
- `get_quick_start` - Get a quick start guide for using MCP tools

### Database Connections

- `init_database` - Initialize a database connection
- `list_connections` - List all active database connections
- `close_connection` - Close a database connection
- `init_schema` - Initialize database schema

### Data Operations

- `execute_query` - Execute read-only queries
- `execute_write` - Execute write operations (INSERT, UPDATE, DELETE)
- `batch_execute` - Execute multiple queries in a transaction
- `export_data` - Export query results to various formats (JSON, CSV, TSV)

### Database-Specific Tools

- `sqlite_query` - Execute SELECT queries on SQLite
- `postgres_query` - Execute SELECT queries on PostgreSQL
- `chromadb_query` - Query vector embeddings in ChromaDB
- `mongodb_query` - Query documents in MongoDB

## 🆘 Getting Help

### Registry Examples

#### 1. Monitor Registry Changes

```python
# Start monitoring a registry key
await monitor_registry(
    path='HKCU\\Software\\Microsoft\\Windows',
    action='start',
    callback_url='https://your-webhook.com/registry-changes'
)

# Stop monitoring
await monitor_registry(
    path='HKCU\\Software\\Microsoft\\Windows',
    action='stop'
)
```

#### 2. Backup and Restore Registry

```python
# Create a backup
backup = await backup_registry(
    path='HKLM\\SOFTWARE\\MyApp',
    output_file='myapp_backup.reg'
)

# Restore from backup
await restore_registry(
    backup_file='myapp_backup.reg',
    create_backup=True  # Creates a backup before restoring
)
```

### Interactive Help

```python
# List all available tools
await list_tools()

# Get help for a specific tool
await get_tool_help('execute_query')

# Get a quick start guide
await get_quick_start()
```

### Example Workflows

#### 1. Initialize and Query SQLite

```python
# Initialize SQLite database
await init_database('sqlite', {'database': 'mydb.sqlite'})

# Create a table
await execute_write('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE
    )
''')

# Insert data
await execute_write(
    'INSERT INTO users (name, email) VALUES (?, ?)',
    ['John Doe', 'john@example.com']
)

# Query data
result = await execute_query('SELECT * FROM users')
```

#### 2. Export Data to CSV

```python
# Execute query and export to CSV
await export_data(
    'SELECT * FROM large_dataset',
    format='csv',
    output_file='export.csv'
)
```

## 💬 Guided Prompts (20 Available)

### 🗄️ Database Exploration & Analysis

- **Explore Database** - Get overview of database structure and available tables
- **Analyze Table Schema** - Examine structure and columns of specific tables
- **Query Data Patterns** - Find patterns, trends, or insights in database data

### ⚡ Performance & Optimization

- **Optimize Query Performance** - Analyze and suggest query optimizations
- **Database Health Check** - Perform comprehensive health and performance checks
- **Database Indexing Strategy** - Design optimal indexing for query performance

### 🏗️ Schema Design & Migration
- **Create Database Schema** - Design new database schemas for specific use cases
- **Data Migration Plan** - Create plans to migrate data between database types
- **Generate Sample Data** - Create realistic sample data for database tables

### 🔍 Vector Search & ChromaDB
- **Vector Search Setup** - Set up vector search and embeddings in ChromaDB

### 🛡️ Security & Data Quality
- **Data Validation Rules** - Create validation rules and constraints for data integrity
- **Data Anonymization** - Create strategies for anonymizing sensitive information
- **Database Security Audit** - Perform security audit and recommendations
- **Data Quality Assessment** - Assess and improve data quality in databases

### 🔧 Utilities & Integration
- **SQL Query Builder** - Generate SQL queries from natural language requirements
- **Database Backup Strategy** - Design backup and recovery strategies
- **Troubleshoot Database Issues** - Diagnose and solve common database problems
- **Database Reporting** - Generate comprehensive reports from database data
- **API Database Integration** - Design integration between databases and APIs
- **Database Monitoring Setup** - Set up monitoring and alerting for database systems


## 📊 Registry Tools Reference

### Registry Monitor

Monitor registry keys for changes in real-time:

- Tracks additions, modifications, and deletions
- Supports webhook notifications
- Configurable polling interval

### Backup & Restore

- Create full or partial registry backups
- Automatic backup before restore operations
- Export to standard .reg format

### Search Capabilities

- Search across all registry hives
- Filter by key names, value names, or value data
- Case-insensitive matching

## 🏗️ Architecture

```
database-operations-mcp/
├── src/
│   ├── server.py              # Main FastMCP server
│   ├── database/              # Database connectors
│   │   ├── __init__.py
│   │   ├── sqlite_connector.py
│   │   ├── postgres_connector.py
│   │   └── chromadb_connector.py
│   └── utils/                 # Utilities
│       ├── __init__.py
│       ├── validators.py
│       └── logger.py
├── manifest.json              # DXT manifest with prompts
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── LICENSE                    # MIT License
```

## 🔧 Manual Installation (Development)

### Prerequisites
- Python 3.8+
- Node.js (for DXT CLI)

### Setup
```bash
# Clone the repository
git clone https://github.com/sandraschi/database-operations-mcp
cd database-operations-mcp

# Install Python dependencies
pip install -r requirements.txt

# Install DXT CLI (for packaging)
npm install -g @anthropic-ai/dxt

# Package as DXT
dxt pack
```

### Configuration
Create a configuration file or use environment variables:

```python
# Environment variables
SQLITE_DATABASE_PATHS=/path/to/sqlite/databases
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USERNAME=your_username
POSTGRES_PASSWORD=your_password
CHROMADB_PATH=/path/to/chromadb/storage
```

### Manual MCP Configuration
Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "database-operations": {
      "command": "python",
      "args": ["path/to/database-operations-mcp/src/server.py"],
      "env": {
        "SQLITE_DATABASE_PATHS": "/path/to/your/databases",
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432"
      }
    }
  }
}
```

## 🛡️ Security Features

### SQL Injection Prevention
- Parameterized queries for all database operations
- Input sanitization and validation
- Query pattern validation

### Secure Credential Storage
- OS keychain integration (DXT installation)
- Environment variable support
- No plain text credential storage

### Access Control
- Directory traversal protection for SQLite paths
- Connection timeout handling
- Error message sanitization

## 📊 Supported Database Types

### SQLite
- **File-based databases**
- Local storage and analysis
- Perfect for development and small applications
- No server setup required

### PostgreSQL
- **Enterprise-grade relational database**
- Remote server connections
- Advanced SQL features
- ACID compliance

### ChromaDB
- **Vector database for AI applications**
- Embedding storage and similarity search
- Perfect for RAG applications
- Cosine, Euclidean, and Manhattan similarity metrics

## 🔍 Example Usage

### Using Guided Prompts (Recommended)
1. Install the DXT extension in Claude Desktop
2. Select "Explore Database" prompt
3. Choose database type: `sqlite`
4. Specify database name: `my_app.db`
5. Get comprehensive database overview with suggested next steps

### Direct Tool Usage
```python
# Query SQLite database
result = sqlite_query(
    database_path="/path/to/database.db",
    query="SELECT * FROM users LIMIT 10"
)

# Insert into PostgreSQL
postgres_execute(
    host="localhost",
    database="myapp",
    query="INSERT INTO products (name, price) VALUES (%s, %s)",
    parameters=["Widget", 29.99]
)

# Vector search in ChromaDB
chromadb_query(
    collection_name="documents",
    query_text="machine learning concepts",
    n_results=5
)
```

## 🚧 Troubleshooting

### Common Issues

**SQLite Database Not Found**
- Verify database file path is correct
- Check file permissions
- Ensure database file exists

**PostgreSQL Connection Failed**
- Verify host, port, username, password
- Check network connectivity
- Ensure PostgreSQL server is running

**ChromaDB Collection Missing**
- Create collection first using `chromadb_insert`
- Verify collection name spelling
- Check ChromaDB installation

### Debug Mode
Enable debug logging:
```bash
export MCP_LOG_LEVEL=DEBUG
python src/server.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow FastMCP 2.10.1 patterns
- Add comprehensive error handling
- Include security validation
- Write descriptive prompts
- Test with all supported database types

## 📋 Requirements

### Python Dependencies
```
fastmcp>=2.10.1
sqlite3  # Built-in
psycopg2-binary>=2.9.0
chromadb>=0.4.0
pydantic>=2.0.0
```

### System Requirements
- **Python**: 3.8 or higher
- **Memory**: 512MB minimum (2GB recommended for ChromaDB)
- **Storage**: 100MB for installation
- **Network**: Required for PostgreSQL connections

## 📈 Performance

### Benchmarks
- **SQLite**: 1000+ queries/second on local SSD
- **PostgreSQL**: Network-dependent, typically 100-500 queries/second
- **ChromaDB**: 50-200 similarity searches/second depending on collection size

### Optimization Tips
- Use indexes for frequently queried columns
- Limit result sets with LIMIT clauses
- Use connection pooling for PostgreSQL
- Optimize ChromaDB collection size for memory usage

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Anthropic** - For Claude Desktop and DXT specification
- **FastMCP** - For the excellent MCP framework
- **Model Context Protocol** - For the open standard
- **Community** - For feedback and contributions

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/sandraschi/database-operations-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sandraschi/database-operations-mcp/discussions)
- **Documentation**: [Wiki](https://github.com/sandraschi/database-operations-mcp/wiki)

---

**Built with ❤️ using FastMCP 2.10.1 and the Model Context Protocol**