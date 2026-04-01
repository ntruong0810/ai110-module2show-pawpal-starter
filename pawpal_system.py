from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Priority(Enum):
	LOW = "low"
	MEDIUM = "medium"
	HIGH = "high"
	CRITICAL = "critical"


@dataclass
class Owner:
	name: str
	available_minutes_per_day: int
	preferences: list[str] = field(default_factory=list)


@dataclass
class Pet:
	name: str
	pet_type: str
	needs: list[str] = field(default_factory=list)


@dataclass
class Task:
	name: str
	duration_minutes: int
	priority: Priority
	required_for: str
	description: str = ""

	def is_feasible(self, remaining_minutes: int) -> bool:
		pass


@dataclass
class Plan:
	tasks: list[Task] = field(default_factory=list)
	total_minutes: int = 0
	explanation: str = ""

	def add_task(self, task: Task) -> None:
		pass

	def summarize(self) -> str:
		pass


class Scheduler:
	def generate_plan(self, owner: Owner, pet: Pet, tasks: list[Task]) -> Plan:
		pass

	def _filter_feasible_tasks(self, tasks: list[Task], remaining_minutes: int) -> list[Task]:
		pass

	def _sort_tasks_by_priority(self, tasks: list[Task]) -> list[Task]:
		pass

	def _fits_time_budget(self, task: Task, remaining_minutes: int) -> bool:
		pass

	def _build_explanation(self, selected: list[Task], skipped: list[Task]) -> str:
		pass
