"""Main module for Database Operations MCP."""
from fastapi import FastAPI
from fastmcp import FastMCP

app = FastAPI()
mcp = FastMCP("database-operations")

# Import and register handlers
from database_operations.handlers import connection_tools, query_tools, schema_tools, management_tools

# Mount MCP app
app.mount("/mcp", mcp.app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

