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

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->
