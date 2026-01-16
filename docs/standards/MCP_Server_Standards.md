# 🚀 MCP Server Standards & Best Practices

> **⚠️ OUTDATED**: This document contains references to DXT packaging which has been replaced by MCPB packaging. See the MCPB Building Guide for current packaging instructions.

## 📋 Table of Contents

1. [MCP Server Selection Criteria](#-mcp-server-selection-criteria)
2. [Technical Standards](#-technical-standards)
3. [Development Guidelines](#-development-guidelines)
4. [Packaging & Distribution](#-packaging--distribution)
5. [Troubleshooting](#-troubleshooting)

## 🎯 MCP Server Selection Criteria

### 1. Target Application Requirements

Applications being wrapped as MCP servers should meet these criteria:

#### ✅ Good Candidates

- **CLI/REST API**: Well-documented, stable interface
- **Popularity**: Actively used and maintained
- **Unique Value**: Not duplicating existing corporate MCPs
- **Complexity**: Moderate to high utility (e.g., Notepad++, HandBrake, GIMP)
- **Automation Potential**: Benefits from AI/automation

#### ❌ Poor Candidates

- Trivial applications (e.g., Notepad, Calculator)
- Duplicates of well-maintained MCPs
- Applications with poor or no API
- Niche tools with limited use cases

### 2. Complexity Assessment

| Application | Complexity | Reasoning |
|-------------|------------|-----------|
| Notepad++   | Low        | Simple text operations, well-defined API |
| HandBrake   | Medium     | Complex media processing, but good CLI |
| GIMP        | High       | Complex UI, plugin system, many features |
| 7-Zip       | Low        | Mature CLI, focused functionality |

## ⚙️ Technical Standards

### 1. FastMCP Version Requirements

- **SOTA Requirement**: FastMCP 2.14.3+ (mandatory for state-of-the-art status)
- **Improvable**: FastMCP 2.11-2.12 (functional but not SOTA - upgrade recommended)
- **Runt Status**: FastMCP <= 2.10.0 (hard failure - upgrade required)

### 2. Code Organization

- Follow Python packaging best practices
- Clear separation of concerns
- Modular design for maintainability

## 🛠 Development Guidelines

### 1. Error Handling

- Comprehensive error messages
- Graceful degradation
- Proper logging with context

### 2. AI-Optimized Logging & Tool Design

#### AI-Centric Logging Best Practices

1. **Structured Logging**

   - Use JSON format for all log entries
   - Include consistent field names across services
   - Add timestamps in ISO 8601 format

   ```python
   # Recommended log structure
   {
     "timestamp": "2023-04-05T14:30:00Z",
     "level": "ERROR",
     "service": "database_operations",
     "operation": "user_authentication",
     "error_code": "DB-1002",
     "message": "Database connection timeout",
     "context": {
       "db_host": "db.example.com",
       "timeout_seconds": 30,
       "retry_count": 3,
       "user_id": "user_12345"
     },
     "stack_trace": "...",
     "suggested_actions": [
       "Check database server status",
       "Verify network connectivity",
       "Review connection pool settings"
     ]
   }
   ```

2. **Error Handling**

   - Use specific error codes (e.g., `DB-1002` for database timeouts)
   - Include machine-readable error types
   - Provide actionable resolution steps
   - Log at appropriate severity levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)

3. **Context Enrichment**

   - Add request IDs for tracing
   - Include user/session context
   - Log performance metrics
   - Track resource usage

4. **Sensitive Data Protection**

   - Never log passwords or API keys
   - Mask PII (Personally Identifiable Information)
   - Use environment variables for sensitive configuration

#### Tool Design Guidelines

1. **Naming Conventions**

   - Use `action_object` format (e.g., `create_user`, `update_document`)
   - Be specific and descriptive
   - Use consistent verb tenses (prefer present tense)
   - Avoid abbreviations unless widely understood

2. **Tool Documentation**

   - Include comprehensive docstrings
   - Document all parameters with types and descriptions
   - Provide usage examples
   - List possible error codes and their meanings

   ```python
   def create_user(
       username: str,
       email: str,
       roles: List[str] = None,
       is_active: bool = True
   ) -> Dict[str, Any]:
       """Create a new user in the system.

       Args:
           username: Unique username (3-32 chars, alphanumeric)
           email: Valid email address
           roles: List of role names (default: ['user'])
           is_active: Whether the user account is active (default: True)

       Returns:
           Dict containing created user details

       Raises:
           ValueError: If username or email is invalid
           UserExistsError: If username or email already exists

       Example:
           >>> create_user('johndoe', 'john@example.com', ['admin', 'editor'])
       """
   ```

3. **Tool Organization**

   - Group related tools in modules by domain
   - Keep tools focused and single-responsibility
   - Document dependencies between tools
   - Version your tool APIs

4. **Performance Considerations**

   - Implement rate limiting
   - Add timeout handling
   - Use caching where appropriate
   - Document performance characteristics

#### llms.txt Integration

Include an `llms.txt` file in your project root with:

```ini
# Supported LLM versions and capabilities
min_llm_version = "claude-3.5-sonnet-20240620"
max_tokens = 4000
supports_tools = true
supports_vision = false

# Tool Registry
[tools.create_user]
description = "Create a new user account with specified roles and permissions"
parameters = {
    "username": {
        "type": "string",
        "description": "Unique username (3-32 chars, alphanumeric)",
        "required": true
    },
    "email": {
        "type": "string",
        "format": "email",
        "description": "User's email address",
        "required": true
    },
    "roles": {
        "type": "array",
        "items": {"type": "string"},
        "description": "List of role names",
        "default": ["user"]
    }
}
error_codes = {
    "USER_EXISTS": "A user with this username or email already exists",
    "INVALID_EMAIL": "The provided email address is not valid"
}

# Error Code Reference
[error_codes]
DB-1001 = "Database connection failed"
DB-1002 = "Query timeout"
AUTH-2001 = "Invalid credentials"
AUTH-2002 = "Insufficient permissions"
```

#### Logging Configuration Example

```python
import logging
import json
from datetime import datetime
import os

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'message': record.getMessage(),
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Add any extra fields
        if hasattr(record, 'extra') and isinstance(record.extra, dict):
            log_record.update(record.extra)

        # Handle exceptions
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_record, ensure_ascii=False)

def setup_logging():
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())

    # File handler
    file_handler = logging.FileHandler('logs/application.log')
    file_handler.setFormatter(JSONFormatter())

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
```

#### Best Practices for AI-Optimized Logs

1. **Consistency**

   - Use the same field names across all services
   - Standardize date/time formats (ISO 8601)
   - Maintain consistent log levels

2. **Context is Key**

   - Include relevant IDs (request_id, user_id, session_id)
   - Add environment information (dev/staging/prod)
   - Include version numbers of services

3. **Performance Logging**

   - Log operation durations
   - Track resource usage
   - Monitor error rates

4. **Security Considerations**

   - Log security-related events
   - Include source IP addresses
   - Track authentication attempts
   - Monitor for suspicious patterns

5. **Monitoring and Alerting**

   - Set up alerts for error patterns
   - Create dashboards for key metrics
   - Implement log retention policies
  [errors]
  MCP-1002 = "Database connection failed. Verify credentials and network."
  ```

### 3. Tool Organization Best Practices

#### Naming Conventions
- **Prefix Tool Names** with service/domain:
  - `notion_create_page` instead of `create_page`
  - `obsidian_add_note` instead of `add_note`
  - `memory_store_fact` instead of `remember`

#### Tool Documentation
- Each tool must include:
  - Clear, specific description
  - Required permissions
  - Example inputs/outputs
  - Potential error conditions
  ```python
  @tool("notion_create_page")
  async def create_notion_page(
      title: str,
      content: str,
      parent_page_id: str = None
  ) -> dict:
      """
      Create a new page in Notion under the specified parent.
      
      Args:
          title: Page title (max 2000 chars)
          content: Page content in Markdown format
          parent_page_id: Optional parent page ID
          
      Returns:
          dict: Created page metadata
          
      Raises:
          NotionAPIError: If API request fails (includes error_code)
          
      Example:
          await create_notion_page("Meeting Notes", "# Weekly Sync\n- Discussed project timeline")
      """
      # Implementation...
  ```

#### Tool Granularity
- **Avoid Tool Overload**: 
  - Prefer fewer, more versatile tools over many single-purpose tools
  - Consider tool "weight" in terms of resource usage, not just count
  - Document expected resource usage in tool metadata
  
- **Composite Tools**:
  - For complex operations, create higher-level tools that call other tools
  - Document the tool chain for transparency
  ```python
  @tool("weekly_report")
  async def generate_weekly_report(week: str) -> str:
      """
      Generate a comprehensive weekly report by combining data from multiple sources.
      Internally uses: 
        - fetch_metrics()
        - generate_charts()
        - format_report()
      """
      metrics = await fetch_metrics(week)
      charts = await generate_charts(metrics)
      return await format_report(metrics, charts)
  ```

### 4. Help System (Recommended)

While not part of the FastMCP standard, implementing a help system is strongly recommended:

```python
@tool("help")
async def get_help(tool_name: str = None) -> dict:
    """
    Get documentation about available tools.
    
    Args:
        tool_name: Optional specific tool to get help for
        
    Returns:
        dict: Tool documentation including parameters and examples
    """
    if tool_name:
        return get_tool_documentation(tool_name)
    return {
        "available_tools": list_available_tools(),
        "usage_tips": [
            "Use specific tool names (e.g., 'notion_' prefix for Notion tools)",
            "Check llms.txt for detailed tool specifications"
        ]
    }
```
- **Be Verbose**: Log extensively in development to aid debugging
- **Context is Key**: Include relevant context in log messages
  ```python
  # Good
  logger.debug(f"Processing request: {request_id} with params: {params}")
  
  # Better
  logger.debug(
      "Processing request",
      extra={
          "request_id": request_id,
          "params": params,
          "user": current_user,
          "source_ip": request.remote_addr
      }
  )
  ```
- **Structured Logging**: Use JSON or structured formats for better parsing
- **Log Levels**:
  - DEBUG: Detailed information for debugging
  - INFO: General operational information
  - WARNING: Indicate potential issues
  - ERROR: Log handled exceptions
  - CRITICAL: System-level failures

#### Production Logging
- **Environment Variables**: Use environment variables to control log levels
  ```python
  import os
  import logging
  
  LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
  logging.basicConfig(level=getattr(logging, LOG_LEVEL))
  ```
- **Sensitive Data**: Ensure no sensitive information is logged
- **Performance**: Be mindful of log volume in production

#### Try-Except Logging Pattern
```python
try:
    # Operation that might fail
    result = some_operation()
    logger.debug("Operation completed", extra={"result": result})
    return result
except SpecificException as e:
    logger.error(
        "Operation failed with specific error",
        exc_info=True,
        extra={
            "error": str(e),
            "context": {"param1": value1, "param2": value2}
        }
    )
    raise  # Re-raise after logging if needed
```

## 📦 Packaging & Distribution

> **Note**: See DXT_BUILDING_GUIDE.md for detailed packaging instructions

### 1. Registry Configuration

- **Official Registry**: `https://registry.dxt.anthropic.com`
- Authentication required with `DXT_API_TOKEN`

```bash
# Configure registry
dxt config set registry.url https://registry.dxt.anthropic.com
dxt config set registry.token $DXT_API_TOKEN
```

### 1. Official Registries
- **Anthropic's Public Registry**
  - URL: `https://registry.dxt.anthropic.com`
  - Requires authentication with `DXT_API_TOKEN`
  - Best for production distribution
  ```bash
  # Configure registry
  dxt config set registry.url https://registry.dxt.anthropic.com
  dxt config set registry.token $DXT_API_TOKEN
  ```

### 2. Self-Hosted Registries
- **Private PyPI Server**
  ```bash
  # Using pypiserver
  pip install pypiserver
  pypi-server -p 8080 /path/to/packages
  
  # Configure DXT to use private registry
  dxt config set registry.url http://your-server:8080/
  ```

### 3. GitHub Packages
```yaml
# .github/workflows/publish.yml
name: Publish DXT Package

on: [push]

jobs:
  build-and-publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
      - name: Install DXT
        run: pip install dxt
      - name: Build package
        run: dxt pack --output dist/package.dxt
      - name: Publish to GitHub Packages
        uses: actions/upload-artifact@v3
        with:
          name: package
          path: dist/package.dxt
```

## 🆕 FastMCP 2.11+ Features

### Enhanced State Management (2.11+)
```python
# New in 2.11: Atomic state updates
async def update_counter():
    async with state.transaction() as tx:
        count = await tx.get("counter", 0)
        await tx.set("counter", count + 1)
        # Changes are committed when the block exits
```

### Performance Improvements (2.12+)
- **Connection Pooling**: Automatic for database connections
- **Request Batching**: Combine multiple tool calls
- **Reduced Latency**: Up to 40% improvement in response times

## 🚀 FastMCP 2.14.3 Features

### Consistent State Management
```python
# 2.13: Strong consistency guarantees
app = FastMCP("App", consistency="strong")

@app.tool()
async def process_data(data: dict):
    # State changes are immediately visible to all clients
    await state.set(f"data/{data['id']}", data)
    return {"status": "processed"}
```

### New in 2.13:
1. **Atomic Transactions**
   ```python
   async with state.transaction() as tx:
       # Multiple operations in a single transaction
       await tx.set("user:1:name", "Alice")
       await tx.set("user:1:last_login", datetime.utcnow())
       # All or nothing
   ```

2. **State Observers**
   ```python
   @app.state_observer("user:*")
   async def log_user_changes(key: str, old_value: Any, new_value: Any):
       logger.info(f"User data changed: {key}")
   ```

3. **Distributed Locks**
   ```python
   async with state.lock("resource:123"):
       # Critical section
       data = await state.get("resource:123")
       await state.set("resource:123", process(data))
   ```

## 🔄 FastMCP 2.14.3 State Management

### Consistent State Management
```python
from fastmcp import FastMCP, StateManager

app = FastMCP("Database Operations MCP")
state = StateManager()

@app.on_startup
async def startup():
    # Initialize database connections and state
    await state.set("db_initialized", False)
    # Add other initialization logic here

@app.tool()
async def query_database(query: str, params: dict = None):
    """Execute a database query with state tracking"""
    if not await state.get("db_initialized"):
        await initialize_database_connection()
        await state.set("db_initialized", True)
    
    # Execute query and return results
    return await execute_sql(query, params or {})
```

## 🔄 DXT Packaging & Distribution

### Package Creation & Signing
```powershell
# Build the package
.\scripts\build-mcp-package.ps1

# Manual alternative
dxt pack . dist/
dxt sign dist/package-name.dxt
```

### Package Structure
```
database-operations-mcp/
├── src/
│   └── database_operations_mcp/
│       ├── __init__.py
│       ├── server.py
│       └── state/          # State management
│           └── __init__.py
├── tests/
├── pyproject.toml
└── dxt.json
```

### dxt.json Example
```json
{
  "name": "@your-org/database-operations-mcp",
  "version": "1.0.0",
  "description": "Database operations MCP server with state management",
  "author": "Your Team",
  "license": "Proprietary",
  "dependencies": {
    "fastmcp": ">=2.13.0",
    "loguru": ">=0.7.0",
    "sqlalchemy": "^2.0.0"
  },
  "mcp": {
    "entrypoint": "database_operations_mcp.server:app",
    "state_backend": "redis",
    "min_fastmcp": "2.13.0"
  }
}
```

## 🔒 Security Best Practices

### Database Security
1. **Connection Handling**:
   ```python
   from contextlib import asynccontextmanager
   
   @asynccontextmanager
   async def get_db_connection():
       conn = await create_db_connection()
       try:
           yield conn
       finally:
           await conn.close()
   ```

2. **Query Safety**:
   ```python
   # Use parameterized queries
   async def get_user(user_id: str):
       async with get_db_connection() as conn:
           return await conn.fetchrow(
               "SELECT * FROM users WHERE id = $1", 
               user_id
           )
   ```

## 🧪 Testing

### Testing with State
```python
import pytest
from fastmcp.testing import TestClient

@pytest.fixture
async def test_app():
    app = create_test_app()
    async with TestClient(app) as client:
        # Setup test database
        await client.state.set("test_db_ready", True)
        yield client

async def test_database_query(test_app):
    result = await test_app.tools.query_database(
        "SELECT * FROM test_table"
    )
    assert result is not None
```

## 🔄 State Persistence

### Redis Configuration
```python
from fastmcp.state.backends import RedisBackend
import os

app = FastMCP("Database Operations")
app.state = RedisBackend(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

@app.on_shutdown
async def cleanup():
    await app.state.close()
```

## 🚀 Performance Tips

1. **Connection Pooling**:
   ```python
   from asyncpg import create_pool
   
   @app.on_startup
   async def init_db_pool():
       app.state.db_pool = await create_pool(
           dsn=os.getenv("DATABASE_URL"),
           min_size=1,
           max_size=10
       )
   ```

2. **Caching**:
   ```python
   @app.tool()
   @cached(ttl=300)  # 5 minute cache
   async def get_frequently_accessed_data():
       return await expensive_database_query()
   ```

## 🛠️ Development Tools & Workflow

### VS Code Launch Configuration
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug MCP Server",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "your_mcp:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
      ],
      "jinja": true,
      "justMyCode": false
    }
  ]
}
```

### Logging Configuration
```python
import logging
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "mcp_server.log"),
        logging.StreamHandler()
    ]
)

