import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

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
3. **Generate schedule** — the Scheduler gathers tasks from every pet and shows today's plan.
"""
    )

st.divider()

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")

owner = st.session_state.owner

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
        if pet is not None:
            pet.add_task(
                Task(
                    description=task_title,
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
            "time": t.time,
            "task": t.description,
            "duration": t.duration_minutes,
            "priority": t.priority,
            "frequency": t.frequency,
            "done": t.completed,
        }
        for t in tasks
    ]


all_tasks = owner.get_all_tasks()
if all_tasks:
    st.write("Current tasks:")
    st.table(task_rows(all_tasks))
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generate today's schedule from all of the owner's pets' tasks.")

if st.button("Generate schedule"):
    scheduler = Scheduler(st.session_state.owner)
    todays = scheduler.get_todays_tasks()
    if todays:
        st.table(task_rows(todays))
    else:
        st.info("No tasks scheduled for today.")
