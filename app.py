"""Streamlit presentation layer; all scheduling decisions use the backend."""
from datetime import date, time
import streamlit as st
from pawpal_system import Owner, Pet, Scheduler, Task
from main import build_demo_owner

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Pet parent")
owner = st.session_state.owner
scheduler = Scheduler(owner)

st.title("🐾 PawPal+")
st.caption("A little planning. A happier pet. Your care routine, in one place.")
if "notice" in st.session_state:
    st.success(st.session_state.pop("notice"))

with st.sidebar:
    st.header("Your household")
    st.write(f"Owner: {owner.name}")
    with st.form("owner_form"):
        name = st.text_input("Owner name", value=owner.name, key="owner_name")
        if st.form_submit_button("Save owner"):
            if name.strip():
                owner.name = name.strip()
                st.session_state.notice = "Owner updated."
                st.rerun()
            else:
                st.error("Owner name is required.")
    if not owner.pets and st.button("Load demo household", key="load_demo"):
        st.session_state.owner = build_demo_owner(date.today())
        st.session_state.notice = "Demo household loaded."
        st.rerun()
    st.caption("Data stays during this session. A browser reload or server restart may clear it.")

left, right = st.columns(2)
with left:
    st.subheader("1. Add a pet")
    with st.form("pet_form", clear_on_submit=True):
        pet_name = st.text_input("Pet name", key="pet_name")
        species = st.text_input("Species", placeholder="Dog, cat, rabbit…", key="species")
        if st.form_submit_button("Add pet"):
            try:
                owner.add_pet(Pet(pet_name, species))
            except ValueError as exc:
                st.error(str(exc))
            else:
                st.session_state.notice = f"Added {pet_name.strip()}."
                st.rerun()
with right:
    st.subheader("2. Schedule care")
    if owner.pets:
        with st.form("task_form", clear_on_submit=True):
            chosen_pet = st.selectbox("Pet", [p.name for p in owner.pets], key="task_pet")
            description = st.text_input("Task description", key="description")
            due = st.date_input("Due date", value=date.today(), key="due")
            clock = st.time_input("Time", value=time(8), step=60, key="clock")
            frequency = st.selectbox("Frequency", ["once", "daily", "weekly"], key="frequency")
            if st.form_submit_button("Schedule task"):
                try:
                    scheduler.schedule_task(chosen_pet, Task(description, clock.strftime("%H:%M"), frequency, due))
                except ValueError as exc:
                    st.error(str(exc))
                else:
                    st.session_state.notice = "Care task scheduled."
                    st.rerun()
    else:
        st.info("Add your first pet to start scheduling care.")

st.divider()
st.subheader("3. Your schedule")
cols = st.columns(4)
pet_filter = cols[0].selectbox("Show pet", ["All pets"] + [p.name for p in owner.pets], key="filter_pet")
status = cols[1].selectbox("Status", ["Pending", "All", "Completed"], key="filter_status")
all_dates = cols[2].checkbox("Show all dates", key="all_dates")
selected_date = cols[3].date_input("Schedule date", date.today(), key="schedule_date", disabled=all_dates)
on_date = None if all_dates else selected_date
entries = scheduler.get_schedule(
    pet_name=None if pet_filter == "All pets" else pet_filter,
    completed={"Pending": False, "All": None, "Completed": True}[status], on_date=on_date)
for warning in scheduler.detect_conflicts(on_date=on_date):
    st.warning(warning)
st.caption("Warnings include all pets for the selected date range, even when a pet or status filter hides a task.")
if entries:
    st.table([{"Date": t.due_date.isoformat(), "Time": t.time, "Pet": p.name,
               "Care task": t.description, "Repeats": t.frequency,
               "Status": "Completed" if t.completed else "Pending"} for p, t in entries])
    for pet, task in entries:
        if not task.completed:
            label = f"Complete {pet.name}: {task.description} ({task.due_date} {task.time})"
            if st.button(label, key=f"complete_{task.task_id}"):
                successor = scheduler.mark_task_complete(task.task_id)
                st.session_state.notice = (f"Completed. Next occurrence: {successor.due_date} at {successor.time}."
                                           if successor else "Task completed.")
                st.rerun()
else:
    st.info("No tasks match these filters.")
st.caption("Daily and weekly tasks create their next occurrence when completed. Dates use the server's local calendar.")
