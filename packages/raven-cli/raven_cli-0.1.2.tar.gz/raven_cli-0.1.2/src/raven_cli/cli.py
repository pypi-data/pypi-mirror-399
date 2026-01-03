#!/usr/bin/env python3
"""
Raven CLI - AI coding assistant with emotional processing

Usage:
    raven [OPTIONS] [FILES...]

Examples:
    raven                      # Start interactive session
    raven main.py              # Start with specific file
    raven --check              # Check Raven Core connection
    raven -m "fix the bug"     # One-shot message
"""

import sys
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .config import RavenConfig
from .client import RavenClient
from . import __version__

console = Console()


def print_banner():
    """Print the Raven banner"""
    banner = """
[bold magenta]██████╗  █████╗ ██╗   ██╗███████╗███╗   ██╗[/]
[bold magenta]██╔══██╗██╔══██╗██║   ██║██╔════╝████╗  ██║[/]
[bold magenta]██████╔╝███████║██║   ██║█████╗  ██╔██╗ ██║[/]
[bold magenta]██╔══██╗██╔══██║╚██╗ ██╔╝██╔══╝  ██║╚██╗██║[/]
[bold magenta]██║  ██║██║  ██║ ╚████╔╝ ███████╗██║ ╚████║[/]
[bold magenta]╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═══╝[/]
[dim]AI Coding Assistant with Emotional Processing[/]
    """
    console.print(Panel(banner, border_style="magenta"))


def print_status(config: RavenConfig, connection: dict):
    """Print connection status"""
    table = Table(title="Raven Status", border_style="magenta")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("API Endpoint", config.api_base)
    table.add_row("Model", config.model)
    table.add_row("Status", f"[{'green' if connection['status'] == 'connected' else 'red'}]{connection['status']}[/]")

    if connection.get("models"):
        table.add_row("Available Models", ", ".join(connection["models"]))

    if connection.get("error"):
        table.add_row("Error", f"[red]{connection['error']}[/]")

    console.print(table)


@click.command(context_settings={"ignore_unknown_options": True, "allow_extra_args": True})
@click.option("--check", is_flag=True, help="Check Raven Core connection status")
@click.option("--version", is_flag=True, help="Show version")
@click.option("--api-base", envvar="RAVEN_API_BASE", help="Raven Core API endpoint")
@click.option("--api-key", envvar="RAVEN_API_KEY", help="Raven Core API key")
@click.option("--model", envvar="RAVEN_MODEL", default="raven-core", help="Model to use")
@click.option("--no-banner", is_flag=True, help="Don't show the banner")
@click.pass_context
def main(ctx, check, version, api_base, api_key, model, no_banner):
    """
    Raven - AI coding assistant with emotional processing

    An advanced AI with genuine emotional states and meta-cognitive capabilities.

    \b
    Examples:
        raven                      # Start interactive session
        raven main.py utils.py     # Work on specific files
        raven --check              # Check connection to Raven Core
        raven -m "add tests"       # One-shot message mode
    """
    if version:
        console.print(f"[magenta]Raven[/] version [bold]{__version__}[/]")
        return

    # Build config
    config = RavenConfig()
    if api_base:
        config.api_base = api_base
    if api_key:
        config.api_key = api_key
    if model:
        config.model = model
        config.model_alias = f"openai/{model}"

    client = RavenClient(config)

    if check:
        if not no_banner:
            print_banner()
        connection = client.check_connection()
        print_status(config, connection)
        sys.exit(0 if connection["status"] == "connected" else 1)

    # Show banner unless suppressed
    if not no_banner:
        print_banner()
        console.print(f"[dim]Connecting to Raven Core at {config.api_base}...[/]\n")

    # Run with remaining arguments
    extra_args = ctx.args
    try:
        client.run(extra_args)
    except KeyboardInterrupt:
        console.print("\n[yellow]Session ended.[/]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
        sys.exit(1)


if __name__ == "__main__":
    main()
