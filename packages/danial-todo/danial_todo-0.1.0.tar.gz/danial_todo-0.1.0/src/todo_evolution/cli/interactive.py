"""Interactive TUI dashboard."""
import questionary
from rich.console import Console
from rich.table import Table

from todo_evolution.services import TaskService
from .utils import clear_screen, display_banner, format_status


class InteractiveCLI:
    """Interactive TUI dashboard for task management.

    Provides arrow-key navigable menu with rich-formatted output.
    This is the default mode when running `todo` without arguments.

    Attributes:
        service: TaskService instance for business logic
        console: rich.console.Console for styled output
    """

    def __init__(self, service: TaskService) -> None:
        """Initialize InteractiveCLI with a TaskService instance.

        Args:
            service: TaskService instance for business logic
        """
        self.service = service
        self.console = Console()

    def run(self) -> None:
        """Launch the interactive dashboard with main menu loop.

        Displays ASCII banner and enters menu loop until user selects Exit.
        """
        while True:
            clear_screen()
            display_banner()

            choice = self._show_main_menu()
            if choice == "Exit":
                self.console.print("\nGoodbye! 👋", style="cyan")
                break

            if choice == "Add Task":
                self._add_task()
            elif choice == "List Tasks":
                self._list_tasks()
            elif choice == "Update Task":
                self._update_task()
            elif choice == "Delete Task":
                self._delete_task()
            elif choice == "Mark Complete/Incomplete":
                self._toggle_status()

            input("\nPress Enter to continue...")

    def _show_main_menu(self) -> str:
        """Display main menu and capture user selection.

        Returns:
            str: Selected menu option
        """
        return questionary.select(
            "What would you like to do?",
            choices=[
                "Add Task",
                "List Tasks",
                "Update Task",
                "Delete Task",
                "Mark Complete/Incomplete",
                "Exit"
            ],
            style=questionary.Style([
                ("selected", "fg:cyan bold"),
                ("pointer", "fg:cyan bold"),
            ])
        ).ask()

    def _add_task(self) -> None:
        """Prompt user for task title and create new task.

        User Story 1: Interactive Dashboard Launch & First Task
        """
        self.console.print("\n[bold cyan]Add New Task[/bold cyan]")
        title = questionary.text(
            "Enter task title:",
            validate=lambda text: len(text.strip()) > 0 or "Task title cannot be empty"
        ).ask()

        if not title:  # User cancelled (Ctrl+C)
            self.console.print("Cancelled", style="yellow")
            return

        try:
            task = self.service.add_task(title)
            self.console.print(
                f"✓ Task {task.id} added successfully: '{task.title}'",
                style="green"
            )
        except ValueError as e:
            self.console.print(f"✗ Error: {e}", style="red")

    def _list_tasks(self) -> None:
        """Display all tasks in a rich-formatted table.

        User Story 1: Interactive Dashboard Launch & First Task
        """
        tasks = self.service.get_all_tasks()

        if not tasks:
            self.console.print(
                "\n[yellow]No tasks yet. Add a task to get started.[/yellow]"
            )
            return

        table = Table(title="Your Tasks", show_header=True, header_style="bold cyan")
        table.add_column("ID", justify="right", style="cyan", width=6)
        table.add_column("Title", style="white")
        table.add_column("Status", justify="center", width=10)

        for task in tasks:
            table.add_row(str(task.id), task.title, format_status(task.status))

        self.console.print()
        self.console.print(table)

    def _update_task(self) -> None:
        """Prompt user to select a task and update its title.

        User Story 3: Task Detail Editing
        """
        self._list_tasks()

        if not self.service.get_all_tasks():
            return

        self.console.print("\n[bold cyan]Update Task[/bold cyan]")
        task_id_str = questionary.text("Enter task ID to update:").ask()

        if not task_id_str:  # User cancelled
            self.console.print("Cancelled", style="yellow")
            return

        try:
            task_id = int(task_id_str)
        except ValueError:
            self.console.print("✗ Invalid ID. Please enter a number.", style="red")
            return

        task = self.service.get_by_id(task_id)
        if task is None:
            self.console.print("✗ Task not found", style="red")
            return

        self.console.print(f"Current title: [dim]{task.title}[/dim]")
        new_title = questionary.text(
            "Enter new title:",
            default=task.title,
            validate=lambda text: len(text.strip()) > 0 or "Task title cannot be empty"
        ).ask()

        if not new_title:  # User cancelled
            self.console.print("Cancelled", style="yellow")
            return

        try:
            self.service.update_task(task_id, new_title)
            self.console.print("✓ Task updated successfully", style="green")
        except ValueError as e:
            self.console.print(f"✗ Error: {e}", style="red")

    def _delete_task(self) -> None:
        """Prompt user to select a task and delete it (with confirmation).

        User Story 2: Task Lifecycle Management
        """
        self._list_tasks()

        if not self.service.get_all_tasks():
            return

        self.console.print("\n[bold cyan]Delete Task[/bold cyan]")
        task_id_str = questionary.text("Enter task ID to delete:").ask()

        if not task_id_str:  # User cancelled
            self.console.print("Cancelled", style="yellow")
            return

        try:
            task_id = int(task_id_str)
        except ValueError:
            self.console.print("✗ Invalid ID. Please enter a number.", style="red")
            return

        task = self.service.get_by_id(task_id)
        if task is None:
            self.console.print("✗ Task not found", style="red")
            return

        # Truncate long titles for confirmation prompt
        title_display = task.title[:50] + "..." if len(task.title) > 50 else task.title

        confirmed = questionary.confirm(
            f"Delete task '{title_display}'?",
            default=False
        ).ask()

        if confirmed:
            if self.service.delete_task(task_id):
                self.console.print("✓ Task deleted successfully", style="green")
            else:
                self.console.print("✗ Task not found", style="red")
        else:
            self.console.print("Deletion cancelled", style="yellow")

    def _toggle_status(self) -> None:
        """Toggle task completion status (complete ↔ incomplete).

        User Story 2: Task Lifecycle Management
        """
        self._list_tasks()

        if not self.service.get_all_tasks():
            return

        self.console.print("\n[bold cyan]Mark Complete/Incomplete[/bold cyan]")
        task_id_str = questionary.text("Enter task ID to toggle:").ask()

        if not task_id_str:  # User cancelled
            self.console.print("Cancelled", style="yellow")
            return

        try:
            task_id = int(task_id_str)
        except ValueError:
            self.console.print("✗ Invalid ID. Please enter a number.", style="red")
            return

        try:
            task = self.service.toggle_status(task_id)
            status_str = "complete" if task.status else "incomplete"
            self.console.print(f"✓ Task marked {status_str}", style="green")
        except ValueError as e:
            self.console.print(f"✗ Error: {e}", style="red")
