# Python Development Guide

## Development Setup

```powershell
# Install dependencies
uv sync

# Run tests
uv run pytest -q

# Lint code
uv run ruff check .

# Format code
uv run ruff format .

# Type checking
uv run mypy src/
```

## Project Structure

- **Entry Point**: `src/database_operations_mcp/main.py`
- **MCP Config**: `src/database_operations_mcp/config/mcp_config.py`
- **Tools**: `src/database_operations_mcp/tools/`
- **Tests**: `tests/`

## Tool Registration

Tools are registered using FastMCP 2.13 decorators:
```python
from database_operations_mcp.config.mcp_config import mcp

@mcp.tool()
async def my_tool(...):
    """Tool description."""
    pass
```

## Testing

Tests use pytest with async support:
- Async tools: `pytest-asyncio` mode
- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`

## Code Quality

- **Linter**: Ruff (configured in `pyproject.toml`)
- **Type checker**: mypy (partial coverage)
- **Format**: Ruff format (auto on commit recommended)

