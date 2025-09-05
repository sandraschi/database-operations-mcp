# Contributing to MCP Server Template

Thank you for your interest in contributing to the MCP Server Template! We welcome contributions from everyone, regardless of experience level.

## How to Contribute

### Reporting Bugs
1. Check if the issue has already been reported in the [issues section](https://github.com/yourusername/mcp-server-template/issues).
2. If not, create a new issue with a clear title and description.
3. Include steps to reproduce the issue and any relevant error messages.

### Suggesting Enhancements
1. Check if the enhancement has already been suggested.
2. Create a new issue describing the enhancement and why it would be valuable.
3. Include any relevant examples or use cases.

### Making Code Changes
1. Fork the repository and create a new branch for your changes.
2. Make your changes following the coding standards.
3. Add tests for your changes.
4. Run the test suite to ensure all tests pass.
5. Submit a pull request with a clear description of your changes.

## Development Setup

### Prerequisites
- Python 3.9+
- Git
- Poetry (recommended) or pip

### Setup

```bash
# Fork and clone the repository
git clone https://github.com/yourusername/mcp-server-template.git
cd mcp-server-template

# Install dependencies
poetry install

# Install development dependencies
poetry install --with dev

# Install pre-commit hooks
pre-commit install
```

### Testing

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=./ --cov-report=term-missing
```

### Code Style

We use the following tools to maintain code quality:
- Black for code formatting
- isort for import sorting
- flake8 for linting
- mypy for type checking

Run these tools before committing:

```bash
# Format code
black .

# Sort imports
isort .

# Check code style
flake8

# Check types
mypy .
```

## Pull Request Process

1. Ensure any install or build dependencies are removed before the end of the layer when doing a build.
2. Update the README.md with details of changes to the interface, including new environment variables, exposed ports, useful file locations, and container parameters.
3. Increase the version numbers in any examples files and the README.md to the new version that this Pull Request would represent. The versioning scheme we use is [SemVer](http://semver.org/).
4. You may merge the Pull Request in once you have the sign-off of two other developers, or if you do not have permission to do that, you may request the second reviewer to merge it for you.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## License

By contributing, you agree that your contributions will be licensed under its MIT License.
