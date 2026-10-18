# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## 🏗️ Implementation Summary

PawPal+ keeps its backend logic in `pawpal_system.py`, using four classes:

- **`Task`** (dataclass): one care activity, with a description, time (HH:MM), duration, priority, frequency (once/daily/weekly), due date, completion status, and pet name. `mark_complete()` marks it done.
- **`Pet`** (dataclass): a pet's name, species, and list of tasks. `add_task()` also stamps the task with the pet's name, so every task knows which pet it belongs to.
- **`Owner`**: the owner's name and list of pets. `get_all_tasks()` combines every pet's tasks into one list.
- **`Scheduler`**: the "brain." It reads tasks **only** through `Owner.get_all_tasks()`, so every feature works across all pets, not just one. `get_todays_tasks()` returns everything due today.

**How they work together:** `main.py` creates an Owner, adds Pets, and adds Tasks to each Pet. The Scheduler asks the Owner for all tasks and returns today's plan.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Running `python main.py` creates an owner with two pets and five tasks added out of order, then demonstrates sorting, filtering, conflict detection, and recurring tasks:

```
Today's Schedule (sorted by time)
=================================
07:30 | Mochi | Morning walk         |  30 min | high   | daily  | [ ] pending
07:45 | Luna  | Breakfast            |  10 min | high   | daily  | [ ] pending
12:00 | Mochi | Give heartworm pill  |   5 min | high   | once   | [ ] pending
12:00 | Luna  | Brush coat           |   5 min | medium | once   | [ ] pending
18:00 | Luna  | Play session         |  20 min | low    | weekly | [ ] pending

Filter: Mochi's tasks
=====================
07:30 | Mochi | Morning walk         |  30 min | high   | daily  | [ ] pending
12:00 | Mochi | Give heartworm pill  |   5 min | high   | once   | [ ] pending

Conflict Check
==============
WARNING: Mochi's 'Morning walk' (07:30, 30 min) overlaps Luna's 'Breakfast' (07:45, 10 min)
WARNING: Mochi's 'Give heartworm pill' (12:00, 5 min) overlaps Luna's 'Brush coat' (12:00, 5 min)

Recurring Task Demo
===================
Completed 'Morning walk' -> next occurrence scheduled for 2026-10-19

Filter: Pending tasks today
===========================
07:45 | Luna  | Breakfast            |  10 min | high   | daily  | [ ] pending
12:00 | Mochi | Give heartworm pill  |   5 min | high   | once   | [ ] pending
12:00 | Luna  | Brush coat           |   5 min | medium | once   | [ ] pending
18:00 | Luna  | Play session         |  20 min | low    | weekly | [ ] pending
```

## 🧪 Testing PawPal+

### Run the demo
```bash
python main.py
```

### Run the tests
```bash
python -m pytest -v
```

### What the tests cover (14 tests in `tests/test_pawpal.py`)

| Area | Tests |
| ---- | ----- |
| **Core classes** | Marking a task complete changes its status; adding a task to a pet increases its count and stamps the pet's name. |
| **Sorting** | Out-of-order tasks come back earliest first. A task entered as "9:00" is normalized and sorts before "10:00" (proves the sort is numeric, not text). The input list isn't changed. |
| **Recurrence** | Daily tasks recur +1 day and weekly +7 days; "once" tasks don't recur; completing twice creates only one follow-up; dates roll over correctly at month end, year end, and leap day (2028-02-29). |
| **Conflict detection** | Overlapping tasks across two pets produce one warning naming both; back-to-back tasks don't conflict; same-start and nested tasks do; completed tasks and other-day tasks are ignored. |
| **Filtering** | Pet filter ignores case and spaces and returns `[]` for an unknown pet; status filter separates done from pending. |
| **Validation and edge cases** | Invalid times ("25:00", "12:60", "0730", "") and zero-minute durations are rejected; a pet with no tasks gives an empty schedule and no conflicts; the Scheduler gathers tasks from all pets. |

All tests use a fixed date (`2026-10-18`) instead of "today", so they give the same result whenever they run.

### Sample test output
```
tests/test_pawpal.py::test_mark_complete_changes_status PASSED                     [  7%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED                [ 14%]
tests/test_pawpal.py::test_sort_by_time_chronological_order PASSED                 [ 21%]
tests/test_pawpal.py::test_daily_task_completion_creates_next_day_task PASSED      [ 28%]
tests/test_pawpal.py::test_weekly_recurrence_and_once_returns_none PASSED          [ 35%]
tests/test_pawpal.py::test_double_complete_does_not_duplicate_recurrence PASSED    [ 42%]
tests/test_pawpal.py::test_recurrence_across_month_and_year_boundary PASSED        [ 50%]
tests/test_pawpal.py::test_detect_conflicts_flags_overlapping_tasks PASSED         [ 57%]
tests/test_pawpal.py::test_detect_conflicts_boundaries PASSED                      [ 64%]
tests/test_pawpal.py::test_detect_conflicts_ignores_completed_and_other_dates PASSED [ 71%]
tests/test_pawpal.py::test_filter_by_pet_and_status PASSED                         [ 78%]
tests/test_pawpal.py::test_invalid_time_rejected_and_normalized PASSED             [ 85%]
tests/test_pawpal.py::test_pet_with_no_tasks PASSED                                [ 92%]
tests/test_pawpal.py::test_scheduler_gets_tasks_from_all_pets PASSED               [100%]

============================== 14 passed in 0.07s ==============================
```

