from datetime import date

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task

D = date(2026, 10, 18)


def make_owner():
    """Build an owner with two empty pets (Mochi and Whiskers) and a scheduler."""
    owner = Owner("Sam")
    mochi = Pet("Mochi", "dog")
    whiskers = Pet("Whiskers", "cat")
    owner.add_pet(mochi)
    owner.add_pet(whiskers)
    return owner, mochi, whiskers, Scheduler(owner)


def test_mark_complete_changes_status():
    """mark_complete flips a new task's completed flag from False to True."""
    task = Task("Morning walk", "07:30")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """add_task appends the task to the pet and stamps it with the pet's name."""
    pet = Pet("Mochi", "dog")
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task("Morning walk", "07:30"))
    assert len(pet.get_tasks()) == 1
    assert pet.get_tasks()[0].pet_name == "Mochi"


def test_sort_by_time_chronological_order():
    """Out-of-order tasks sort earliest first, numerically, without mutating the input."""
    _, _, _, scheduler = make_owner()
    late = Task("Dinner", "18:00", due_date=D)
    morning = Task("Walk", "9:00", due_date=D)
    mid = Task("Meds", "10:00", due_date=D)
    tasks = [late, mid, morning]

    result = scheduler.sort_by_time(tasks)

    assert result == [morning, mid, late]
    assert tasks == [late, mid, morning]
    assert scheduler.sort_by_time([]) == []


def test_daily_task_completion_creates_next_day_task():
    """Completing a daily task adds a pending copy due the next day to the same pet."""
    _, mochi, _, scheduler = make_owner()
    task = Task("Feed", "08:00", frequency="daily", due_date=D)
    mochi.add_task(task)

    nxt = scheduler.mark_task_complete(task)

    assert task.completed is True
    assert nxt is not None
    assert nxt.due_date == date(2026, 10, 19)
    assert nxt.completed is False
    assert nxt.pet_name == "Mochi"
    assert nxt in mochi.get_tasks()
    assert len(mochi.get_tasks()) == 2


def test_weekly_recurrence_and_once_returns_none():
    """A weekly task recurs 7 days later, while a once task creates no follow-up."""
    _, mochi, _, scheduler = make_owner()
    weekly = Task("Bath", "10:00", frequency="weekly", due_date=D)
    once = Task("Vet visit", "11:00", frequency="once", due_date=D)
    mochi.add_task(weekly)
    mochi.add_task(once)

    weekly_next = scheduler.mark_task_complete(weekly)
    once_next = scheduler.mark_task_complete(once)

    assert weekly_next is not None
    assert weekly_next.due_date == date(2026, 10, 25)
    assert once_next is None
    assert len(mochi.get_tasks()) == 3


def test_double_complete_does_not_duplicate_recurrence():
    """Completing the same recurring task twice schedules only one follow-up."""
    _, mochi, _, scheduler = make_owner()
    task = Task("Feed", "08:00", frequency="daily", due_date=D)
    mochi.add_task(task)

    first = scheduler.mark_task_complete(task)
    second = scheduler.mark_task_complete(task)

    assert first is not None
    assert second is None
    assert len(mochi.get_tasks()) == 2


def test_recurrence_across_month_and_year_boundary():
    """Daily and weekly recurrence roll over month, year, and leap-day boundaries correctly."""
    _, mochi, _, scheduler = make_owner()
    new_year = Task("Feed", "08:00", frequency="daily", due_date=date(2026, 12, 31))
    month_end = Task("Bath", "10:00", frequency="weekly", due_date=date(2026, 2, 25))
    leap_day = Task("Walk", "07:00", frequency="daily", due_date=date(2028, 2, 28))
    for task in (new_year, month_end, leap_day):
        mochi.add_task(task)

    assert scheduler.mark_task_complete(new_year).due_date == date(2027, 1, 1)
    assert scheduler.mark_task_complete(month_end).due_date == date(2026, 3, 4)
    assert scheduler.mark_task_complete(leap_day).due_date == date(2028, 2, 29)


def test_detect_conflicts_flags_overlapping_tasks():
    """Two overlapping same-day tasks produce exactly one warning naming both pets."""
    _, mochi, whiskers, scheduler = make_owner()
    mochi.add_task(Task("Walk", "09:00", duration_minutes=30, due_date=D))
    whiskers.add_task(Task("Groom", "09:15", duration_minutes=30, due_date=D))

    warnings = scheduler.detect_conflicts(scheduler.get_todays_tasks(today=D))

    assert len(warnings) == 1
    assert "Mochi" in warnings[0]
    assert "Whiskers" in warnings[0]


