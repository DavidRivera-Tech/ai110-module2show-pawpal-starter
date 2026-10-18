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

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
