"""Menu navigation service for TeamFlow Console App.

This module implements the state machine pattern for menu navigation.
"""

from enum import Enum
from typing import Literal


class MenuState(Enum):
    """States in the menu navigation state machine."""

    MAIN = "main"
    TASK_MANAGEMENT = "task_management"
    USER_MANAGEMENT = "user_management"
    VIEW_TASKS = "view_tasks"
    VIEW_RESOURCES = "view_resources"
    EXIT = "exit"


class MenuService:
    """Service for managing menu navigation state.

    This class implements the state machine pattern for menu navigation.
    It tracks the current state and maintains a history stack for
    implementing the "Back" functionality.
    """

    def __init__(self) -> None:
        """Initialize menu service with main menu as initial state."""
        self._state: MenuState = MenuState.MAIN
        self._history: list[MenuState] = []

    @property
    def current_state(self) -> MenuState:
        """Get the current menu state.

        Returns:
            The current MenuState
        """
        return self._state

    def navigate(self, selection: str | int) -> MenuState:
        """Navigate to a new state based on user selection.

        Args:
            selection: The user's menu selection

        Returns:
            The new menu state

        Raises:
            ValueError: If selection is invalid for current state
        """
        # Convert string to int if needed
        if isinstance(selection, str) and selection.isdigit():
            selection = int(selection)

        # Navigate based on current state
        if self._state == MenuState.MAIN:
            return self._navigate_from_main(selection)
        elif self._state == MenuState.TASK_MANAGEMENT:
            return self._navigate_from_task_management(selection)
        elif self._state == MenuState.USER_MANAGEMENT:
            return self._navigate_from_user_management(selection)
        else:
            # For view states, any selection goes back to main
            self._state = MenuState.MAIN
            return self._state

    def _navigate_from_main(self, selection: str | int) -> MenuState:
        """Navigate from main menu.

        Args:
            selection: The user's selection

        Returns:
            The new menu state
        """
        # Handle letter shortcuts
        if isinstance(selection, str):
            selection_lower = selection.lower()
            if selection_lower == "c":
                selection = 1  # Create task
            elif selection_lower == "l":
                selection = 3  # List tasks
            elif selection_lower == "q":
                selection = 5  # Exit

        # Handle numeric selection
        if selection == 1:
            self._state = MenuState.TASK_MANAGEMENT
        elif selection == 2:
            self._state = MenuState.USER_MANAGEMENT
        elif selection == 3:
            self._state = MenuState.VIEW_TASKS
        elif selection == 4:
            self._state = MenuState.VIEW_RESOURCES
        elif selection == 5:
            self._state = MenuState.EXIT
        else:
            raise ValueError("Invalid selection. Please enter a number between 1 and 5.")

        return self._state

    def _navigate_from_task_management(self, selection: str | int) -> MenuState:
        """Navigate from task management submenu.

        Args:
            selection: The user's selection

        Returns:
            The new menu state
        """
        # Handle letter shortcuts
        if isinstance(selection, str):
            selection_lower = selection.lower()
            if selection_lower in ("b", "q"):
                selection = 0  # Back
            else:
                # Convert to int if possible
                try:
                    selection = int(selection)
                except ValueError:
                    raise ValueError("Invalid selection. Please enter a number between 0 and 5.")

        # Handle numeric selection
        if selection == 0:
            self._state = MenuState.MAIN
        else:
            # For actions (1-5), stay in task management
            # The actual action will be handled by the CLI
            pass

        return self._state

    def _navigate_from_user_management(self, selection: str | int) -> MenuState:
        """Navigate from user management submenu.

        Args:
            selection: The user's selection

        Returns:
            The new menu state
        """
        # Handle letter shortcuts
        if isinstance(selection, str):
            selection_lower = selection.lower()
            if selection_lower in ("b", "q"):
                selection = 0  # Back
            else:
                # Convert to int if possible
                try:
                    selection = int(selection)
                except ValueError:
                    raise ValueError("Invalid selection. Please enter a number between 0 and 4.")

        # Handle numeric selection
        if selection == 0:
            self._state = MenuState.MAIN
        else:
            # For actions (1-4), stay in user management
            # The actual action will be handled by the CLI
            pass

        return self._state

    def back(self) -> MenuState:
        """Navigate back to the main menu.

        For this simple menu structure, back always goes to main.

        Returns:
            MenuState.MAIN
        """
        self._state = MenuState.MAIN
        return self._state

    def reset(self) -> None:
        """Reset to main menu with cleared history."""
        self._state = MenuState.MAIN
        self._history.clear()

    def is_main_menu(self) -> bool:
        """Check if currently at main menu.

        Returns:
            True if at main menu, False otherwise
        """
        return self._state == MenuState.MAIN

    def should_exit(self) -> bool:
        """Check if the application should exit.

        Returns:
            True if in EXIT state, False otherwise
        """
        return self._state == MenuState.EXIT
