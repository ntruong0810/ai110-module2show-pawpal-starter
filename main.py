#!/usr/bin/env python3
"""
PawPal+ Main Script
Demonstrates the pet care scheduling system with Owner, Pets, Tasks, and Scheduler.
"""

from pawpal_system import Owner, Pet, Task, Scheduler, Priority, Frequency, TaskStatus


def main():
	"""Create a sample pet care scenario and generate daily schedules."""
	
	# Create an Owner
	print("="*70)
	print("PawPal+ DAILY SCHEDULER")
	print("="*70)
	print()
	
	owner = Owner(
		name="Alice Johnson",
		available_minutes_per_day=120,
		preferences=["outdoor", "exercise", "bonding"]
	)
	print(f"✓ Created Owner: {owner.name}")
	print(f"  Available time: {owner.available_minutes_per_day} minutes/day")
	print(f"  Preferences: {', '.join(owner.preferences)}")
	print()
	
	# Create Pet 1: Max (Dog)
	max_dog = Pet(
		name="Max",
		pet_type="Dog",
		age_years=3,
		weight_lbs=45.5,
		needs=["exercise", "water", "food", "attention"]
	)
	
	# Add tasks for Max
	max_task1 = Task(
		name="Morning Walk",
		duration_minutes=30,
		priority=Priority.HIGH,
		required_for="Max",
		description="Outdoor walk for exercise and bonding",
		preferred_window="morning",
		mandatory=True,
		frequency=Frequency.DAILY
	)
	
	max_task2 = Task(
		name="Feeding",
		duration_minutes=15,
		priority=Priority.CRITICAL,
		required_for="Max",
		description="Feed Max dry kibble and fresh water",
		preferred_window="any",
		mandatory=True,
		frequency=Frequency.DAILY
	)
	
	max_task3 = Task(
		name="Playtime",
		duration_minutes=20,
		priority=Priority.MEDIUM,
		required_for="Max",
		description="Interactive play with toys for mental stimulation",
		preferred_window="afternoon",
		mandatory=False,
		frequency=Frequency.DAILY
	)
	
	max_dog.add_task(max_task1)
	max_dog.add_task(max_task2)
	max_dog.add_task(max_task3)
	owner.add_pet(max_dog)
	
	print(f"✓ Created Pet: {max_dog}")
	print(f"  Tasks added: {len(max_dog.tasks)}")
	for task in max_dog.tasks:
		print(f"    - {task.name} ({task.duration_minutes} min, {task.priority.value})")
	print()
	
	# Create Pet 2: Whiskers (Cat)
	whiskers_cat = Pet(
		name="Whiskers",
		pet_type="Cat",
		age_years=5,
		weight_lbs=8.2,
		needs=["feeding", "litter box", "grooming"]
	)
	
	# Add tasks for Whiskers
	whiskers_task1 = Task(
		name="Feed Cat",
		duration_minutes=10,
		priority=Priority.CRITICAL,
		required_for="Whiskers",
		description="Feed Whiskers wet and dry food",
		preferred_window="morning",
		mandatory=True,
		frequency=Frequency.DAILY
	)
	
	whiskers_task2 = Task(
		name="Clean Litter Box",
		duration_minutes=5,
		priority=Priority.HIGH,
		required_for="Whiskers",
		description="Scoop and refresh litter",
		preferred_window="any",
		mandatory=True,
		frequency=Frequency.DAILY
	)
	
	whiskers_task3 = Task(
		name="Grooming",
		duration_minutes=15,
		priority=Priority.MEDIUM,
		required_for="Whiskers",
		description="Brush fur and check for mats",
		preferred_window="evening",
		mandatory=False,
		frequency=Frequency.WEEKLY
	)
	
	whiskers_cat.add_task(whiskers_task1)
	whiskers_cat.add_task(whiskers_task2)
	whiskers_cat.add_task(whiskers_task3)
	owner.add_pet(whiskers_cat)
	
	print(f"✓ Created Pet: {whiskers_cat}")
	print(f"  Tasks added: {len(whiskers_cat.tasks)}")
	for task in whiskers_cat.tasks:
		print(f"    - {task.name} ({task.duration_minutes} min, {task.priority.value})")
	print()
	
	# Create Pet 3: Rocky (Guinea Pig)
	rocky_guinea = Pet(
		name="Rocky",
		pet_type="Guinea Pig",
		age_years=2,
		weight_lbs=2.5,
		needs=["hay", "vegetables", "water", "cage cleaning"]
	)
	
	# Add tasks for Rocky
	rocky_task1 = Task(
		name="Feed Rocky",
		duration_minutes=10,
		priority=Priority.CRITICAL,
		required_for="Rocky",
		description="Fresh hay, vegetables, and water",
		preferred_window="morning",
		mandatory=True,
		frequency=Frequency.DAILY
	)
	
	rocky_task2 = Task(
		name="Cage Cleaning",
		duration_minutes=20,
		priority=Priority.HIGH,
		required_for="Rocky",
		description="Weekly deep clean of cage and bedding",
		preferred_window="weekend",
		mandatory=True,
		frequency=Frequency.WEEKLY
	)
	
	rocky_guinea.add_task(rocky_task1)
	rocky_guinea.add_task(rocky_task2)
	owner.add_pet(rocky_guinea)
	
	print(f"✓ Created Pet: {rocky_guinea}")
	print(f"  Tasks added: {len(rocky_guinea.tasks)}")
	for task in rocky_guinea.tasks:
		print(f"    - {task.name} ({task.duration_minutes} min, {task.priority.value})")
	print()
	
	# Display owner summary
	print(owner.owner_summary())
	
	# Create Scheduler and generate plans
	scheduler = Scheduler()
	plans = scheduler.generate_daily_plans(owner)
	
	print("\n" + "="*70)
	print("TODAY'S SCHEDULE")
	print("="*70)
	
	for plan in plans:
		print(plan.summarize())
	
	# Display overall schedule report
	print(scheduler.get_schedule_report(owner))
	
	# Demonstrate task completion tracking
	print("\n" + "="*70)
	print("COMPLETING TASKS...")
	print("="*70 + "\n")
	
	max_task1.mark_completed()
	max_task2.mark_completed()
	whiskers_task1.mark_completed()
	
	print(f"✓ {max_task1.name}: {max_task1.status.value}")
	print(f"✓ {max_task2.name}: {max_task2.status.value}")
	print(f"✓ {whiskers_task1.name}: {whiskers_task1.status.value}")
	print()
	
	# Show updated summary
	print("UPDATED TASK STATUS:")
	for pet in owner.pets:
		completed = len(pet.get_tasks_by_status(TaskStatus.COMPLETED))
		pending = len(pet.get_pending_tasks())
		print(f"  {pet.name}: {completed} completed, {pending} pending")
	
	print()


if __name__ == "__main__":
	main()
