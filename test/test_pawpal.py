"""
Unit tests for PawPal+ system.
Tests Task completion, Pet task management, and scheduling logic.
"""

import pytest
from pawpal_system import (
	Owner, Pet, Task, Plan, Scheduler,
	Priority, Frequency, TaskStatus
)


class TestTaskCompletion:
	"""Test task completion and status tracking."""

	def test_task_initial_status_is_pending(self):
		"""Verify that new tasks start with PENDING status."""
		task = Task(
			name="Feeding",
			duration_minutes=15,
			priority=Priority.HIGH,
			required_for="Max"
		)
		assert task.status == TaskStatus.PENDING
		assert task.status.value == "pending"

	def test_mark_completed_changes_status(self):
		"""Verify that calling mark_completed() changes task status to COMPLETED."""
		task = Task(
			name="Morning Walk",
			duration_minutes=30,
			priority=Priority.HIGH,
			required_for="Max",
			description="Daily walk"
		)
		
		# Initial state
		assert task.status == TaskStatus.PENDING
		
		# Mark as completed
		task.mark_completed()
		
		# Verify status changed
		assert task.status == TaskStatus.COMPLETED
		assert task.status.value == "completed"

	def test_mark_skipped_changes_status(self):
		"""Verify that calling mark_skipped() changes task status to SKIPPED."""
		task = Task(
			name="Playtime",
			duration_minutes=20,
			priority=Priority.MEDIUM,
			required_for="Max"
		)
		
		# Initial state
		assert task.status == TaskStatus.PENDING
		
		# Mark as skipped
		task.mark_skipped()
		
		# Verify status changed
		assert task.status == TaskStatus.SKIPPED
		assert task.status.value == "skipped"

	def test_task_can_transition_from_completed_to_skipped(self):
		"""Verify that task status can be changed multiple times."""
		task = Task(
			name="Test Task",
			duration_minutes=10,
			priority=Priority.LOW,
			required_for="Max"
		)
		
		# Transition: pending -> completed -> skipped
		assert task.status == TaskStatus.PENDING
		task.mark_completed()
		assert task.status == TaskStatus.COMPLETED
		task.mark_skipped()
		assert task.status == TaskStatus.SKIPPED

	def test_is_feasible_returns_true_when_fits_time(self):
		"""Verify is_feasible() returns True when task fits in available time."""
		task = Task(
			name="Quick Task",
			duration_minutes=15,
			priority=Priority.LOW,
			required_for="Max"
		)
		
		assert task.is_feasible(30) is True
		assert task.is_feasible(15) is True  # Exact fit
		assert task.is_feasible(20) is True  # More time than needed

	def test_is_feasible_returns_false_when_exceeds_time(self):
		"""Verify is_feasible() returns False when task exceeds available time."""
		task = Task(
			name="Long Task",
			duration_minutes=30,
			priority=Priority.HIGH,
			required_for="Max"
		)
		
		assert task.is_feasible(20) is False
		assert task.is_feasible(29) is False
		assert task.is_feasible(0) is False


