# 🐾 PawPal+

PawPal+ is a pet care planning app for busy owners with more than one pet. It tracks daily care tasks (walks, feeding, medications, grooming, play) across **all** of an owner's pets, builds a sorted daily schedule, warns when tasks overlap, finds free time slots, and automatically reschedules recurring tasks. It has a Streamlit web UI and a command-line demo, and saves your data between runs.

## ✨ Features

- **Multi-pet management**: one owner, many pets, each with its own task list
- **Sorting by time**: schedules are always in chronological order (numeric, so "9:00" never sorts after "10:00")
- **Priority scheduling**: an alternate view that sorts high → medium → low, then by time
- **Filtering**: by pet (case-insensitive) and by status (pending/done)
- **Conflict warnings**: flags tasks whose time ranges overlap (start + duration), even across different pets
- **Next available slot**: finds the earliest time a task of a given length fits without overlapping anything
- **Daily and weekly recurrence**: completing a recurring task automatically schedules the next one (+1 day or +7 days)
- **Input validation**: rejects invalid times, zero-minute durations, and unknown frequencies when a task is created
- **Data persistence**: pets and tasks are saved to `data.json` and restored on the next run
- **Formatted CLI output**: bordered tables, emoji task types, and color-coded priorities

## 🏗️ System Design

All backend logic lives in `pawpal_system.py`, using four classes:

- **`Task`** (dataclass): one care activity: description, time (HH:MM), duration, priority, frequency (once/daily/weekly), due date, completion status, and pet name. Validates itself on creation, can mark itself complete, create its next occurrence, and convert to/from a dictionary.
- **`Pet`** (dataclass): a pet's name, species, and list of tasks. `add_task()` stamps each task with the pet's name, so a task always knows which pet it belongs to.
- **`Owner`**: the owner's name and list of pets. `get_all_tasks()` combines every pet's tasks into one list. Also handles saving and loading with `save_to_json()` and `load_from_json()`.
- **`Scheduler`**: the "brain." It reads tasks **only** through `Owner.get_all_tasks()`, so every feature works across all pets, not just one.

Two module-level helpers support the classes: `time_to_minutes()` converts "HH:MM" to minutes (used for sorting, conflicts, and slot finding), and `PRIORITY_RANK` maps priorities to sort order.

**UML:** the final class diagram is in [`diagrams/uml_final.mmd`](diagrams/uml_final.mmd) (Mermaid). The original draft is in [`diagrams/uml_draft.mmd`](diagrams/uml_draft.mmd); comparing them shows how the design grew during implementation.

## 🚀 Getting Started

### Setup
```bash
python -m venv .venv
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### Run the app
```bash
streamlit run app.py
```

### Run the CLI demo
```bash
python main.py
```

### Run the tests
```bash
python -m pytest -v
```

## 📸 Demo Walkthrough

**Main UI features:**
1. **Owner**: enter the owner's name at the top.
2. **Add a Pet**: type a pet name, choose a species (dog/cat/other), and click **Add pet**. Duplicate names are blocked, ignoring capitalization ("Luna" and "luna" count as the same pet).
3. **Add a Task**: pick the pet, enter a title, time, duration, priority (low/medium/high), and frequency (once/daily/weekly), then click **Add task**. Empty titles are rejected.
4. **Current tasks**: a table of every task across all pets, sorted by due date, then time.
5. **Today's Schedule**: updates live. Filter by pet and status, and choose **Sort by** "Time" or "Priority, then time." Overlapping tasks show a yellow warning naming both tasks and pets; otherwise a green "No scheduling conflicts today" message appears.
6. **Find a free slot**: enter a duration and click **Find next free slot** to see the earliest time it fits today.
7. **Mark a Task Complete**: choose a pending task and click **Mark complete**. Daily and weekly tasks show a message like *"Done! Next 'Morning walk' scheduled for 2026-10-19."*

Everything saves automatically to `data.json`, so closing and reopening the app keeps your pets and tasks.

**Example workflow:**
1. Add **Mochi** (dog) and **Luna** (cat).
2. Add Mochi's **Morning walk** at 07:30 for 30 min (high, daily) and Luna's **Breakfast** at 07:45 for 10 min (high, daily).
3. Today's Schedule shows both tasks in time order, with a **yellow warning** that the walk (07:30–08:00) overlaps breakfast.
4. **Find a free slot** for 20 minutes returns 07:00, before the walk.
5. Mark the **Morning walk** complete. The conflict warning clears (completed tasks can't conflict), and a new walk appears in Current tasks, due tomorrow.

**Key Scheduler behaviors shown:** time sorting, priority sorting, pet and status filtering, cross-pet conflict detection, next-available-slot search, and automatic daily/weekly recurrence.

## 🖥️ Sample CLI Output

`python main.py` creates an owner with two pets and six tasks (added deliberately out of order), then demonstrates every Scheduler feature:

```
📅 Today's Schedule (sorted by time)
╭────────┬───────┬────────────────────────┬────────────┬────────────┬────────┬────────────╮
│ Time   │ Pet   │ Task                   │ Duration   │ Priority   │ Freq   │ Status     │
├────────┼───────┼────────────────────────┼────────────┼────────────┼────────┼────────────┤
│ 06:45  │ Mochi │ 🐕 Fetch in the yard   │ 15 min     │ low        │ once   │ ⏳ pending │
│ 07:30  │ Mochi │ 🐕 Morning walk        │ 30 min     │ high       │ daily  │ ⏳ pending │
│ 07:45  │ Luna  │ 🍖 Breakfast           │ 10 min     │ high       │ daily  │ ⏳ pending │
│ 12:00  │ Mochi │ 💊 Give heartworm pill │ 5 min      │ high       │ once   │ ⏳ pending │
│ 12:00  │ Luna  │ 🧼 Brush coat          │ 5 min      │ medium     │ once   │ ⏳ pending │
│ 18:00  │ Luna  │ 🎾 Play session        │ 20 min     │ low        │ weekly │ ⏳ pending │
╰────────┴───────┴────────────────────────┴────────────┴────────────┴────────┴────────────╯

