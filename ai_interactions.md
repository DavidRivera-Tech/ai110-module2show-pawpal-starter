# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**
I gave Claude in VS Code (agent mode) one multi-step task: implement a "next available slot" feature end to end. That meant adding `Scheduler.find_next_available_slot()`, writing tests for it, adding a demo section to `main.py`, and adding a "Find a free slot" control to the Streamlit app. I specified the rules (pending tasks across all pets count as busy, back-to-back is allowed, return `None` if nothing fits by 22:00, raise `ValueError` for a duration under 1) and limited it to four files.

**Which files were modified?**
- `pawpal_system.py`: new `Scheduler.find_next_available_slot()` method
- `tests/test_pawpal.py`: 6 new tests (empty day, gap between two pets' tasks, skipping overlapping tasks, ignoring completed tasks, a full day returning `None`, duration 0 raising `ValueError`)
- `main.py`: new "Next Available Slot" section printing results for 20- and 45-minute tasks
- `app.py`: "Find a free slot" duration input and button under the conflict warnings

**What did the agent do?**
It implemented all four parts in one run, ran pytest (21 passed) and `main.py`, and reported back with a summary of each file plus what it was unsure about: it passed the date positionally, it didn't add a separate check for `end` earlier than `start` (it just returns `None`), and it had not run the Streamlit app, so the UI control was untested.

**What did you have to verify or fix manually?**
- **Scope:** I ran `git status` to confirm the agent only changed the four files I allowed.
- **Results:** Before reading its output, I worked out the expected answers by hand: a 20-minute slot fits at 07:00 (between a task ending at 07:00 and a walk at 07:30), and a 45-minute slot lands at 08:00 (after the 07:30–08:00 walk, skipping a 07:45 breakfast for a different pet that falls inside the walk). I re-ran pytest and `main.py` myself, and both matched.
- **Logic review:** I read the method line by line and traced the 45-minute case through the loop to confirm it handles overlapping busy blocks from different pets.
- **UI:** The agent never ran the Streamlit control, so I tested it in the browser: with a 07:00, 30-minute task, a 30-minute search correctly returned 07:30.
- **Decisions:** I accepted returning `None` when `end` is before `start`, since "no slot fits" is an honest answer and doesn't crash. No code corrections were needed; the main manual work was verification, especially the UI piece the agent skipped.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

**Task:** Write `Task.next_occurrence()` for daily/weekly recurring tasks, and decide whether a task completed late should recur from its original due date or from its completion date. I sent the identical prompt to both models, without showing either one my existing code.

| | Option A | Option B |
| --- | --- | --- |
| **Model / tool used** | Claude (Claude in VS Code, fresh chat) | ChatGPT (chatgpt.com) |
| **Prompt** | Identical prompt: the Task fields, "return a new Task for the next daily/weekly occurrence or None for one-time tasks," and "should a late task recur from its due date or its completion date? Explain, then give code." | Same as Option A |
| **Response summary** | Chose the due date. Used a dictionary of timedeltas plus `dataclasses.replace`. Unknown frequencies return `None`. Rewrote the entire Task class around the method. | Chose the due date. Used `if/elif` with `timedelta(days=1)` / `timedelta(weeks=1)` plus `dataclasses.replace`. Unknown frequencies raise `ValueError`. Gave a dated example (due Oct 12, done Oct 15, next due Oct 19). |
| **What was useful** | Concise, type-hinted, with a docstring. Clearly explained the real tradeoff: if a task is done very late, its next occurrence may already be overdue, which is honest because that occurrence really was missed. | Very readable branches and a concrete worked example. Explicitly flagged its limitation: a task several periods overdue only advances one period. Failing loudly on an unknown frequency is a good instinct. |
| **Problems noticed** | Returning `None` for an unknown frequency hides typos: a task with `"weekley"` would silently never recur. Rewriting the whole class was risky; pasting it would have deleted my `eq=False`, `__post_init__` validation, defaults, and persistence methods. | No type hints or docstring. Raising `ValueError` inside `next_occurrence()` means `Scheduler.mark_task_complete()` would crash at the moment a user clicks "Mark complete" in the app, instead of when the bad data was created. |
| **Decision** | Kept my existing `next_occurrence()`, which already matched both models on the core logic (due-date anchor, `replace`, `timedelta`). | Adopted ChatGPT's "fail loudly" idea, but moved it to where the bad data enters: `Task.__post_init__` now raises `ValueError` for any frequency other than once/daily/weekly, with a new test. |

**Which approach did you use in your final implementation and why?**
Both models independently chose to anchor recurrence on the original due date, which confirmed the decision I made in Phase 4: a weekly task done late shouldn't drift the whole schedule. I kept my implementation and combined the best idea from each model. From Claude I kept the behavior that `next_occurrence()` never crashes. From ChatGPT I took failing loudly on bad input, but I moved the check to `Task.__post_init__`, so a typo like "weekley" is rejected immediately when the task is created, rather than silently never recurring (Claude's version) or crashing later when the user marks the task complete (ChatGPT's version). The biggest lesson was to never paste a model's full class rewrite: Claude's answer looked clean, but it would have quietly removed validation and persistence code I depended on.
