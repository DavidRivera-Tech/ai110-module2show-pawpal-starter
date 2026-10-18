from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from itertools import combinations


def time_to_minutes(hhmm: str) -> int:
    """Parse an "HH:MM" string and return minutes since midnight, raising ValueError if invalid."""
    parts = str(hhmm).strip().split(":")
    if len(parts) != 2 or not all(p.isascii() and p.isdigit() for p in parts):
        raise ValueError(f"Invalid time {hhmm!r}; expected HH:MM")
    hours, minutes = int(parts[0]), int(parts[1])
    if hours > 23 or minutes > 59:
        raise ValueError(f"Invalid time {hhmm!r}; hour must be 0-23 and minute 0-59")
    return hours * 60 + minutes


@dataclass(eq=False)
class Task:
    """A single pet care task with timing, priority, and recurrence details."""

    description: str
    time: str
    duration_minutes: int = 15
    priority: str = "medium"
    frequency: str = "once"
    due_date: date = field(default_factory=date.today)
    completed: bool = False
    pet_name: str = ""

    def __post_init__(self) -> None:
        """Validate and normalize time to HH:MM and lowercase priority and frequency."""
        if self.duration_minutes < 1:
            raise ValueError(f"duration_minutes must be at least 1, got {self.duration_minutes}")
        minutes = time_to_minutes(self.time)
        self.time = f"{minutes // 60:02d}:{minutes % 60:02d}"
        self.priority = self.priority.strip().lower()
        self.frequency = self.frequency.strip().lower()

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def next_occurrence(self) -> Task | None:
        """Return a new task for the next daily/weekly occurrence, or None if the task is one-time."""
        if self.frequency == "daily":
            days = 1
        elif self.frequency == "weekly":
            days = 7
        else:
            return None
        return replace(self, due_date=self.due_date + timedelta(days=days), completed=False)


@dataclass
class Pet:
    """A pet and the list of care tasks assigned to it."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Assign a task to this pet and set the task's pet_name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove the exact task object from this pet, doing nothing if it is absent."""
        for i, existing in enumerate(self.tasks):
            if existing is task:
                del self.tasks[i]
                return

    def get_tasks(self) -> list[Task]:
        """Return a copy of this pet's task list."""
        return list(self.tasks)


@dataclass
class Owner:
    """A pet owner who manages one or more pets."""

    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_pet(self, name: str) -> Pet | None:
        """Return the pet with the given name, or None if there is no match."""
        for pet in self.pets:
            if pet.name.strip().casefold() == name.strip().casefold():
                return pet
        return None

    def get_all_tasks(self) -> list[Task]:
        """Return a single combined list of every task across all pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Builds and manages schedules from all of an owner's pets' tasks."""

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler for the given owner."""
        self.owner = owner

    def get_todays_tasks(self, today: date | None = None) -> list[Task]:
        """Return all of the owner's tasks due on the given date (default: today)."""
        if today is None:
            today = date.today()
        return [t for t in self.owner.get_all_tasks() if t.due_date == today]

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return a new list of tasks sorted by time (HH:MM), earliest first."""
        return sorted(tasks, key=lambda t: time_to_minutes(t.time))

    def filter_by_pet(self, tasks: list[Task], pet_name: str) -> list[Task]:
        """Return only the tasks belonging to the named pet, ignoring case and surrounding spaces."""
        target = pet_name.strip().casefold()
        return [t for t in tasks if t.pet_name.strip().casefold() == target]

    def filter_by_status(self, tasks: list[Task], completed: bool) -> list[Task]:
        """Return only the tasks whose completed status matches the given value."""
        return [t for t in tasks if t.completed == completed]

    def mark_task_complete(self, task: Task) -> Task | None:
        """Complete a task and return its newly scheduled next occurrence, or None if there is none."""
        if task.completed:
            return None
        task.mark_complete()
        nxt = task.next_occurrence()
        if nxt is None:
            return None
        pet = self.owner.get_pet(task.pet_name)
        if pet is None:
            return None
        pet.add_task(nxt)
        return nxt

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """Return warning messages for pending same-day tasks whose time ranges overlap."""
        warnings: list[str] = []
        ranges: list[tuple[Task, int, int]] = []
        for t in self.sort_by_time(tasks):
            if t.completed:
                continue
            start = time_to_minutes(t.time)
            ranges.append((t, start, start + t.duration_minutes))

        for (a, start_a, end_a), (b, start_b, end_b) in combinations(ranges, 2):
            if a.due_date != b.due_date:
                continue
            if start_a < end_b and start_b < end_a:
                warnings.append(
                    f"WARNING: {a.pet_name}'s '{a.description}' "
                    f"({a.time}, {a.duration_minutes} min) overlaps "
                    f"{b.pet_name}'s '{b.description}' "
                    f"({b.time}, {b.duration_minutes} min)"
                )
        return warnings
