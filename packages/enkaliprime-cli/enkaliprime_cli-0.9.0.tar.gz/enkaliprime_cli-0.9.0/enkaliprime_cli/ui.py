"""
UI components for the EnkaliPrime CLI.
Provides consistent styling matching the Fastfetch cyberpunk aesthetic.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.style import Style
from rich.layout import Layout
from rich import box
import platform
import psutil
import os
import time
import sys
import re
from typing import Optional, List, Tuple
from . import __version__

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

console = Console()

# Theme Colors
COLOR_PRIMARY = "cyan"
COLOR_SECONDARY = "magenta"
COLOR_ACCENT = "green"
COLOR_DIM = "dim white"


def typewriter_animation(text: str, delay: float = 0.02, end: str = "\n") -> None:
    """
    Display text with a typewriter animation effect.

    Args:
        text: The text to animate
        delay: Delay between each character (seconds)
        end: What to print at the end (default: newline)
    """
    try:
        for char in text:
            console.print(char, end="", style="white")
            console.file.flush()  # Force immediate output
            time.sleep(delay)

        if end:
            console.print(end, end="")
            console.file.flush()

    except KeyboardInterrupt:
        # If user interrupts, print the rest instantly
        console.print(text[len(text) - text.rfind(char) - 1:], end=end)
        console.file.flush()
        raise


def animate_ai_response(response: str, typewriter: bool = True, typewriter_speed: float = 0.02) -> None:
    """
    Display AI response with optional typewriter animation.

    Args:
        response: The AI response text
        typewriter: Whether to use typewriter animation
        typewriter_speed: Speed of typewriter animation
    """
    if typewriter:
        typewriter_animation(response, delay=typewriter_speed)
    else:
        console.print(response)


def extract_code_blocks(text: str) -> List[Tuple[str, str]]:
    """
    Extract code blocks from markdown text.

    Returns:
        List of tuples (code, language) where language might be empty string
    """
    # Pattern to match markdown code blocks: ```language\ncode\n```
    code_block_pattern = r'```(\w+)?\n(.*?)\n```'
    code_blocks = re.findall(code_block_pattern, text, re.DOTALL)

    # Also look for inline code: `code`
    inline_code_pattern = r'`([^`\n]+)`'
    inline_codes = re.findall(inline_code_pattern, text)

    results = []

    # Add code blocks
    for lang, code in code_blocks:
        results.append((code.strip(), lang or ""))

    # Add inline codes (only if substantial)
    for code in inline_codes:
        if len(code.strip()) > 10:  # Only substantial inline code
            results.append((code.strip(), "inline"))

    return results


def copy_to_clipboard(text: str) -> bool:
    """
    Copy text to system clipboard.

    Returns:
        True if successful, False otherwise
    """
    if not CLIPBOARD_AVAILABLE:
        return False

    try:
        pyperclip.copy(text)
        return True
    except Exception:
        return False


def display_code_copy_options(code_blocks: List[Tuple[str, str]]) -> None:
    """
    Display interactive options to copy code blocks.

    Args:
        code_blocks: List of (code, language) tuples
    """
    if not code_blocks or not CLIPBOARD_AVAILABLE:
        return

    console.print()
    console.print("[bold cyan]📋 Code Copy Options:[/]")
    console.print("[dim]Press the number to copy code to clipboard[/]")

    for i, (code, lang) in enumerate(code_blocks, 1):
        lang_display = f" ({lang})" if lang else ""
        # Show first line or truncated preview
        preview = code.split('\n')[0][:50]
        if len(code.split('\n')) > 1 or len(code) > 50:
            preview += "..."

        console.print(f"[cyan]{i}.[/] [green]{lang_display}[/] [dim]{preview}[/]")

    console.print("[dim]Or press Enter to continue...[/]")


def interactive_code_copy(code_blocks: List[Tuple[str, str]]) -> None:
    """
    Handle interactive code copying.

    Args:
        code_blocks: List of (code, language) tuples
    """
    if not code_blocks or not CLIPBOARD_AVAILABLE:
        return

    display_code_copy_options(code_blocks)

    try:
        choice = input().strip()
        if choice and choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(code_blocks):
                code, lang = code_blocks[idx]
                if copy_to_clipboard(code):
                    lang_display = f" ({lang})" if lang else ""
                    console.print(f"[green]✅ Copied{lang_display} code to clipboard![/]")
                else:
                    console.print("[red]❌ Failed to copy to clipboard[/]")
                return
    except (KeyboardInterrupt, EOFError):
        pass

    # Clear the options display
    # Move cursor up and clear lines
    num_lines = len(code_blocks) + 4  # options + header + instructions
    for _ in range(num_lines):
        console.print("\033[1A\033[K", end="")  # Move up and clear line


def display_ai_response(
    response: str,
    agent_name: str = "AI Assistant",
    typewriter: bool = True,
    typewriter_speed: float = 0.02,
    copy_code: bool = False,
    interactive_copy: bool = False
) -> None:
    """
    Display AI response with optional typewriter animation and code copying.

    Args:
        response: The AI response text
        agent_name: Name of the AI agent
        typewriter: Whether to use typewriter animation
        typewriter_speed: Speed of animation
        copy_code: Whether to auto-copy code blocks
        interactive_copy: Whether to show interactive copy options
    """
    from rich.markdown import Markdown

    if typewriter:
        # Animate the text first
        typewriter_animation(response, delay=typewriter_speed, end="")

        # Then display in panel (this will overwrite the animated text)
        # We need to clear the line and move cursor appropriately
        # For simplicity, let's just display the panel after animation
        console.print()  # New line after animation

    # Display the response in cyber panel
    console.print(cyber_panel(
        Markdown(response),
        title=agent_name,
        style=COLOR_SECONDARY
    ))
    console.print()

    # Handle code copying
    if CLIPBOARD_AVAILABLE:
        code_blocks = extract_code_blocks(response)

        if code_blocks:
            if copy_code and len(code_blocks) == 1:
                # Auto-copy if only one code block
                code, lang = code_blocks[0]
                if copy_to_clipboard(code):
                    lang_display = f" ({lang})" if lang else ""
                    console.print(f"[green]📋 Auto-copied{lang_display} code to clipboard[/]")
                    console.print()
            elif interactive_copy:
                # Show interactive copy options
                interactive_code_copy(code_blocks)
    elif (copy_code or interactive_copy) and code_blocks:
        console.print("[yellow]⚠️  Code copying requires 'pyperclip' but it's not available[/]")
        console.print("[dim]Install with: pip install pyperclip[/]")
        console.print()


FOX_ART = """
[magenta]    .::::::.[/]       [cyan].::::::.[/]
[magenta]  .::::::::::.[/]   [cyan].::::::::::.[/]
[magenta] .::::::::::::::.[/] [cyan].::::::::::::::.[/]
[magenta] .::::::::::::::.[/] [cyan].::::::::::::::.[/]
[magenta]  .::::::::::::.[/]   [cyan].::::::::::::.[/]
[magenta]    '::::::::'[/]       [cyan]'::::::::'[/]

