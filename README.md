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

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
| ------- | --------- | ----- |
| Task sorting | `Scheduler.sort_by_time()` | Sorts by converting "HH:MM" to minutes, so "7:30" can never sort after "10:00". Returns a new list. |
| Filtering | `Scheduler.filter_by_pet()`, `Scheduler.filter_by_status()` | Filter by pet name (case-insensitive) or by completed/pending. Both return lists, so they can be chained. |
| Conflict handling | `Scheduler.detect_conflicts()` | Flags pending, same-day tasks whose time ranges overlap (start + duration), across **all** pets. Back-to-back tasks are not conflicts. Returns warning strings, never crashes. |
| Recurring tasks | `Task.next_occurrence()`, `Scheduler.mark_task_complete()` | Completing a daily task creates the next one at due date + 1 day (weekly: + 7 days) using `timedelta`, and adds it to the same pet. Completing a task twice does not create duplicates. |
| Time validation | `time_to_minutes()`, `Task.__post_init__()` | Normalizes "7:30" to "07:30" and rejects invalid times like "25:99" when a task is created. |

All Scheduler features read tasks through `Owner.get_all_tasks()`, so they work across every pet, not just one.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