⭐ Today's Schedule (by priority, then time)
╭────────┬───────┬────────────────────────┬────────────┬────────────┬────────┬────────────╮
│ Time   │ Pet   │ Task                   │ Duration   │ Priority   │ Freq   │ Status     │
├────────┼───────┼────────────────────────┼────────────┼────────────┼────────┼────────────┤
│ 07:30  │ Mochi │ 🐕 Morning walk        │ 30 min     │ high       │ daily  │ ⏳ pending │
│ 07:45  │ Luna  │ 🍖 Breakfast           │ 10 min     │ high       │ daily  │ ⏳ pending │
│ 12:00  │ Mochi │ 💊 Give heartworm pill │ 5 min      │ high       │ once   │ ⏳ pending │
│ 12:00  │ Luna  │ 🧼 Brush coat          │ 5 min      │ medium     │ once   │ ⏳ pending │
│ 06:45  │ Mochi │ 🐕 Fetch in the yard   │ 15 min     │ low        │ once   │ ⏳ pending │
│ 18:00  │ Luna  │ 🎾 Play session        │ 20 min     │ low        │ weekly │ ⏳ pending │
╰────────┴───────┴────────────────────────┴────────────┴────────────┴────────┴────────────╯

🐶 Filter: Mochi's tasks
╭────────┬───────┬────────────────────────┬────────────┬────────────┬────────┬────────────╮
│ Time   │ Pet   │ Task                   │ Duration   │ Priority   │ Freq   │ Status     │
├────────┼───────┼────────────────────────┼────────────┼────────────┼────────┼────────────┤
│ 06:45  │ Mochi │ 🐕 Fetch in the yard   │ 15 min     │ low        │ once   │ ⏳ pending │
│ 07:30  │ Mochi │ 🐕 Morning walk        │ 30 min     │ high       │ daily  │ ⏳ pending │
│ 12:00  │ Mochi │ 💊 Give heartworm pill │ 5 min      │ high       │ once   │ ⏳ pending │
╰────────┴───────┴────────────────────────┴────────────┴────────────┴────────┴────────────╯

🚨 Conflict Check
WARNING: Mochi's 'Morning walk' (07:30, 30 min) overlaps Luna's 'Breakfast' (07:45, 10 min)
WARNING: Mochi's 'Give heartworm pill' (12:00, 5 min) overlaps Luna's 'Brush coat' (12:00, 5 min)

🔎 Next Available Slot
Next free 20-min slot: 07:00
Next free 45-min slot: 08:00

🔁 Recurring Task Demo
Completed 'Morning walk' -> next occurrence scheduled for 2026-10-19

