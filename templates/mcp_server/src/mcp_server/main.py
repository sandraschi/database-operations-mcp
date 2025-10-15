"""MCP Server Template Implementation."""

from typing import Any, Dict

from fastapi import FastAPI
from mcp import Application

app = FastAPI()
mcp = Application()


@mcp.tool()
async def example_tool(param1: str, param2: int = 42) -> Dict[str, Any]:
    """Example tool that demonstrates the interface.

    Args:
        param1: A string parameter
        param2: An integer parameter with default value

    Returns:
        A dictionary with the processed data
    """
    return {"result": f"Processed {param1} with {param2}", "success": True}


@app.on_event("startup")
async def startup_event():
    """Initialize MCP server on startup."""
    await mcp.start()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    await mcp.stop()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
