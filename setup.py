from pathlib import Path
from setuptools import setup, find_packages

# Read the contents of README.md
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements from requirements files
def read_requirements(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Core dependencies
install_requires = [
    "fastmcp>=2.11.3",
    "pydantic>=1.10.0",
    "sqlalchemy>=2.0.0",
    "psycopg2-binary>=2.9.0",
    "pymongo>=4.0.0",
    "chromadb>=0.4.0",
    "pandas>=1.5.0",
    "python-dotenv>=1.0.0",
    "pywin32>=305; sys_platform == 'win32'"
]

# Development dependencies
extras_require = {
    'dev': [
        'pytest>=7.0.0',
        'pytest-asyncio>=0.21.0',
        'pytest-cov>=4.0.0',
        'pytest-mock>=3.10.0',
        'black>=23.0.0',
        'isort>=5.12.0',
        'mypy>=1.0.0',
        'flake8>=6.0.0',
        'sphinx>=6.0.0',
        'sphinx-rtd-theme>=1.2.0',
        'pre-commit>=3.0.0',
    ],
    'test': [
        'pytest>=7.0.0',
        'pytest-asyncio>=0.21.0',
        'pytest-cov>=4.0.0',
        'pytest-mock>=3.10.0',
    ],
}

setup(
    name="database-operations-mcp",
    version="0.1.0",
    author="Sandra Schilling",
    author_email="sandra@example.com",
    description="Universal Database Operations MCP with Windows Registry support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sandraschi/database-operations-mcp",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=install_requires,
    extras_require=extras_require,
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS"
    ],
    entry_points={
        "console_scripts": [
            "database-operations-mcp=database_operations_mcp.main:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/sandraschi/database-operations-mcp/issues",
        "Source": "https://github.com/sandraschi/database-operations-mcp",
    },
)
