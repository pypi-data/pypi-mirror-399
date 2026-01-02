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
import keyring
from typing import Optional

console = Console()

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
        console.print("[red]❌ No API key configured.[/]")
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
        True,
        "--loading/--no-loading",
        help="Show loading animations",
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
        console.print("[bold blue]🤖 EnkaliPrime Interactive Chat[/]")
        console.print(f"Agent: [cyan]{agent_name}[/]")
        console.print("[dim]Type 'exit', 'quit', or 'q' to end the conversation.[/]")
        console.print()

        # Create client and session
        client = create_client()
        session = client.create_session(agent_name=agent_name)

        console.print(f"[green]✅ Session started: {session.id}[/]")
        console.print()

        while True:
            # Get user input
            try:
                user_input = Prompt.ask("[bold green]You[/]").strip()
            except KeyboardInterrupt:
                console.print("\n[yellow]👋 Goodbye![/]")
                break

            # Check for exit commands
            if user_input.lower() in ['exit', 'quit', 'q']:
                console.print("[yellow]👋 Goodbye![/]")
                break

            if not user_input:
                continue

            # Show loading animation if enabled
            if loading:
                # Custom spinner for PowerShell compatibility
                import time
                import sys
                import threading

                class PowerShellSpinner:
                    def __init__(self, message="Thinking"):
                        self.message = message
                        self.running = False
                        self.thread = None
                        self.chars = ['-', '\\', '|', '/']
                        self.start_time = None

                    def _spin(self):
                        idx = 0
                        while self.running:
                            elapsed = time.time() - self.start_time if self.start_time else 0
                            char = self.chars[idx % len(self.chars)]
                            # Simple print without cursor manipulation for PowerShell compatibility
                            print(f"\r{char} {self.message}... {elapsed:.1f}s", end="", flush=True)
                            idx += 1
                            time.sleep(0.1)

                    def start(self):
                        self.running = True
                        self.start_time = time.time()
                        self.thread = threading.Thread(target=self._spin, daemon=True)
                        self.thread.start()

                    def stop(self, success=True):
                        self.running = False
                        if self.thread:
                            self.thread.join(timeout=0.5)
                        # Clear the line and print completion message
                        print("\r" + " " * 50 + "\r", end="")
                        if success:
                            console.print("[green]✓ Response generated![/]")
                        else:
                            console.print("[red]✗ Request failed[/]")

                spinner = PowerShellSpinner(message="Thinking")
                spinner.start()
                try:
                    response = client.send_message(
                        message=user_input,
                        session_id=session.id,
                        loading=True,  # Use the beautiful brain animation
                    )
                    spinner.stop(success=True)
                except Exception as e:
                    spinner.stop(success=False)
                    console.print(f"[red]❌ Error: {str(e)}[/]")
                    continue
            else:
                try:
                    response = client.send_message(
                        message=user_input,
                        session_id=session.id,
                        loading=False,
                    )
                except Exception as e:
                    console.print(f"[red]❌ Error: {str(e)}[/]")
                    continue

            # Display AI response
            response_panel = Panel(
                Markdown(response),
                title=f"[bold blue]{agent_name}[/]",
                border_style="blue",
            )
            console.print(response_panel)
            console.print()

    except Exception as e:
        console.print(f"[red]❌ Chat session failed: {str(e)}[/]")
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
        True,
        "--loading/--no-loading",
        help="Show loading animations",
    ),
):
    """Send a single message to AI and get response."""
    try:
        client = create_client()
        session = client.create_session(agent_name=agent_name)

        if loading:
            # Custom spinner for PowerShell compatibility
            import time
            import sys
            import threading

            class PowerShellSpinner:
                def __init__(self, message="Thinking"):
                    self.message = message
                    self.running = False
                    self.thread = None
                    self.chars = ['-', '\\', '|', '/']
                    self.start_time = None

                def _spin(self):
                    idx = 0
                    while self.running:
                        elapsed = time.time() - self.start_time if self.start_time else 0
                        char = self.chars[idx % len(self.chars)]
                        # Simple print without cursor manipulation for PowerShell compatibility
                        print(f"\r{char} {self.message}... {elapsed:.1f}s", end="", flush=True)
                        idx += 1
                        time.sleep(0.1)

                def start(self):
                    self.running = True
                    self.start_time = time.time()
                    self.thread = threading.Thread(target=self._spin, daemon=True)
                    self.thread.start()

                def stop(self, success=True):
                    self.running = False
                    if self.thread:
                        self.thread.join(timeout=0.5)
                    # Clear the line and print completion message
                    print("\r" + " " * 50 + "\r", end="")
                    if success:
                        console.print("[green]✓ Response generated![/]")
                    else:
                        console.print("[red]✗ Request failed[/]")

            spinner = PowerShellSpinner(message="Thinking")
            spinner.start()
            try:
                response = client.send_message(
                    message=message,
                    session_id=session.id,
                    loading=True,
                )
                spinner.stop(success=True)
            except Exception as e:
                spinner.stop(success=False)
                raise
        else:
            response = client.send_message(
                message=message,
                session_id=session.id,
                loading=False,
            )

        # Display response
        response_panel = Panel(
            Markdown(response),
            title=f"[bold blue]{agent_name}[/]",
            border_style="blue",
        )
        console.print(response_panel)

    except Exception as e:
        console.print(f"[red]❌ Failed to get response: {str(e)}[/]")
        raise typer.Exit(1)


@app.command()
def history():
    """Show conversation history for current session."""
    try:
        client = create_client()

        if not client.current_session:
            console.print("[yellow]⚠️  No active session.[/]")
            console.print("Start a chat with: [cyan]enkaliprime chat interactive[/]")
            return

        history = client.get_history()

        if not history:
            console.print("[yellow]📝 No conversation history yet.[/]")
            return

        console.print(f"[bold blue]📚 Conversation History ({len(history)//2} exchanges)[/]")
        console.print()

        for i, message in enumerate(history):
            role = message["role"]
            content = message["content"]

            if role == "user":
                console.print(f"[bold green]You:[/] {content}")
            else:
                console.print(f"[bold blue]AI:[/] {content}")
            console.print()

    except Exception as e:
        console.print(f"[red]❌ Failed to get history: {str(e)}[/]")
        raise typer.Exit(1)