class TestPetTaskManagement:
	"""Test adding/removing tasks from Pet."""

	def test_pet_starts_with_empty_task_list(self):
		"""Verify that new Pet has no tasks initially."""
		pet = Pet(name="Max", pet_type="Dog")
		assert len(pet.tasks) == 0
		assert pet.tasks == []

	def test_add_single_task_increases_count(self):
		"""Verify that adding one task increases task count to 1."""
		pet = Pet(name="Max", pet_type="Dog")
		task = Task(
			name="Feeding",
			duration_minutes=15,
			priority=Priority.CRITICAL,
			required_for="Max"
		)
		
		# Initial count
		assert len(pet.tasks) == 0
		
		# Add task
		pet.add_task(task)
		
		# Verify count increased
		assert len(pet.tasks) == 1
		assert pet.tasks[0] == task

	def test_add_multiple_tasks_increases_count(self):
		"""Verify that adding multiple tasks increases count correctly."""
		pet = Pet(name="Max", pet_type="Dog")
		
		task1 = Task("Feeding", 15, Priority.CRITICAL, "Max")
		task2 = Task("Morning Walk", 30, Priority.HIGH, "Max")
		task3 = Task("Playtime", 20, Priority.MEDIUM, "Max")
		
		# Add tasks one by one
		pet.add_task(task1)
		assert len(pet.tasks) == 1
		
		pet.add_task(task2)
		assert len(pet.tasks) == 2
		
		pet.add_task(task3)
		assert len(pet.tasks) == 3

	def test_tasks_are_stored_in_pet(self):
		"""Verify that tasks are actually stored in pet.tasks list."""
		pet = Pet(name="Whiskers", pet_type="Cat")
		task = Task("Feed Cat", 10, Priority.CRITICAL, "Whiskers")
		
		pet.add_task(task)
		
		# Verify task is in the list
		assert task in pet.tasks
		assert pet.tasks[0].name == "Feed Cat"
		assert pet.tasks[0].duration_minutes == 10

	def test_remove_task_by_name_decreases_count(self):
		"""Verify that removing a task decreases task count."""
		pet = Pet(name="Max", pet_type="Dog")
		task1 = Task("Feeding", 15, Priority.CRITICAL, "Max")
		task2 = Task("Walking", 30, Priority.HIGH, "Max")
		
		pet.add_task(task1)
		pet.add_task(task2)
		assert len(pet.tasks) == 2
		
		# Remove one task
		result = pet.remove_task("Feeding")
		
		# Verify removal
		assert result is True
		assert len(pet.tasks) == 1
		assert pet.tasks[0].name == "Walking"

	def test_remove_nonexistent_task_returns_false(self):
		"""Verify that removing nonexistent task returns False."""
		pet = Pet(name="Max", pet_type="Dog")
		task = Task("Feeding", 15, Priority.CRITICAL, "Max")
		pet.add_task(task)
		
		# Try to remove task that doesn't exist
		result = pet.remove_task("Nonexistent Task")
		
		# Verify no change
		assert result is False
		assert len(pet.tasks) == 1

	def test_get_pending_tasks(self):
		"""Verify get_pending_tasks() returns only pending tasks."""
		pet = Pet(name="Max", pet_type="Dog")
		
		task1 = Task("Feeding", 15, Priority.CRITICAL, "Max")
		task2 = Task("Walking", 30, Priority.HIGH, "Max")
		task3 = Task("Playtime", 20, Priority.MEDIUM, "Max")
		
		pet.add_task(task1)
		pet.add_task(task2)
		pet.add_task(task3)
		
		# Mark some as completed
		task1.mark_completed()
		task2.mark_completed()
		
		# Get pending
		pending = pet.get_pending_tasks()
		
		assert len(pending) == 1
		assert pending[0] == task3

	def test_total_daily_minutes(self):
		"""Verify total_daily_minutes() sums pending task durations."""
		pet = Pet(name="Max", pet_type="Dog")
		
		task1 = Task("Feeding", 15, Priority.CRITICAL, "Max")  # pending
		task2 = Task("Walking", 30, Priority.HIGH, "Max")       # pending
		task3 = Task("Playtime", 20, Priority.MEDIUM, "Max")    # will be completed
		
		pet.add_task(task1)
		pet.add_task(task2)
		pet.add_task(task3)
		
		# Mark one as completed
		task3.mark_completed()
		
		# Total should only count pending: 15 + 30 = 45
		assert pet.total_daily_minutes() == 45


class TestSchedulerLogic:
	"""Test Scheduler's planning and sorting logic."""

	def test_scheduler_generates_plans_for_all_pets(self):
		"""Verify scheduler generates one plan per pet."""
		owner = Owner("Alice", 120)
		
		dog = Pet("Max", "Dog")
		cat = Pet("Whiskers", "Cat")
		
		dog_task = Task("Walk", 30, Priority.HIGH, "Max", mandatory=True)
		cat_task = Task("Feed", 10, Priority.CRITICAL, "Whiskers", mandatory=True)
		
		dog.add_task(dog_task)
		cat.add_task(cat_task)
		
		owner.add_pet(dog)
		owner.add_pet(cat)
		
		scheduler = Scheduler()
		plans = scheduler.generate_daily_plans(owner)
		
		# Should have one plan per pet
		assert len(plans) == 2
		assert plans[0].pet.name == "Max"
		assert plans[1].pet.name == "Whiskers"

	def test_mandatory_tasks_are_prioritized(self):
		"""Verify that mandatory tasks are included in plan before optional ones."""
		owner = Owner("Alice", 60)  # Limited time
		pet = Pet("Max", "Dog")
		
		# Mandatory task (should fit)
		mandatory = Task("Feeding", 20, Priority.HIGH, "Max", mandatory=True)
		# Optional task (might not fit)
		optional = Task("Playtime", 50, Priority.MEDIUM, "Max", mandatory=False)
		
		pet.add_task(mandatory)
		pet.add_task(optional)
		owner.add_pet(pet)
		
		scheduler = Scheduler()
		plans = scheduler.generate_daily_plans(owner)
		
		# Should only have mandatory task (20 min fits, but 20+50=70 > 60)
		assert len(plans[0].tasks) == 1
		assert plans[0].tasks[0].name == "Feeding"

	def test_task_scoring_by_preference(self):
		"""Verify task scoring considers owner preferences."""
		task = Task(
			name="Outdoor Walk",
			duration_minutes=30,
			priority=Priority.HIGH,
			required_for="Max",
			description="Exercise in the park"
		)
		
		# With matching preferences
		prefs = ["outdoor", "exercise"]
		score = task.score_for_owner(prefs)
		
		# Should have positive score due to preference matches
		assert score > 0
		
		# Without matching preferences
		prefs_no_match = ["swimming", "flying"]
		score_no_match = task.score_for_owner(prefs_no_match)
		
		# Score should be lower without preference matches
		assert score > score_no_match

	def test_critical_priority_gets_highest_score(self):
		"""Verify critical tasks get highest priority score."""
		critical_task = Task("Medication", 10, Priority.CRITICAL, "Max")
		high_task = Task("Grooming", 20, Priority.HIGH, "Max")
		medium_task = Task("Playtime", 20, Priority.MEDIUM, "Max")
		low_task = Task("Extra Walk", 30, Priority.LOW, "Max")
		
		# Score without preferences (just priority)
		critical_score = critical_task.score_for_owner([])
		high_score = high_task.score_for_owner([])
		medium_score = medium_task.score_for_owner([])
		low_score = low_task.score_for_owner([])
		
		# Higher priority = higher score
		assert critical_score > high_score
		assert high_score > medium_score
		assert medium_score > low_score

	def test_mandatory_tasks_get_score_boost(self):
		"""Verify mandatory tasks get a scoring boost."""
		mandatory_task = Task("Feeding", 15, Priority.HIGH, "Max", mandatory=True)
		optional_task = Task("Feeding", 15, Priority.HIGH, "Max", mandatory=False)
		
		prefs = []  # No preferences
		
		mandatory_score = mandatory_task.score_for_owner(prefs)
		optional_score = optional_task.score_for_owner(prefs)
		
		# Mandatory should have higher score
		assert mandatory_score > optional_score
		# The difference should be the mandatory boost (+2)
		assert mandatory_score - optional_score == 2