### Confidence Level: ⭐⭐⭐⭐☆ (4/5)
Every scheduling algorithm is tested on both normal and edge cases, and all 14 tests pass. It's not 5/5 because the Streamlit UI has no automated tests, and tasks that run past midnight aren't handled (a documented tradeoff).

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
| ------- | --------- | ----- |
| Task sorting | `Scheduler.sort_by_time()` | Sorts by converting "HH:MM" to minutes, so "7:30" can never sort after "10:00". Returns a new list. |
| Priority scheduling | `Scheduler.sort_by_priority()` | Sorts high → medium → low, then by time within each priority. Unknown priorities go last. Separate from `sort_by_time()` so both views are available (UI "Sort by" dropdown). |
| Filtering | `Scheduler.filter_by_pet()`, `Scheduler.filter_by_status()` | Filter by pet name (case-insensitive) or by completed/pending. Both return lists, so they can be chained. |
| Conflict handling | `Scheduler.detect_conflicts()` | Flags pending, same-day tasks whose time ranges overlap (start + duration), across **all** pets. Back-to-back tasks are not conflicts. Returns warning strings, never crashes. |
| Next available slot | `Scheduler.find_next_available_slot()` | Finds the earliest start time (07:00–22:00) where a task of a given length fits without overlapping any pending task from any pet. Back-to-back is allowed; returns `None` if the day is full. |
| Recurring tasks | `Task.next_occurrence()`, `Scheduler.mark_task_complete()` | Completing a daily task creates the next one at due date + 1 day (weekly: + 7 days) using `timedelta`, and adds it to the same pet. Completing a task twice does not create duplicates. |
| Time validation | `time_to_minutes()`, `Task.__post_init__()` | Normalizes "7:30" to "07:30" and rejects invalid times like "25:99" when a task is created. |

All Scheduler features read tasks through `Owner.get_all_tasks()`, so they work across every pet, not just one.

## 💾 Data Persistence

PawPal+ remembers your pets and tasks between runs by saving them to `data.json`.

**How it works:**
1. When the Streamlit app starts, it calls `Owner.load_from_json("data.json")`. If the file exists, your owner, pets, and tasks are restored. If it doesn't exist (first run), the app starts fresh.
2. Every change is saved immediately with `Owner.save_to_json("data.json")`: adding a pet, adding a task, marking a task complete, or changing the owner name.
3. Each class converts itself to and from a plain dictionary: `Task.to_dict()` / `Task.from_dict()`, `Pet.to_dict()` / `Pet.from_dict()`, `Owner.to_dict()` / `Owner.from_dict()`. Dates are stored as ISO strings (e.g., `"2026-10-18"`), since JSON has no date type.
4. If `data.json` is corrupted, the app shows a warning and starts with a fresh schedule instead of crashing.

I used custom dictionary conversion instead of a library like marshmallow. It's only a few lines, adds no dependencies, and works simply because each Task stores its pet as a `pet_name` string rather than a Pet object reference (a design decision from Phase 1).

**Files modified:**
| File | Change |
| ---- | ------ |
| `pawpal_system.py` | Added `to_dict` / `from_dict` on Task, Pet, and Owner, plus `Owner.save_to_json()` and `Owner.load_from_json()` |
| `app.py` | Loads `data.json` on startup (with a corrupt-file fallback) and auto-saves after every change |
| `main.py` | Added a "Persistence Demo" section that saves to a temp file, reloads it, and prints the counts |
| `tests/test_pawpal.py` | Added a full save/load round-trip test and a missing-file test |
| `.gitignore` | Added `data.json` so personal data isn't committed |

## 🎨 CLI Output Formatting

`main.py` prints the demo as formatted tables instead of plain text:

| Feature | How it's done | Function / library |
| ------- | ------------- | ------------------ |
| **Bordered tables** | Each task list prints as a rounded-border table with headers | `tabulate` (`tablefmt="rounded_outline"`) in `print_tasks()` |
| **Emoji task types** | 🐕 walk/fetch, 🍖 food, 💊 meds, 🧼 grooming, 🎾 play, 🐾 other | `task_emoji()` (keyword match on the description) |
| **Emoji status** | ✅ done / ⏳ pending | `print_tasks()` |
| **Color-coded priority** | high = red, medium = yellow, low = green; conflict warnings in yellow; bold section titles | ANSI escape codes via `color()` and `PRIORITY_COLORS` |
| **Correct alignment with emojis** | Emojis are double-width; without help, table borders go crooked | `wcwidth` (used automatically by `tabulate`) |

**Safety choices:**
- Colors only turn on when printing to a real terminal (`sys.stdout.isatty()`) and respect the `NO_COLOR` environment variable, so redirected output never fills with escape codes like `\x1b[31m`.
- `sys.stdout.reconfigure(encoding="utf-8")` prevents a `UnicodeEncodeError` crash when output is piped or redirected on Windows.
- I avoided emojis with "variation selectors" (like 🍽️ and ✂️), which render inconsistently on Windows and break table alignment.

`tabulate` and `wcwidth` are listed in `requirements.txt`.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