# Use in your code
logger = logging.getLogger(__name__)
```

## 🛠️ DXT CLI Reference (2.13+)

### Package Management
```bash
# List installed packages
dxt list

# Show package details
dxt info package-name

# Install specific version
dxt install --source github:your-org/your-repo#v1.2.3

# Update all dependencies
dxt update

# Build package
dxt pack . dist/

# Validate manifest
dxt validate manifest.json

# Sign package
dxt sign --key your-key.pem dist/package.dxt

# Verify package
dxt verify --key your-key.pem dist/package.dxt

# Publish package
dxt publish --registry your-registry dist/package.dxt
```

### Registry Management

```bash
# List packages in registry
dxt search --registry your-registry

# Configure registry
dxt config set registry.url https://your-registry.example.com

# Add new registry
dxt registry add my-registry https://registry.example.com

# Set default registry
dxt registry use my-registry

# List configured registries
dxt registry list
```

## 🛠 Troubleshooting & Best Practices

### Avoiding Common Pitfalls

#### 1. Proper Decorator Usage
```python
# Good: Properly indented multi-line decorator
@tool()
async def process_data(
    param1: str,
    param2: dict,
    param3: list = None
) -> dict:
    """Process data with proper type hints and docstrings."""
    
# Bad: Inconsistent indentation
@tool()
   async def bad_example():
    pass
