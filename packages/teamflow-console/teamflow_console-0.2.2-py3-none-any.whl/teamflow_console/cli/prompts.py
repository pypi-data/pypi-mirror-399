"""Interactive prompt handlers for TeamFlow Console App.

This module contains the interactive prompt workflows for creating,
listing, updating, completing, and deleting tasks.
"""

from typing import Optional

from ..lib.formatting import (
    Style,
    create_console,
    render_border,
    render_error_panel,
    render_success_panel,
    render_task_table,
)
from ..lib.validation import (
    validate_enum_selection,
    validate_numbered_input,
    validate_optional_text,
    validate_required_text,
)
from ..models.task import Priority, Status, Task
from ..models.team import Team
from ..models.user import Role, User
from ..services.task_service import TaskNotFoundError, TaskService
from ..services.user_service import DuplicateUserNameError, UserNotFoundError, UserService


class TaskPrompts:
    """Interactive prompt workflows for task operations."""

    def __init__(
        self, console, task_service: TaskService, user_service: UserService = None
    ) -> None:
        """Initialize task prompts.

        Args:
            console: The Rich console instance
            task_service: The task service instance
            user_service: Optional user service for assignee operations
        """
        self.console = console
        self.task_service = task_service
        self.user_service = user_service

    def prompt_create_task(self) -> None:
        """Prompt user to create a new task.

        Follows the workflow: title → description → priority → assignee
        """
        self.console.print()
        self.console.print("[bold cyan]Create New Task[/bold cyan]")
        self.console.print()

        try:
            # Step 1: Title
            title = self._prompt_title()

            # Step 2: Description
            description = self._prompt_description()

            # Step 3: Priority
            priority = self._prompt_priority()

            # Step 4: Assignee
            assignee_id = self._prompt_assignee()

            # Create the task
            task = self.task_service.create(
                title=title,
                description=description,
                priority=priority,
                assignee_id=assignee_id,
            )

            # Show success
            self._show_task_created_success(task)
        except CancelledException:
            # User cancelled, return to menu silently
            pass

    def prompt_list_tasks(self) -> None:
        """Display all tasks in a table format with optional filtering.

        Users can press 1-9 to view task details, or Enter to return to menu.
        """
        self.console.print()

        # Check if there are any tasks
        all_tasks = self.task_service.list_all()
        if not all_tasks:
            self.console.print("[yellow]No tasks found.[/yellow]")
            self.console.print()
            self.console.print("Press Enter to return to menu...")
            input()
            return

        # Show filter menu
        tasks_to_show = self._prompt_filter_or_show_all(all_tasks)

        # Back if user selected 0 in filter menu
        if tasks_to_show == [] and all_tasks:
            return

        # Display the filtered tasks
        if not tasks_to_show:
            self.console.print("[yellow]No tasks found matching your criteria.[/yellow]")
            self.console.print()
            self.console.print("Press Enter to return to menu...")
            input()
            return

        # Show tasks with numbered options
        self._show_numbered_tasks(tasks_to_show)

        # Prompt for action (view details or back)
        self._prompt_task_selection_or_back(tasks_to_show)

    def _prompt_filter_or_show_all(self, all_tasks: list[Task]) -> list[Task]:
        """Prompt user for filter selection or show all tasks.

        Args:
            all_tasks: List of all tasks to potentially filter

        Returns:
            List of tasks to display (filtered or all)
        """
        self.console.print("Filter tasks:")
        self.console.print("  [1] All Tasks")
        self.console.print("  [2] By Status")
        self.console.print("  [3] By Priority")
        self.console.print("  [4] By Assignee")
        self.console.print("  [0] Back")
        self.console.print()

        while True:
            choice = input("Select filter option [0-4] (default: 1): ").strip()
            filter_choice = choice or "1"

            if filter_choice == "0":
                return []  # Back
            elif filter_choice == "1":
                return all_tasks
            elif filter_choice == "2":
                return self._filter_by_status()
            elif filter_choice == "3":
                return self._filter_by_priority()
            elif filter_choice == "4":
                return self._filter_by_assignee()
            else:
                self.console.print("[red]Please enter a number between 0 and 4.[/red]")

    def _filter_by_status(self) -> list[Task]:
        """Filter tasks by status.

        Returns:
            List of filtered tasks
        """
        self.console.print()
        self.console.print("Select status:")
        self.console.print("  [1] Todo")
        self.console.print("  [2] In Progress")
        self.console.print("  [3] Done")

        while True:
            choice = input("Enter choice [1-3]: ").strip()
            if not choice:
                return self.task_service.list_all()

            try:
                status = validate_enum_selection(choice, Status)
                return self.task_service.filter_by_status(status)
            except ValueError as e:
                self.console.print(f"[red]{e}[/red]")

    def _filter_by_priority(self) -> list[Task]:
        """Filter tasks by priority.

        Returns:
            List of filtered tasks
        """
        self.console.print()
        self.console.print("Select priority:")
        self.console.print("  [1] High")
        self.console.print("  [2] Medium")
        self.console.print("  [3] Low")

        while True:
            choice = input("Enter choice [1-3]: ").strip()
            if not choice:
                return self.task_service.list_all()

            try:
                priority = validate_enum_selection(choice, Priority)
                return self.task_service.filter_by_priority(priority)
            except ValueError as e:
                self.console.print(f"[red]{e}[/red]")

    def _filter_by_assignee(self) -> list[Task]:
        """Filter tasks by assignee.

        Returns:
            List of filtered tasks
        """
        self.console.print()
        self.console.print("Select assignee:")
        self.console.print("  [0] Unassigned")

        # Get users and display
        users = []
        if self.user_service:
            users = self.user_service.list_all()

        if users:
            for user in users:
                self.console.print(f"  [{user.id}] {user.name}")
        else:
            self.console.print("  (No users available)")

        while True:
            max_id = max([u.id for u in users], default=0)
            prompt = f"Enter choice [0-{max_id}]: " if users else "Enter choice [0]: "
            choice = input(prompt).strip()

            if not choice:
                return self.task_service.list_all()

            try:
                user_id = int(choice)
                if user_id == 0:
                    return self.task_service.filter_by_assignee(None)
                return self.task_service.filter_by_assignee(user_id)
            except ValueError:
                self.console.print("[red]Please enter a valid number.[/red]")

    def _show_numbered_tasks(self, tasks: list[Task]) -> None:
        """Display tasks with numbered options (1-9).

        Args:
            tasks: List of tasks to display (max 9 shown with numbers)
        """
        # Display table with assignee names
        render_task_table(self.console, tasks, user_service=self.user_service)

        # Show numbered options (max 9)
        max_show = min(9, len(tasks))
        self.console.print()
        self.console.print("[dim]Press 1-9 to view details, or Enter to return:[/dim]")

    def _prompt_task_selection_or_back(self, tasks: list[Task]) -> None:
        """Prompt user to select a task by number or return to menu.

        Args:
            tasks: List of displayed tasks
        """
        while True:
            choice = input("Enter selection [1-9] or Enter to return: ").strip()

            # Return to menu on empty input
            if not choice:
                return

            # Validate numeric input
            try:
                task_num = int(choice)
                if 1 <= task_num <= min(9, len(tasks)):
                    # Get the selected task (1-indexed)
                    task = tasks[task_num - 1]
                    # Show task detail view
                    self._prompt_task_detail(task)
                    # After detail view, return to task list
                    return
                else:
                    self.console.print(
                        f"[red]Please enter a number between 1 and {min(9, len(tasks))}.[/red]"
                    )
            except ValueError:
                self.console.print("[red]Please enter a valid number.[/red]")

    def _prompt_task_detail(self, task: Task) -> None:
        """Display task detail view with available actions.

        Args:
            task: The task to display details for
        """
        while True:
            self.console.print()
            self.console.print("[bold cyan]Task Details[/bold cyan]")
            self.console.print()

            # Display task information
            from rich.panel import Panel
            from rich.table import Table

            # Create detail panel
            detail_table = Table(show_header=False, box=None, padding=(0, 2))
            detail_table.add_column("Field", style="cyan")
            detail_table.add_column("Value")

            detail_table.add_row("ID:", str(task.id))
            detail_table.add_row("Title:", task.title)
            detail_table.add_row("Description:", task.description or "(none)")
            detail_table.add_row("Priority:", str(task.priority))
            detail_table.add_row("Status:", str(task.status))

            # Show assignee name if available
            if task.assignee_id and self.user_service:
                try:
                    user = self.user_service.get_by_id(task.assignee_id)
                    detail_table.add_row("Assigned To:", user.name)
                except Exception:
                    detail_table.add_row("Assigned To:", f"User #{task.assignee_id}")
            elif task.assignee_id:
                detail_table.add_row("Assigned To:", f"User #{task.assignee_id}")
            else:
                detail_table.add_row("Assigned To:", "Unassigned")

            self.console.print(
                Panel(detail_table, title=f"[bold]Task #{task.id}[/bold]", border_style="cyan")
            )

            # Show available actions
            self.console.print()
            self.console.print("Available actions:")
            self.console.print("  [1] Complete Task")
            self.console.print("  [2] Edit Task")
            self.console.print("  [3] Delete Task")
            self.console.print("  [0] Back to Task List")
            self.console.print()

            # Prompt for action
            choice = input("Select action [0-3]: ").strip()

            if choice == "0":
                return
            elif choice == "1":
                # Complete task
                if self._confirm_complete(task):
                    updated = self.task_service.update_status(task.id, Status.DONE)
                    self._show_task_complete_success(updated)
                    return  # Return to task list after action
            elif choice == "2":
                # Edit task
                self._update_task_from_detail(task)
                return  # Return to task list after action
            elif choice == "3":
                # Delete task
                if self._confirm_delete(task):
                    self.task_service.delete(task.id)
                    self._show_task_delete_success(task.id)
                    return  # Return to task list after action
            else:
                self.console.print("[red]Please enter a number between 0 and 3.[/red]")

    def _update_task_from_detail(self, task: Task) -> None:
        """Update task fields from detail view.

        Args:
            task: The task to update
        """
        self.console.print()
        self.console.print("[bold cyan]Edit Task[/bold cyan]")
        self.console.print()

        # Select field to update
        field = self._prompt_update_field()
        if field is None:
            return

        # Update the field
        self._update_task_field(task, field)

    def prompt_update_task(self) -> None:
        """Prompt user to update an existing task."""
        self.console.print()
        self.console.print("[bold cyan]Update Task[/bold cyan]")
        self.console.print()

        # Step 1: Select task
        task = self._prompt_select_task()
        if task is None:
            return

        # Step 2: Select field to update
        field = self._prompt_update_field()
        if field is None:
            return

        # Step 3: Enter new value
        self._update_task_field(task, field)

    def prompt_complete_task(self) -> None:
        """Prompt user to mark a task as complete."""
        self.console.print()
        self.console.print("[bold cyan]Complete Task[/bold cyan]")
        self.console.print()

        # Step 1: Select task
        task = self._prompt_select_task()
        if task is None:
            return

        # Step 2: Confirm
        if self._confirm_complete(task):
            updated = self.task_service.update_status(task.id, Status.DONE)
            self._show_task_complete_success(updated)

    def prompt_delete_task(self) -> None:
        """Prompt user to delete a task."""
        self.console.print()
        self.console.print("[bold cyan]Delete Task[/bold cyan]")
        self.console.print()

        # Step 1: Select task
        task = self._prompt_select_task()
        if task is None:
            return

        # Step 2: Confirm deletion
        if self._confirm_delete(task):
            self.task_service.delete(task.id)
            self._show_task_delete_success(task.id)

    # Private helper methods

    def _prompt_title(self) -> str:
        """Prompt for task title.

        Returns:
            The validated title
        """
        while True:
            try:
                title = input("Enter task title (or 'q' to cancel): ").strip()
                if title.lower() == "q":
                    raise CancelledException()

                return validate_required_text(title, min_length=1, max_length=200)
            except ValueError as e:
                self.console.print(f"[red]{e}[/red]")

    def _prompt_description(self) -> Optional[str]:
        """Prompt for task description.

        Returns:
            The validated description, or None if skipped
        """
        while True:
            try:
                desc = input("Enter description (optional, press Enter to skip): ").strip()
                return validate_optional_text(desc, max_length=1000)
            except ValueError as e:
                self.console.print(f"[red]{e}[/red]")

    def _prompt_priority(self) -> Priority:
        """Prompt for task priority.

        Returns:
            The selected priority
        """
        while True:
            self.console.print("Select priority:")
            self.console.print("  [1] High")
            self.console.print("  [2] Medium")
            self.console.print("  [3] Low")

            try:
                choice = input("Enter choice [1-3] (default: 2): ").strip()
                return validate_enum_selection(
                    choice or "2",
                    Priority,
                    allow_empty=True,
                    default=Priority.MEDIUM,
                )
            except ValueError as e:
                self.console.print(f"[red]{e}[/red]")

    def _prompt_assignee(self) -> Optional[int]:
        """Prompt for task assignee.

        Returns:
            The selected user ID, or None for unassigned
        """
        self.console.print("Select assignee:")
        self.console.print("  [0] Unassigned")

        # Get users and display with task counts
        users = []
        if self.user_service:
            users = self.user_service.list_all()

        if users:
            for user in users:
                task_count = (
                    self.user_service.get_active_task_count(user.id) if self.user_service else 0
                )
                skills_str = (
                    ", ".join(user.skills[:2]) if user.skills else ""
                )  # Show first 2 skills
                skills_display = f" | Skills: {skills_str}" if skills_str else ""

                # Workload warning indicator
                if task_count >= 5:
                    workload = " [red](High workload!)[/red]"
                elif task_count >= 3:
                    workload = " [yellow](Medium workload)[/yellow]"
                else:
                    workload = ""

                self.console.print(
                    f"  [{user.id}] {user.name} ({task_count} tasks){workload}{skills_display}"
                )
        else:
            self.console.print(
                "  (No users available. Tip: Create users in the User Management menu.)"
            )

        while True:
            try:
                max_id = max([u.id for u in users], default=0)
                prompt = (
                    f"Enter choice [0-{max_id}] (default: 0): "
                    if users
                    else "Enter choice [0] (default: 0): "
                )
                choice = input(prompt).strip()
                if not choice:
                    return None

                user_id = int(choice)
                if user_id == 0:
                    return None

                # Validate user exists
                if self.user_service:
                    try:
                        self.user_service.get_by_id(user_id)
                    except UserNotFoundError:
                        self.console.print(
                            f"[red]User #{user_id} not found. Please enter a valid number.[/red]"
                        )
                        continue

                    # Check for workload warning (5+ active tasks)
                    task_count = self.user_service.get_active_task_count(user_id)
                    if task_count >= 5:
                        self.console.print(
                            f"[yellow]Warning: User has {task_count} active tasks. Continue? [Y/n]: [/yellow]",
                            end="",
                        )
                        confirm = input().strip().lower()
                        if confirm in ("n", "no"):
                            continue

                return user_id

            except ValueError:
                self.console.print("[red]Please enter a valid number.[/red]")

    def _prompt_select_task(self) -> Optional[Task]:
        """Prompt user to select a task by ID.

        Returns:
            The selected task, or None if cancelled
        """
        while True:
            task_id_str = input("Enter task ID to update (or '0' to cancel): ").strip()
            if task_id_str == "0":
                return None

            try:
                task_id = int(task_id_str)
                return self.task_service.get_by_id(task_id)
            except ValueError:
                self.console.print("[red]Please enter a valid task ID.[/red]")
            except TaskNotFoundError as e:
                self.console.print(f"[red]{e}[/red]")
                self.console.print("Press Enter to continue...")
                input()
                return None

    def _prompt_update_field(self) -> Optional[int]:
        """Prompt user to select which field to update.

        Returns:
            The selected field number (0-5), or None if cancelled
        """
        self.console.print("Update Task:")
        self.console.print("  [1] Title")
        self.console.print("  [2] Description")
        self.console.print("  [3] Priority")
        self.console.print("  [4] Status")
        self.console.print("  [5] Assignee")
        self.console.print("  [0] Cancel")

        while True:
            choice = input("Enter field to update [0-5]: ").strip()
            if not choice:
                continue

            try:
                field_id = int(choice)
                if 0 <= field_id <= 5:
                    return field_id
                self.console.print("[red]Please enter a number between 0 and 5.[/red]")
            except ValueError:
                self.console.print("[red]Please enter a valid number.[/red]")

    def _update_task_field(self, task: Task, field_id: int) -> None:
        """Update a specific field of a task.

        Args:
            task: The task to update
            field_id: The field number (1-5)
        """
        field_map = {
            1: ("title", self._update_title),
            2: ("description", self._update_description),
            3: ("priority", self._update_priority),
            4: ("status", self._update_status),
            5: ("assignee_id", self._update_assignee),
        }

        if field_id not in field_map:
            self.console.print("[red]Invalid field.[/red]")
            return

        field_name, update_func = field_map[field_id]
        new_value = update_func()
        if new_value is not None:
            updated = self.task_service.update(task.id, **{field_name: new_value})
            self._show_task_updated_success(updated, field_name)

    def _update_title(self) -> str:
        """Prompt for new title.

        Returns:
            The new title
        """
        while True:
            try:
                title = input(f"Enter new title: ").strip()
                return validate_required_text(title, max_length=200)
            except ValueError as e:
                self.console.print(f"[red]{e}[/red]")

    def _update_description(self) -> Optional[str]:
        """Prompt for new description.

        Returns:
            The new description, or None to clear
        """
        while True:
            try:
                desc = input("Enter new description (press Enter to clear): ").strip()
                if not desc:
                    return None
                return validate_optional_text(desc, max_length=1000)
            except ValueError as e:
                self.console.print(f"[red]{e}[/red]")

    def _update_priority(self) -> Priority:
        """Prompt for new priority.

        Returns:
            The new priority
        """
        self.console.print("Select new priority:")
        self.console.print("  [1] High")
        self.console.print("  [2] Medium")
        self.console.print("  [3] Low")

        while True:
            try:
                choice = input("Enter choice [1-3]: ").strip()
                return validate_enum_selection(choice, Priority)
            except ValueError as e:
                self.console.print(f"[red]{e}[/red]")

    def _update_status(self) -> Status:
        """Prompt for new status.

        Returns:
            The new status
        """
        self.console.print("Select new status:")
        self.console.print("  [1] Todo")
        self.console.print("  [2] In Progress")
        self.console.print("  [3] Done")

        while True:
            try:
                choice = input("Enter choice [1-3]: ").strip()
                return validate_enum_selection(choice, Status)
            except ValueError as e:
                self.console.print(f"[red]{e}[/red]")

    def _update_assignee(self) -> Optional[int]:
        """Prompt for new assignee.

        Returns:
            The new assignee ID, or None for unassigned
        """
        self.console.print("Select new assignee:")
        self.console.print("  [0] Unassigned")

        # Get users and display with task counts
        users = []
        if self.user_service:
            users = self.user_service.list_all()

        if users:
            for user in users:
                task_count = (
                    self.user_service.get_active_task_count(user.id) if self.user_service else 0
                )
                self.console.print(f"  [{user.id}] {user.name} ({task_count} tasks)")
        else:
            self.console.print("  (No users available)")

        while True:
            try:
                max_id = max([u.id for u in users], default=0)
                prompt = f"Enter choice [0-{max_id}]: " if users else "Enter choice [0]: "
                choice = input(prompt).strip()
                if not choice:
                    continue

                user_id = int(choice)
                if user_id == 0:
                    return None

                # Validate user exists
                if self.user_service:
                    try:
                        self.user_service.get_by_id(user_id)
                        return user_id
                    except UserNotFoundError:
                        self.console.print(
                            f"[red]User #{user_id} not found. Please enter a valid number.[/red]"
                        )
                        continue
                return user_id

            except ValueError:
                self.console.print("[red]Please enter a valid number.[/red]")

    def _confirm_complete(self, task: Task) -> bool:
        """Confirm marking a task as complete.

        Args:
            task: The task to complete

        Returns:
            True if user confirms, False otherwise
        """
        self.console.print()
        prompt = f'Mark task #{task.id} "{task.title}" as complete? [Y/n]: '
        response = input(prompt).strip().lower()
        return response in ("", "y", "yes")

    def _confirm_delete(self, task: Task) -> bool:
        """Confirm deleting a task.

        Args:
            task: The task to delete

        Returns:
            True if user confirms, False otherwise
        """
        self.console.print()
        prompt = f'Delete task #{task.id} "{task.title}"? This cannot be undone. [Y/n]: '
        response = input(prompt).strip().lower()
        return response in ("", "y", "yes")

    def _show_task_created_success(self, task: Task) -> None:
        """Display success message after creating a task.

        Args:
            task: The created task
        """
        # Get assignee name if available
        assignee_display = "Unassigned"
        if task.assignee_id and self.user_service:
            try:
                user = self.user_service.get_by_id(task.assignee_id)
                assignee_display = user.name
            except UserNotFoundError:
                assignee_display = f"User #{task.assignee_id}"
        elif task.assignee_id:
            assignee_display = f"User #{task.assignee_id}"

        message = f"""[SUCCESS] Task created!

ID: {task.id}
Title: {task.title}
Priority: {task.priority}
Status: {task.status}
Assignee: {assignee_display}"""
        render_success_panel(self.console, message)

    def _show_task_updated_success(self, task: Task, field_name: str) -> None:
        """Display success message after updating a task.

        Args:
            task: The updated task
            field_name: The name of the field that was updated
        """
        message = f"""[SUCCESS] Task updated!

ID: {task.id}
Title: {task.title}"""
        render_success_panel(self.console, message)

    def _show_task_complete_success(self, task: Task) -> None:
        """Display success message after completing a task.

        Args:
            task: The completed task
        """
        message = f"""[SUCCESS] Task marked as Done!

ID: {task.id}
Title: {task.title}
Status: Done"""
        render_success_panel(self.console, message)

    def _show_task_delete_success(self, task_id: int) -> None:
        """Display success message after deleting a task.

        Args:
            task_id: The ID of the deleted task
        """
        message = f"""[SUCCESS] Task deleted!

Task #{task_id} has been removed."""
        render_success_panel(self.console, message)


