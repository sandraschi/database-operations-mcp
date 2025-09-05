# FastMCP Server Template

A standardized template for creating MCP (Model Control Protocol) servers using FastMCP. This template follows the [MCP Server Standards](docs/standards/MCP_Server_Standards.md) and provides a solid foundation for building production-ready MCP servers.

## Features

- 🚀 **FastMCP Integration** - Built on FastMCP 2.13+ for maximum performance
- 🧪 **Testing Ready** - Pytest with coverage reporting
- 🔄 **CI/CD** - GitHub Actions workflow for testing and deployment
- 📦 **Packaging** - Modern Python packaging with pyproject.toml
- 📚 **Documentation** - Comprehensive guides and examples
- 🔒 **Type Safety** - Full type hints and mypy support
- 🧹 **Code Quality** - Pre-commit hooks with Black, isort, and flake8
- 🛠 **Tool System** - Easy-to-implement tool system following MCP standards
- 🤖 **AI-Optimized** - Structured logging and error handling for AI integration

## 🚀 Quick Start with AI Assistance

For the best development experience, we recommend using AI-powered tools. Check out our [AI Tooling Guide](docs/ai_tooling_guide_for_the_perplexed.md) to set up your environment with the latest AI coding assistants and tools.

### Prerequisites

#### 🛠️ Core Requirements
- [Python 3.10+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)
- [Poetry](https://python-poetry.org/) (recommended) or pip

#### 🤖 AI Development Tools (Recommended)
- [Windsurf](https://windsurf.dev) - AI coding assistant
- [GitHub Copilot](https://github.com/features/copilot) or [Cursor](https://cursor.sh/)
- [Docker](https://www.docker.com/) - For containerized development

#### 📦 Python Dependencies
- FastMCP 2.13+
- See `pyproject.toml` for a complete list

## Installation

```bash
# Clone the template
git clone <repository-url> your-mcp-server
cd your-mcp-server

# Install dependencies
poetry install  # or pip install -e .

# Install development dependencies
poetry install --with dev

# Install pre-commit hooks
pre-commit install
```

## Project Structure

```
mcp-server/
├── src/
│   └── mcp_server/       # Main package
│       ├── __init__.py
│       ├── main.py       # FastMCP server entry point
│       ├── config.py     # Configuration management
│       └── tools/        # Tool implementations
│           ├── __init__.py
│           └── example_tools.py
├── tests/                # Test files
│   ├── __init__.py
│   └── test_tools.py
├── docs/                 # Documentation
│   └── standards/        # MCP Server Standards
├── .github/              # CI/CD workflows
├── pyproject.toml        # Project metadata
├── README.md             # Project documentation
├── CHANGELOG.md          # Version history
└── requirements.txt      # Dependencies
```

## Running the Server (OLD SKOOL)

```bash
# Development mode with hot-reload
python -m mcp_server.main

# Production mode
FASTMCP_ENV=production python -m mcp_server.main
```

## Running the Server (With VIBE added!)

### Claude Desktop

1. Add this to your MCP config (usually at `~/.config/claude/mcp_servers.json`):

   ```json
   {
     "database-ops": {
       "command": "python -m mcp_server.main",
       "cwd": "/path/to/your/project",
       "environment": {
         "ENV": "development"
       },
       "autoStart": true
     }
   }
   ```

### Windsurf

1. Create or update `windsurf.json` in your project root:

   ```json
   {
     "mcpServers": [
       {
         "name": "Database Ops",
         "command": "python -m mcp_server.main",
         "workingDirectory": "${workspaceFolder}",
         "autoStart": true,
         "env": {
           "LOG_LEVEL": "debug"
         }
       }
     ]
   }
   ```

### Cursor

1. Add to `.cursor/mcp.json`:

   ```json
   {
     "servers": [
       {
         "id": "db-ops",
         "name": "Database Operations",
         "command": "python -m mcp_server.main",
         "cwd": "${workspaceRoot}",
         "env": {
           "PYTHONPATH": "${workspaceRoot}/src"
         },
         "autoRestart": true
       }
     ]
   }
   ```

### Zed

1. Create `.zed/mcp.toml`:

   ```toml
   [[server]]
   name = "database-ops"
   command = "python -m mcp_server.main"
   workspace = "/path/to/your/project"
   auto_start = true
   
   [server.env]
   RUST_LOG = "info"
   ```

### General Tips

- Use environment variables for configuration
- Set `autoStart: true` for automatic server startup
- Check logs in the respective IDE's output panel
- Ensure Python path is correctly set if using virtual environments

## AI Integration

### LLM Configuration (llms.txt)

MCP servers support an `llms.txt` file in the project root to document and configure LLM interactions. This file helps with:

1. **Self-documentation** of available LLM tools and their capabilities
2. **Version control** of LLM interactions
3. **Reproducibility** of AI behaviors

Example `llms.txt`:
```
# LLM Tools Configuration
# Format: tool_name | description | input_schema | output_schema | version

get_weather | Get current weather for a location | {"location": "string", "unit": "celsius|fahrenheit"} | {"temperature": "number", "conditions": "string"} | 1.0
analyze_sentiment | Analyze text sentiment | {"text": "string"} | {"sentiment": "positive|neutral|negative", "confidence": "float"} | 1.1
```

Key features:
- **Tool Discovery**: AI assistants can read this file to understand available capabilities
- **Input Validation**: Schemas help validate inputs before execution
- **Versioning**: Track changes to tool signatures over time
- **Documentation**: Human-readable format for both developers and AI systems

## Creating a New Tool

### The VIBE Method (Recommended)

1. **Ask Windsurf** - Just tell me what you need:
   ```
   @windsurf Make a new tool that does [your tool's purpose]
   ```

2. **I'll handle**:
   - Creating the tool with proper typing
   - Writing tests
   - Registering it in the system
   - Updating documentation
   - Making sure it's properly exposed

3. **Example**:
   ```
   @windsurf Make a tool that searches our database for customer orders by email
   ```

### The Artisan Python Method (For Reference)

If you prefer to craft tools by hand:

```python
# 1. Create a new file in src/mcp_server/tools/ or add to an existing one
from typing import Dict, Any
from pydantic import BaseModel

# 2. Define your input model
class ToolInput(BaseModel):
    query: str
    max_results: int = 10

# 3. Implement your tool
async def search_orders(input_data: ToolInput) -> Dict[str, Any]:
    """
    Search for customer orders by email.
    
    Args:
        input_data: Contains search parameters
        
    Returns:
        Dict with search results
    """
    # Your implementation here
    return {"results": []}

# 4. Add to __init__.py
# from .your_module import search_orders
# __all__ = ['search_orders']
```

### Testing Your Tool

1. **Unit Tests** - Create tests in `tests/unit/test_your_tool.py`
2. **Integration Tests** - Add to `tests/integration/`
3. **Test Command**:
   ```bash
   pytest tests/unit/test_your_tool.py -v
   ```

### Registration

The tool will be automatically discovered if:
- It's in the `tools` directory
- Has proper type hints
- Is imported in the package's `__init__.py`

### Best Practices

- Keep tools focused on a single responsibility
- Use descriptive names and docstrings
- Include input validation
- Handle errors gracefully
- Add logging
- Document example usage
3. Decorate it with `@mcp.tool()`

Example tool implementation:

```python
from typing import Dict, List, Optional
from mcp import tool

@tool("convert_video")
async def convert_video(
    input_path: str,
    output_path: str,
    preset: str = "fast",
    quality: int = 22,
    audio_tracks: Optional[List[int]] = None
) -> Dict[str, any]:
    """Convert a video file using HandBrake CLI.
    
    Args:
        input_path: Path to the input video file
        output_path: Path for the converted output file
        preset: Encoding preset (e.g., 'fast', 'hq', 'superhq')
        quality: RF quality (lower is better quality, 18-28 recommended)
        audio_tracks: List of audio track numbers to include (None for all)
        
    Returns:
        Dict containing conversion status and metadata
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If preset or quality is invalid
    """
    # Implementation here
    return {
        "status": "success",
        "input": input_path,
        "output": output_path,
        "preset": preset,
        "quality": quality,
        "audio_tracks": audio_tracks or "all"
    }
```

## Development

### Testing

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=./ --cov-report=term-missing
```

### Code Quality

```bash
# Format code
black .

# Sort imports
isort .

# Check code style
flake8

# Type checking
mypy .
```

### Building and Publishing

```bash
# Build package
python -m build

# Publish to PyPI (requires credentials)
python -m twine upload dist/*
```

## Documentation

- [MCP Server Standards](docs/standards/MCP_Server_Standards.md) - Technical standards and guidelines
- [Development Workflow](DEVELOPMENT.md) - Guide for developers
- [Branching Strategy](BRANCHING_STRATEGY.md) - Version control workflow
- [HandBrake MCP PRD](#handbrake-mcp-prd) - Example implementation PRD

## HandBrake MCP PRD

### Overview
This is a Product Requirements Document (PRD) for a HandBrake video compressor MCP server that provides AI-accessible video conversion capabilities.

### Features

#### Core Functionality

- Video format conversion (MP4, MKV, WebM, etc.)
- Preset management (Fast, HQ, Super HQ, etc.)
- Batch processing support
- Progress tracking and notifications

#### Technical Specifications

- **Input Formats**: All formats supported by HandBrake CLI
- **Output Formats**: MP4, MKV, WebM
- **Codecs**: H.264, H.265, VP9, AV1
- **Resolution**: 240p to 8K
- **Bitrate Control**: CQ, ABR, 2-pass

#### Tool Definitions

1. **convert_video**
   - Converts a single video file
   - Handles format, codec, quality settings

2. **batch_convert**
   - Processes multiple files with same settings
   - Supports directory watching

3. **get_presets**
   - Lists available HandBrake presets
   - Shows preset details and recommended use cases

4. **get_progress**
   - Monitors active conversions
   - Provides ETA and current progress

### Example Usage

```python
# Convert a single video
await convert_video(
    input_path="/videos/input.mkv",
    output_path="/videos/output.mp4",
    preset="hq",
    quality=20
)

# Batch convert all videos in a directory
await batch_convert(
    input_dir="/videos/raw",
    output_dir="/videos/compressed",
    output_format="mp4",
    preset="fast"
)
```

## License

MIT - See [LICENSE](LICENSE) for more information.

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details on our [Code of Conduct](CODE_OF_CONDUCT.md) and the process for submitting pull requests.

## Support

For support, please open an issue in the GitHub repository.

## Acknowledgments

- Built with [FastMCP](https://github.com/yourorg/fastmcp)
- Powered by [HandBrake CLI](https://handbrake.fr/)
- Testing with [pytest](https://docs.pytest.org/)
- Code formatting with [Black](https://github.com/psf/black)
