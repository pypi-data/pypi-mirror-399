"""Prompt pattern template with cancellation handling.

This template shows how to create interactive prompts that:
1. Handle user cancellation (pressing 'q')
2. Validate input with re-prompting
3. Show rich UI feedback
"""

from typing import Optional
from rich.console import Console
from rich.panel import Panel


# ============================================================================
# CANCELLATION EXCEPTION
# ============================================================================

class CancelledException(Exception):
    """Raised when user cancels an operation by entering 'q'."""
    pass


# ============================================================================
# PROMPT HANDLER CLASS
# ============================================================================

class EntityPrompts:
    """Interactive prompt workflows for entity operations.

    Key patterns:
    1. Try/except CancelledException in create methods
    2. Separate validation methods for each field
    3. Rich success/error panels
    4. Clear user prompts with numbered selections
    """

    def __init__(self, console: Console, service) -> None:
        """Initialize prompt handler.

        Args:
            console: Rich console instance
            service: Business logic service
        """
        self.console = console
        self.service = service

    def prompt_create(self) -> None:
        """Prompt user to create a new entity.

        This method MUST be wrapped in try/except to handle cancellation.
        """
        self.console.print()
        self.console.print("[bold cyan]Create New Entity[/bold cyan]")
        self.console.print()

        try:
            # Step 1: Name (required)
            name = self._prompt_name()

            # Step 2: Description (optional)
            description = self._prompt_description()

            # Step 3: Option selection (numbered)
            option = self._prompt_option()

            # Create the entity
            entity = self.service.create(
                name=name,
                description=description,
                option=option,
            )

            # Show success
            self._show_success(entity)

        except CancelledException:
            # User pressed 'q' - return to menu silently
            pass

    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================

    def _prompt_name(self) -> str:
        """Prompt for entity name.

        Returns:
            The validated name

        User can cancel by entering 'q'.
        """
        while True:
            try:
                name = input("Enter name (or 'q' to cancel): ").strip()
                if name.lower() == 'q':
                    raise CancelledException()

                # Validation
                if not name:
                    raise ValueError("Name is required.")
                if len(name) > 200:
                    raise ValueError("Name must be 200 characters or less.")

                return name

            except ValueError as e:
                self.console.print(f"[red]{e}[/red]")

    def _prompt_description(self) -> Optional[str]:
        """Prompt for optional description.

        Returns:
            The validated description, or None if skipped

        Press Enter to skip/return None.
        """
        while True:
            try:
                desc = input("Enter description (press Enter to skip): ").strip()
                if not desc:
                    return None
                if len(desc) > 1000:
                    raise ValueError("Description must be 1000 characters or less.")
                return desc

            except ValueError as e:
                self.console.print(f"[red]{e}[/red]")

    def _prompt_option(self) -> str:
        """Prompt for numbered option selection.

        Returns:
            The selected option

        Shows numbered list and validates selection.
        """
        self.console.print("Select option:")
        self.console.print("  [1] Option A")
        self.console.print("  [2] Option B")
        self.console.print("  [3] Option C")

        while True:
            choice = input("Enter choice [1-3] (default: 1): ").strip()
            if not choice:
                return "option_a"  # Default

            try:
                if choice == "1":
                    return "option_a"
                if choice == "2":
                    return "option_b"
                if choice == "3":
                    return "option_c"
                raise ValueError("Please enter a number between 1 and 3.")

            except ValueError as e:
                self.console.print(f"[red]{e}[/red]")

    def _show_success(self, entity) -> None:
        """Display success message after creating entity.

        Args:
            entity: The created entity
        """
        message = f"""[SUCCESS] Entity created!

ID: {entity.id}
Name: {entity.name}
Description: {entity.description or '(none)'}
Option: {entity.status}"""
        render_success_panel(self.console, message)


# ============================================================================
# RICH UI HELPERS
# ============================================================================

def render_success_panel(console: Console, message: str) -> None:
    """Render a success message in a green panel.

    Args:
        console: Rich console instance
        message: Success message to display
    """
    console.print()
    panel = Panel(
        message,
        title="[bold green]SUCCESS[/bold green]",
        border_style="green",
        padding=(1, 2),
    )
    console.print(panel)


def render_error_panel(console: Console, message: str) -> None:
    """Render an error message in a red panel.

    Args:
        console: Rich console instance
        message: Error message to display
    """
    console.print()
    panel = Panel(
        message,
        title="[bold red]ERROR[/bold red]",
        border_style="red",
        padding=(1, 2),
    )
    console.print(panel)