class CancelledException(Exception):
    """Raised when user cancels an operation."""

    pass


class UserPrompts:
    """Interactive prompt workflows for user and team operations."""

    def __init__(
        self, console, user_service: UserService, task_service: TaskService = None
    ) -> None:
        """Initialize user prompts.

        Args:
            console: The Rich console instance
            user_service: The user service instance
            task_service: Optional task service for workload display
        """
        self.console = console
        self.user_service = user_service
        self.task_service = task_service

    def prompt_create_user(self) -> None:
        """Prompt user to create a new user.

        Follows the workflow: name → role → skills
        """
        self.console.print()
        self.console.print("[bold cyan]Create New User[/bold cyan]")
        self.console.print()

        try:
            # Step 1: Name
            name = self._prompt_user_name()

            # Step 2: Role
            role = self._prompt_user_role()

            # Step 3: Skills
            skills = self._prompt_user_skills()

            # Create the user
            user = self.user_service.create(
                name=name,
                role=role,
                skills=skills,
            )

            # Show success
            self._show_user_created_success(user)
        except CancelledException:
            # User cancelled, return to menu silently
            pass

    def prompt_list_users(self) -> None:
        """Display all users with their roles, skills, and task counts."""
        self.console.print()
        self.console.print("[bold cyan]All Users[/bold cyan]")
        self.console.print()

        users = self.user_service.list_all()

        if not users:
            self.console.print("[yellow]No users found.[/yellow]")
            self.console.print("Tip: Create users to assign tasks to team members.")
        else:
            # Display users with details
            self._display_user_list(users)

        self.console.print()
        self.console.print("Press Enter to return to menu...")
        input()

    def prompt_create_team(self) -> None:
        """Prompt user to create a new team.

        Follows the workflow: team name → select members
        """
        self.console.print()
        self.console.print("[bold cyan]Create New Team[/bold cyan]")
        self.console.print()

        # Check if there are users to add
        users = self.user_service.list_all()
        if not users:
            self.console.print(
                "[yellow]No users available. Create users first before creating teams.[/yellow]"
            )
            self.console.print("Press Enter to continue...")
            input()
            return

        try:
            # Step 1: Team name
            team_name = self._prompt_team_name()

            # Step 2: Select members
            members = self._prompt_team_members(users)

            if not members:
                self.console.print("[yellow]Team must have at least one member.[/yellow]")
                self.console.print("Press Enter to continue...")
                input()
                return

            # Import here to avoid circular dependency
            from ..lib.storage import get_team_store
            from ..services.team_service import TeamService

            team_service = TeamService(get_team_store())
            team = team_service.create(team_name, [m.name for m in members])

            # Show success
            self._show_team_created_success(team, members)
        except CancelledException:
            # User cancelled, return to menu silently
            pass

    def prompt_list_teams(self) -> None:
        """Display all teams with their members."""
        self.console.print()
        self.console.print("[bold cyan]All Teams[/bold cyan]")
        self.console.print()

        # Import here to avoid circular dependency
        from ..lib.storage import get_team_store
        from ..services.team_service import TeamService

        team_service = TeamService(get_team_store())
        teams = team_service.list_all()

        if not teams:
            self.console.print("[yellow]No teams found.[/yellow]")
        else:
            # Display teams with members
            self._display_team_list(teams)

        self.console.print()
        self.console.print("Press Enter to return to menu...")
        input()

    def prompt_view_resources(self) -> None:
        """Display resource overview showing all users with their workload."""
        self.console.print()
        self.console.print("[bold cyan]Resource Overview[/bold cyan]")
        self.console.print()

        users = self.user_service.list_all()

        if not users:
            self.console.print("[yellow]No resources found.[/yellow]")
            self.console.print("Tip: Create users to start tracking team resources.")
        else:
            # Display resources with workload
            self._display_resource_overview(users)

        self.console.print()
        self.console.print("Press Enter to return to menu...")
        input()

    # Private helper methods

    def _prompt_user_name(self) -> str:
        """Prompt for user name.

        Returns:
            The validated user name
        """
        while True:
            try:
                name = input("Enter user name (or 'q' to cancel): ").strip()
                if name.lower() == "q":
                    raise CancelledException()

                validated = validate_required_text(name, min_length=1, max_length=100)

                # Check for duplicate name
                if self.user_service.name_exists(validated):
                    self.console.print(
                        f"[red]User '{validated}' already exists. Please use a different name.[/red]"
                    )
                    continue

                return validated
            except ValueError as e:
                self.console.print(f"[red]{e}[/red]")

    def _prompt_user_role(self) -> Role:
        """Prompt for user role.

        Returns:
            The selected role
        """
        while True:
            self.console.print("Select role:")
            self.console.print("  [1] Admin")
            self.console.print("  [2] Developer")
            self.console.print("  [3] Designer")

            try:
                choice = input("Enter choice [1-3] (default: 2): ").strip()
                return validate_enum_selection(
                    choice or "2",
                    Role,
                    allow_empty=True,
                    default=Role.DEVELOPER,
                )
            except ValueError as e:
                self.console.print(f"[red]{e}[/red]")

    def _prompt_user_skills(self) -> list[str]:
        """Prompt for user skills.

        Returns:
            List of validated skills (deduplicated)
        """
        while True:
            try:
                skills_input = input("Enter skills (comma-separated, optional): ").strip()
                if not skills_input:
                    return []

                # Parse and validate skills
                skills = [s.strip() for s in skills_input.split(",") if s.strip()]
                return list(set(skills))  # Deduplicate
            except ValueError as e:
                self.console.print(f"[red]{e}[/red]")

    def _prompt_team_name(self) -> str:
        """Prompt for team name.

        Returns:
            The validated team name
        """
        while True:
            try:
                name = input("Enter team name (or 'q' to cancel): ").strip()
                if name.lower() == "q":
                    raise CancelledException()

                validated = validate_required_text(name, min_length=1, max_length=100)

                # Check for duplicate name
                from ..lib.storage import get_team_store
                from ..services.team_service import TeamService

                team_service = TeamService(get_team_store())

                if team_service.name_exists(validated):
                    self.console.print(
                        f"[red]Team '{validated}' already exists. Please use a different name.[/red]"
                    )
                    continue

                return validated
            except ValueError as e:
                self.console.print(f"[red]{e}[/red]")

    def _prompt_team_members(self, users: list[User]) -> list[User]:
        """Prompt for team member selection.

        Args:
            users: List of available users

        Returns:
            List of selected users
        """
        self.console.print()
        self.console.print("Select team members (comma-separated numbers):")

        # Display users with task counts
        for idx, user in enumerate(users, 1):
            task_count = (
                self.user_service.get_active_task_count(user.id) if self.task_service else 0
            )
            skills_str = ", ".join(user.skills) if user.skills else "None"
            self.console.print(
                f"  [{idx}] {user.name} ({user_role_emoji(user.role)} {user.role}) | Tasks: {task_count} | Skills: {skills_str}"
            )

        while True:
            try:
                choice = input("Enter member numbers [e.g., 1,2,3]: ").strip()
                if not choice:
                    return []

                # Parse selection
                indices = [int(x.strip()) for x in choice.split(",")]

                # Validate indices
                selected = []
                for idx in indices:
                    if 1 <= idx <= len(users):
                        selected.append(users[idx - 1])
                    else:
                        self.console.print(
                            f"[red]Invalid selection: {idx}. Please enter numbers between 1 and {len(users)}.[/red]"
                        )
                        break
                else:
                    return selected

            except ValueError:
                self.console.print(
                    "[red]Invalid format. Please enter comma-separated numbers (e.g., 1,2,3).[/red]"
                )

    def _display_user_list(self, users: list[User]) -> None:
        """Display list of users with their details.

        Args:
            users: List of users to display
        """
        for user in users:
            task_count = (
                self.user_service.get_active_task_count(user.id) if self.task_service else 0
            )
            skills_str = ", ".join(user.skills) if user.skills else "None"

            self.console.print(
                f"[bold cyan]{user.name}[/bold cyan] ({user_role_emoji(user.role)} {user.role})"
            )
            self.console.print(f"  Tasks: {task_count} active | Skills: {skills_str}")
            self.console.print()

    def _display_team_list(self, teams: list[Team]) -> None:
        """Display list of teams with their members.

        Args:
            teams: List of teams to display
        """
        for team in teams:
            self.console.print(f"[bold cyan]{team.name}[/bold cyan]")
            if team.member_names:
                for member_name in team.member_names:
                    try:
                        user = self.user_service.get_by_name(member_name)
                        task_count = (
                            self.user_service.get_active_task_count(user.id)
                            if self.task_service
                            else 0
                        )
                        skills_str = ", ".join(user.skills) if user.skills else "None"
                        self.console.print(
                            f"  - {member_name} ({user_role_emoji(user.role)} {user.role}) | Tasks: {task_count} | Skills: {skills_str}"
                        )
                    except UserNotFoundError:
                        self.console.print(f"  - {member_name} (User not found)")
            else:
                self.console.print("  (No members)")
            self.console.print()

    def _display_resource_overview(self, users: list[User]) -> None:
        """Display resource overview with workload.

        Args:
            users: List of users to display
        """
        for user in users:
            task_count = (
                self.user_service.get_active_task_count(user.id) if self.task_service else 0
            )
            skills_str = ", ".join(user.skills) if user.skills else "None"

            # Workload indicator
            if task_count >= 5:
                workload_color = "[red]"
                workload_text = "High workload"
            elif task_count >= 3:
                workload_color = "[yellow]"
                workload_text = "Medium workload"
            else:
                workload_color = "[green]"
                workload_text = "Available"

            self.console.print(
                f"[bold]{user.name}[/bold] ({user_role_emoji(user.role)} {user.role})"
            )
            self.console.print(
                f"  Tasks: {task_count} active {workload_color}({workload_text})[/green]"
            )
            self.console.print(f"  Skills: {skills_str}")
            self.console.print()

    def _show_user_created_success(self, user: User) -> None:
        """Display success message after creating a user.

        Args:
            user: The created user
        """
        skills_str = ", ".join(user.skills) if user.skills else "None"
        message = f"""[SUCCESS] User created!

ID: {user.id}
Name: {user.name}
Role: {user_role_emoji(user.role)} {user.role}
Skills: {skills_str}

Tip: You can now assign tasks to this user."""
        render_success_panel(self.console, message)

    def _show_team_created_success(self, team: Team, members: list[User]) -> None:
        """Display success message after creating a team.

        Args:
            team: The created team
            members: List of team members
        """
        members_str = ", ".join(m.name for m in members)
        message = f"""[SUCCESS] Team created!

ID: {team.id}
Name: {team.name}
Members: {members_str}

Tip: View team details in the Resources menu."""
        render_success_panel(self.console, message)


def user_role_emoji(role: Role) -> str:
    """Get emoji for user role.

    Args:
        role: The user role

    Returns:
        Emoji string for the role
    """
    emoji_map = {
        Role.ADMIN: "👑",
        Role.DEVELOPER: "💻",
        Role.DESIGNER: "🎨",
    }
    return emoji_map.get(role, "👤")
