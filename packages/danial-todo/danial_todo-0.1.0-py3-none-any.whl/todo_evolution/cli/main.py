"""Main entry point for todo CLI."""
import sys
import argparse
from todo_evolution.services import TaskService
from .interactive import InteractiveCLI
from .commands import CommandCLI


def main() -> int:
    """Main entry point - routes between interactive and command modes.

    Returns:
        int: Exit code (0 = success, 1 = error)
    """
    parser = argparse.ArgumentParser(
        prog='todo',
        description='Professional todo management with beautiful TUI',
        epilog='Run without arguments to launch interactive mode'
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # todo add "title"
    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('title', help='Task title')

    # todo list
    subparsers.add_parser('list', help='List all tasks')

    # todo update <id> "new title"
    update_parser = subparsers.add_parser('update', help='Update task title')
    update_parser.add_argument('id', type=int, help='Task ID')
    update_parser.add_argument('title', help='New task title')

    # todo delete <id>
    delete_parser = subparsers.add_parser('delete', help='Delete a task')
    delete_parser.add_argument('id', type=int, help='Task ID')

    # todo complete <id>
    complete_parser = subparsers.add_parser('complete', help='Mark task complete')
    complete_parser.add_argument('id', type=int, help='Task ID')

    # todo incomplete <id>
    incomplete_parser = subparsers.add_parser('incomplete', help='Mark task incomplete')
    incomplete_parser.add_argument('id', type=int, help='Task ID')

    args = parser.parse_args()

    # Initialize service (single instance for both modes)
    service = TaskService()

    # No command = interactive mode
    if args.command is None:
        try:
            cli = InteractiveCLI(service)
            cli.run()
            return 0
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully in interactive mode
            print("\n\nGoodbye! 👋")
            return 0
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    else:
        # Command mode
        cmd_cli = CommandCLI(service)
        return cmd_cli.execute(args)


if __name__ == "__main__":
    sys.exit(main())
