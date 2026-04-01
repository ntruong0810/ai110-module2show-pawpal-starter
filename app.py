import streamlit as st
import json
from pathlib import Path
from datetime import datetime, time, timedelta
from datetime import date as date_type
from pawpal_system import Owner, Pet, Task, Scheduler, Priority, TimeWindow
from pawpal_system import Frequency, TaskStatus

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.divider()

DATA_FILE = Path(__file__).with_name("pawpal_data.json")


def task_to_dict(task: Task) -> dict:
    return {
        "name": task.name,
        "duration_minutes": task.duration_minutes,
        "priority": task.priority.value,
        "required_for": task.required_for,
        "description": task.description,
        "time_window": task.time_window.value,
        "custom_time_frame_start": task.custom_time_frame_start,
        "custom_time_frame_end": task.custom_time_frame_end,
        "mandatory": task.mandatory,
        "frequency": task.frequency.value,
        "status": task.status.value,
        "due_date": task.due_date.isoformat() if task.due_date else None,
    }


def pet_to_dict(pet: Pet) -> dict:
    return {
        "name": pet.name,
        "pet_type": pet.pet_type,
        "tasks": [task_to_dict(task) for task in pet.tasks],
    }


def owner_to_dict(owner: Owner) -> dict:
    return {
        "name": owner.name,
        "available_minutes_per_day": owner.available_minutes_per_day,
        "preferences": owner.preferences,
        "pets": [pet_to_dict(pet) for pet in owner.pets],
    }


def _safe_priority(value: str) -> Priority:
    try:
        return Priority(value)
    except ValueError:
        return Priority.MEDIUM


def _safe_time_window(value: str) -> TimeWindow:
    try:
        return TimeWindow(value)
    except ValueError:
        return TimeWindow.ANY


def _safe_frequency(value: str) -> Frequency:
    try:
        return Frequency(value)
    except ValueError:
        return Frequency.ONCE


def _safe_status(value: str) -> TaskStatus:
    try:
        return TaskStatus(value)
    except ValueError:
        return TaskStatus.PENDING


def task_from_dict(data: dict, pet_name: str) -> Task:
    due_date_raw = data.get("due_date")
    parsed_due_date = None
    if isinstance(due_date_raw, str) and due_date_raw:
        try:
            parsed_due_date = date_type.fromisoformat(due_date_raw)
        except ValueError:
            parsed_due_date = None

    return Task(
        name=data.get("name", "Untitled Task"),
        duration_minutes=int(data.get("duration_minutes", 0)),
        priority=_safe_priority(data.get("priority", Priority.MEDIUM.value)),
        required_for=data.get("required_for", pet_name),
        description=data.get("description", ""),
        time_window=_safe_time_window(data.get("time_window", TimeWindow.ANY.value)),
        custom_time_frame_start=data.get("custom_time_frame_start", ""),
        custom_time_frame_end=data.get("custom_time_frame_end", ""),
        mandatory=bool(data.get("mandatory", False)),
        frequency=_safe_frequency(data.get("frequency", Frequency.ONCE.value)),
        status=_safe_status(data.get("status", TaskStatus.PENDING.value)),
        due_date=parsed_due_date,
    )


def owner_from_dict(data: dict) -> Owner:
    owner = Owner(
        name=data.get("name", "Jordan"),
        available_minutes_per_day=int(data.get("available_minutes_per_day", 120)),
        preferences=list(data.get("preferences", [])),
    )

    for pet_data in data.get("pets", []):
        pet = Pet(
            name=pet_data.get("name", "Unnamed Pet"),
            pet_type=pet_data.get("pet_type", "other"),
        )
        for task_data in pet_data.get("tasks", []):
            pet.add_task(task_from_dict(task_data, pet.name))
        owner.add_pet(pet)

    return owner


def save_owner_to_disk(owner: Owner) -> None:
    DATA_FILE.write_text(json.dumps(owner_to_dict(owner), indent=2), encoding="utf-8")


def load_owner_from_disk() -> Owner:
    if not DATA_FILE.exists():
        return Owner(name="Jordan", available_minutes_per_day=120, preferences=[])

    try:
        raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        return owner_from_dict(raw)
    except (json.JSONDecodeError, OSError, ValueError, TypeError):
        return Owner(name="Jordan", available_minutes_per_day=120, preferences=[])

if "owner" not in st.session_state:
    st.session_state.owner = load_owner_from_disk()

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()

owner: Owner = st.session_state.owner
scheduler: Scheduler = st.session_state.scheduler


def calculate_end_time(start_time: time, duration_minutes: int) -> time:
    start_datetime = datetime.combine(datetime.today(), start_time)
    end_datetime = start_datetime + timedelta(minutes=duration_minutes)
    return end_datetime.time()

st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner.name = st.text_input("Owner name", value=owner.name)
with col2:
    owner.available_minutes_per_day = st.number_input(
        "Available minutes/day", min_value=0, max_value=1440, value=owner.available_minutes_per_day
    )

