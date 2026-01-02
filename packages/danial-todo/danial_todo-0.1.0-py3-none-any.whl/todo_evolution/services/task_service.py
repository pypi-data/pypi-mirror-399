"""Task management service."""
from todo_evolution.models import Task


class TaskService:
    """Manages CRUD operations for Task entities with in-memory storage.

    This service is the single source of truth for task state. It provides
    thread-unsafe, in-memory task management suitable for single-user CLI usage.

    Attributes:
        _tasks: Internal list of Task objects (ordered by creation)
        _next_id: Counter for auto-incrementing task IDs
    """

    def __init__(self) -> None:
        """Initialize empty task service."""
        self._tasks: list[Task] = []
        self._next_id: int = 1

    def add_task(self, title: str) -> Task:
        """Create a new task with auto-assigned ID.

        Args:
            title: Task description, non-empty string

        Returns:
            Task: Created task with auto-assigned ID and status=False

        Raises:
            ValueError: If title is empty or whitespace-only
        """
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")

        task = Task(id=self._next_id, title=title, status=False)
        self._tasks.append(task)
        self._next_id += 1
        return task

    def get_all_tasks(self) -> list[Task]:
        """Retrieve all tasks in creation order.

        Returns:
            list[Task]: Shallow copy of internal task list (may be empty)
        """
        return self._tasks.copy()

    def get_by_id(self, task_id: int) -> Task | None:
        """Retrieve a specific task by ID.

        Args:
            task_id: Task identifier

        Returns:
            Task | None: Task object if found, None otherwise
        """
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None

    def update_task(self, task_id: int, new_title: str) -> Task:
        """Update the title of an existing task.

        Args:
            task_id: Task identifier
            new_title: New task description, non-empty string

        Returns:
            Task: Updated task object

        Raises:
            ValueError: If task not found or new_title is empty
        """
        task = self.get_by_id(task_id)
        if task is None:
            raise ValueError("Task not found")
        if not new_title or not new_title.strip():
            raise ValueError("Task title cannot be empty")

        task.title = new_title
        return task

    def delete_task(self, task_id: int) -> bool:
        """Remove a task from the collection.

        Args:
            task_id: Task identifier

        Returns:
            bool: True if deleted, False if task not found
        """
        task = self.get_by_id(task_id)
        if task is None:
            return False

        self._tasks.remove(task)
        return True

    def toggle_status(self, task_id: int) -> Task:
        """Toggle task completion status (complete ↔ incomplete).

        Args:
            task_id: Task identifier

        Returns:
            Task: Updated task with toggled status

        Raises:
            ValueError: If task not found
        """
        task = self.get_by_id(task_id)
        if task is None:
            raise ValueError("Task not found")

        task.status = not task.status
        return task