def test_detect_conflicts_boundaries():
    """Back-to-back tasks don't conflict, but identical starts and nested tasks do."""
    _, _, _, scheduler = make_owner()

    back_to_back = [
        Task("A", "09:00", duration_minutes=30, due_date=D, pet_name="Mochi"),
        Task("B", "09:30", duration_minutes=30, due_date=D, pet_name="Mochi"),
    ]
    same_start = [
        Task("A", "09:00", duration_minutes=30, due_date=D, pet_name="Mochi"),
        Task("B", "09:00", duration_minutes=15, due_date=D, pet_name="Whiskers"),
    ]
    nested = [
        Task("A", "09:00", duration_minutes=60, due_date=D, pet_name="Mochi"),
        Task("B", "09:15", duration_minutes=10, due_date=D, pet_name="Whiskers"),
    ]

    assert scheduler.detect_conflicts(back_to_back) == []
    assert len(scheduler.detect_conflicts(same_start)) == 1
    assert len(scheduler.detect_conflicts(nested)) == 1


def test_detect_conflicts_ignores_completed_and_other_dates():
    """Completed tasks and tasks due on a different day never cause conflict warnings."""
    _, _, _, scheduler = make_owner()
    pending = Task("Walk", "09:00", duration_minutes=30, due_date=D, pet_name="Mochi")
    done = Task("Groom", "09:00", duration_minutes=30, due_date=D, pet_name="Whiskers")
    done.mark_complete()
    other_day = Task("Bath", "09:00", duration_minutes=30, due_date=date(2026, 10, 19), pet_name="Whiskers")

    assert scheduler.detect_conflicts([pending, done]) == []
    assert scheduler.detect_conflicts([pending, other_day]) == []


def test_filter_by_pet_and_status():
    """filter_by_pet ignores case and spaces and returns [] for unknown pets; filter_by_status splits done from pending."""
    _, mochi, whiskers, scheduler = make_owner()
    walk = Task("Walk", "09:00", due_date=D)
    feed = Task("Feed", "08:00", due_date=D)
    litter = Task("Litter", "10:00", due_date=D)
    mochi.add_task(walk)
    mochi.add_task(feed)
    whiskers.add_task(litter)
    feed.mark_complete()
    tasks = scheduler.get_todays_tasks(today=D)

    assert scheduler.filter_by_pet(tasks, "  mochi ") == [walk, feed]
    assert scheduler.filter_by_pet(tasks, "Rex") == []
    assert scheduler.filter_by_status(tasks, completed=True) == [feed]
    assert scheduler.filter_by_status(tasks, completed=False) == [walk, litter]


def test_invalid_time_rejected_and_normalized():
    """Malformed times and non-positive durations raise ValueError, and H:MM is normalized to HH:MM."""
    for bad_time in ("25:00", "12:60", "7:3x", "0730", ""):
        with pytest.raises(ValueError):
            Task("x", bad_time, due_date=D)
    with pytest.raises(ValueError):
        Task("x", "10:00", duration_minutes=0, due_date=D)

    assert Task("x", "7:30", due_date=D).time == "07:30"


def test_pet_with_no_tasks():
    """An owner whose only pet has no tasks yields no tasks today and no conflicts."""
    owner = Owner("Sam")
    owner.add_pet(Pet("Mochi", "dog"))
    scheduler = Scheduler(owner)

    assert scheduler.get_todays_tasks(today=D) == []
    assert scheduler.detect_conflicts(scheduler.get_todays_tasks(today=D)) == []


def test_scheduler_gets_tasks_from_all_pets():
    """get_todays_tasks combines due-today tasks from every pet."""
    _, mochi, whiskers, scheduler = make_owner()
    mochi.add_task(Task("Walk", "09:00", due_date=D))
    whiskers.add_task(Task("Groom", "10:00", due_date=D))

    tasks = scheduler.get_todays_tasks(today=D)

    assert len(tasks) == 2
    assert {t.pet_name for t in tasks} == {"Mochi", "Whiskers"}