```

#### 2. Auto Tool Registration
```python
# In your __init__.py
from fastmcp import FastMCP
from pathlib import Path

app = FastMCP("MyApp", auto_discover=True)

# Auto-discover tools in the 'tools' package
app.auto_discover("tools")
```

#### 3. Avoiding Dual Event Loops
```python
# Good: Proper async context
async def main():
    app = FastMCP("MyApp")
    await app.start()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

# Bad: Nested event loops
async def bad_example():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)  # Causes issues with Claude Desktop
```

### Claude Desktop Integration

#### Effective Debugging Workflow
1. **Start Fresh**
   - Close Claude Desktop completely
   - Clear any existing logs: `%LOCALAPPDATA%\Claude\logs\*`
   - Start Claude Desktop with logging:
     ```powershell
     $env:ANTHROPIC_ENABLE_LOGGING=1
     Start-Process "C:\Path\To\Claude.exe"
     ```

2. **Monitor Logs in Real-Time**
   - Open log file in Notepad++ with "View" > "Monitoring (tail -f)"
   - Default log location: `%LOCALAPPDATA%\Claude\logs\claude.log`
   - Filter for errors: `ERROR|Exception|Traceback`

3. **Error Resolution Strategy**
   - Copy error messages to Windsurf
   - Use Windsurf's free tier for quick fixes
   - Apply fixes incrementally
   - Test after each change

#### Common Issues & Fixes
1. **MCP Not Loading**
   - Check manifest.json for correct format
   - Verify all required fields are present
   - Ensure package name follows conventions: `@org/package-name`

2. **Connection Timeouts**
   - Increase timeout in config:
     ```json
     {
       "timeout": 30,
       "retries": 3
     }
     ```

3. **Version Conflicts**
   - Pin critical dependencies
   - Use virtual environments
   - Document known working versions

## 📚 Additional Resources
- [FastMCP 2.14.3 Documentation](https://fastmcp.anthropic.com/docs/2.14.3/)
- [MCPB Building Guide](./../mcpb-packaging/MCPB_BUILDING_GUIDE.md)
- [Database Operations MCP Architecture](./ARCHITECTURE.md)