class TestOwnerTaskAccess:
	"""Test Owner's ability to access all pet tasks."""

	def test_owner_get_all_tasks(self):
		"""Verify owner can retrieve all tasks across all pets."""
		owner = Owner("Alice", 120)
		
		dog = Pet("Max", "Dog")
		cat = Pet("Whiskers", "Cat")
		
		dog_task1 = Task("Walk", 30, Priority.HIGH, "Max")
		dog_task2 = Task("Feed", 15, Priority.CRITICAL, "Max")
		cat_task1 = Task("Feed", 10, Priority.CRITICAL, "Whiskers")
		
		dog.add_task(dog_task1)
		dog.add_task(dog_task2)
		cat.add_task(cat_task1)
		
		owner.add_pet(dog)
		owner.add_pet(cat)
		
		# Get all tasks
		all_tasks = owner.get_all_tasks()
		
		assert len(all_tasks) == 3
		assert dog_task1 in all_tasks
		assert dog_task2 in all_tasks
		assert cat_task1 in all_tasks

	def test_owner_can_fit_all_tasks(self):
		"""Verify owner can check if all tasks fit in available time."""
		owner = Owner("Alice", 100)
		
		pet = Pet("Max", "Dog")
		task1 = Task("Walk", 30, Priority.HIGH, "Max")
		task2 = Task("Feed", 20, Priority.CRITICAL, "Max")
		task3 = Task("Play", 40, Priority.MEDIUM, "Max")  # 30+20+40 = 90, fits in 100
		
		pet.add_task(task1)
		pet.add_task(task2)
		pet.add_task(task3)
		owner.add_pet(pet)
		
		assert owner.can_fit_all_tasks() is True

	def test_owner_cannot_fit_all_tasks(self):
		"""Verify owner detects when tasks exceed available time."""
		owner = Owner("Alice", 50)
		
		pet = Pet("Max", "Dog")
		task1 = Task("Walk", 30, Priority.HIGH, "Max")
		task2 = Task("Feed", 20, Priority.CRITICAL, "Max")
		task3 = Task("Play", 20, Priority.MEDIUM, "Max")  # 30+20+20 = 70 > 50
		
		pet.add_task(task1)
		pet.add_task(task2)
		pet.add_task(task3)
		owner.add_pet(pet)
		
		assert owner.can_fit_all_tasks() is False


class TestPlanManagement:
	"""Test Plan task management and summarization."""

	def test_plan_add_task_updates_total_minutes(self):
		"""Verify adding tasks to Plan updates total_minutes correctly."""
		plan = Plan()
		
		task1 = Task("Walk", 30, Priority.HIGH, "Max")
		task2 = Task("Feed", 15, Priority.CRITICAL, "Max")
		
		assert plan.total_minutes == 0
		
		plan.add_task(task1)
		assert plan.total_minutes == 30
		
		plan.add_task(task2)
		assert plan.total_minutes == 45

	def test_plan_remove_task_updates_total_minutes(self):
		"""Verify removing tasks from Plan updates total_minutes correctly."""
		plan = Plan()
		
		task1 = Task("Walk", 30, Priority.HIGH, "Max")
		task2 = Task("Feed", 15, Priority.CRITICAL, "Max")
		
		plan.add_task(task1)
		plan.add_task(task2)
		assert plan.total_minutes == 45
		
		plan.remove_task("Walk")
		assert plan.total_minutes == 15
		
		plan.remove_task("Feed")
		assert plan.total_minutes == 0

	def test_plan_summarize_returns_string(self):
		"""Verify plan.summarize() returns a formatted string."""
		owner = Owner("Alice", 120)
		pet = Pet("Max", "Dog")
		plan = Plan(owner=owner, pet=pet)
		
		task = Task("Walk", 30, Priority.HIGH, "Max")
		plan.add_task(task)
		
		summary = plan.summarize()
		
		assert isinstance(summary, str)
		assert "Max" in summary
		assert "Walk" in summary
		assert "30" in summary


if __name__ == "__main__":
	pytest.main([__file__, "-v"])
