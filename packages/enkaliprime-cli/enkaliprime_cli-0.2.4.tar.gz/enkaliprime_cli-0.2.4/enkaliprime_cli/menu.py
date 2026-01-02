"""
Interactive menu system for EnkaliPrime CLI.

Provides a sleek GUI menu for command selection.
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, IntPrompt
from rich import box
from rich.columns import Columns
from rich.align import Align
from typing import List, Tuple, Optional

console = Console()


class MenuOption:
    """Represents a menu option."""

    def __init__(self, key: str, name: str, description: str, icon: str = "", color: str = "cyan"):
        self.key = key
        self.name = name
        self.description = description
        self.icon = icon
        self.color = color


class InteractiveMenu:
    """Interactive menu system for command selection."""

    def __init__(self):
        self.options = [
            MenuOption("1", "Chat", "Interactive AI chat session", ">", "green"),
            MenuOption("2", "Ask", "Quick AI question & answer", "?", "blue"),
            MenuOption("3", "Config", "Manage API keys & settings", "*", "yellow"),
            MenuOption("4", "Session", "Manage chat sessions", "#", "magenta"),
            MenuOption("5", "Info", "Show CLI information", "i", "cyan"),
            MenuOption("6", "Help", "Show help & commands", "!", "red"),
            MenuOption("0", "Exit", "Exit the CLI", "x", "white"),
        ]

    def display_menu(self) -> Panel:
        """Create and display the interactive menu."""
        table = Table(box=box.MINIMAL, show_header=False, show_edge=False, pad_edge=False)
        table.add_column("Key", style="bold cyan", width=3, justify="center")
        table.add_column("Icon", width=3, justify="center")
        table.add_column("Command", style="bold white", width=15)
        table.add_column("Description", style="dim white")

        for option in self.options:
            table.add_row(
                f"[{option.color}]{option.key}[/{option.color}]",
                option.icon,
                f"[{option.color}]{option.name}[/{option.color}]",
                f"[dim]{option.description}[/dim]"
            )

        # Create a sleek panel
        menu_panel = Panel(
            Align.center(table),
            title="[bold cyan]EnkaliPrime CLI Menu[/bold cyan]",
            title_align="center",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2)
        )

        return menu_panel

    def get_user_choice(self) -> Optional[str]:
        """Get user input for menu selection."""
        try:
            choice = IntPrompt.ask(
                "\n[bold cyan]Enter your choice[/bold cyan]",
                choices=[str(i) for i in range(len(self.options))],
                show_choices=False
            )
            return str(choice)
        except (KeyboardInterrupt, EOFError):
            return "0"  # Exit on Ctrl+C
        except ValueError:
            return None

    def execute_choice(self, choice: str) -> bool:
        """Execute the selected menu option."""
        commands = {
            "1": ["enkaliprime", "chat", "interactive"],
            "2": ["enkaliprime", "chat", "ask"],
            "3": ["enkaliprime", "config", "show"],
            "4": ["enkaliprime", "session", "current"],
            "5": ["enkaliprime", "info"],
            "6": ["enkaliprime", "--help"],
            "0": None  # Exit
        }

        if choice == "0":
            console.print("\n[green]👋 Goodbye![/green]")
            return False

        if choice in commands and commands[choice]:
            console.print(f"\n[bold cyan]Executing:[/bold cyan] {' '.join(commands[choice])}")
            console.print("[dim]─" * 50 + "[/dim]")

            # Here we would normally execute the command, but since we're in the same process,
            # we'll just show what would be executed and return to menu
            console.print(f"[yellow]💡 Tip: Run this command directly: [cyan]{' '.join(commands[choice])}[/cyan][/yellow]")
            console.print()

        return True

    def run(self):
        """Run the interactive menu loop."""
        while True:
            console.print(self.display_menu())
            choice = self.get_user_choice()

            if choice is None:
                console.print("[red]❌ Invalid choice. Please try again.[/red]")
                continue

            if not self.execute_choice(choice):
                break

            # Wait for user to see result and press enter to continue
            try:
                input("\n[dim]Press Enter to return to menu...[/dim]")
            except (KeyboardInterrupt, EOFError):
                break

            console.clear()


def show_interactive_menu():
    """Show the interactive menu system."""
    menu = InteractiveMenu()
    menu.run()