[magenta]   .::[/][cyan]::.[/]   [magenta].::[/][cyan]::.[/]
[magenta] .::::[/][cyan]::::.[/] [magenta].::::[/][cyan]::::.[/]
"""

class Header:
    """Displays the CLI header with ASCII art and system info."""
    
    @staticmethod
    def draw(agent_name: str = "EnkaliPrime CLI"):
        grid = Table.grid(expand=True, padding=(0, 2))
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="left", ratio=2)
        
        # System Info Assembly
        sys_info = Table.grid(padding=(0, 1))
        sys_info.add_column(style=COLOR_PRIMARY, justify="right")
        sys_info.add_column(style="white")
        
        # Gather real info
        uname = platform.uname()
        mem = psutil.virtual_memory()
        
        rows = [
            ("User", f"[bold {COLOR_SECONDARY}]{os.getlogin()}[/]@[bold {COLOR_PRIMARY}]{uname.node}[/]"),
            ("OS", f"{uname.system} {uname.release} ({uname.machine})"),
            ("Host", uname.node),
            ("Kernel", uname.release),
            ("Uptime", "Just started"), # Placeholder or calc if needed
            ("Memory", f"{mem.used // (1024**2)} MiB / {mem.total // (1024**2)} MiB"),
            ("SDK", f"v{__version__}"),
        ]
        
        for label, value in rows:
            sys_info.add_row(f"{label}", value)
            
        color_dots = Text("● ● ● ● ● ● ● ●", style=f"bold {COLOR_SECONDARY}")

        # Combine Art and Info
        grid.add_row(
            Panel(FOX_ART, box=box.MINIMAL, border_style=COLOR_DIM),
            Panel(
                sys_info, 
                title=f"[bold {COLOR_PRIMARY}]{agent_name}[/]",
                subtitle=color_dots,
                border_style=COLOR_SECONDARY,
                box=box.ROUNDED
            )
        )
        
        console.print(grid)

def cyber_panel(content, title=None, style=COLOR_PRIMARY):
    """Creates a styled panel with the cyberpunk aesthetic."""
    return Panel(
        content,
        title=f"[bold {style}]{title}[/]" if title else None,
        border_style=style,
        box=box.ROUNDED,
        padding=(1, 2)
    )

def print_success(message: str):
    console.print(f"[bold {COLOR_ACCENT}]✓[/] {message}")

def print_error(message: str):
    console.print(f"[bold red]✗[/] {message}")

def print_warning(message: str):
    console.print(f"[bold yellow]![/] {message}")
