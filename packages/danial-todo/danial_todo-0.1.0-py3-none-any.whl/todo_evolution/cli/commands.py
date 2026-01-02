"""Command-line power user mode."""
import argparse
from rich.console import Console
from rich.table import Table

from todo_evolution.services import TaskService
from .utils import format_status


class CommandCLI:
    """Command-line power user mode for task operations.

    Executes operations immediately based on arguments and exits.
    Activated when `todo` is run with arguments (e.g., `todo add "Task"`).

    Attributes:
        service: TaskService instance for business logic
        console: rich.console.Console for styled output
    """

    def __init__(self, service: TaskService) -> None:
        """Initialize CommandCLI with a TaskService instance.

        Args:
            service: TaskService instance for business logic
        """
        self.service = service
        self.console = Console()

    def execute(self, args: argparse.Namespace) -> int:
        """Execute command based on parsed arguments and return exit code.

        Args:
            args: Parsed command-line arguments from argparse

        Returns:
            int: Exit code (0 = success, 1 = error)
        """
        try:
            if args.command == "add":
                return self._cmd_add(args)
            elif args.command == "list":
                return self._cmd_list()
            elif args.command == "update":
                return self._cmd_update(args)
            elif args.command == "delete":
                return self._cmd_delete(args)
            elif args.command == "complete":
                return self._cmd_complete(args)
            elif args.command == "incomplete":
                return self._cmd_incomplete(args)
            else:
                self.console.print(f"✗ Unknown command: {args.command}", style="red")
                return 1

        except ValueError as e:
            self.console.print(f"✗ Error: {e}", style="red")
            return 1
        except Exception as e:
            self.console.print(f"✗ Unexpected error: {e}", style="red")
            return 1

    def _cmd_add(self, args: argparse.Namespace) -> int:
        """Add a new task.

        Args:
            args: Parsed arguments with 'title' attribute

        Returns:
            int: 0 for success, 1 for error
        """
        task = self.service.add_task(args.title)
        self.console.print(
            f"✓ Task {task.id} added: {task.title}",
            style="green"
        )
        return 0

    def _cmd_list(self) -> int:
        """List all tasks in a formatted table.

        Returns:
            int: Always returns 0
        """
        tasks = self.service.get_all_tasks()

        if not tasks:
            self.console.print("No tasks yet.", style="yellow")
            return 0

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("ID", justify="right", style="cyan", width=6)
        table.add_column("Title", style="white")
        table.add_column("Status", justify="center", width=10)

        for task in tasks:
            table.add_row(str(task.id), task.title, format_status(task.status))

        self.console.print(table)
        return 0

    def _cmd_update(self, args: argparse.Namespace) -> int:
        """Update a task's title.

        Args:
            args: Parsed arguments with 'id' and 'title' attributes

        Returns:
            int: 0 for success, 1 for error
        """
        self.service.update_task(args.id, args.title)
        self.console.print(f"✓ Task {args.id} updated", style="green")
        return 0

    def _cmd_delete(self, args: argparse.Namespace) -> int:
        """Delete a task.

        Args:
            args: Parsed arguments with 'id' attribute

        Returns:
            int: 0 for success, 1 for error
        """
        if self.service.delete_task(args.id):
            self.console.print(f"✓ Task {args.id} deleted", style="green")
            return 0
        else:
            self.console.print("✗ Error: Task not found", style="red")
            return 1

    def _cmd_complete(self, args: argparse.Namespace) -> int:
        """Mark a task as complete.

        Args:
            args: Parsed arguments with 'id' attribute

        Returns:
            int: 0 for success, 1 for error
        """
        task = self.service.get_by_id(args.id)
        if task is None:
            self.console.print("✗ Error: Task not found", style="red")
            return 1

        # Only toggle if not already complete
        if not task.status:
            self.service.toggle_status(args.id)

        self.console.print(f"✓ Task {args.id} marked complete", style="green")
        return 0

    def _cmd_incomplete(self, args: argparse.Namespace) -> int:
        """Mark a task as incomplete.

        Args:
            args: Parsed arguments with 'id' attribute

        Returns:
            int: 0 for success, 1 for error
        """
        task = self.service.get_by_id(args.id)
        if task is None:
            self.console.print("✗ Error: Task not found", style="red")
            return 1

        # Only toggle if not already incomplete
        if task.status:
            self.service.toggle_status(args.id)

        self.console.print(f"✓ Task {args.id} marked incomplete", style="green")
        return 0
