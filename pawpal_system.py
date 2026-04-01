from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Priority(Enum):
	LOW = "low"
	MEDIUM = "medium"
	HIGH = "high"
	CRITICAL = "critical"


class Frequency(Enum):
	"""How often a task should be done."""
	ONCE = "once"
	DAILY = "daily"
	WEEKLY = "weekly"
	AS_NEEDED = "as_needed"


class TaskStatus(Enum):
	"""Completion status of a task."""
	PENDING = "pending"
	COMPLETED = "completed"
	SKIPPED = "skipped"


@dataclass
class Owner:
	name: str
	available_minutes_per_day: int
	preferences: list[str] = field(default_factory=list)
	pets: list[Pet] = field(default_factory=list)

	def add_pet(self, pet: Pet) -> None:
		"""Add a pet to the owner's care."""
		self.pets.append(pet)

	def remove_pet(self, pet_name: str) -> bool:
		"""Remove a pet by name. Returns True if removed, False if not found."""
		for i, pet in enumerate(self.pets):
			if pet.name == pet_name:
				self.pets.pop(i)
				return True
		return False

	def get_pet(self, pet_name: str) -> Pet | None:
		"""Get a specific pet by name."""
		for pet in self.pets:
			if pet.name == pet_name:
				return pet
		return None

	def get_all_tasks(self) -> list[Task]:
		"""Get all tasks across all pets."""
		all_tasks = []
		for pet in self.pets:
			all_tasks.extend(pet.tasks)
		return all_tasks

	def get_pending_tasks(self) -> list[Task]:
		"""Get all pending tasks across all pets."""
		return [t for t in self.get_all_tasks() if t.status == TaskStatus.PENDING]

	def get_tasks_by_priority(self, priority: Priority) -> list[Task]:
		"""Get all tasks of a specific priority across all pets."""
		return [t for t in self.get_all_tasks() if t.priority == priority]

	def get_critical_tasks(self) -> list[Task]:
		"""Get all critical priority tasks across all pets."""
		return self.get_tasks_by_priority(Priority.CRITICAL)

	def get_mandatory_tasks(self) -> list[Task]:
		"""Get all mandatory tasks across all pets."""
		return [t for t in self.get_all_tasks() if t.mandatory]

	def total_daily_minutes_needed(self) -> int:
		"""Calculate total minutes needed for all pending tasks across all pets."""
		return sum(t.duration_minutes for t in self.get_pending_tasks())

	def time_available(self) -> int:
		"""Return available minutes per day."""
		return self.available_minutes_per_day

	def can_fit_all_tasks(self) -> bool:
		"""Check if all pending tasks can fit within available time."""
		return self.total_daily_minutes_needed() <= self.available_minutes_per_day

	def daily_workload_percentage(self) -> float:
		"""Calculate what percentage of available time is needed for all pending tasks."""
		if self.available_minutes_per_day == 0:
			return 0.0
		return (self.total_daily_minutes_needed() / self.available_minutes_per_day) * 100

	def owner_summary(self) -> str:
		"""Return a comprehensive summary of the owner's pet care situation."""
		all_tasks = self.get_all_tasks()
		pending_tasks = self.get_pending_tasks()
		critical_tasks = self.get_critical_tasks()
		total_minutes = self.total_daily_minutes_needed()
		workload_pct = self.daily_workload_percentage()
		
		summary = f"\n{self.name}'s Pet Care Dashboard\n"
		summary += f"{'='*50}\n"
		summary += f"Number of pets: {len(self.pets)}\n"
		summary += f"Total tasks: {len(all_tasks)}\n"
		summary += f"Pending tasks: {len(pending_tasks)}\n"
		summary += f"Critical tasks: {len(critical_tasks)}\n\n"
		
		summary += f"Time Available: {self.available_minutes_per_day} minutes/day\n"
		summary += f"Time Needed: {total_minutes} minutes/day\n"
		summary += f"Workload: {workload_pct:.1f}%\n"
		summary += f"Feasible: {'✓ Yes' if self.can_fit_all_tasks() else '✗ No - Need to prioritize'}\n\n"
		
		summary += "Pets:\n"
		for pet in self.pets:
			summary += f"  - {pet.name} ({pet.pet_type}): {len(pet.get_pending_tasks())} pending tasks\n"
		
		summary += f"\nPreferences: {', '.join(self.preferences) if self.preferences else 'None specified'}\n"
		
		return summary

	def __str__(self) -> str:
		"""Return readable representation of owner."""
		return f"{self.name} (Pets: {len(self.pets)}, Available: {self.available_minutes_per_day} min/day)"


