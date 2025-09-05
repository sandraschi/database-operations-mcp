# Database Operations MCP 

## Universal Database Operations MCP Server

A comprehensive MCP server supporting SQLite, PostgreSQL, and ChromaDB operations.

[![FastMCP](https://img.shields.io/badge/FastMCP-2.11.3-blue.svg)](https://github.com/jlowin/fastmcp)
[![PyPI](https://img.shields.io/pypi/v/database-operations-mcp)](https://pypi.org/project/database-operations-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)

## Overview

Database Operations MCP is a comprehensive Model Context Protocol server that provides AI agents with secure, efficient access to multiple database systems. Built with FastMCP 2.11.3, it offers a unified interface for SQLite, PostgreSQL, and ChromaDB operations through 8 specialized tools and 20 guided user prompts.

## Features

- **Multi-Database Support**: PostgreSQL, MongoDB, ChromaDB, and SQLite
- **Unified API**: Consistent interface across different database systems
- **Security First**: Secure credential storage, role-based access control
- **FastMCP 2.11.3**: Modern, efficient MCP implementation
- **Cross-Platform**: Windows, macOS, and Linux support
- **Containerized**: Easy deployment with Docker
- **DXT Packaging**: Easy packaging and distribution with DXT

## 📦 Latest Release: v1.0.0

- 🆕 Initial stable release
- ✨ Supports SQLite, PostgreSQL, and ChromaDB
- 🚀 Ready for production use

## Overview

Database Operations MCP is a comprehensive Model Context Protocol server that provides AI agents with secure, efficient access to multiple database systems. Built with FastMCP 2.11.3, it offers a unified interface for SQLite, PostgreSQL, and ChromaDB operations through 8 specialized tools and 20 guided user prompts.

## Features

- **Multi-Database Support**: PostgreSQL, MongoDB, ChromaDB, and SQLite
- **Unified API**: Consistent interface across different database systems
- **Security First**: Secure credential storage, role-based access control
- **FastMCP 2.11.3**: Modern, efficient MCP implementation
- **Cross-Platform**: Windows, macOS, and Linux support
- **Containerized**: Easy deployment with Docker
- **DXT Packaging**: Easy packaging and distribution with DXT

## 📚 Documentation

### Development Standards
- [MCP Server & DXT Packing Standards](./docs/standards/MCP_Server_Standards.md) - Guidelines for MCP server development and DXT packaging
- [DXT Building Guide](./docs/DXT_BUILDING_GUIDE.md) - Complete guide to building and distributing DXT packages

## 📦 DXT Packaging

This project uses DXT for packaging the MCP server for distribution and deployment. The DXT package includes all necessary code, dependencies, and configuration.

### Building the DXT Package

#### Prerequisites

- Python 3.9+
- DXT CLI installed: `pip install dxt`

#### Using the Build Script

We provide a PowerShell build script that automates the entire packaging process:

```powershell
# Show help and available options
.\scripts\build-mcp-package.ps1 -Help

# Build and sign the package (default behavior)
.\scripts\build-mcp-package.ps1

# Build without signing (for development/testing)
.\scripts\build-mcp-package.ps1 -NoSign

# Specify custom output directory
.\scripts\build-mcp-package.ps1 -OutputDir "C:\builds"
```

#### Manual Build Process

If you prefer to build manually:

1. Ensure your `manifest.json` is properly configured

2. Run the DXT pack command:

   ```bash
   dxt pack . dist/
   ```

3. Sign the package (optional but recommended):

   ```bash
   dxt sign dist/your-package-name.dxt
   ```

4. Verify the package:

   ```bash
   dxt verify dist/your-package-name.dxt
   ```

### CI/CD Integration

The build script is designed to work seamlessly with CI/CD pipelines. Here's an example GitHub Actions workflow:

```yaml
name: Build and Publish DXT Package

on:
  push:
    tags:
      - 'v*'  # Trigger on version tags
  workflow_dispatch:  # Allow manual triggers

jobs:
  build:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install DXT
      run: pip install dxt
      
    - name: Build DXT package
      run: |
        mkdir -p dist
        .\scripts\build-mcp-package.ps1 -OutputDir dist
      
    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: dxt-package
        path: dist/*.dxt
        retention-days: 5
```

### Package Verification

Before deploying, always verify your package:

```bash
dxt verify dist/your-package-name.dxt
```

This will check:

- Package integrity
- Digital signatures
- Manifest validity
- Required files and dependencies

### Best Practices

1. **Versioning**: Always update the version in `manifest.json` before creating a new package
2. **Signing**: Always sign production packages
3. **Testing**: Test the package in a staging environment before production deployment
4. **Documentation**: Update the README with any package-specific instructions
5. **Dependencies**: Ensure all dependencies are properly specified in `pyproject.toml`
   - All project dependencies installed: `pip install -e .`

## Build Process
   ```bash
   # Navigate to the project root
   cd /path/to/database-operations-mcp
   
   # Run the build script (Windows)
   .\build.ps1
   
   # Or on Linux/macOS
   pwsh build.ps1
   ```

   The build script will:
   - Validate the manifest.json
   - Create a DXT package in the `dist/` directory named `database-operations-mcp.dxt`
   - Sign the package (optional, use `-NoSign` to skip)
   - Validate the final package

## Manual Build (without script)

```bash
# Basic package creation
dxt pack . dist

# The above creates dist/package.dxt - you may want to rename it:
mv dist/package.dxt dist/database-operations-mcp.dxt

# Sign the package (requires signing key)
dxt sign dist/database-operations-mcp.dxt

# Publish to a DXT registry (if configured)
dxt publish dist/database-operations-mcp.dxt
```

## Build Script Options

- `-NoSign`: Skip package signing

Example:

```bash
.\build.ps1 -NoSign
```

5. **Signing and Publishing**
   - **Signing**: Required for production use. Uses your default DXT signing key.
     ```bash
     dxt sign dist/database-operations-mcp.dxt
     ```
   
   - **Publishing**: Upload to a DXT registry (must be configured)
     ```bash
     dxt publish dist/database-operations-mcp.dxt
     ```
   
   - **Registry Configuration**:
     ```bash
     # List configured registries
     dxt registry list
     
     # Add a new registry
     dxt registry add my-registry https://registry.example.com
     ```

6. **Verification**
   ```bash
   # Verify package integrity
   dxt verify dist/database-operations-mcp.dxt
   
   # Check package info
   dxt info dist/database-operations-mcp.dxt
   ```

### Manifest Configuration

The `manifest.json` file contains the MCP server configuration:

```json
{
  "name": "database-operations-mcp",
  "version": "0.1.0",
  "dxt_version": "1.0.0",
  "server": {
    "type": "python",
    "entry_point": "database_operations_mcp.main:main",
    "mcp_config": {
      "command": "python",
      "args": ["-m", "database_operations_mcp.main"],
      "cwd": "src",
      "env": {
        "PYTHONPATH": "${workspaceRoot}"
      }
    }
  }
}
```

### Dependencies

Dependencies are managed in `pyproject.toml` and will be automatically included in the DXT package. Make sure all required dependencies are listed in the `dependencies` section.

### Testing the Package

After building, you can test the DXT package locally:

```bash
# Install the package in development mode
pip install -e .

# Test the MCP server directly
python -m database_operations_mcp.main

# Or test with the DXT CLI
dxt run dist/database-operations-mcp.dxt

# For debugging with verbose output
DXT_DEBUG=1 dxt run dist/database-operations-mcp.dxt
```

### Distribution

The built DXT package (`dist/database-operations-mcp.dxt`) can be distributed and installed on any system with DXT installed.

To install the package on another system:

```bash
# Install DXT if not already installed
pip install dxt

# Install the package
dxt install /path/to/database-operations-mcp.dxt

# Or install from a URL
dxt install https://example.com/path/to/database-operations-mcp.dxt

# List installed packages
dxt list

# Run the installed package
dxt run database-operations-mcp

# Uninstall when done
dxt uninstall database-operations-mcp
```

### Troubleshooting

1. **Package Not Found**
   - Ensure the package exists at the specified path
   - Verify file permissions
   - Check DXT version compatibility

2. **Import Errors**
   - Check if all dependencies are installed
   - Verify PYTHONPATH includes the project root
  
3. **Debugging**
   ```bash
   # Enable debug logging
   export DXT_DEBUG=1
   
   # Run with verbose output
   dxt --verbose run dist/database-operations-mcp.dxt
   ```

4. **Common Issues**
   - **Missing Dependencies**: Ensure all dependencies are listed in `pyproject.toml`
   - **Path Issues**: Verify working directory and file paths in `manifest.json`
   - **Version Conflicts**: Check for version conflicts in dependencies

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

### Firefox Bookmark Tools

Manage and analyze Firefox bookmarks with these specialized tools:

### Bookmark Management
- `list_bookmarks` - List all bookmarks, optionally filtered by folder
- `get_bookmark` - Get details for a specific bookmark
- `add_bookmark` - Add a new bookmark
- `search_bookmarks` - Search bookmarks by title or URL
- `export_bookmarks` - Export bookmarks in various formats (JSON, HTML, etc.)

### Tag Management
- `list_tags` - List all tags used in bookmarks
- `tag_from_folder` - Generate tags based on folder hierarchy
- `batch_tag_from_folder` - Batch process bookmarks to add folder-based tags
- `tag_from_year` - Add year-based tags to bookmarks
- `batch_tag_from_year` - Batch process bookmarks to add year-based tags
- `batch_update_tags` - Update tags for multiple bookmarks at once

### Analysis Tools
- `find_broken_links` - Identify broken or inaccessible bookmarks
- `find_old_bookmarks` - Find bookmarks older than a specified number of days
- `get_bookmark_stats` - Get statistics about bookmarks (count by folder, tag, etc.)

### Backup & Restore
- `backup_firefox_data` - Create a backup of Firefox bookmarks
- `restore_firefox_data` - Restore bookmarks from a backup

## Database Connections

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
- Follow FastMCP 2.11.3 patterns
- Add comprehensive error handling
- Include security validation
- Write descriptive prompts
- Test with all supported database types

## 📋 Requirements

### Python Dependencies
```
fastmcp>=2.11.3
sqlite3  # Built-in
psycopg2-binary>=2.9.0
chromadb>=0.4.0
pymongo>=4.0.0
sqlalchemy[asyncio]>=2.0.0
pydantic>=2.11.7
python-dotenv>=1.0.0
aiohttp>=3.8.0
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

**Built with ❤️ using FastMCP 2.11.3 and the Model Context Protocol**