from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from itertools import combinations

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


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

    def to_dict(self) -> dict:
        """Return a JSON-serializable dict of this task, with due_date as an ISO string."""
        return {
            "description": self.description,
            "time": self.time,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "frequency": self.frequency,
            "due_date": self.due_date.isoformat(),
            "completed": self.completed,
            "pet_name": self.pet_name,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        """Build a task from a dict produced by to_dict."""
        return cls(
            description=data["description"],
            time=data["time"],
            duration_minutes=data["duration_minutes"],
            priority=data["priority"],
            frequency=data["frequency"],
            due_date=date.fromisoformat(data["due_date"]),
            completed=data["completed"],
            pet_name=data.get("pet_name", ""),
        )


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

    def to_dict(self) -> dict:
        """Return a JSON-serializable dict of this pet and its tasks."""
        return {
            "name": self.name,
            "species": self.species,
            "tasks": [t.to_dict() for t in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Pet:
        """Build a pet and its tasks from a dict produced by to_dict."""
        pet = cls(name=data["name"], species=data["species"])
        for task_data in data.get("tasks", []):
            pet.add_task(Task.from_dict(task_data))
        return pet


@dataclass
class Owner:
    """A pet owner who manages one or more pets."""

    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_pet(self, name: str) -> Pet | None:
        """Return the pet whose name matches (case-insensitive), or None if there is no match."""
        for pet in self.pets:
            if pet.name.strip().casefold() == name.strip().casefold():
                return pet
        return None

    def get_all_tasks(self) -> list[Task]:
        """Return a single combined list of every task across all pets."""
        return [task for pet in self.pets for task in pet.tasks]

    def to_dict(self) -> dict:
        """Return a JSON-serializable dict of this owner and all pets."""
        return {"name": self.name, "pets": [p.to_dict() for p in self.pets]}

    @classmethod
    def from_dict(cls, data: dict) -> Owner:
        """Build an owner with pets and tasks from a dict produced by to_dict."""
        owner = cls(name=data["name"])
        for pet_data in data.get("pets", []):
            owner.add_pet(Pet.from_dict(pet_data))
        return owner

    def save_to_json(self, path: str = "data.json") -> None:
        """Write this owner's data to a JSON file at the given path."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_json(cls, path: str = "data.json") -> Owner | None:
        """Load an owner from a JSON file, returning None if the file does not exist."""
        if not os.path.exists(path):
            return None
        with open(path, encoding="utf-8") as f:
            return cls.from_dict(json.load(f))


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

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return a new list sorted high priority first, then by earliest time within each priority."""
        return sorted(
            tasks, key=lambda t: (PRIORITY_RANK.get(t.priority, 3), time_to_minutes(t.time))
        )

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

    def find_next_available_slot(
        self,
        duration_minutes: int,
        day: date | None = None,
        start: str = "07:00",
        end: str = "22:00",
    ) -> str | None:
        """Return the earliest HH:MM at or after start where a pending-task-free block fits by end, else None."""
        if duration_minutes < 1:
            raise ValueError(f"duration_minutes must be at least 1, got {duration_minutes}")
        limit = time_to_minutes(end)
        busy = sorted(
            (time_to_minutes(t.time), time_to_minutes(t.time) + t.duration_minutes)
            for t in self.get_todays_tasks(day)
            if not t.completed
        )
        candidate = time_to_minutes(start)
        for busy_start, busy_end in busy:
            if busy_start >= candidate + duration_minutes:
                break
            if busy_end > candidate:
                candidate = busy_end
        if candidate + duration_minutes > limit:
            return None
        return f"{candidate // 60:02d}:{candidate % 60:02d}"

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
