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
from typing import Optional, Dict, Any
import requests
import json

from ..ui import console, Header, cyber_panel, print_success, print_error, COLOR_PRIMARY, COLOR_SECONDARY, COLOR_ACCENT

SERVICE_NAME = "enkaliprime-cli"


class LocalLLMProvider:
    """Base class for local LLM providers."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.available_models = []

    def is_available(self) -> bool:
        """Check if the local provider is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def list_models(self) -> list:
        """List available models."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
        except:
            pass
        return []

    def generate(self, prompt: str, model: str = "llama2", **kwargs) -> str:
        """Generate text using the local LLM."""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                **kwargs
            }
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60
            )
            if response.status_code == 200:
                return response.json().get('response', '')
        except Exception as e:
            raise Exception(f"Local LLM generation failed: {str(e)}")
        return ""


class OllamaProvider(LocalLLMProvider):
    """Ollama-specific implementation."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        super().__init__(base_url)

    def is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = requests.get(f"{self.base_url}/api/version", timeout=5)
            return response.status_code == 200
        except:
            return False


class LLMProviderManager:
    """Manages different LLM providers."""

    def __init__(self):
        self.providers = {
            'ollama': OllamaProvider(),
            'remote': None  # Will be set when EnkaliPrime client is created
        }
        self.preferred_provider = 'remote'  # Default to remote

    def set_preferred_provider(self, provider: str):
        """Set the preferred LLM provider."""
        if provider in self.providers:
            self.preferred_provider = provider

    def get_available_providers(self) -> list:
        """Get list of available providers."""
        available = []
        for name, provider in self.providers.items():
            if provider and (name == 'remote' or provider.is_available()):
                available.append(name)
        return available

    def get_client(self):
        """Get the appropriate client based on preferences and availability."""
        if self.preferred_provider == 'remote':
            return create_remote_client()
        elif self.preferred_provider in self.providers:
            provider = self.providers[self.preferred_provider]
            if provider and provider.is_available():
                return provider
            else:
                # Fallback to remote if local is not available
                console.print(f"[yellow]⚠️  {self.preferred_provider.title()} not available, falling back to remote[/yellow]")
                return create_remote_client()
        else:
            return create_remote_client()


# Global provider manager
provider_manager = LLMProviderManager()

app = typer.Typer(
    help="💬 Interactive chat with AI",
    rich_markup_mode="rich",
)


def get_api_key():
    """Get API key from keyring."""
    return keyring.get_password(SERVICE_NAME, "api_key")


def create_remote_client():
    """Create EnkaliPrime client with stored API key."""
    api_key = get_api_key()
    if not api_key:
        print_error("No API key configured.")
        console.print("Run: [cyan]enkaliprime config set-api-key[/]")
        raise typer.Exit(1)

    from enkaliprime import EnkaliPrimeClient
    client = EnkaliPrimeClient({
        "unified_api_key": api_key,
        "base_url": "https://sdk.enkaliprime.com"
    })
    provider_manager.providers['remote'] = client
    return client


def create_client():
    """Create LLM client using provider manager."""
    return provider_manager.get_client()


