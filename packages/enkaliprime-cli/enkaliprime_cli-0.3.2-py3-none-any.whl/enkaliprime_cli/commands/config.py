"""
Configuration management commands.

Handles API key storage, settings, and configuration validation.
"""

import keyring
import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from typing import Optional

from enkaliprime.type_guards import is_valid_api_key

console = Console()

# Keyring service name
SERVICE_NAME = "enkaliprime-cli"

app = typer.Typer(
    help="⚙️  Manage CLI configuration and API keys",
    rich_markup_mode="rich",
)


@app.command()
def set_api_key(
    api_key: Optional[str] = typer.Option(
        None,
        "--key",
        "-k",
        help="API key (if not provided, will prompt securely)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing API key without confirmation",
    ),
):
    """Set your EnkaliPrime API key securely."""
    try:
        # Check if key already exists
        existing_key = keyring.get_password(SERVICE_NAME, "api_key")
        if existing_key and not force:
            if not Confirm.ask("API key already exists. Overwrite?", default=False):
                console.print("[yellow]Operation cancelled.[/]")
                return

        # Get API key from argument or prompt
        if not api_key:
            api_key = Prompt.ask("Enter your EnkaliPrime API key", password=True)

        # Validate API key format
        if not is_valid_api_key(api_key):
            console.print("[red]❌ Invalid API key format. Should start with 'ek_bridge_'[/]")
            return

        # Store securely
        keyring.set_password(SERVICE_NAME, "api_key", api_key)

        # Mask the key for display
        masked_key = api_key[:15] + "..." + api_key[-4:] if len(api_key) > 20 else api_key

        console.print(f"[green]✅ API key set successfully: {masked_key}[/]")
        console.print("[dim]Your API key is stored securely using your system's keyring.[/]")

    except Exception as e:
        console.print(f"[red]❌ Failed to set API key: {str(e)}[/]")


@app.command()
def get_api_key():
    """Show current API key (masked for security)."""
    try:
        api_key = keyring.get_password(SERVICE_NAME, "api_key")

        if not api_key:
            console.print("[yellow]⚠️  No API key configured.[/]")
            console.print("Set one with: [cyan]enkaliprime config set-api-key[/]")
            return

        # Mask the key for display
        masked_key = api_key[:15] + "..." + api_key[-4:] if len(api_key) > 20 else api_key

        console.print(f"[green]API Key: {masked_key}[/]")

        # Validate the stored key
        if is_valid_api_key(api_key):
            console.print("[green]✅ Key format is valid[/]")
        else:
            console.print("[red]❌ Key format appears invalid[/]")

    except Exception as e:
        console.print(f"[red]❌ Failed to retrieve API key: {str(e)}[/]")


@app.command()
def remove_api_key(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Remove without confirmation",
    ),
):
    """Remove stored API key."""
    try:
        api_key = keyring.get_password(SERVICE_NAME, "api_key")

        if not api_key:
            console.print("[yellow]⚠️  No API key to remove.[/]")
            return

        if not force:
            masked_key = api_key[:15] + "..." + api_key[-4:] if len(api_key) > 20 else api_key
            if not Confirm.ask(f"Remove API key '{masked_key}'?", default=False):
                console.print("[yellow]Operation cancelled.[/]")
                return

        keyring.delete_password(SERVICE_NAME, "api_key")
        console.print("[green]✅ API key removed successfully.[/]")

    except Exception as e:
        console.print(f"[red]❌ Failed to remove API key: {str(e)}[/]")


@app.command()
def test_connection():
    """Test connection to EnkaliPrime API."""
    try:
        from enkaliprime import EnkaliPrimeClient

        api_key = keyring.get_password(SERVICE_NAME, "api_key")

        if not api_key:
            console.print("[red]❌ No API key configured.[/]")
            console.print("Set one with: [cyan]enkaliprime config set-api-key[/]")
            return

        console.print("🔗 Testing connection...")

        # Create client and test connection
        client = EnkaliPrimeClient({
            "unified_api_key": api_key,
            "base_url": "https://sdk.enkaliprime.com"
        })

        connection = client.get_connection()

        console.print("[green]✅ Connection successful![/]")
        console.print(f"Widget: [cyan]{connection.widget_name}[/]")
        console.print(f"Base URL: [cyan]{connection.base_url}[/]")
        console.print(f"Status: [green]{'Active' if connection.is_active else 'Inactive'}[/]")

    except Exception as e:
        console.print(f"[red]❌ Connection test failed: {str(e)}[/]")
        console.print("Check your API key and internet connection.")


@app.command()
def show():
    """Show current configuration."""
    try:
        panel_content = []

        # API Key status
        api_key = keyring.get_password(SERVICE_NAME, "api_key")
        if api_key:
            masked_key = api_key[:15] + "..." + api_key[-4:]
            panel_content.append(f"[green]API Key:[/] {masked_key}")
            panel_content.append(f"[green]Key Valid:[/] {'✅' if is_valid_api_key(api_key) else '❌'}")
        else:
            panel_content.append("[red]API Key: Not configured[/]")

        # Default settings
        panel_content.append("[blue]Base URL:[/] https://sdk.enkaliprime.com")

        panel = Panel(
            "\n".join(panel_content),
            title="[bold blue]EnkaliPrime CLI Configuration[/]",
            border_style="blue",
        )

        console.print(panel)

    except Exception as e:
        console.print(f"[red]❌ Failed to show configuration: {str(e)}[/]")
