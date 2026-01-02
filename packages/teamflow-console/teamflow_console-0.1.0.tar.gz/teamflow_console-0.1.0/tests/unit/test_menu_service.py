"""Unit tests for MenuService."""

import pytest

from services.menu_service import MenuService, MenuState


class TestMenuService:
    """Tests for MenuService state management."""

    def test_initial_state_is_main(self) -> None:
        """Test that the initial state is MAIN."""
        service = MenuService()
        assert service.current_state == MenuState.MAIN

    def test_navigate_from_main_to_task_management(self) -> None:
        """Test navigating from main menu to task management."""
        service = MenuService()
        service.navigate(1)
        assert service.current_state == MenuState.TASK_MANAGEMENT

    def test_navigate_from_main_to_user_management(self) -> None:
        """Test navigating from main menu to user management."""
        service = MenuService()
        service.navigate(2)
        assert service.current_state == MenuState.USER_MANAGEMENT

    def test_navigate_from_main_to_view_tasks(self) -> None:
        """Test navigating from main menu to view tasks."""
        service = MenuService()
        service.navigate(3)
        assert service.current_state == MenuState.VIEW_TASKS

    def test_navigate_from_main_to_view_resources(self) -> None:
        """Test navigating from main menu to view resources."""
        service = MenuService()
        service.navigate(4)
        assert service.current_state == MenuState.VIEW_RESOURCES

    def test_navigate_from_main_to_exit(self) -> None:
        """Test navigating from main menu to exit."""
        service = MenuService()
        service.navigate(5)
        assert service.current_state == MenuState.EXIT

    def test_navigate_shortcut_c_to_create_task(self) -> None:
        """Test that 'c' shortcut navigates to task management."""
        service = MenuService()
        service.navigate("c")
        assert service.current_state == MenuState.TASK_MANAGEMENT

    def test_navigate_shortcut_l_to_list_tasks(self) -> None:
        """Test that 'l' shortcut navigates to view tasks."""
        service = MenuService()
        service.navigate("l")
        assert service.current_state == MenuState.VIEW_TASKS

    def test_navigate_shortcut_q_to_exit(self) -> None:
        """Test that 'q' shortcut navigates to exit."""
        service = MenuService()
        service.navigate("q")
        assert service.current_state == MenuState.EXIT

    def test_back_from_task_management(self) -> None:
        """Test going back from task management to main menu."""
        service = MenuService()
        service.navigate(1)  # Go to task management
        service.navigate(0)  # Go back
        assert service.current_state == MenuState.MAIN

    def test_back_from_user_management(self) -> None:
        """Test going back from user management to main menu."""
        service = MenuService()
        service.navigate(2)  # Go to user management
        service.navigate(0)  # Go back
        assert service.current_state == MenuState.MAIN

    def test_back_method_returns_to_previous_state(self) -> None:
        """Test that back() method pops from history."""
        service = MenuService()
        service.navigate(1)  # MAIN -> TASK_MANAGEMENT
        previous = service.current_state
        service.back()
        assert service.current_state == MenuState.MAIN
        assert service.is_main_menu()

    def test_is_main_menu_returns_true_for_main(self) -> None:
        """Test that is_main_menu() returns True when at main menu."""
        service = MenuService()
        assert service.is_main_menu()

    def test_is_main_menu_returns_false_for_submenu(self) -> None:
        """Test that is_main_menu() returns False when in submenu."""
        service = MenuService()
        service.navigate(1)
        assert not service.is_main_menu()

    def test_should_exit_returns_true_only_in_exit_state(self) -> None:
        """Test that should_exit() returns True only in EXIT state."""
        service = MenuService()
        assert not service.should_exit()
        service.navigate(5)
        assert service.should_exit()

    def test_invalid_selection_raises_value_error(self) -> None:
        """Test that invalid selection raises ValueError."""
        service = MenuService()
        with pytest.raises(ValueError):
            service.navigate(99)
