import os
import sys
import tempfile

from tabulate import tabulate

from pawpal_system import Owner, Pet, Scheduler, Task

USE_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ

PRIORITY_COLORS = {"high": "31", "medium": "33", "low": "32"}


def color(text: str, code: str) -> str:
    """Wrap text in the ANSI color code when color is enabled, else return it unchanged."""
    return f"[{code}m{text}[0m" if USE_COLOR else text


def task_emoji(description: str) -> str:
    """Return an emoji matching keywords in the task description, defaulting to a paw."""
    d = description.lower()
    if "walk" in d or "fetch" in d:
        return "🐕"
    if any(k in d for k in ("feed", "breakfast", "dinner", "food")):
        return "🍖"
    if "pill" in d or "med" in d:
        return "💊"
    if any(k in d for k in ("brush", "groom", "bath")):
        return "🧼"
    if "play" in d:
        return "🎾"
    return "🐾"


def print_title(title: str) -> None:
    """Print a section title in bold."""
    print(color(title, "1"))


def print_tasks(title: str, tasks: list[Task]) -> None:
    """Print a titled table of tasks, or "(no tasks)" if the list is empty."""
    print_title(title)
    if not tasks:
        print("(no tasks)")
    else:
        rows = [
            [
                t.time,
                t.pet_name,
                f"{task_emoji(t.description)} {t.description}",
                f"{t.duration_minutes} min",
                color(t.priority, PRIORITY_COLORS.get(t.priority, "0")),
                t.frequency,
                "✅ done" if t.completed else "⏳ pending",
            ]
            for t in tasks
        ]
        headers = ["Time", "Pet", "Task", "Duration", "Priority", "Freq", "Status"]
        print(tabulate(rows, headers=headers, tablefmt="rounded_outline"))
    print()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    owner = Owner(name="David")

    mochi = Pet(name="Mochi", species="dog")
    luna = Pet(name="Luna", species="cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Added deliberately out of order
    luna.add_task(Task("Play session", "18:00", 20, "low", "weekly"))
    mochi.add_task(Task("Give heartworm pill", "12:00", 5, "high", "once"))
    mochi.add_task(Task("Morning walk", "07:30", 30, "high", "daily"))
    luna.add_task(Task("Breakfast", "07:45", 10, "high", "daily"))
    luna.add_task(Task("Brush coat", "12:00", 5, "medium", "once"))
    mochi.add_task(Task("Fetch in the yard", "06:45", 15, "low", "once"))

    scheduler = Scheduler(owner)

    # 1. Sorting
    print_tasks(
        "📅 Today's Schedule (sorted by time)",
        scheduler.sort_by_time(scheduler.get_todays_tasks()),
    )

    print_tasks(
        "⭐ Today's Schedule (by priority, then time)",
        scheduler.sort_by_priority(scheduler.get_todays_tasks()),
    )

    # 2. Filtering by pet (lowercase name shows case-insensitive matching)
    print_tasks(
        "🐶 Filter: Mochi's tasks",
        scheduler.sort_by_time(
            scheduler.filter_by_pet(scheduler.get_todays_tasks(), "mochi")
        ),
    )

    # 3. Conflict detection
    title = "🚨 Conflict Check"
    print_title(title)
    conflicts = scheduler.detect_conflicts(scheduler.get_todays_tasks())
    if conflicts:
        for warning in conflicts:
            print(color(warning, "33"))
    else:
        print("No conflicts found.")
    print()

    # 4. Next available slot
    title = "🔎 Next Available Slot"
    print_title(title)
    for minutes in (20, 45):
        slot = scheduler.find_next_available_slot(minutes)
        print(f"Next free {minutes}-min slot: {slot or 'none today'}")
    print()

    # 5. Recurring tasks
    title = "🔁 Recurring Task Demo"
    print_title(title)
    walk = next(t for t in mochi.get_tasks() if t.description == "Morning walk")
    nxt = scheduler.mark_task_complete(walk)
    if nxt is None:
        print("No next occurrence")
    else:
        print(f"Completed 'Morning walk' -> next occurrence scheduled for {nxt.due_date}")
    print()

    # 6. Filtering by status
    print_tasks(
        "📋 Filter: Pending tasks today",
        scheduler.sort_by_time(
            scheduler.filter_by_status(scheduler.get_todays_tasks(), False)
        ),
    )

    # 6b. Completed tasks
    print_tasks(
        "✅ Filter: Completed tasks today",
        scheduler.sort_by_time(
            scheduler.filter_by_status(scheduler.get_todays_tasks(), True)
        ),
    )

    # 7. Persistence
    title = "💾 Persistence Demo"
    print_title(title)
    path = os.path.join(tempfile.gettempdir(), "pawpal_demo.json")
    owner.save_to_json(path)
    loaded = Owner.load_from_json(path)
    os.remove(path)
    print(
        f"Saved and reloaded {loaded.name}: {len(loaded.pets)} pets, "
        f"{len(loaded.get_all_tasks())} tasks"
    )


if __name__ == "__main__":
    main()
