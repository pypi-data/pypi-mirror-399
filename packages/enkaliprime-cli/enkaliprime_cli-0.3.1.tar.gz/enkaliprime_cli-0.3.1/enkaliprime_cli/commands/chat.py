"""
Interactive chat commands.

Provides real-time chat interface with AI using the EnkaliPrime SDK.
"""

import typer
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.spinner import Spinner
from rich.text import Text
from rich.table import Table
from rich import box
import keyring
from typing import Optional

from ..ui import console, Header, cyber_panel, print_success, print_error, COLOR_PRIMARY, COLOR_SECONDARY, COLOR_ACCENT

SERVICE_NAME = "enkaliprime-cli"

app = typer.Typer(
    help="💬 Interactive chat with AI",
    rich_markup_mode="rich",
)


def get_api_key():
    """Get API key from keyring."""
    return keyring.get_password(SERVICE_NAME, "api_key")


def create_client():
    """Create EnkaliPrime client with stored API key."""
    api_key = get_api_key()
    if not api_key:
        print_error("No API key configured.")
        console.print("Run: [cyan]enkaliprime config set-api-key[/]")
        raise typer.Exit(1)

    from enkaliprime import EnkaliPrimeClient
    return EnkaliPrimeClient({
        "unified_api_key": api_key,
        "base_url": "https://sdk.enkaliprime.com"
    })


@app.command()
def interactive(
    agent_name: str = typer.Option(
        "CLI Assistant",
        "--agent",
        "-a",
        help="Name of the AI agent",
    ),
    loading: bool = typer.Option(
        False,
        "--loading/--no-loading",
        help="Show loading animations (disabled by default for PowerShell compatibility)",
    ),
    stream: bool = typer.Option(
        False,
        "--stream",
        "-s",
        help="Enable streaming responses",
    ),
):
    """Start interactive chat session with AI."""
    try:
        console.clear()
        Header.draw(agent_name=agent_name)
        
        console.print(f"\n[dim]Type 'exit', 'quit', or 'q' to end the conversation.[/]")
        console.print()

        # Create client and session with status indicator
        with console.status("[dim]Connecting...[/]", spinner="dots"):
            client = create_client()
            session = client.create_session(agent_name=agent_name)

        print_success(f"Session started: {session.id}")
        console.print()

        while True:
            # Get user input
            try:
                user_input = Prompt.ask(f"[bold {COLOR_ACCENT}]You[/]").strip()
            except KeyboardInterrupt:
                console.print("\n[yellow]👋 Goodbye![/]")
                break

            # Check for exit commands
            if user_input.lower() in ['exit', 'quit', 'q']:
                console.print("[yellow]👋 Goodbye![/]")
                break

            if not user_input:
                continue

            try:
                # Show connection indicator
                with console.status("[dim]Thinking...[/]", spinner="dots"):
                    # The SDK will still show its brain animation internally
                    response = client.send_message(
                        message=user_input,
                        session_id=session.id,
                        loading=False,  # Disable CLI loading to avoid PowerShell conflicts
                    )

            except Exception as e:
                print_error(f"Error: {str(e)}")
                continue

            # Display AI response
            console.print(cyber_panel(
                Markdown(response),
                title=agent_name,
                style=COLOR_SECONDARY
            ))
            console.print()

    except Exception as e:
        print_error(f"Chat session failed: {str(e)}")
        raise typer.Exit(1)


@app.command()
def ask(
    message: str = typer.Argument(..., help="Message to send to AI"),
    agent_name: str = typer.Option(
        "CLI Assistant",
        "--agent",
        "-a",
        help="Name of the AI agent",
    ),
    loading: bool = typer.Option(
        False,
        "--loading/--no-loading",
        help="Show loading animations (disabled by default for PowerShell compatibility)",
    ),
):
    """Send a single message to AI and get response."""
    try:
        with console.status("[dim]Connecting...[/]", spinner="dots"):
            client = create_client()
            session = client.create_session(agent_name=agent_name)

        try:
            # Show connection indicator
            with console.status("[dim]Thinking...[/]", spinner="dots"):
                response = client.send_message(
                    message=message,
                    session_id=session.id,
                    loading=False,  # Disable CLI loading to avoid PowerShell conflicts
                )

        except Exception as e:
            print_error("Request failed")
            raise

        # Display response
        console.print(cyber_panel(
            Markdown(response),
            title=agent_name,
            style=COLOR_SECONDARY
        ))

    except Exception as e:
        print_error(f"Failed to get response: {str(e)}")
        raise typer.Exit(1)


@app.command()
def history():
    """Show conversation history for current session."""
    try:
        client = create_client()

        if not client.current_session:
            print_error("No active session.")
            console.print("Start a chat with: [cyan]enkaliprime chat interactive[/]")
            return

        history = client.get_history()

        if not history:
            console.print("[yellow]📝 No conversation history yet.[/]")
            return
        
        Header.draw("History Viewer")
        console.print(f"\n[bold {COLOR_PRIMARY}]Conversation History ({len(history)//2} exchanges)[/]")
        console.print()

        table = Table(box=box.ROUNDED, border_style=COLOR_DIM)
        table.add_column("Role", style=f"bold {COLOR_PRIMARY}", width=10)
        table.add_column("Message", style="white")

        for message in history:
            role = message["role"]
            content = message["content"]
            
            # Truncate content for table view if too long, or keep it basic
            display_role = "You" if role == "user" else "AI"
            role_style = COLOR_ACCENT if role == "user" else COLOR_SECONDARY
            
            table.add_row(
                f"[{role_style}]{display_role}[/]",
                content
            )

        console.print(table)
        console.print()

    except Exception as e:
        print_error(f"Failed to get history: {str(e)}")
        raise typer.Exit(1)

