"""Main entry point for TeamFlow Console App.

This is the entry point for the Phase 1 console application.
It displays an interactive menu-driven interface for task management.
"""

import sys

from teamflow_console.cli.menus import (
    MainMenu,
    TaskManagementMenu,
    UserManagementMenu,
    display_exit_confirmation,
)
from teamflow_console.cli.prompts import TaskPrompts, UserPrompts
from teamflow_console.lib.formatting import create_console
from teamflow_console.lib.storage import get_task_store, get_team_store, get_user_store
from teamflow_console.lib.validation import validate_numbered_input
from teamflow_console.services.menu_service import MenuService, MenuState
from teamflow_console.services.task_service import TaskService
from teamflow_console.services.user_service import UserService

# Data loss warning
DATA_LOSS_WARNING = """
[yellow bold]⚠️  WARNING: DATA STORAGE[/yellow bold]

Data is stored in-memory only. All data will be lost when the application exits.

Press Enter to continue...
"""


class Application:
    """Main application class managing the CLI interface."""

    def __init__(self) -> None:
        """Initialize the application."""
        self.console = create_console()
        self.menu_service = MenuService()

        # Initialize services with storage
        # Note: We create services first, then wire them together to avoid circular dependency
        self.user_service = UserService(get_user_store())
        self.task_service = TaskService(get_task_store(), user_service=self.user_service)

        # Wire UserService to use TaskService for active task counts
        self.user_service._task_service = self.task_service

        # Initialize prompt handlers with wired services
        self.task_prompts = TaskPrompts(
            self.console, self.task_service, user_service=self.user_service
        )
        self.user_prompts = UserPrompts(
            self.console, self.user_service, task_service=self.task_service
        )

        # Terminal capability detection
        self.use_unicode = self._detect_terminal_capabilities()

    def _detect_terminal_capabilities(self) -> bool:
        """Detect if terminal supports Unicode box-drawing characters.

        Returns:
            True if Unicode is likely supported, False for ASCII fallback
        """
        # For now, assume Unicode support on most modern terminals
        # A more sophisticated implementation would try terminal queries
        return True

    def show_data_loss_warning(self) -> None:
        """Display the in-memory data loss warning."""
        self.console.print(DATA_LOSS_WARNING)
        input()

    def run(self) -> None:
        """Run the main application loop."""
        self.show_data_loss_warning()

        while not self.menu_service.should_exit():
            self._dispatch_menu()

        # Exit confirmation
        if display_exit_confirmation(self.console):
            self.console.print("[green]Thank you for using TeamFlow![/green]")
        else:
            # User cancelled exit, reset to main menu
            self.menu_service.reset()
            self.run()

    def _dispatch_menu(self) -> None:
        """Dispatch to the appropriate menu based on current state."""
        state = self.menu_service.current_state

        if state == MenuState.MAIN:
            self._handle_main_menu()
        elif state == MenuState.TASK_MANAGEMENT:
            self._handle_task_management_menu()
        elif state == MenuState.USER_MANAGEMENT:
            self._handle_user_management_menu()
        elif state == MenuState.VIEW_TASKS:
            self._handle_view_tasks()
        elif state == MenuState.VIEW_RESOURCES:
            self._handle_view_resources()

    def _handle_main_menu(self) -> None:
        """Handle main menu interaction."""
        MainMenu.display(self.console, self.use_unicode)

        selection = MainMenu.get_selection()
        if not selection:
            return

        try:
            self.menu_service.navigate(selection)
        except ValueError as e:
            self.console.print(f"[red]Invalid option: {e}[/red]")
            self.console.print("Press Enter to continue...")
            input()

    def _handle_task_management_menu(self) -> None:
        """Handle task management submenu interaction."""
        TaskManagementMenu.display(self.console, self.use_unicode)

        selection = input().strip()
        if not selection:
            return

        try:
            # Check for back command
            if selection.lower() in ("b", "q", "0"):
                self.menu_service.navigate(0)
            else:
                # Navigate to submenu state (stays in task management)
                self.menu_service.navigate(selection)
                # Handle actual action
                self._handle_task_action(selection)
        except ValueError as e:
            self.console.print(f"[red]Invalid option: {e}[/red]")
            self.console.print("Press Enter to continue...")
            input()

    def _handle_task_action(self, selection: str) -> None:
        """Handle task management action selection.

        Args:
            selection: The selected action number
        """
        action_map = {
            "1": self._action_create_task,
            "2": self._action_list_tasks,
            "3": self._action_update_task,
            "4": self._action_complete_task,
            "5": self._action_delete_task,
        }

        action = action_map.get(selection)
        if action:
            action()
        else:
            self.console.print("[red]Invalid action.[/red]")
            self.console.print("Press Enter to continue...")
            input()

    def _action_create_task(self) -> None:
        """Handle create task action."""
        self.task_prompts.prompt_create_task()

    def _action_list_tasks(self) -> None:
        """Handle list tasks action."""
        self.task_prompts.prompt_list_tasks()

    def _action_update_task(self) -> None:
        """Handle update task action."""
        self.task_prompts.prompt_update_task()

    def _action_complete_task(self) -> None:
        """Handle complete task action."""
        self.task_prompts.prompt_complete_task()

    def _action_delete_task(self) -> None:
        """Handle delete task action."""
        self.task_prompts.prompt_delete_task()

    def _handle_user_management_menu(self) -> None:
        """Handle user management submenu interaction."""
        UserManagementMenu.display(self.console, self.use_unicode)

        selection = input().strip()
        if not selection:
            return

        try:
            # Check for back command
            if selection.lower() in ("b", "q", "0"):
                self.menu_service.navigate(0)
            else:
                # Navigate to submenu state
                self.menu_service.navigate(selection)
                # Handle actual action
                self._handle_user_action(selection)
        except ValueError as e:
            self.console.print(f"[red]Invalid option: {e}[/red]")
            self.console.print("Press Enter to continue...")
            input()

    def _handle_user_action(self, selection: str) -> None:
        """Handle user management action selection.

        Args:
            selection: The selected action number
        """
        action_map = {
            "1": self._action_create_user,
            "2": self._action_create_team,
            "3": self._action_list_users,
            "4": self._action_list_teams,
        }

        action = action_map.get(selection)
        if action:
            action()
        else:
            self.console.print("[red]Invalid action.[/red]")
            self.console.print("Press Enter to continue...")
            input()

    def _action_create_user(self) -> None:
        """Handle create user action."""
        self.user_prompts.prompt_create_user()

    def _action_create_team(self) -> None:
        """Handle create team action."""
        self.user_prompts.prompt_create_team()

    def _action_list_users(self) -> None:
        """Handle list users action."""
        self.user_prompts.prompt_list_users()

    def _action_list_teams(self) -> None:
        """Handle list teams action."""
        self.user_prompts.prompt_list_teams()

    def _handle_view_tasks(self) -> None:
        """Handle view tasks direct action."""
        self.task_prompts.prompt_list_tasks()
        self.menu_service.back()

    def _handle_view_resources(self) -> None:
        """Handle view resources direct action."""
        self.user_prompts.prompt_view_resources()
        self.menu_service.back()


def main() -> None:
    """Main application entry point."""
    app = Application()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n[yellow]Application interrupted.[/yellow]")
        sys.exit(0)
    except Exception as e:
        print(f"[red]An error occurred: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
