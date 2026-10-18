from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


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

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def next_occurrence(self) -> Task | None:
        """Return a new task for the next daily/weekly occurrence, or None if the task is one-time."""
        # Implemented in Phase 4
        pass


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
            if pet.name == name:
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
        """Return tasks sorted by time (HH:MM), earliest first."""
        # Implemented in Phase 4
        pass

    def filter_by_pet(self, tasks: list[Task], pet_name: str) -> list[Task]:
        """Return only the tasks that belong to the pet with the given name."""
        # Implemented in Phase 4
        pass

    def filter_by_status(self, tasks: list[Task], completed: bool) -> list[Task]:
        """Return only the tasks whose completed status matches the given value."""
        # Implemented in Phase 4
        pass

    def mark_task_complete(self, task: Task) -> Task | None:
        """Mark a task complete and, in Phase 4, return its next recurrence if any."""
        # Recurrence handled in Phase 4
        task.mark_complete()
        return None

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """Return warning messages for tasks whose time slots overlap."""
        # Implemented in Phase 4
        pass