@dataclass
class Pet:
	name: str
	pet_type: str
	needs: list[str] = field(default_factory=list)
	tasks: list[Task] = field(default_factory=list)
	age_years: int = 0
	weight_lbs: float = 0.0

	def add_task(self, task: Task) -> None:
		"""Add a task to the pet's task list."""
		self.tasks.append(task)

	def remove_task(self, task_name: str) -> bool:
		"""Remove a task by name. Returns True if removed, False if not found."""
		for i, task in enumerate(self.tasks):
			if task.name == task_name:
				self.tasks.pop(i)
				return True
		return False

	def get_tasks_by_priority(self, priority: Priority) -> list[Task]:
		"""Get all tasks of a specific priority level."""
		return [t for t in self.tasks if t.priority == priority]

	def get_tasks_by_status(self, status: TaskStatus) -> list[Task]:
		"""Get all tasks with a specific completion status."""
		return [t for t in self.tasks if t.status == status]

	def get_pending_tasks(self) -> list[Task]:
		"""Get all pending (not yet completed) tasks."""
		return self.get_tasks_by_status(TaskStatus.PENDING)

	def get_mandatory_tasks(self) -> list[Task]:
		"""Get all mandatory tasks for this pet."""
		return [t for t in self.tasks if t.mandatory]

	def total_daily_minutes(self) -> int:
		"""Calculate total minutes needed for all pending tasks."""
		return sum(t.duration_minutes for t in self.get_pending_tasks())

	def daily_summary(self) -> str:
		"""Return a summary of the pet's daily care requirements."""
		pending = self.get_pending_tasks()
		total_minutes = self.total_daily_minutes()
		
		summary = f"\n{self.name} ({self.pet_type}) - Daily Care Summary\n"
		summary += f"{'='*50}\n"
		summary += f"Total pending tasks: {len(pending)}\n"
		summary += f"Total time required: {total_minutes} minutes\n"
		summary += f"Needs: {', '.join(self.needs) if self.needs else 'None specified'}\n\n"
		
		if pending:
			summary += "Tasks:\n"
			for task in pending:
				summary += f"  - {task.name}: {task.duration_minutes} min ({task.priority.value})\n"
		else:
			summary += "No pending tasks!\n"
		
		return summary

	def __str__(self) -> str:
		"""Return readable representation of pet."""
		return f"{self.name} (Age: {self.age_years}, Weight: {self.weight_lbs} lbs, Type: {self.pet_type})"


@dataclass
class Task:
	name: str
	duration_minutes: int
	priority: Priority
	required_for: str
	description: str = ""
	preferred_window: str = ""  # e.g., "morning", "evening", "any"
	mandatory: bool = False
	frequency: Frequency = Frequency.ONCE
	status: TaskStatus = TaskStatus.PENDING

	def is_feasible(self, remaining_minutes: int) -> bool:
		"""Check if task fits within available time budget."""
		return self.duration_minutes <= remaining_minutes

	def score_for_owner(self, owner_preferences: list[str]) -> int:
		"""
		Score this task based on owner preferences and priority.
		
		Returns a score where higher = better match.
		Considers:
		- Priority level (critical=4, high=3, medium=2, low=1)
		- Whether task is mandatory (mandatory +2)
		- Whether task relates to owner preferences (+3 per match)
		"""
		score = 0
		
		# Base priority score
		priority_scores = {
			Priority.LOW: 1,
			Priority.MEDIUM: 2,
			Priority.HIGH: 3,
			Priority.CRITICAL: 4,
		}
		score += priority_scores.get(self.priority, 0)
		
		# Mandatory tasks get a boost
		if self.mandatory:
			score += 2
		
		# Check for preference matches
		for pref in owner_preferences:
			if pref.lower() in self.name.lower() or pref.lower() in self.description.lower():
				score += 3
		
		return score

	def mark_completed(self) -> None:
		"""Mark task as completed."""
		self.status = TaskStatus.COMPLETED

	def mark_skipped(self) -> None:
		"""Mark task as skipped."""
		self.status = TaskStatus.SKIPPED

	def __str__(self) -> str:
		"""Return readable representation of task."""
		return f"{self.name} ({self.duration_minutes} min, {self.priority.value}, {self.status.value})"