st.subheader("Add a Pet")
with st.form("add_pet_form"):
    pet_name = st.text_input("Pet name", value="Mochi")
    pet_type = st.selectbox("Species", ["dog", "cat", "other"])
    add_pet_submitted = st.form_submit_button("Add pet")

if add_pet_submitted:
    if not pet_name.strip():
        st.error("Pet name is required.")
    elif owner.get_pet(pet_name.strip()) is not None:
        st.warning("A pet with this name already exists.")
    else:
        owner.add_pet(Pet(name=pet_name.strip(), pet_type=pet_type))
        st.success(f"Added pet: {pet_name.strip()}")

st.markdown("### Current Pets")
if owner.pets:
    st.table(
        [
            {
                "name": pet.name,
                "type": pet.pet_type,
                "tasks": len(pet.tasks),
            }
            for pet in owner.pets
        ]
    )
else:
    st.caption("No pets added yet.")

st.subheader("Schedule a Task")
if owner.pets:
    with st.form("add_task_form"):
        pet_names = [p.name for p in owner.pets]
        target_pet_name = st.selectbox("Pet", pet_names)
        task_title = st.text_input("Task title", value="Morning walk")
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority_label = st.selectbox("Priority", ["LOW", "MEDIUM", "HIGH", "CRITICAL"], index=2)
        st.caption("Choose a custom time frame for this task.")
        frame_start = st.time_input("Start time", value=time(8, 0))
        frame_end = calculate_end_time(frame_start, int(duration))
        description = st.text_input("Description", value="")
        mandatory = st.checkbox("Mandatory task", value=False)
        add_task_submitted = st.form_submit_button("Add task")

    if add_task_submitted:
        pet = owner.get_pet(target_pet_name)
        if pet is None:
            st.error("Selected pet not found.")
        elif not task_title.strip():
            st.error("Task title is required.")
        else:
            task = Task(
                name=task_title.strip(),
                duration_minutes=int(duration),
                priority=Priority[priority_label],
                required_for=pet.name,
                description=description.strip(),
                time_window=TimeWindow.ANY,
                custom_time_frame_start=frame_start.strftime("%H:%M"),
                custom_time_frame_end=frame_end.strftime("%H:%M"),
                mandatory=mandatory,
            )
            if owner.has_time_overlap(task):
                st.error("Task time overlaps with an existing pending task in your overall schedule.")
            else:
                pet.add_task(task)
                save_owner_to_disk(owner)
                st.success(f"Added task '{task.name}' to {pet.name}.")
else:
    st.info("Add at least one pet before creating tasks.")

st.markdown("### Current Pets & Tasks")
if owner.pets:
    for pet in owner.pets:
        st.markdown(f"**{pet.name}** ({pet.pet_type})")
        if pet.tasks:
            st.table(
                [
                    {
                        "title": t.name,
                        "duration_minutes": t.duration_minutes,
                        "priority": t.priority.value,
                        "time_window": t.display_time_frame(),
                        "mandatory": t.mandatory,
                        "status": t.status.value,
                    }
                    for t in pet.tasks
                ]
            )
        else:
            st.caption("No tasks yet.")
else:
    st.caption("No pets added yet.")

st.subheader("Update Task Status")
if owner.pets:
    pets_with_pending = [p for p in owner.pets if p.get_pending_tasks()]
    if pets_with_pending:
        with st.form("mark_task_complete_form"):
            selected_pet_name = st.selectbox("Pet (pending tasks)", [p.name for p in pets_with_pending])
            selected_pet = owner.get_pet(selected_pet_name)
            pending_task_names = [t.name for t in selected_pet.get_pending_tasks()] if selected_pet else []
            selected_task_name = st.selectbox("Pending task", pending_task_names)
            mark_complete_submitted = st.form_submit_button("Mark complete")

        if mark_complete_submitted:
            pet = owner.get_pet(selected_pet_name)
            if pet is None:
                st.error("Selected pet not found.")
            else:
                next_task = scheduler.mark_task_completed(pet, selected_task_name)
                if next_task is not None:
                    st.success(
                        f"Marked '{selected_task_name}' complete. "
                        f"Created next recurring task (due {next_task.due_date})."
                    )
                else:
                    st.success(f"Marked '{selected_task_name}' complete.")
    else:
        st.caption("No pending tasks to mark complete.")
else:
    st.caption("Add pets and tasks first.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generate daily plans using your Scheduler.")

if st.button("Generate schedule"):
    if not owner.pets:
        st.warning("Please add at least one pet.")
    elif len(owner.get_all_tasks()) == 0:
        st.warning("Please add at least one task.")
    else:
        plans = scheduler.generate_daily_plans(owner)
        st.success("Today's Schedule")
        for plan in plans:
            st.text(plan.summarize())
