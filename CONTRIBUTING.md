# Contributing to Database Operations MCP

Thank you for your interest in contributing to Database Operations MCP! We welcome contributions from everyone, whether it's reporting bugs, suggesting new features, or submitting code changes.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Running Tests](#running-tests)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)
- [Feature Requests](#feature-requests)
- [License](#license)

## Code of Conduct

This project adheres to the [Contributor Covenant](https://www.contributor-covenant.org/). By participating, you are expected to uphold this code.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment (see below)
4. Create a feature branch for your changes
5. Make your changes and commit them with clear, descriptive messages
6. Push your changes to your fork
7. Open a pull request against the main repository

## Development Setup

1. **Prerequisites**
   - Python 3.9 or higher
   - Git
   - (Optional) A virtual environment (recommended)

2. **Installation**
   ```bash
   # Clone the repository
   git clone https://github.com/your-username/database-operations-mcp.git
   cd database-operations-mcp
   
   # Create and activate a virtual environment (recommended)
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install the package in development mode with all dependencies
   pip install -e ".[dev]"
   
   # Install pre-commit hooks
   pre-commit install
   ```

## Running Tests

Run the test suite with:

```bash
pytest
```

For test coverage report:

```bash
pytest --cov=src --cov-report=term-missing
```

## Code Style

We use several tools to maintain code quality and style:

- **Black** for code formatting
- **isort** for import sorting
- **Flake8** for linting
- **mypy** for static type checking

These are automatically checked by pre-commit hooks. You can also run them manually:

```bash
# Format code with Black
black src tests

# Sort imports with isort
isort src tests

# Check code style with flake8
flake8 src tests

# Check types with mypy
mypy src tests
```

## Submitting Changes

1. Make sure all tests pass
2. Ensure your code follows the style guidelines
3. Update the documentation if necessary
4. Write clear commit messages
5. Push your changes to your fork
6. Open a pull request with a clear description of your changes

## Reporting Issues

When reporting issues, please include:

- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs. actual behavior
- Any relevant error messages or logs
- Your environment (OS, Python version, etc.)

## Feature Requests

We welcome feature requests! Please open an issue to discuss your idea before submitting a pull request.

## License

By contributing to this project, you agree that your contributions will be licensed under the [MIT License](LICENSE).
