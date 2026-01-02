"""
Main CLI application for EnkaliPrime.

Provides commands for interactive chat, configuration management, and session handling.
"""

import typer
from typing import Optional
from rich.console import Console

from . import __app_name__, __version__
from .commands import chat, config, session

# Initialize Rich console for beautiful output
console = Console()

# Create the main Typer app
app = typer.Typer(
    name=__app_name__,
    help="🤖 EnkaliPrime CLI - AI Chat from your terminal",
    add_completion=True,
    rich_markup_mode="rich",
)

# Add subcommands
app.add_typer(chat.app, name="chat", help="💬 Interactive chat with AI")
app.add_typer(config.app, name="config", help="⚙️  Manage configuration and API keys")
app.add_typer(session.app, name="session", help="📝 Manage chat sessions")


@app.callback()
def callback(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-V",
        help="Show version information",
        is_eager=True,
    ),
):
    """EnkaliPrime CLI - AI Chat from your terminal."""
    if version:
        console.print(f"[bold blue]{__app_name__}[/] version [bold green]{__version__}[/]")
        console.print("Built with ❤️ by the EnkaliPrime Team")
        raise typer.Exit()


@app.command()
def info():
    """Show information about the CLI and SDK."""
    console.print("\n[bold blue]🤖 EnkaliPrime CLI[/]")
    console.print(f"Version: [green]{__version__}[/]")
    console.print("\n[bold]Features:[/]")
    console.print("• 💬 Interactive AI chat")
    console.print("• 🧠 Beautiful loading animations")
    console.print("• ⚙️  Secure API key management")
    console.print("• 📝 Session management")
    console.print("• 🌈 Rich terminal output")
    console.print("\n[bold]Get started:[/]")
    console.print("1. Configure your API key: [cyan]enkaliprime config set-api-key[/]")
    console.print("2. Start chatting: [cyan]enkaliprime chat[/]")
    console.print("\n[dim]For more help, use: enkaliprime --help[/]")


if __name__ == "__main__":
    app()
