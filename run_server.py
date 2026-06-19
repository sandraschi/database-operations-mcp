"""PyInstaller entry point."""
import _strptime  # noqa: F401
import sys
sys.path.insert(0, "src")
import _strptime  # noqa: F401
import uvicorn
from database_operations_mcp.http_app import run_http_web
sys.exit(run_http_web())