📋 Filter: Pending tasks today
╭────────┬───────┬────────────────────────┬────────────┬────────────┬────────┬────────────╮
│ Time   │ Pet   │ Task                   │ Duration   │ Priority   │ Freq   │ Status     │
├────────┼───────┼────────────────────────┼────────────┼────────────┼────────┼────────────┤
│ 06:45  │ Mochi │ 🐕 Fetch in the yard   │ 15 min     │ low        │ once   │ ⏳ pending │
│ 07:45  │ Luna  │ 🍖 Breakfast           │ 10 min     │ high       │ daily  │ ⏳ pending │
│ 12:00  │ Mochi │ 💊 Give heartworm pill │ 5 min      │ high       │ once   │ ⏳ pending │
│ 12:00  │ Luna  │ 🧼 Brush coat          │ 5 min      │ medium     │ once   │ ⏳ pending │
│ 18:00  │ Luna  │ 🎾 Play session        │ 20 min     │ low        │ weekly │ ⏳ pending │
╰────────┴───────┴────────────────────────┴────────────┴────────────┴────────┴────────────╯

✅ Filter: Completed tasks today
╭────────┬───────┬─────────────────┬────────────┬────────────┬────────┬──────────╮
│ Time   │ Pet   │ Task            │ Duration   │ Priority   │ Freq   │ Status   │
├────────┼───────┼─────────────────┼────────────┼────────────┼────────┼──────────┤
│ 07:30  │ Mochi │ 🐕 Morning walk │ 30 min     │ high       │ daily  │ ✅ done  │
╰────────┴───────┴─────────────────┴────────────┴────────────┴────────┴──────────╯

💾 Persistence Demo
Saved and reloaded David: 2 pets, 7 tasks
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
| ------- | --------- | ----- |
| Task sorting | `Scheduler.sort_by_time()` | Sorts by converting "HH:MM" to minutes, so "7:30" can never sort after "10:00". Returns a new list. |
| Priority scheduling | `Scheduler.sort_by_priority()` | Sorts high → medium → low, then by time within each priority. Unknown priorities go last. Separate from `sort_by_time()` so both views are available (UI "Sort by" dropdown). |
| Filtering | `Scheduler.filter_by_pet()`, `Scheduler.filter_by_status()` | Filter by pet name (case-insensitive) or by completed/pending. Both return lists, so they can be chained. |
| Conflict handling | `Scheduler.detect_conflicts()` | Flags pending, same-day tasks whose time ranges overlap (start + duration), across **all** pets. Back-to-back tasks are not conflicts. Returns warning strings, never crashes. |
| Next available slot | `Scheduler.find_next_available_slot()` | Finds the earliest start time (07:00–22:00) where a task of a given length fits without overlapping any pending task from any pet. Back-to-back is allowed; returns `None` if the day is full. |
| Recurring tasks | `Task.next_occurrence()`, `Scheduler.mark_task_complete()` | Completing a daily task creates the next one at due date + 1 day (weekly: + 7 days) using `timedelta`, and adds it to the same pet. Completing a task twice does not create duplicates. |
| Validation | `time_to_minutes()`, `Task.__post_init__()` | Normalizes "7:30" to "07:30" and rejects invalid times ("25:99"), durations under 1 minute, and frequencies other than once/daily/weekly when a task is created. |

All Scheduler features read tasks through `Owner.get_all_tasks()`, so they work across every pet, not just one.

### Priority scheduling: CLI example

The same six tasks, sorted two ways. By time, the low-priority **Fetch in the yard** (06:45) comes first. By priority, it drops below every high- and medium-priority task, while still coming before the other low task (18:00) because time breaks ties within a priority level:

```
📅 Today's Schedule (sorted by time)          ⭐ Today's Schedule (by priority, then time)
06:45  Mochi  Fetch in the yard     low       07:30  Mochi  Morning walk          high
07:30  Mochi  Morning walk          high      07:45  Luna   Breakfast             high
07:45  Luna   Breakfast             high      12:00  Mochi  Give heartworm pill   high
12:00  Mochi  Give heartworm pill   high      12:00  Luna   Brush coat            medium
12:00  Luna   Brush coat            medium    06:45  Mochi  Fetch in the yard     low
18:00  Luna   Play session          low       18:00  Luna   Play session          low
```

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

`tabulate` and `wcwidth` are listed in `requirements.txt`. (Colors don't appear in the output pasted above, because copied terminal text doesn't include them.)

## 🧪 Testing PawPal+

### Run the tests
```bash
python -m pytest -v
```

### What the tests cover (24 tests in `tests/test_pawpal.py`)

