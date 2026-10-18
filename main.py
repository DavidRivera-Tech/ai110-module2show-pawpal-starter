from pawpal_system import Owner, Pet, Scheduler, Task


def print_tasks(title: str, tasks: list[Task]) -> None:
    print(title)
    print("=" * len(title))
    if not tasks:
        print("(no tasks)")
    for task in tasks:
        status = "[x] done" if task.completed else "[ ] pending"
        print(
            f"{task.time} | {task.pet_name:<5} | {task.description:<20} | "
            f"{task.duration_minutes:>3} min | {task.priority:<6} | "
            f"{task.frequency:<6} | {status}"
        )
    print()


def main() -> None:
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
        "Today's Schedule (sorted by time)",
        scheduler.sort_by_time(scheduler.get_todays_tasks()),
    )

    print_tasks(
        "Today's Schedule (by priority, then time)",
        scheduler.sort_by_priority(scheduler.get_todays_tasks()),
    )

    # 2. Filtering by pet (lowercase name shows case-insensitive matching)
    print_tasks(
        "Filter: Mochi's tasks",
        scheduler.sort_by_time(
            scheduler.filter_by_pet(scheduler.get_todays_tasks(), "mochi")
        ),
    )

    # 3. Conflict detection
    title = "Conflict Check"
    print(title)
    print("=" * len(title))
    conflicts = scheduler.detect_conflicts(scheduler.get_todays_tasks())
    if conflicts:
        for warning in conflicts:
            print(warning)
    else:
        print("No conflicts found.")
    print()

    # 4. Next available slot
    title = "Next Available Slot"
    print(title)
    print("=" * len(title))
    for minutes in (20, 45):
        slot = scheduler.find_next_available_slot(minutes)
        print(f"Next free {minutes}-min slot: {slot or 'none today'}")
    print()

    # 5. Recurring tasks
    title = "Recurring Task Demo"
    print(title)
    print("=" * len(title))
    walk = next(t for t in mochi.get_tasks() if t.description == "Morning walk")
    nxt = scheduler.mark_task_complete(walk)
    if nxt is None:
        print("No next occurrence")
    else:
        print(f"Completed 'Morning walk' -> next occurrence scheduled for {nxt.due_date}")
    print()

    # 6. Filtering by status
    print_tasks(
        "Filter: Pending tasks today",
        scheduler.sort_by_time(
            scheduler.filter_by_status(scheduler.get_todays_tasks(), False)
        ),
    )


if __name__ == "__main__":
    main()