def test_sort_by_priority_then_time():
    """sort_by_priority orders high before medium before low, earliest first within a priority, without mutating input."""
    _, _, _, scheduler = make_owner()
    low = Task("Play", "07:00", priority="low", due_date=D)
    high_late = Task("Pill", "12:00", priority="high", due_date=D)
    medium = Task("Brush", "09:00", priority="medium", due_date=D)
    high_early = Task("Walk", "08:00", priority="high", due_date=D)
    tasks = [low, high_late, medium, high_early]

    result = scheduler.sort_by_priority(tasks)

    assert result == [high_early, high_late, medium, low]
    assert tasks == [low, high_late, medium, high_early]


def test_next_slot_empty_day_returns_start():
    """With no tasks, the slot is the requested start time."""
    _, _, _, scheduler = make_owner()

    assert scheduler.find_next_available_slot(30, day=D) == "07:00"
    assert scheduler.find_next_available_slot(30, day=D, start="09:15") == "09:15"


def test_next_slot_finds_gap_between_tasks_on_different_pets():
    """A gap between tasks belonging to different pets is found, allowing back-to-back placement."""
    _, mochi, whiskers, scheduler = make_owner()
    mochi.add_task(Task("Walk", "07:00", 60, due_date=D))
    whiskers.add_task(Task("Play", "09:00", 30, due_date=D))

    assert scheduler.find_next_available_slot(60, day=D) == "08:00"
    assert scheduler.find_next_available_slot(61, day=D) == "09:30"


def test_next_slot_skips_overlapping_tasks_to_first_real_gap():
    """Overlapping tasks form one busy block; the slot starts after the latest end."""
    _, mochi, whiskers, scheduler = make_owner()
    mochi.add_task(Task("Walk", "07:00", 60, due_date=D))
    whiskers.add_task(Task("Groom", "07:30", 90, due_date=D))
    mochi.add_task(Task("Pill", "09:15", 15, due_date=D))

    assert scheduler.find_next_available_slot(15, day=D) == "09:00"
    assert scheduler.find_next_available_slot(30, day=D) == "09:30"


def test_next_slot_ignores_completed_tasks():
    """Completed tasks do not block time."""
    _, mochi, _, scheduler = make_owner()
    task = Task("Walk", "07:00", 60, due_date=D)
    mochi.add_task(task)
    task.mark_complete()

    assert scheduler.find_next_available_slot(30, day=D) == "07:00"


def test_next_slot_none_when_day_is_full():
    """Returns None when no block fits before the end time."""
    _, mochi, _, scheduler = make_owner()
    mochi.add_task(Task("All day", "07:00", 900, due_date=D))

    assert scheduler.find_next_available_slot(1, day=D) is None
    assert scheduler.find_next_available_slot(60, day=D, start="21:30") is None


def test_next_slot_zero_duration_raises():
    """A duration below 1 minute is rejected."""
    _, _, _, scheduler = make_owner()

    with pytest.raises(ValueError):
        scheduler.find_next_available_slot(0, day=D)


def test_save_and_load_round_trip(tmp_path):
    """Saving then loading preserves the owner, pets, and every task field."""
    owner, mochi, whiskers, _ = make_owner()
    mochi.add_task(Task("Walk", "07:30", 30, "high", "daily", due_date=D))
    mochi.add_task(Task("Pill", "12:00", 5, "medium", "once", due_date=date(2026, 11, 2), completed=True))
    whiskers.add_task(Task("Play", "18:45", 20, "low", "weekly", due_date=date(2027, 1, 1)))
    path = str(tmp_path / "data.json")

    owner.save_to_json(path)
    loaded = Owner.load_from_json(path)

    assert loaded.name == owner.name
    assert [(p.name, p.species) for p in loaded.pets] == [(p.name, p.species) for p in owner.pets]
    fields = ("description", "time", "duration_minutes", "priority", "frequency", "due_date", "completed", "pet_name")
    for original_pet, loaded_pet in zip(owner.pets, loaded.pets):
        assert len(loaded_pet.tasks) == len(original_pet.tasks)
        for a, b in zip(original_pet.tasks, loaded_pet.tasks):
            for name in fields:
                assert getattr(b, name) == getattr(a, name), name


def test_load_missing_file_returns_none(tmp_path):
    """Loading from a path that does not exist returns None."""
    assert Owner.load_from_json(str(tmp_path / "nope.json")) is None