@app.command()
def interactive(
    agent_name: str = typer.Option(
        "CLI Assistant",
        "--agent",
        "-a",
        help="Name of the AI agent",
    ),
    provider: str = typer.Option(
        "auto",
        "--provider",
        "-p",
        help="LLM provider: auto, remote, ollama (auto detects available providers)",
    ),
    model: str = typer.Option(
        None,
        "--model",
        "-m",
        help="Model name for local providers (e.g., llama2, codellama)",
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

        # Set provider preference
        if provider != "auto":
            provider_manager.set_preferred_provider(provider)

        available_providers = provider_manager.get_available_providers()
        current_provider = provider_manager.preferred_provider

        # Show provider information
        if current_provider == "remote":
            console.print(f"\n[dim]🤖 Using remote AI provider (EnkaliPrime)[/]")
        else:
            console.print(f"\n[dim]🏠 Using local AI provider ({current_provider})[/]")
            if model:
                console.print(f"[dim]📋 Model: {model}[/]")

        console.print(f"\n[dim]Type 'exit', 'quit', or 'q' to end the conversation.[/]")
        console.print()

        # Create client and session
        client = create_client()

        # For remote provider, create session; for local, no session needed
        if hasattr(client, 'create_session'):
            session = client.create_session(agent_name=agent_name)
            session_id = session.id if session else None
            print_success(f"Session started: {session_id}")
        else:
            session_id = None
            if model:
                print_success(f"Connected to local LLM: {model}")
            else:
                print_success("Connected to local LLM")

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
                # Send message based on provider type
                if hasattr(client, 'send_message'):
                    # Remote provider (EnkaliPrime)
                    response = client.send_message(
                        message=user_input,
                        session_id=session_id,
                        loading=False,  # Disable CLI loading to avoid PowerShell conflicts
                    )
                else:
                    # Local provider
                    with console.status("[dim]Thinking...[/]", spinner="dots"):
                        model_name = model or "llama2"  # Default model
                        response = client.generate(user_input, model=model_name)

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
    provider: str = typer.Option(
        "auto",
        "--provider",
        "-p",
        help="LLM provider: auto, remote, ollama (auto detects available providers)",
    ),
    model: str = typer.Option(
        None,
        "--model",
        "-m",
        help="Model name for local providers (e.g., llama2, codellama)",
    ),
    loading: bool = typer.Option(
        False,
        "--loading/--no-loading",
        help="Show loading animations (disabled by default for PowerShell compatibility)",
    ),
):
    """Send a single message to AI and get response."""
    try:
        # Set provider preference
        if provider != "auto":
            provider_manager.set_preferred_provider(provider)

        client = create_client()

        try:
            # Send message based on provider type
            if hasattr(client, 'send_message'):
                # Remote provider (EnkaliPrime)
                session = client.create_session(agent_name=agent_name)
                response = client.send_message(
                    message=message,
                    session_id=session.id,
                    loading=False,  # Disable CLI loading to avoid PowerShell conflicts
                )
            else:
                # Local provider
                with console.status("[dim]Thinking...[/]", spinner="dots"):
                    model_name = model or "llama2"  # Default model
                    response = client.generate(message, model=model_name)

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
def providers():
    """List available LLM providers and models."""
    try:
        available_providers = provider_manager.get_available_providers()

        table = Table(title="🤖 Available LLM Providers", box=box.ROUNDED)
        table.add_column("Provider", style=f"bold {COLOR_PRIMARY}")
        table.add_column("Status", style="bold")
        table.add_column("Models", style="dim")

        # Check remote provider
        remote_available = "remote" in available_providers
        table.add_row(
            "EnkaliPrime (Remote)",
            f"[{'green' if remote_available else 'red'}]{'✓ Available' if remote_available else '✗ Needs API Key'}[/]",
            "Various models via API"
        )

        # Check local providers
        for provider_name in ['ollama']:
            if provider_name in provider_manager.providers:
                provider = provider_manager.providers[provider_name]
                is_available = provider.is_available()
                models = provider.list_models() if is_available else []
                model_list = ", ".join(models[:5]) + ("..." if len(models) > 5 else "") if models else "None"

                table.add_row(
                    f"{provider_name.title()} (Local)",
                    f"[{'green' if is_available else 'red'}]{'✓ Running' if is_available else '✗ Not running'}[/]",
                    model_list or "Not available"
                )

        console.print(table)

        # Show instructions
        console.print(f"\n[bold {COLOR_ACCENT}]💡 Usage:[/]")
        console.print(f"• [cyan]enkaliprime chat interactive --provider ollama --model llama2[/]")
        console.print(f"• [cyan]enkaliprime chat ask \"Hello\" --provider remote[/]")
        console.print(f"• [cyan]enkaliprime chat providers[/] (this command)")

        if not any(p in available_providers for p in ['ollama']):
            console.print(f"\n[yellow]💡 To use local LLMs:[/]")
            console.print(f"• Install Ollama: [cyan]https://ollama.ai/[/]")
            console.print(f"• Pull a model: [cyan]ollama pull llama2[/]")
            console.print(f"• Start Ollama: [cyan]ollama serve[/]")

    except Exception as e:
        print_error(f"Failed to check providers: {str(e)}")
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