@dataclass
class Plan:
	tasks: list[Task] = field(default_factory=list)
	total_minutes: int = 0
	explanation: str = ""
	owner: Owner | None = None
	pet: Pet | None = None

	def add_task(self, task: Task) -> None:
		"""Add task to plan and update total_minutes."""
		self.tasks.append(task)
		self.total_minutes += task.duration_minutes

	def remove_task(self, task_name: str) -> bool:
		"""Remove a task from plan by name. Returns True if removed, False if not found."""
		for i, task in enumerate(self.tasks):
			if task.name == task_name:
				self.total_minutes -= task.duration_minutes
				self.tasks.pop(i)
				return True
		return False

	def summarize(self) -> str:
		"""Return human-readable summary of the plan."""
		summary = f"\n{'='*60}\n"
		summary += f"DAILY PLAN FOR {self.pet.name if self.pet else 'Unknown'}\n"
		summary += f"{'='*60}\n"
		summary += f"Owner: {self.owner.name if self.owner else 'Unknown'}\n"
		summary += f"Total scheduled tasks: {len(self.tasks)}\n"
		summary += f"Total time allocated: {self.total_minutes} minutes\n"
		summary += f"Available time: {self.owner.available_minutes_per_day if self.owner else 0} minutes\n\n"
		
		if self.tasks:
			summary += "SCHEDULED TASKS:\n"
			summary += "-" * 60 + "\n"
			for i, task in enumerate(self.tasks, 1):
				summary += f"{i}. {task.name}\n"
				summary += f"   Duration: {task.duration_minutes} min | Priority: {task.priority.value}\n"
				summary += f"   Description: {task.description}\n"
				summary += f"   Window: {task.preferred_window if task.preferred_window else 'Any time'}\n"
				summary += f"   Status: {task.status.value}\n\n"
		else:
			summary += "No tasks scheduled.\n\n"
		
		if self.explanation:
			summary += "SCHEDULING NOTES:\n"
			summary += "-" * 60 + "\n"
			summary += self.explanation + "\n"
		
		summary += "=" * 60 + "\n"
		return summary

	def __str__(self) -> str:
		"""Return readable representation of plan."""
		return f"Plan: {len(self.tasks)} tasks, {self.total_minutes} min total"


