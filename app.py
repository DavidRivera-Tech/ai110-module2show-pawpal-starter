import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task, time_to_minutes

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
PawPal+ helps a busy pet owner plan daily care across **all** of their pets.
Add your pets, schedule tasks (walks, feeding, meds, play), and generate today's plan.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.
"""
    )

with st.expander("How it works", expanded=False):
    st.markdown(
        """
1. **Add a pet** — give it a name and species.
2. **Add tasks** — pick the pet, set a time, duration, priority, and how often it repeats.
3. **Today's Schedule** — updates live: tasks from every pet, sorted by time, with filters and conflict warnings.
4. **Mark a task complete** — daily and weekly tasks automatically schedule their next occurrence.
"""
    )

st.divider()

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")

owner = st.session_state.owner
scheduler = Scheduler(owner)

st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)

st.divider()

st.subheader("Add a Pet")
col1, col2 = st.columns(2)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    if not pet_name.strip():
        st.warning("Please enter a pet name.")
    elif owner.get_pet(pet_name.strip()) is not None:
        st.warning(f"A pet named {pet_name.strip()} already exists.")
    else:
        owner.add_pet(Pet(pet_name.strip(), species))
        st.success(f"Added {pet_name.strip()} the {species}.")

if owner.pets:
    st.write("Current pets:")
    for pet in owner.pets:
        st.write(f"- {pet.name} ({pet.species})")
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Add a Task")
if not owner.pets:
    st.info("Add a pet first.")
else:
    selected_pet = st.selectbox("Pet", [p.name for p in owner.pets])
    col1, col2 = st.columns(2)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
        task_time = st.time_input("Time")
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col2:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])

    if st.button("Add task"):
        pet = owner.get_pet(selected_pet)
        if not task_title.strip():
            st.warning("Please enter a task title.")
        elif pet is not None:
            pet.add_task(
                Task(
                    description=task_title.strip(),
                    time=task_time.strftime("%H:%M"),
                    duration_minutes=int(duration),
                    priority=priority,
                    frequency=frequency,
                )
            )
            st.success(f"Added '{task_title}' for {pet.name}.")


def task_rows(tasks):
    return [
        {
            "pet": t.pet_name,
            "due": t.due_date,
            "time": t.time,
            "task": t.description,
            "duration": t.duration_minutes,
            "priority": t.priority,
            "frequency": t.frequency,
            "done": t.completed,
        }
        for t in tasks
    ]


all_tasks = sorted(owner.get_all_tasks(), key=lambda t: (t.due_date, time_to_minutes(t.time)))
if all_tasks:
    st.write("Current tasks:")
    st.table(task_rows(all_tasks))
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Today's Schedule")
today_tasks = scheduler.get_todays_tasks()

col1, col2, col3 = st.columns(3)
with col1:
    pet_filter = st.selectbox("Filter by pet", ["All pets"] + [p.name for p in owner.pets])
with col2:
    status_filter = st.selectbox("Filter by status", ["All", "Pending", "Done"])
with col3:
    sort_choice = st.selectbox("Sort by", ["Time", "Priority, then time"])

filtered = today_tasks
if pet_filter != "All pets":
    filtered = scheduler.filter_by_pet(filtered, pet_filter)
if status_filter == "Pending":
    filtered = scheduler.filter_by_status(filtered, False)
elif status_filter == "Done":
    filtered = scheduler.filter_by_status(filtered, True)

if filtered:
    if sort_choice == "Priority, then time":
        ordered = scheduler.sort_by_priority(filtered)
    else:
        ordered = scheduler.sort_by_time(filtered)
    st.table(task_rows(ordered))
else:
    st.info("No tasks to show for today.")

conflicts = scheduler.detect_conflicts(today_tasks)
if conflicts:
    for message in conflicts:
        st.warning(f"{message} — consider moving one of these tasks.")
elif today_tasks:
    st.success("No scheduling conflicts today.")

st.divider()

st.subheader("Mark a Task Complete")
if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"))

pending = scheduler.sort_by_time(scheduler.filter_by_status(today_tasks, False))
if not pending:
    st.info("No pending tasks today.")
else:
    choice = st.selectbox(
        "Pending task",
        range(len(pending)),
        format_func=lambda i: f"{pending[i].time} - {pending[i].pet_name} - {pending[i].description}",
    )
    if st.button("Mark complete"):
        nxt = scheduler.mark_task_complete(pending[choice])
        if nxt is not None:
            st.session_state.flash = f"Done! Next '{nxt.description}' scheduled for {nxt.due_date}."
        else:
            st.session_state.flash = "Done!"
        st.rerun()