| Area | Tests |
| ---- | ----- |
| **Core classes** | Marking a task complete changes its status; adding a task to a pet increases its count and stamps the pet's name. |
| **Sorting** | Out-of-order tasks come back earliest first. A task entered as "9:00" is normalized and sorts before "10:00" (proves the sort is numeric, not text). The input list isn't changed. |
| **Priority sorting** | High tasks come before medium and low, with time breaking ties within each priority; the input list isn't changed. |
| **Recurrence** | Daily tasks recur +1 day and weekly +7 days; "once" tasks don't recur; completing twice creates only one follow-up; dates roll over correctly at month end, year end, and leap day (2028-02-29). |
| **Conflict detection** | Overlapping tasks across two pets produce one warning naming both; back-to-back tasks don't conflict; same-start and nested tasks do; completed tasks and other-day tasks are ignored. |
| **Next available slot** | An empty day returns the start time; finds a gap between two pets' tasks; skips overlapping tasks to the first real gap; ignores completed tasks; returns `None` when the day is full; a zero-minute duration raises an error. |
| **Filtering** | Pet filter ignores case and spaces and returns `[]` for an unknown pet; status filter separates done from pending. |
| **Persistence** | A full save → load round trip preserves every field of every task, plus pet and owner data; loading a missing file returns `None`. |
| **Validation and edge cases** | Invalid times ("25:00", "12:60", "0730", "") and zero-minute durations are rejected; an invalid frequency ("weekley") is rejected while " Weekly " is normalized; a pet with no tasks gives an empty schedule and no conflicts; the Scheduler gathers tasks from all pets. |

All tests use a fixed date (`2026-10-18`) instead of "today", so they give the same result whenever they run.

### Sample test output
```
tests/test_pawpal.py::test_mark_complete_changes_status PASSED                                [  4%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED                           [  8%]
tests/test_pawpal.py::test_sort_by_time_chronological_order PASSED                            [ 12%]
tests/test_pawpal.py::test_daily_task_completion_creates_next_day_task PASSED                 [ 16%]
tests/test_pawpal.py::test_weekly_recurrence_and_once_returns_none PASSED                     [ 20%]
tests/test_pawpal.py::test_double_complete_does_not_duplicate_recurrence PASSED               [ 25%]
tests/test_pawpal.py::test_recurrence_across_month_and_year_boundary PASSED                   [ 29%]
tests/test_pawpal.py::test_detect_conflicts_flags_overlapping_tasks PASSED                    [ 33%]
tests/test_pawpal.py::test_detect_conflicts_boundaries PASSED                                 [ 37%]
tests/test_pawpal.py::test_detect_conflicts_ignores_completed_and_other_dates PASSED          [ 41%]
tests/test_pawpal.py::test_filter_by_pet_and_status PASSED                                    [ 45%]
tests/test_pawpal.py::test_invalid_time_rejected_and_normalized PASSED                        [ 50%]
tests/test_pawpal.py::test_pet_with_no_tasks PASSED                                           [ 54%]
tests/test_pawpal.py::test_scheduler_gets_tasks_from_all_pets PASSED                          [ 58%]
tests/test_pawpal.py::test_sort_by_priority_then_time PASSED                                  [ 62%]
tests/test_pawpal.py::test_next_slot_empty_day_returns_start PASSED                           [ 66%]
tests/test_pawpal.py::test_next_slot_finds_gap_between_tasks_on_different_pets PASSED         [ 70%]
tests/test_pawpal.py::test_next_slot_skips_overlapping_tasks_to_first_real_gap PASSED         [ 75%]
tests/test_pawpal.py::test_next_slot_ignores_completed_tasks PASSED                           [ 79%]
tests/test_pawpal.py::test_next_slot_none_when_day_is_full PASSED                             [ 83%]
tests/test_pawpal.py::test_next_slot_zero_duration_raises PASSED                              [ 87%]
tests/test_pawpal.py::test_save_and_load_round_trip PASSED                                    [ 91%]
tests/test_pawpal.py::test_load_missing_file_returns_none PASSED                              [ 95%]
tests/test_pawpal.py::test_invalid_frequency_rejected PASSED                                  [100%]

============================== 24 passed in 0.21s ==============================
```

### Confidence Level: ⭐⭐⭐⭐☆ (4/5)
Every scheduling algorithm is tested on both normal and edge cases, and all 24 tests pass. It's not 5/5 because the Streamlit UI has no automated tests, and tasks that run past midnight aren't handled (a documented tradeoff in `reflection.md`).

## 📁 Project Files

| File | Purpose |
| ---- | ------- |
| `pawpal_system.py` | Backend logic: Task, Pet, Owner, Scheduler |
| `app.py` | Streamlit web UI |
| `main.py` | CLI demo of every feature |
| `tests/test_pawpal.py` | 24 automated pytest tests |
| `diagrams/uml_final.mmd` | Final UML class diagram (Mermaid) |
| `diagrams/uml_draft.mmd` | Initial UML draft |
| `reflection.md` | Design decisions, tradeoffs, and AI collaboration reflection |
| `ai_interactions.md` | Agent workflow and model comparison (stretch features) |