#!/usr/bin/env python3
"""
Command Line Interface for Database Operations MCP Server.

This CLI provides direct access to database operations without requiring an MCP client.
"""

import asyncio
import json
import sys
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from database_operations_mcp.services.database.connectors.mongodb_connector import MongoDBConnector
from database_operations_mcp.services.database.connectors.postgresql_connector import (
    PostgreSQLConnector,
)
from database_operations_mcp.services.database.connectors.sqlite_connector import SQLiteConnector
from database_operations_mcp.tools.firefox.utils import (
    get_firefox_profiles as get_profiles,
)

console = Console()


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
            if database_type == "sqlite":
                connector = SQLiteConnector(connection_string)
            elif database_type == "postgresql":
                connector = PostgreSQLConnector(connection_string)
            elif database_type == "mongodb":
                connector = MongoDBConnector(connection_string)
            else:
                console.print(f"[red]Unsupported database type: {database_type}[/red]")
                return

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
                    table.add_row(
                        db.get("name", "N/A"), db.get("type", "N/A"), str(db.get("size", "N/A"))
                    )

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
def list_tables(
    connection_string: str, database_type: str, database_name: Optional[str], output_format: str
):
    """List all tables in a database."""

    async def _list_tables():
        try:
            if database_type == "sqlite":
                connector = SQLiteConnector(connection_string)
            elif database_type == "postgresql":
                connector = PostgreSQLConnector(connection_string)
            elif database_type == "mongodb":
                connector = MongoDBConnector(connection_string)
            else:
                console.print(f"[red]Unsupported database type: {database_type}[/red]")
                return

            tables = await connector.list_tables(database=database_name)

            if output_format == "json":
                console.print(json.dumps(tables, indent=2))
            elif output_format == "csv":
                for table in tables:
                    console.print(
                        f"{table.get('name', '')},{table.get('type', '')},"
                        f"{table.get('row_count', '')}"
                    )
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
    database_name: Optional[str],
    output_format: str,
):
    """Describe table schema."""

    async def _describe_table():
        try:
            if database_type == "sqlite":
                connector = SQLiteConnector(connection_string)
            elif database_type == "postgresql":
                connector = PostgreSQLConnector(connection_string)
            elif database_type == "mongodb":
                connector = MongoDBConnector(connection_string)
            else:
                console.print(f"[red]Unsupported database type: {database_type}[/red]")
                return

            schema = await connector.get_table_schema(table_name, database=database_name)

            if output_format == "json":
                console.print(json.dumps(schema, indent=2))
            elif output_format == "csv":
                for column in schema.get("columns", []):
                    console.print(
                        f"{column.get('name', '')},{column.get('type', '')},"
                        f"{column.get('nullable', '')}"
                    )
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


@cli.group()
def firefox():
    """Firefox bookmark operations."""
    pass


@firefox.command()
def list_profiles():
    """List available Firefox profiles."""
    try:
        profiles = get_profiles()

        if profiles.get("success"):
            table = Table(title="Firefox Profiles")
            table.add_column("Name", style="cyan")
            table.add_column("Path", style="green")
            table.add_column("Default", style="yellow")

            for profile in profiles.get("profiles", []):
                table.add_row(
                    profile.get("name", "N/A"),
                    profile.get("path", "N/A"),
                    "OK" if profile.get("is_default", False) else "",
                )

            console.print(table)
        else:
            console.print(f"[red]Error: {profiles.get('error', 'Unknown error')}[/red]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
def health():
    """Check system health and dependencies."""
    console.print(Panel("Checking System Health", style="bold blue"))

    # Check Python version
    console.print(f"Python: {sys.version}")

    # Check available connectors
    connectors = ["SQLite", "PostgreSQL", "MongoDB"]
    console.print(f"Available connectors: {', '.join(connectors)}")

    # Check Firefox availability
    try:
        profiles = get_profiles()
        if profiles.get("success"):
            console.print(
                f"[green]OK Firefox: {len(profiles.get('profiles', []))} profiles found[/green]"
            )
        else:
            console.print(
                f"[yellow]WARN Firefox: {profiles.get('error', 'Not available')}[/yellow]"
            )
    except Exception as e:
        console.print(f"[yellow]WARN Firefox: {e}[/yellow]")

    console.print(Panel("Health check complete", style="bold green"))


if __name__ == "__main__":
    cli()
