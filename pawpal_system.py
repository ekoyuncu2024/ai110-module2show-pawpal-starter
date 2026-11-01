"""PawPal+ domain classes, independent of the interface."""
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from uuid import uuid4


@dataclass
class Task:
    """A dated activity with a 24-hour HH:MM time."""
    description: str
    time: str
    frequency: str = "once"
    due_date: date = field(default_factory=date.today)
    completed: bool = False
    task_id: str = field(default_factory=lambda: uuid4().hex, init=False)

    def __post_init__(self):
        """Validate and normalize user inputs."""
        self.description = self.description.strip()
        if not self.description:
            raise ValueError("Task description is required.")
        try:
            parsed = datetime.strptime(self.time, "%H:%M")
        except (ValueError, TypeError):
            raise ValueError("Time must use 24-hour HH:MM format.") from None
        if parsed.strftime("%H:%M") != self.time:
            raise ValueError("Time must use 24-hour HH:MM format.")
        self.frequency = self.frequency.strip().lower()
        if self.frequency not in {"once", "daily", "weekly"}:
            raise ValueError("Frequency must be once, daily, or weekly.")
        if type(self.due_date) is not date:
            raise ValueError("Due date must be a datetime.date.")

    def mark_complete(self):
        """Set status; use Scheduler.mark_task_complete for recurrence."""
        self.completed = True

    def next_occurrence(self, completed_on: date):
        """Create a successor one day or week after the completion day."""
        days = {"daily": 1, "weekly": 7}.get(self.frequency)
        if days is None:
            return None
        return Task(self.description, self.time, self.frequency,
                    completed_on + timedelta(days=days))


@dataclass
class Pet:
    """Store pet details and an independent task list."""
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def __post_init__(self):
        """Require a name and species."""
        self.name, self.species = self.name.strip(), self.species.strip()
        if not self.name or not self.species:
            raise ValueError("Pet name and species are required.")

    def add_task(self, task: Task):
        """Attach a task once to this pet."""
        if any(t.task_id == task.task_id for t in self.tasks):
            raise ValueError("This task is already assigned to the pet.")
        self.tasks.append(task)


@dataclass
class Owner:
    """Manage one owner's pets and expose their tasks."""
    name: str
    pets: list[Pet] = field(default_factory=list)

    def __post_init__(self):
        """Require a nonempty owner name."""
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("Owner name is required.")

    def add_pet(self, pet: Pet):
        """Register a unique case-insensitive pet name."""
        if any(p.name.casefold() == pet.name.casefold() for p in self.pets):
            raise ValueError("A pet with this name already exists.")
        self.pets.append(pet)

    def get_pet(self, name: str):
        """Find a pet by case-insensitive name."""
        for pet in self.pets:
            if pet.name.casefold() == name.strip().casefold():
                return pet
        raise ValueError(f"Unknown pet: {name}")

    def get_all_tasks(self):
        """Return pet-task pairs, retaining each task's pet identity."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


@dataclass
class Scheduler:
    """Organize and manage tasks across an owner's pets."""
    owner: Owner

    def schedule_task(self, pet_name: str, task: Task):
        """Assign a new task to a registered pet."""
        if any(t.task_id == task.task_id for _, t in self.owner.get_all_tasks()):
            raise ValueError("This task is already assigned.")
        self.owner.get_pet(pet_name).add_task(task)

    def sort_by_time(self, tasks=None):
        """Return a stable sorted copy ordered by date then HH:MM time."""
        entries = self.owner.get_all_tasks() if tasks is None else tasks
        return sorted(entries, key=lambda entry: (entry[1].due_date, entry[1].time))

    def filter_tasks(self, pet_name=None, completed=None, on_date=None):
        """Combine optional pet, status, and date filters."""
        return [(p, t) for p, t in self.owner.get_all_tasks()
                if (pet_name is None or p.name.casefold() == pet_name.strip().casefold())
                and (completed is None or t.completed == completed)
                and (on_date is None or t.due_date == on_date)]

    def get_schedule(self, pet_name=None, completed=None, on_date=None):
        """Return filtered tasks in chronological order."""
        return self.sort_by_time(self.filter_tasks(pet_name, completed, on_date))

    def mark_task_complete(self, task_id: str, completed_on: date | None = None):
        """Complete once and append at most one recurring successor."""
        for pet, task in self.owner.get_all_tasks():
            if task.task_id == task_id:
                if task.completed:
                    return None
                successor = task.next_occurrence(completed_on or date.today())
                if successor is not None:
                    pet.add_task(successor)
                task.mark_complete()
                return successor
        raise ValueError("Unknown task ID.")

    def detect_conflicts(self, on_date: date | None = None):
        """Warn about pending tasks sharing an exact date and time."""
        groups = {}
        for pet, task in self.get_schedule(completed=False, on_date=on_date):
            groups.setdefault((task.due_date, task.time), []).append(
                f"{pet.name}: {task.description}")
        return [f"Conflict on {day.isoformat()} at {time}: " + "; ".join(labels)
                for (day, time), labels in groups.items() if len(labels) > 1]
