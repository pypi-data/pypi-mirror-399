"""Shared CLI utilities."""
import os
from rich.console import Console

console = Console()


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def display_banner() -> None:
    """Display ASCII banner 'TODO EVOLUTION'.

    Uses pyfiglet for dramatic ASCII art, with fallback to rich.Text
    if pyfiglet is not available.
    """
    try:
        import pyfiglet
        ascii_art = pyfiglet.figlet_format("TODO EVOLUTION", font="slant")
        console.print(ascii_art, style="bold cyan")
    except ImportError:
        # Fallback to rich Text if pyfiglet not installed
        from rich.text import Text
        banner = Text("TODO EVOLUTION", style="bold cyan")
        console.print(banner, justify="center")
        console.print()


def format_status(status: bool) -> str:
    """Convert boolean status to ✓/✗ symbol with color.

    Args:
        status: Task completion state (True=complete, False=incomplete)

    Returns:
        str: Rich-formatted status symbol
    """
    return "[green]✓[/green]" if status else "[red]✗[/red]"
