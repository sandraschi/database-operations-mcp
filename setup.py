from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="database-operations-mcp",
    version="0.1.0",
    author="Sandra",
    author_email="sandra@example.com",
    description="Universal Database Operations MCP with Windows Registry support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sandraschi/database-operations-mcp",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "fastmcp>=2.10.1",
        "pydantic>=1.10.0",
        "sqlalchemy>=2.0.0",
        "psycopg2-binary>=2.9.0",
        "pymongo>=4.0.0",
        "chromadb>=0.4.0",
        "pandas>=1.5.0",
        "python-dotenv>=1.0.0",
        "pywin32>=305; sys_platform == 'win32'"
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
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
            "database-operations-mcp=src.database_operations.main:main",
        ],
    },
)