class Scheduler:
	"""
	The 'Brain' of the scheduling system.
	Retrieves, organizes, prioritizes, and manages tasks across pets.
	Generates daily plans based on owner availability and pet needs.
	"""

	def generate_daily_plans(self, owner: Owner) -> list[Plan]:
		"""
		Generate optimized daily plans for all of owner's pets.
		Retrieves all tasks from owner (across all pets) and creates individual plans.
		
		Returns:
		- List of Plan objects, one per pet
		"""
		plans = []
		
		if not owner.pets:
			return plans
		
		# Get all tasks across all pets
		all_tasks = owner.get_all_tasks()
		
		# Generate plan for each pet using only their tasks
		for pet in owner.pets:
			pet_tasks = [t for t in all_tasks if t.required_for == pet.name]
			plan = self._generate_plan_for_pet(owner, pet, pet_tasks)
			plans.append(plan)
		
		return plans

	def _generate_plan_for_pet(self, owner: Owner, pet: Pet, available_tasks: list[Task]) -> Plan:
		"""
		Generate an optimized daily plan for a specific pet.
		
		Algorithm:
		1. Filter tasks to only feasible ones (fit within available time)
		2. Separate mandatory vs optional tasks
		3. Prioritize by task priority and owner preferences
		4. Fit as many high-priority tasks as possible within time budget
		5. Generate explanation of decisions
		"""
		plan = Plan(owner=owner, pet=pet)
		
		if not available_tasks:
			plan.explanation = "No tasks available to schedule."
			return plan
		
		# Separate mandatory and optional tasks
		mandatory_tasks = [t for t in available_tasks if t.mandatory]
		optional_tasks = [t for t in available_tasks if not t.mandatory]
		
		# Try to fit all mandatory tasks first
		remaining_minutes = owner.available_minutes_per_day
		selected_tasks = []
		skipped_mandatory = []
		
		# Sort mandatory tasks by owner preference score (descending)
		mandatory_tasks_sorted = sorted(
			mandatory_tasks,
			key=lambda t: t.score_for_owner(owner.preferences),
			reverse=True
		)
		
		for task in mandatory_tasks_sorted:
			if self._fits_time_budget(task, remaining_minutes):
				plan.add_task(task)
				selected_tasks.append(task)
				remaining_minutes -= task.duration_minutes
			else:
				skipped_mandatory.append(task)
		
		# Then fit optional tasks, sorted by priority and preference score
		optional_tasks_sorted = self._sort_tasks_by_priority(optional_tasks)
		optional_tasks_sorted = sorted(
			optional_tasks_sorted,
			key=lambda t: (t.score_for_owner(owner.preferences), t.priority.value),
			reverse=True
		)
		
		skipped_optional = []
		for task in optional_tasks_sorted:
			if self._fits_time_budget(task, remaining_minutes):
				plan.add_task(task)
				selected_tasks.append(task)
				remaining_minutes -= task.duration_minutes
			else:
				skipped_optional.append(task)
		
		# Build explanation
		skipped_all = skipped_mandatory + skipped_optional
		plan.explanation = self._build_explanation(selected_tasks, skipped_all)
		
		return plan

	def _filter_feasible_tasks(self, tasks: list[Task], remaining_minutes: int) -> list[Task]:
		"""Return only tasks that fit within the remaining time budget."""
		return [t for t in tasks if t.is_feasible(remaining_minutes)]

	def _sort_tasks_by_priority(self, tasks: list[Task]) -> list[Task]:
		"""Sort tasks by priority (highest first: critical > high > medium > low)."""
		priority_order = {
			Priority.CRITICAL: 4,
			Priority.HIGH: 3,
			Priority.MEDIUM: 2,
			Priority.LOW: 1,
		}
		return sorted(
			tasks,
			key=lambda t: priority_order.get(t.priority, 0),
			reverse=True
		)

	def _fits_time_budget(self, task: Task, remaining_minutes: int) -> bool:
		"""Delegate to task.is_feasible() to avoid duplicate logic."""
		return task.is_feasible(remaining_minutes)

	def _build_explanation(self, selected: list[Task], skipped: list[Task]) -> str:
		"""Build a human-readable explanation of scheduling decisions."""
		explanation = ""
		
		if selected:
			explanation += f"✓ Selected {len(selected)} task(s):\n"
			for task in selected:
				explanation += f"  - {task.name} ({task.duration_minutes} min, {task.priority.value})\n"
		
		if skipped:
			explanation += f"\n✗ Could not fit {len(skipped)} task(s) due to time constraints:\n"
			# Separate mandatory and optional skipped
			mandatory_skipped = [t for t in skipped if t.mandatory]
			optional_skipped = [t for t in skipped if not t.mandatory]
			
			if mandatory_skipped:
				explanation += "  ⚠ MANDATORY (need more time!):\n"
				for task in mandatory_skipped:
					explanation += f"    - {task.name} ({task.duration_minutes} min)\n"
			
			if optional_skipped:
				explanation += "  Optional (consider future):\n"
				for task in optional_skipped:
					explanation += f"    - {task.name} ({task.duration_minutes} min)\n"
		
		if not selected and not skipped:
			explanation = "No tasks to schedule."
		
		return explanation

	def optimize_plan(self, plan: Plan, owner: Owner) -> None:
		"""
		Try to optimize an existing plan by:
		- Removing lower-priority optional tasks to fit mandatory ones
		- Reordering tasks by time window preference
		"""
		# This could implement more sophisticated optimization
		# For now, it's a placeholder for future enhancement
		pass

	def get_schedule_report(self, owner: Owner) -> str:
		"""Generate a comprehensive report of all pets' scheduling needs."""
		report = owner.owner_summary()
		
		if owner.can_fit_all_tasks():
			report += "\n✓ All tasks can fit within available time!\n"
		else:
			shortfall = owner.total_daily_minutes_needed() - owner.available_minutes_per_day
			report += f"\n✗ Warning: {shortfall} minutes over budget!\n"
			report += "  Consider:\n"
			report += "  - Deferring non-mandatory tasks\n"
			report += "  - Finding additional help\n"
			report += "  - Adjusting pet care priorities\n"
		
		return report
