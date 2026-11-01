"""Initial PawPal+ class skeleton translated from the draft UML."""

from dataclasses import dataclass, field


@dataclass
class Task:
    """Represent a pet-care activity."""

    description: str
    time: str
    frequency: str = "once"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this activity complete."""
        raise NotImplementedError


@dataclass
class Pet:
    """Store a pet and its care tasks."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        raise NotImplementedError


@dataclass
class Owner:
    """Manage pets belonging to one owner."""

    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        raise NotImplementedError

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Collect each pet together with its tasks."""
        raise NotImplementedError


@dataclass
class Scheduler:
    """Organize the tasks accessible through an owner."""

    owner: Owner

    def sort_by_time(self, tasks=None) -> list[tuple[Pet, Task]]:
        """Return a chronologically sorted copy of the task entries."""
        raise NotImplementedError
