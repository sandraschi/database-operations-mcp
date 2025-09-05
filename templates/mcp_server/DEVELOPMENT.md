# FastMCP Server Development Guide

## 🚀 Getting Started

### Prerequisites
- Python 3.10+ (3.11+ recommended)
- Git 2.30+
- Docker 20.10+ & Docker Compose 2.0+
- Poetry 1.4+ (recommended) or pip 22.0+
- Node.js 18+ (for frontend development)
- Make (optional, for convenience commands)

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd database-operations-mcp

# Set up Python environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
# OR
source .venv/bin/activate   # Linux/macOS

# Install dependencies
poetry install --with dev

# Set up pre-commit hooks
pre-commit install

# Run the development server
make dev
```

## 🏗️ Project Structure

```
.
├── .github/              # GitHub Actions workflows
├── docker/               # Docker configurations
├── docs/                 # Documentation
├── src/                  # Source code
│   ├── mcp_server/       # FastMCP server implementation
│   │   ├── api/          # FastAPI routes
│   │   ├── core/         # Core functionality
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic
│   │   └── utils/        # Utility functions
│   └── tests/            # Test suite
├── .env.example         # Environment variables template
├── docker-compose.yml   # Docker Compose configuration
├── pyproject.toml       # Python project metadata
└── README.md            # Project overview
```

## 🛠️ Development Workflow

### Branching Strategy
We use GitHub Flow with the following branch types:
- `main` - Production-ready code
- `develop` - Integration branch
- `feature/*` - New features
- `fix/*` - Bug fixes
- `chore/*` - Maintenance tasks

### Making Changes

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit:
   ```bash
   # Stage changes
   git add .
   
   # Commit with semantic message
   git commit -m "feat: add new database connection handler"
   ```

3. Run tests and checks:
   ```bash
   make test       # Run tests
   make lint       # Check code style
   make typecheck  # Type checking
   ```

4. Push your changes:
   ```bash
   git push -u origin feature/your-feature-name
   ```

5. Create a Pull Request (PR) on GitHub

## 🐳 Docker Development

### Development Environment

```bash
# Start all services
docker-compose up -d

# Run specific service
docker-compose up -d postgres redis

# View logs
docker-compose logs -f

# Run commands in container
docker-compose exec mcp-server bash
```

### Building Images

```bash
# Build development image
docker-compose build

# Build production image
docker build -t your-org/mcp-server:latest .
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflows

1. **CI Pipeline** (`.github/workflows/ci.yml`)
   - Runs on every push/pull request
   - Lints code
   - Runs tests
   - Builds Docker image
   - Runs security scans

2. **CD Pipeline** (`.github/workflows/cd.yml`)
   - Triggers on tags (v*)
   - Builds and pushes production Docker image
   - Deploys to staging/production
   - Updates documentation

### Environment Variables

Required GitHub Secrets:
- `DOCKERHUB_USERNAME` - Docker Hub username
- `DOCKERHUB_TOKEN` - Docker Hub access token
- `PYPI_TOKEN` - PyPI API token
- `PROD_SSH_KEY` - SSH key for production deployment

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_models.py

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run tests in parallel
pytest -n auto
```

### Test Organization

- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`
- E2E tests: `tests/e2e/`
- Fixtures: `tests/conftest.py`

## 📦 Packaging & Distribution

### Building Packages

```bash
# Build Python package
poetry build

# Build Docker image
docker build -t your-org/mcp-server:latest .

# Build DXT package
dxt pack -o dist/mcp-server.dxt
```

### Versioning

We follow [Semantic Versioning](https://semver.org/):
- MAJOR: Incompatible API changes
- MINOR: Backwards-compatible functionality
- PATCH: Backwards-compatible bug fixes

### Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create a release tag:
   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin v1.0.0
   ```
4. GitHub Actions will automatically publish the package

## 🔒 Security

### Best Practices

- Never commit secrets to version control
- Use environment variables for configuration
- Keep dependencies updated
- Run security scans regularly

### Security Tools

```bash
# Dependency scanning
safety check

# Static code analysis
bandit -r src/

# Container scanning
docker scan your-org/mcp-server
```

## 📚 Documentation

### Building Docs

```bash
# Install docs dependencies
poetry install --with docs

# Build documentation
cd docs
make html

# Serve docs locally
python -m http.server 8000 --directory _build/html
```

### Documentation Standards

- Use Google-style docstrings
- Include type hints
- Document all public APIs
- Keep README.md up to date

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 🚨 Troubleshooting

### Common Issues

**Docker Compose Fails**
- Check if ports are in use
- Verify Docker is running
- Check disk space

**Database Connection Issues**
- Verify database is running
- Check connection strings
- Look for migration issues

**Dependency Conflicts**
```bash
poetry update
poetry lock --no-update
```

## 📞 Support

For help, please:
1. Check the [documentation](docs/)
2. Search existing issues
3. Open a new issue if needed

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
