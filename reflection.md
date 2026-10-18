# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

**Core user actions:**
1. **Add a pet** — The owner enters a pet's name and species so PawPal+ can track care for each of their pets separately.
2. **Schedule a care task** — The owner adds a task (like a walk, feeding, or medication) for a specific pet with a time, duration, priority, and how often it repeats (once, daily, weekly).
3. **View today's plan** — The owner sees all of today's tasks across every pet, sorted by time, with warnings if two tasks clash.

- **Briefly describe your initial UML design.**
  My UML has four classes. An Owner has many Pets (aggregation), each Pet has many Tasks (composition), and a Scheduler uses the Owner to work with tasks across all pets. I added "1" and "*" multiplicity so the one-to-many relationships are explicit.

- **What classes did you include, and what responsibilities did you assign to each?**
  - **Task** — one care activity: description, time (HH:MM), duration, priority, frequency (once/daily/weekly), due date, completion status, and which pet it belongs to. It can mark itself complete and create its next occurrence.
  - **Pet** — a pet's name and species plus its list of tasks, with methods to add, remove, and list them.
  - **Owner** — the owner's name and list of pets. `get_all_tasks()` gathers every pet's tasks into one list.
  - **Scheduler** — the "brain." It reads tasks through `Owner.get_all_tasks()` (never from a single pet), then sorts, filters, handles recurring tasks, and detects conflicts.



**b. Design changes**

- **Did your design change during implementation?**
  Yes. Claude generated my first UML, but it left return types off five Scheduler methods and used text labels instead of multiplicity. I added the return types and "1"/"*" multiplicity myself.

- **If yes, describe at least one change and why you made it.**
After generating the skeleton, I asked Claude to review it against the UML. I accepted 7 of its 9 points and rejected 2:

- **Accepted:** Made `get_pet`, `next_occurrence`, and `mark_task_complete` return `X | None`, because a missing pet or a one-time task has nothing to return, and the old hints promised a value that might not exist. Changed Task to `@dataclass(eq=False)` so `remove_task` removes the exact task object, not just the first one with identical fields. Added an optional `today` parameter to `get_todays_tasks()` so tests can use a fixed date. Decided `Pet.add_task()` will set `task.pet_name` automatically so it can't drift, and that times will be sorted as minutes rather than strings, since "9:00" sorts after "10:00" as text.

- **Rejected:** Storing a Pet object reference on each Task. It creates a circular reference that complicates printing, comparison, and JSON saving, and the pet_name string is enough. Also rejected Enums for priority and frequency: the UI dropdowns already limit the values, and Enums would add complexity without much benefit at this size.

- **Phase 4 changes:** I added a `time_to_minutes()` helper and `Task.__post_init__` validation (so "7:30" becomes "07:30" and "25:99" is rejected), and I changed conflict detection from "same start time" to "overlapping time ranges" after Claude pointed out that a 30-minute walk at 07:30 really does clash with a 07:45 feeding. I also made `Owner.get_pet()` case-insensitive to match `filter_by_pet()`. Claude had applied case-insensitive matching to only one of the two methods.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- **What constraints does your scheduler consider (for example: time, priority, preferences)?**
  Time of day (HH:MM), task duration, due date, completion status, frequency (once/daily/weekly), and which pet a task belongs to. Priority is stored on every task and shown in the schedule.

- **How did you decide which constraints mattered most?**
  Time and duration matter most, because a pet owner can only be in one place at a time. That's why conflict detection checks whether time ranges overlap (start + duration), not just whether start times match. Due date comes next, so recurring tasks land on the right day and conflicts are only compared within the same day.

**b. Tradeoffs**

- **Describe one tradeoff your scheduler makes.**
  The scheduler warns about overlapping tasks but never moves them automatically, and it doesn't handle tasks that run past midnight. Claude suggested auto-rescheduling lower-priority tasks into the next free slot, but I rejected that.

- **Why is that tradeoff reasonable for this scenario?**
  Silently moving an owner's tasks would be surprising. They may have a reason for the time they chose (like a vet appointment). A warning keeps the owner in control. Pet care tasks are daytime routines, so midnight-crossing tasks aren't a realistic case. I also kept a simple "check every pair" conflict algorithm instead of Claude's faster sort-and-break version, because a household has a few dozen tasks at most, and the simpler version is easier to read and verify.

---

## 3. AI Collaboration

**a. How you used AI**

- **How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?**
  I used Claude in VS Code for design brainstorming (generating the Mermaid UML from my class list), scaffolding (turning the UML into dataclass skeletons), design review (asking it to critique the skeleton against the UML), and implementation (filling in the core methods and the main.py demo).

- **What kinds of prompts or questions were most helpful?**
  Specific, constrained prompts worked best: listing exact attributes and methods, saying "do not edit any other file," and asking for a review with "do NOT edit, just give feedback" so I could decide what to accept instead of having changes applied automatically.

**b. Judgment and verification**

- **Describe one moment where you did not accept an AI suggestion as-is.**
  Claude's design review suggested storing a Pet object reference on each Task. I rejected it because it creates a circular reference that complicates printing, comparison, and JSON saving, and a pet_name string set automatically by `Pet.add_task()` is enough. Also, when the em dash in my output showed up garbled, Claude suggested `set PYTHONIOENCODING=utf-8`, which is Command Prompt syntax and wouldn't work in my PowerShell terminal. I replaced the em dash with a plain hyphen instead, so the output works on any machine.

- **How did you evaluate or verify what the AI suggested?**
  Claude often reported that it hadn't run its own code, so I verified everything myself: I rendered the UML in Mermaid Live to confirm it drew correctly, ran an import check after every change to `pawpal_system.py`, ran `main.py` to confirm the output, and wrote pytest tests, including one that confirms `add_task()` sets `pet_name`.

---

## 4. Testing and Verification

**a. What you tested**

- **What behaviors did you test?**
  14 tests covering: task completion and adding tasks to pets; sorting (including a "9:00" vs "10:00" case that a text sort would get wrong); daily and weekly recurrence, "once" tasks not recurring, the double-completion guard, and date rollover at month end, year end, and leap day; conflict detection for overlaps, back-to-back tasks, identical starts, nested tasks, completed tasks, and tasks on other days; case-insensitive pet filtering and status filtering; time and duration validation; a pet with no tasks; and gathering tasks across all pets.

- **Why were these tests important?**
  They target where bugs were most likely: off-by-one errors at conflict boundaries, duplicate recurring tasks, and string-vs-number sorting. Claude's first sort test used "09:00" vs "10:00", which would pass even with a broken text sort. I changed it to "9:00" so the test actually proves the sort is numeric. I also caught that the empty-pet test was checking a hand-typed `[]` instead of what the Scheduler returned, and fixed it. All tests use a fixed date so they don't break depending on what day they run.

**b. Confidence**

- **How confident are you that your scheduler works correctly?**
  4 out of 5. Every algorithm has passing tests for both normal and edge cases, and the `main.py` demo shows them working across two pets. I'm not at 5 because the Streamlit UI isn't covered by automated tests.

- **What edge cases would you test next if you had more time?**
  Tasks that run past midnight (e.g., 23:50 for 30 minutes), which my scheduler currently doesn't handle. Completing a recurring task whose pet was removed (the follow-up is silently not created). And UI-level behavior: the backend now treats "luna" and "Luna" as the same pet, but there's no automated test that the Streamlit form actually shows the duplicate warning.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
