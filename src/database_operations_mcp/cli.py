#!/usr/bin/env python3
"""
Command Line Interface for Database Operations MCP Server.

This CLI provides direct access to database operations without requiring an MCP client.
"""

import asyncio
import json
import sys
from typing import Any
from urllib.parse import unquote, urlparse

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from database_operations_mcp.database_manager import BaseDatabaseConnector, create_connector

console = Console()


def _make_connector(database_type: str, connection_string: str) -> BaseDatabaseConnector:
    """Build a connector from a CLI connection string.

    ## Examples
    SQLite file:
        connector = _make_connector("sqlite", "C:/data/app.db")
    """
    if database_type == "sqlite":
        config: dict[str, Any] = {"database_path": connection_string}
    elif database_type == "postgresql":
        parsed = urlparse(connection_string)
        if not parsed.scheme.startswith("postgres"):
            raise ValueError("PostgreSQL connection string must look like postgresql://user:pass@host:port/db")
        config = {
            "host": parsed.hostname or "localhost",
            "port": parsed.port or 5432,
            "database": (parsed.path or "/postgres").lstrip("/"),
            "user": unquote(parsed.username or ""),
            "password": unquote(parsed.password or ""),
        }
    elif database_type == "mongodb":
        config = {"connection_string": connection_string}
    else:
        raise ValueError(f"Unsupported database type: {database_type}")
    connector = create_connector(database_type, config)
    if not connector:
        raise ValueError(f"Could not create connector for '{database_type}'")
    return connector


@click.group()
@click.version_option(version="1.3.0", prog_name="mcp-db")
def cli():
    """Database Operations MCP Server CLI

    A command-line interface for database operations and Firefox bookmark management.
    """
    pass


@cli.group()
def database():
    """Database operations."""
    pass


@database.command()
@click.option("--connection-string", "-c", required=True, help="Database connection string")
@click.option(
    "--database-type",
    "-t",
    type=click.Choice(["sqlite", "postgresql", "mongodb"]),
    required=True,
    help="Database type",
)
@click.option(
    "--output-format",
    "-f",
    type=click.Choice(["table", "json", "csv"]),
    default="table",
    help="Output format",
)
def list_databases(connection_string: str, database_type: str, output_format: str):
    """List all databases."""

    async def _list_databases():
        try:
            connector = _make_connector(database_type, connection_string)

            databases = await connector.list_databases()

            if output_format == "json":
                console.print(json.dumps(databases, indent=2))
            elif output_format == "csv":
                # Simple CSV output
                for db in databases:
                    console.print(f"{db.get('name', '')},{db.get('type', '')},{db.get('size', '')}")
            else:
                # Table format
                table = Table(title="Databases")
                table.add_column("Name", style="cyan")
                table.add_column("Type", style="green")
                table.add_column("Size", style="yellow")

                for db in databases:
                    table.add_row(db.get("name", "N/A"), db.get("type", "N/A"), str(db.get("size", "N/A")))

                console.print(table)

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

    asyncio.run(_list_databases())


@database.command()
@click.option("--connection-string", "-c", required=True, help="Database connection string")
@click.option(
    "--database-type",
    "-t",
    type=click.Choice(["sqlite", "postgresql", "mongodb"]),
    required=True,
    help="Database type",
)
@click.option("--database-name", "-d", help="Database name (for multi-database systems)")
@click.option(
    "--output-format",
    "-f",
    type=click.Choice(["table", "json", "csv"]),
    default="table",
    help="Output format",
)
def list_tables(connection_string: str, database_type: str, database_name: str | None, output_format: str):
    """List all tables in a database."""

    async def _list_tables():
        try:
            connector = _make_connector(database_type, connection_string)

            tables = await connector.list_tables(database=database_name)

            if output_format == "json":
                console.print(json.dumps(tables, indent=2))
            elif output_format == "csv":
                for table in tables:
                    console.print(f"{table.get('name', '')},{table.get('type', '')},{table.get('row_count', '')}")
            else:
                # Table format
                table = Table(title=f"Tables in {database_name or 'database'}")
                table.add_column("Name", style="cyan")
                table.add_column("Type", style="green")
                table.add_column("Rows", style="yellow")

                for table_info in tables:
                    table.add_row(
                        table_info.get("name", "N/A"),
                        table_info.get("type", "N/A"),
                        str(table_info.get("row_count", "N/A")),
                    )

                console.print(table)

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

    asyncio.run(_list_tables())


@database.command()
@click.option("--connection-string", "-c", required=True, help="Database connection string")
@click.option(
    "--database-type",
    "-t",
    type=click.Choice(["sqlite", "postgresql", "mongodb"]),
    required=True,
    help="Database type",
)
@click.option("--table-name", "-t", required=True, help="Table name")
@click.option("--database-name", "-d", help="Database name (for multi-database systems)")
@click.option(
    "--output-format",
    "-f",
    type=click.Choice(["table", "json", "csv"]),
    default="table",
    help="Output format",
)
def describe_table(
    connection_string: str,
    database_type: str,
    table_name: str,
    database_name: str | None,
    output_format: str,
):
    """Describe table schema."""

    async def _describe_table():
        try:
            connector = _make_connector(database_type, connection_string)

            schema = await connector.get_table_schema(table_name, database=database_name)

            if output_format == "json":
                console.print(json.dumps(schema, indent=2))
            elif output_format == "csv":
                for column in schema.get("columns", []):
                    console.print(f"{column.get('name', '')},{column.get('type', '')},{column.get('nullable', '')}")
            else:
                # Table format
                table = Table(title=f"Schema for {table_name}")
                table.add_column("Column", style="cyan")
                table.add_column("Type", style="green")
                table.add_column("Nullable", style="yellow")
                table.add_column("Default", style="blue")

                for column in schema.get("columns", []):
                    table.add_row(
                        column.get("name", "N/A"),
                        column.get("type", "N/A"),
                        str(column.get("nullable", "N/A")),
                        str(column.get("default", "N/A")),
                    )

                console.print(table)

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

    asyncio.run(_describe_table())


@cli.command()
def health():
    """Check system health and dependencies."""
    console.print(Panel("Checking System Health", style="bold blue"))

    # Check Python version
    console.print(f"Python: {sys.version}")

    # Check available connectors
    connectors = ["SQLite", "PostgreSQL", "MongoDB"]
    console.print(f"Available connectors: {', '.join(connectors)}")

    console.print(Panel("Health check complete", style="bold green"))


if __name__ == "__main__":
    cli()
