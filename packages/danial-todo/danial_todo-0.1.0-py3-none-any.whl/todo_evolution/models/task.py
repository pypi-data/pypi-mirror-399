"""Task entity model."""
from dataclasses import dataclass


@dataclass
class Task:
    """Represents a single todo item.

    Attributes:
        id: Unique auto-incrementing identifier
        title: User-provided task description (1-500 chars)
        status: Completion state (False=incomplete, True=complete)
    """

    id: int
    title: str
    status: bool = False
