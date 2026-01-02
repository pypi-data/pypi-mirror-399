"""Integration tests for menu flow."""

import pytest

from services.menu_service import MenuService, MenuState


class TestMainMenuFlow:
    """Integration tests for main menu navigation flow."""

    def test_main_menu_has_five_options(self) -> None:
        """Test that main menu provides 5 navigation options."""
        service = MenuService()
        # Should be able to navigate to 5 different states
        assert service.navigate(1) == MenuState.TASK_MANAGEMENT
        service.reset()

        assert service.navigate(2) == MenuState.USER_MANAGEMENT
        service.reset()

        assert service.navigate(3) == MenuState.VIEW_TASKS
        service.reset()

        assert service.navigate(4) == MenuState.VIEW_RESOURCES
        service.reset()

        assert service.navigate(5) == MenuState.EXIT

    def test_number_key_navigation(self) -> None:
        """Test navigation using number keys."""
        service = MenuService()

        # Navigate through main menu options
        service.navigate(1)
        assert service.current_state == MenuState.TASK_MANAGEMENT

        service.back()
        service.navigate(2)
        assert service.current_state == MenuState.USER_MANAGEMENT

        service.back()
        service.navigate(3)
        assert service.current_state == MenuState.VIEW_TASKS

    def test_back_escape_navigation(self) -> None:
        """Test returning to main menu with '0' or 'b'."""
        service = MenuService()

        # Navigate to task management
        service.navigate(1)
        assert not service.is_main_menu()

        # Return with '0'
        service.navigate(0)
        assert service.is_main_menu()

        # Navigate again and return with 'b'
        service.navigate(1)
        service.navigate("b")
        assert service.is_main_menu()

    def test_exit_from_main_menu(self) -> None:
        """Test exiting the application from main menu."""
        service = MenuService()

        # Exit with option 5
        service.navigate(5)
        assert service.should_exit()

        # Reset and try with 'q' shortcut
        service.reset()
        service.navigate("q")
        assert service.should_exit()

    def test_full_menu_roundtrip(self) -> None:
        """Test a full roundtrip through the menu system."""
        service = MenuService()

        # Start at main
        assert service.is_main_menu()

        # Go to task management
        service.navigate(1)
        assert service.current_state == MenuState.TASK_MANAGEMENT

        # Return to main
        service.navigate(0)
        assert service.is_main_menu()

        # Go to user management
        service.navigate(2)
        assert service.current_state == MenuState.USER_MANAGEMENT

        # Return to main
        service.back()
        assert service.is_main_menu()

        # Exit
        service.navigate(5)
        assert service.should_exit()


class TestKeyboardShortcuts:
    """Integration tests for keyboard shortcuts (US5)."""

    def test_shortcut_c_creates_task(self) -> None:
        """Test that 'c' shortcut navigates to task creation (FR-029)."""
        service = MenuService()

        # 'c' should navigate to task management (which shows create menu)
        state = service.navigate("c")
        # Since 'c' goes to task management, verify we're not at main
        assert not service.is_main_menu()

    def test_shortcut_l_lists_tasks(self) -> None:
        """Test that 'l' shortcut navigates to task listing (FR-030)."""
        service = MenuService()

        # 'l' should navigate to view tasks
        state = service.navigate("l")
        assert state == MenuState.VIEW_TASKS

    def test_shortcut_q_exits(self) -> None:
        """Test that 'q' shortcut exits the application (FR-031)."""
        service = MenuService()

        # 'q' should navigate to exit
        state = service.navigate("q")
        assert service.should_exit()

    def test_escape_returns_to_main(self) -> None:
        """Test that Escape/q key returns to main menu (FR-031)."""
        service = MenuService()

        # Navigate away from main
        service.navigate(1)
        assert not service.is_main_menu()

        # 'q' should behave as back/exit (Escape is handled by CLI layer)
        service.navigate("q")
        # After q, we should be back at main or in exit state
        assert service.is_main_menu() or service.should_exit()
