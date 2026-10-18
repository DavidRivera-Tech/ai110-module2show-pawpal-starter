from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner(name="David")

    mochi = Pet(name="Mochi", species="dog")
    luna = Pet(name="Luna", species="cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(Task("Morning walk", "07:30", 30, "high", "daily"))
    luna.add_task(Task("Breakfast", "08:00", 10, "high", "daily"))
    mochi.add_task(Task("Give heartworm pill", "12:00", 5, "high", "once"))
    luna.add_task(Task("Play session", "18:00", 20, "low", "weekly"))

    scheduler = Scheduler(owner)
    tasks = scheduler.get_todays_tasks()

    header = f"Today's Schedule - {date.today()}"
    print(header)
    print("=" * len(header))

    for task in tasks:
        status = "[x] done" if task.completed else "[ ] pending"
        print(
            f"{task.time} | {task.pet_name:<5} | {task.description:<20} | "
            f"{task.duration_minutes:>3} min | {task.priority:<6} | "
            f"{task.frequency:<6} | {status}"
        )


if __name__ == "__main__":
    main()
