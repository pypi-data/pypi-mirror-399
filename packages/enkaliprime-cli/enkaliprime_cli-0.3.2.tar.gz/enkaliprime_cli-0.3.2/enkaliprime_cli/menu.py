"""
Modern chat interface for EnkaliPrime CLI.

Provides a conversational interface similar to Gemini CLI.
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich import box
from rich.align import Align
from typing import Optional
import re

console = Console()


class ModernChatInterface:
    """Modern conversational interface for command selection."""

    def __init__(self):
        self.command_patterns = {
            # Chat commands
            r'\b(chat|talk|converse|interactive)\b': ["enkaliprime", "chat", "interactive"],
            r'\b(ask|question|query)\b': ["enkaliprime", "chat", "ask"],

            # Configuration commands
            r'\b(config|configure|settings|setup|api)\b': ["enkaliprime", "config", "show"],

            # Session commands
            r'\b(session|sessions|history)\b': ["enkaliprime", "session", "current"],

            # Info commands
            r'\b(info|information|about|help)\b': ["enkaliprime", "info"],

            # Help commands
            r'\b(help|commands|usage)\b': ["enkaliprime", "--help"],

            # Exit commands
            r'\b(exit|quit|bye|goodbye|leave)\b': None,
        }

    def display_welcome(self) -> Panel:
        """Create and display the modern welcome interface."""
        welcome_text = Text()
        welcome_text.append("Welcome to ", style="bold cyan")
        welcome_text.append("EnkaliPrime CLI", style="bold white")
        welcome_text.append("\n\nA modern AI chat interface for your terminal\n\n", style="dim")

        # Quick commands hint
        welcome_text.append("* Quick commands:\n", style="yellow")
        welcome_text.append("• 'chat' or 'talk' - Start interactive chat\n", style="dim white")
        welcome_text.append("• 'ask' or 'question' - Quick question & answer\n", style="dim white")
        welcome_text.append("• 'config' or 'settings' - Manage configuration\n", style="dim white")
        welcome_text.append("• 'session' or 'history' - View chat sessions\n", style="dim white")
        welcome_text.append("• 'info' or 'about' - Show CLI information\n", style="dim white")
        welcome_text.append("• 'help' - Show help & commands\n", style="dim white")
        welcome_text.append("• 'exit' or 'quit' - Exit the CLI\n\n", style="dim white")

        # Create a sleek panel
        welcome_panel = Panel(
            Align.left(welcome_text),
            title="[bold cyan]EnkaliPrime CLI[/bold cyan]",
            title_align="left",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 3)
        )

        return welcome_panel

    def parse_command(self, user_input: str) -> Optional[list]:
        """Parse natural language input to determine the intended command."""
        user_input = user_input.lower().strip()

        # Direct command mapping for common phrases
        for pattern, command in self.command_patterns.items():
            if re.search(pattern, user_input):
                return command

        # If no pattern matches, try to interpret as a chat request
        if user_input and len(user_input) > 0:
            # If it looks like a question or statement, default to chat
            if user_input.endswith('?') or len(user_input.split()) > 2:
                return ["enkaliprime", "chat", "ask"]
            else:
                return ["enkaliprime", "chat", "interactive"]

        return None

    def get_user_input(self) -> Optional[str]:
        """Get user input with modern chat prompt."""
        try:
            # Create a modern chat prompt
            prompt_text = Text(">", style="bold blue")
            prompt_text.append(" Ask me anything", style="bold cyan")
            prompt_text.append(" (or type 'help' for commands)", style="dim white")

            user_input = Prompt.ask(prompt_text, default="")
            return user_input.strip()
        except (KeyboardInterrupt, EOFError):
            return "exit"  # Exit on Ctrl+C
        except Exception:
            return None

    def execute_command(self, command: list) -> bool:
        """Execute the parsed command."""
        if command is None:
            console.print("\n[green]Goodbye! Thanks for using EnkaliPrime CLI![/green]")
            return False

        console.print(f"\n[bold blue]Executing:[/bold blue] {' '.join(command)}")
        console.print("[dim]" + "─" * 60 + "[/dim]")

        # Here we would normally execute the command, but since we're in the same process,
        # we'll just show what would be executed and return to chat
        console.print(f"[yellow]Tip: Run this command directly: [cyan]{' '.join(command)}[/cyan][/yellow]")
        console.print()

        return True

    def run(self):
        """Run the modern chat interface loop."""
        console.print(self.display_welcome())

        while True:
            user_input = self.get_user_input()

            if user_input is None:
                console.print("[red]❌ Error reading input. Please try again.[/red]")
                continue

            if not user_input:  # Empty input
                console.print("[dim]Please enter a command or question...[/dim]")
                continue

            command = self.parse_command(user_input)

            if command is None:
                console.print("[yellow]I didn't understand that command. Try 'help' for available options.[/yellow]")
                continue

            if not self.execute_command(command):
                break

            # Wait for user to see result and press enter to continue
            try:
                input("\n[dim]Press Enter to continue...[/dim]")
            except (KeyboardInterrupt, EOFError):
                console.print("\n[green]Goodbye![/green]")
                break

            console.clear()
            # Show welcome again for next interaction
            console.print(self.display_welcome())


def show_interactive_menu():
    """Show the modern chat interface."""
    chat_interface = ModernChatInterface()
    chat_interface.run()
