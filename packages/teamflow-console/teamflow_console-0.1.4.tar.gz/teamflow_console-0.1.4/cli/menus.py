"""Menu definitions and rendering for TeamFlow Console App."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from lib.formatting import (
    BoxChars,
    Style,
    create_console,
    render_border,
    render_bottom_border,
)
from lib.validation import validate_numbered_input


class MainMenu:
    """Main menu display and interaction."""

    WIDTH = 51

    @staticmethod
    def display(console: Console, use_unicode: bool = True) -> None:
        """Display the main menu.

        Args:
            console: The Rich console instance
            use_unicode: Whether to use Unicode box-drawing characters (unused with Panel)
        """
        console.clear()

        menu_text = Text()
        menu_text.append("1. Task Management\n", style="white")
        menu_text.append("2. User & Team Management\n", style="white")
        menu_text.append("3. View Tasks\n", style="white")
        menu_text.append("4. View Resources\n", style="white")
        menu_text.append("5. Exit", style="white")

        panel = Panel(
            menu_text,
            title="[bold blue]TEAMFLOW - Task Manager[/bold blue]",
            subtitle="[dim]c=Create, l=List, q=Quit[/dim]",
            border_style="blue",
            width=51,
        )
        console.print(panel)

    @staticmethod
    def get_selection(prompt: str = "Select option [1-5]: ") -> str:
        """Get and validate menu selection.

        Args:
            prompt: Optional prompt override

        Returns:
            The validated selection string
        """
        return input(prompt).strip()


class TaskManagementMenu:
    """Task management submenu display and interaction."""

    WIDTH = 51

    @staticmethod
    def display(console: Console, use_unicode: bool = True) -> None:
        """Display the task management submenu.

        Args:
            console: The Rich console instance
            use_unicode: Whether to use Unicode box-drawing characters (unused with Panel)
        """
        console.clear()

        menu_text = Text()
        menu_text.append("1. Create Task\n", style="white")
        menu_text.append("2. List Tasks\n", style="white")
        menu_text.append("3. Update Task\n", style="white")
        menu_text.append("4. Complete Task\n", style="white")
        menu_text.append("5. Delete Task\n", style="white")
        menu_text.append("0. Back to Main Menu", style="white")

        panel = Panel(
            menu_text,
            title="[bold cyan]TASK MANAGEMENT[/bold cyan]",
            border_style="cyan",
            width=51,
        )
        console.print(panel)


class UserManagementMenu:
    """User management submenu display and interaction."""

    WIDTH = 51

    @staticmethod
    def display(console: Console, use_unicode: bool = True) -> None:
        """Display the user management submenu.

        Args:
            console: The Rich console instance
            use_unicode: Whether to use Unicode box-drawing characters (unused with Panel)
        """
        console.clear()

        menu_text = Text()
        menu_text.append("1. Create User\n", style="white")
        menu_text.append("2. Create Team\n", style="white")
        menu_text.append("3. List All Users\n", style="white")
        menu_text.append("4. List All Teams\n", style="white")
        menu_text.append("0. Back to Main Menu", style="white")

        panel = Panel(
            menu_text,
            title="[bold green]USER & TEAM MANAGEMENT[/bold green]",
            border_style="green",
            width=51,
        )
        console.print(panel)


def display_exit_confirmation(console: Console) -> bool:
    """Display exit confirmation and get user response.

    Args:
        console: The Rich console instance

    Returns:
        True if user confirms exit, False otherwise
    """
    console.clear()
    console.print()
    console.print("[yellow bold]Are you sure you want to exit? [Y/n]:[/yellow bold] ", end="")
    response = input().strip().lower()

    return response in ("", "y", "yes")
