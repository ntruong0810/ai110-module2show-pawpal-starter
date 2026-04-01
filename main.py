#!/usr/bin/env python3
"""Terminal demo for sorting + filtering in PawPal+."""

from pawpal_system import Owner, Pet, Task, Scheduler, Priority, TaskStatus


def main() -> None:
    owner = Owner(
        name="Alice Johnson",
        available_minutes_per_day=120,
        preferences=["outdoor", "exercise", "bonding"],
    )

    max_dog = Pet(name="Max", pet_type="Dog")
    whiskers_cat = Pet(name="Whiskers", pet_type="Cat")

    # Intentionally add Max's tasks OUT OF TIME ORDER.
    task_evening = Task(
        name="Evening Walk",
        duration_minutes=25,
        priority=Priority.HIGH,
        required_for="Max",
        custom_time_frame_start="18:45",
    )
    task_morning = Task(
        name="Morning Feed",
        duration_minutes=10,
        priority=Priority.CRITICAL,
        required_for="Max",
        custom_time_frame_start="08:00",
        mandatory=True,
    )
    task_noon = Task(
        name="Noon Play",
        duration_minutes=20,
        priority=Priority.MEDIUM,
        required_for="Max",
        custom_time_frame_start="12:30",
    )

    max_dog.add_task(task_evening)
    max_dog.add_task(task_morning)
    max_dog.add_task(task_noon)

    whiskers_feed = Task(
        name="Cat Feeding",
        duration_minutes=10,
        priority=Priority.CRITICAL,
        required_for="Whiskers",
        custom_time_frame_start="07:30",
        mandatory=True,
    )
    whiskers_litter = Task(
        name="Litter Box",
        duration_minutes=8,
        priority=Priority.HIGH,
        required_for="Whiskers",
        custom_time_frame_start="20:00",
    )

    whiskers_cat.add_task(whiskers_feed)
    whiskers_cat.add_task(whiskers_litter)

    owner.add_pet(max_dog)
    owner.add_pet(whiskers_cat)

    scheduler = Scheduler()

    print("=" * 64)
    print("ORIGINAL TASK ORDER (MAX)")
    print("=" * 64)
    for t in max_dog.tasks:
        print(f"- {t.name}: {t.custom_time_frame_start}")

    print("\n" + "=" * 64)
    print("SORTED TASK ORDER (MAX) USING sort_by_time()")
    print("=" * 64)
    for t in scheduler.sort_by_time(max_dog.tasks):
        print(f"- {t.name}: {t.custom_time_frame_start}")

    # Mark a few tasks completed so filtering has visible output.
    task_morning.mark_completed()
    whiskers_feed.mark_completed()

    print("\n" + "=" * 64)
    print("FILTER: COMPLETED TASKS (ALL PETS)")
    print("=" * 64)
    for t in owner.filter_tasks(status=TaskStatus.COMPLETED):
        print(f"- {t.required_for}: {t.name} [{t.status.value}]")

    print("\n" + "=" * 64)
    print("FILTER: PENDING TASKS FOR PET = MAX")
    print("=" * 64)
    for t in owner.filter_tasks(status=TaskStatus.PENDING, pet_name="Max"):
        print(f"- {t.required_for}: {t.name} [{t.status.value}]")


if __name__ == "__main__":
    main()
