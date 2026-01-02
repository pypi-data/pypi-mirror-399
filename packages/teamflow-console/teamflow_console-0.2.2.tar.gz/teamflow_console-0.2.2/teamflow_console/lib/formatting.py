"""Terminal formatting utilities for TeamFlow Console App.

This module provides Rich-based formatting for tables, panels, and menus.
"""

from typing import Any, Literal

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


# Color styles
class Style:
    """Terminal color styles."""

    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"
    BLUE = "blue"
    BOLD = "bold"
    ERROR = "bold red"
    SUCCESS = "green"


# Box-drawing characters
class BoxChars:
    """Unicode box-drawing characters for menu borders."""

    # Unicode (primary)
    HORZ = "\u2500"  # ─
    VERT = "\u2502"  # │
    TOP_LEFT = "\u250C"  # ┌
    TOP_RIGHT = "\u2510"  # ┐
    BOTTOM_LEFT = "\u2514"  # └
    BOTTOM_RIGHT = "\u2518"  # ┘
    LEFT_T = "\u251C"  # ├
    RIGHT_T = "\u2524"  # ┤

    # ASCII fallback
    HORZ_ASCII = "-"
    VERT_ASCII = "|"
    CORNER_ASCII = "+"


def create_console() -> Console:
    """Create a Rich console instance with color support.

    Returns:
        A configured Rich Console instance
    """
    return Console(force_terminal=True)


def render_border(console: Console, title: str, width: int = 51,
                 use_unicode: bool = True) -> None:
    """Render a bordered menu box.

    Args:
        console: The Rich console instance
        title: The title to display
        width: Total width of the box
        use_unicode: Whether to use Unicode box-drawing characters
    """
    if use_unicode:
        chars = BoxChars
    else:
        chars = BoxChars.HORZ_ASCII, BoxChars.VERT_ASCII, BoxChars.CORNER_ASCII

    # Top border
    console.print(chars.TOP_LEFT + chars.HORZ * (width - 2) + chars.TOP_RIGHT)

    # Title line
    title_padding = (width - 2 - len(title)) // 2
    console.print(chars.VERT + " " * title_padding + title + " " * (width - 2 - title_padding - len(title)) + chars.VERT)

    # Separator
    console.print(chars.LEFT_T + chars.HORZ * (width - 2) + chars.RIGHT_T)


def render_bottom_border(console: Console, width: int = 51,
                        use_unicode: bool = True) -> None:
    """Render a bottom border.

    Args:
        console: The Rich console instance
        width: Total width of the box
        use_unicode: Whether to use Unicode box-drawing characters
    """
    if use_unicode:
        chars = BoxChars
    else:
        chars = BoxChars.HORZ_ASCII, BoxChars.VERT_ASCII, BoxChars.CORNER_ASCII

    console.print(chars.BOTTOM_LEFT + chars.HORZ * (width - 2) + chars.BOTTOM_RIGHT)


def render_success_panel(console: Console, message: str) -> None:
    """Render a success message in a green panel.

    Args:
        console: The Rich console instance
        message: The success message to display
    """
    console.print()
    console.print(Panel(message, title="[SUCCESS]", border_style=Style.SUCCESS))
    console.print()


def render_error_panel(console: Console, message: str) -> None:
    """Render an error message in a red panel.

    Args:
        console: The Rich console instance
        message: The error message to display
    """
    console.print()
    console.print(Panel(message, title="[ERROR]", border_style=Style.ERROR))
    console.print()


def render_task_table(console: Console, tasks: list[Any],
                     show_assignee: bool = True, user_service=None) -> None:
    """Render tasks in a formatted table.

    Args:
        console: The Rich console instance
        tasks: List of tasks to display
        show_assignee: Whether to show the assignee column
        user_service: Optional user service for looking up assignee names
    """
    if not tasks:
        console.print("[yellow]No tasks found.[/yellow]")
        return

    table = Table(title="Tasks")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Title", style="white")
    table.add_column("Priority", style="white")
    table.add_column("Status", style="white")
    if show_assignee:
        table.add_column("Assigned To", style="white")

    for task in tasks:
        # Color code priority
        priority_style = {
            "High": Style.RED,
            "Medium": Style.YELLOW,
            "Low": Style.BLUE,
        }.get(task.priority, "white")

        # Color code status
        status_style = {
            "Done": Style.GREEN,
        }.get(task.status, "white")

        # Get assignee name
        if show_assignee:
            if task.assignee_id and user_service:
                try:
                    user = user_service.get_by_id(task.assignee_id)
                    assignee = user.name
                except Exception:
                    assignee = f"User #{task.assignee_id}"
            elif task.assignee_id:
                assignee = f"User #{task.assignee_id}"
            else:
                assignee = "Unassigned"
        else:
            assignee = None

        row = [
            str(task.id),
            task.title[:30] + "..." if len(task.title) > 30 else task.title,
            Text(task.priority, style=priority_style),
            Text(task.status, style=status_style),
        ]

        if show_assignee:
            row.append(str(assignee))

        table.add_row(*row)

    console.print(table)


def render_user_list(console: Console, users: list[Any]) -> None:
    """Render users in a formatted list.

    Args:
        console: The Rich console instance
        users: List of users to display
    """
    if not users:
        console.print("[yellow]No users found.[/yellow]")
        return

    table = Table(title="Users")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Name", style="white")
    table.add_column("Role", style="white")
    table.add_column("Skills", style="white")

    for user in users:
        skills_str = ", ".join(user.skills) if user.skills else "-"
        table.add_row(str(user.id), user.name, user.role, skills_str)

    console.print(table)


def render_team_list(console: Console, teams: list[Any]) -> None:
    """Render teams in a formatted list.

    Args:
        console: The Rich console instance
        teams: List of teams to display
    """
    if not teams:
        console.print("[yellow]No teams found.[/yellow]")
        return

    table = Table(title="Teams")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Name", style="white")
    table.add_column("Members", style="white")

    for team in teams:
        members_str = ", ".join(team.member_names)
        table.add_row(str(team.id), team.name, members_str)

    console.print(table)


def highlight_option(text: str, selected: bool = False) -> str:
    """Add visual highlighting to a menu option.

    Args:
        text: The option text to highlight
        selected: Whether this option is currently selected

    Returns:
        The formatted text with highlighting
    """
    if selected:
        return f"[bold reverse] {text} [/]"
    return f"   {text}"
