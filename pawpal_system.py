from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
import re


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TimeWindow(Enum):
    ANY = "any"
    MORNING = "morning"
    AFTERNOON = "afternoon"
    NIGHT = "night"


class Frequency(Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    AS_NEEDED = "as_needed"


class TaskStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    SKIPPED = "skipped"


@dataclass
class Task:
    name: str
    duration_minutes: int
    priority: Priority
    required_for: str
    description: str = ""
    time_window: TimeWindow = TimeWindow.ANY
    custom_time_frame_start: str = ""
    custom_time_frame_end: str = ""
    mandatory: bool = False
    frequency: Frequency = Frequency.ONCE
    status: TaskStatus = TaskStatus.PENDING
    due_date: date | None = None

    def is_feasible(self, remaining_minutes: int) -> bool:
        return self.duration_minutes <= remaining_minutes

    def mark_completed(self) -> None:
        self.status = TaskStatus.COMPLETED

    def mark_skipped(self) -> None:
        self.status = TaskStatus.SKIPPED

    def create_next_occurrence(self) -> Task | None:
        if self.frequency not in (Frequency.DAILY, Frequency.WEEKLY):
            return None

        base_due_date = self.due_date or date.today()
        delta_days = 1 if self.frequency == Frequency.DAILY else 7

        return Task(
            name=self.name,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            required_for=self.required_for,
            description=self.description,
            time_window=self.time_window,
            custom_time_frame_start=self.custom_time_frame_start,
            custom_time_frame_end=self.custom_time_frame_end,
            mandatory=self.mandatory,
            frequency=self.frequency,
            status=TaskStatus.PENDING,
            due_date=base_due_date + timedelta(days=delta_days),
        )

    def matches_window(self, current_window: TimeWindow) -> bool:
        return (
            self.time_window == TimeWindow.ANY
            or current_window == TimeWindow.ANY
            or self.time_window == current_window
        )

    def display_time_frame(self) -> str:
        if self.custom_time_frame_start and self.custom_time_frame_end:
            return f"{self.custom_time_frame_start} - {self.custom_time_frame_end}"
        return self.time_window.value

    def overlaps_with(self, other: Task) -> bool:
        self_range = self._time_range_minutes()
        other_range = other._time_range_minutes()

        if self_range is None or other_range is None:
            return False

        self_start, self_end = self_range
        other_start, other_end = other_range
        return self_start < other_end and other_start < self_end

    def _time_range_minutes(self) -> tuple[int, int] | None:
        start = self._parse_hhmm_to_minutes(self.custom_time_frame_start)
        end = self._parse_hhmm_to_minutes(self.custom_time_frame_end)
        if start is None or end is None:
            return None
        if end <= start:
            return None
        return start, end

    @staticmethod
    def _parse_hhmm_to_minutes(value: str) -> int | None:
        try:
            hour_str, minute_str = value.split(":", 1)
            hour = int(hour_str)
            minute = int(minute_str)
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return hour * 60 + minute
        except (ValueError, AttributeError):
            pass
        return None

    def score_for_owner(self, owner_preferences: list[str]) -> int:
        priority_score = {
            Priority.CRITICAL: 4,
            Priority.HIGH: 3,
            Priority.MEDIUM: 2,
            Priority.LOW: 1,
        }.get(self.priority, 0)

        pref_tokens = self._normalize_tokens(owner_preferences)
        haystack_tokens = self._normalize_tokens([self.name, self.description])
        preference_score = len(pref_tokens.intersection(haystack_tokens))

        mandatory_boost = 2 if self.mandatory else 0
        return priority_score + preference_score + mandatory_boost

    @staticmethod
    def _normalize_tokens(values: list[str]) -> set[str]:
        tokens: set[str] = set()
        for value in values:
            if not value:
                continue
            tokens.update(re.findall(r"[a-z0-9]+", value.lower()))
        return tokens


@dataclass
class Pet:
    name: str
    pet_type: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, task_name: str) -> bool:
        for i, task in enumerate(self.tasks):
            if task.name == task_name:
                del self.tasks[i]
                return True
        return False

    def get_pending_tasks(self) -> list[Task]:
        return [task for task in self.tasks if task.status == TaskStatus.PENDING]

    def get_tasks_by_status(self, status: TaskStatus) -> list[Task]:
        return [task for task in self.tasks if task.status == status]

    def total_daily_minutes(self) -> int:
        return sum(task.duration_minutes for task in self.get_pending_tasks())

    def has_time_overlap(self, candidate_task: Task, include_completed: bool = False) -> bool:
        for existing in self.tasks:
            if existing is candidate_task:
                continue
            if not include_completed and existing.status != TaskStatus.PENDING:
                continue
            if candidate_task.overlaps_with(existing):
                return True
        return False


@dataclass
class Owner:
    name: str
    available_minutes_per_day: int
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def get_pet(self, pet_name: str) -> Pet | None:
        for pet in self.pets:
            if pet.name == pet_name:
                return pet
        return None

    def get_all_tasks(self) -> list[Task]:
        tasks: list[Task] = []
        for pet in self.pets:
            tasks.extend(pet.tasks)
        return tasks

    def has_time_overlap(
        self,
        candidate_task: Task,
        include_completed: bool = False,
    ) -> bool:
        for pet in self.pets:
            for existing in pet.tasks:
                if existing is candidate_task:
                    continue
                if not include_completed and existing.status != TaskStatus.PENDING:
                    continue
                if candidate_task.overlaps_with(existing):
                    return True
        return False

    def filter_tasks(
        self,
        status: TaskStatus | None = None,
        pet_name: str | None = None,
    ) -> list[Task]:
        filtered: list[Task] = []

        for pet in self.pets:
            if pet_name is not None and pet.name != pet_name:
                continue

            for task in pet.tasks:
                if status is not None and task.status != status:
                    continue
                filtered.append(task)

        return filtered

    def can_fit_all_tasks(self) -> bool:
        return sum(task.duration_minutes for task in self.get_all_tasks()) <= self.available_minutes_per_day

    def owner_summary(self) -> str:
        total_tasks = len(self.get_all_tasks())
        return (
            f"Owner: {self.name}\n"
            f"Available time: {self.available_minutes_per_day} minutes/day\n"
            f"Pets: {len(self.pets)}\n"
            f"Tasks: {total_tasks}"
        )


@dataclass
class Plan:
    owner: Owner | None = None
    pet: Pet | None = None
    tasks: list[Task] = field(default_factory=list)
    total_minutes: int = 0
    explanation: str = ""

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)
        self.total_minutes += task.duration_minutes

    def summarize(self) -> str:
        pet_name = self.pet.name if self.pet else "Unknown Pet"
        owner_name = self.owner.name if self.owner else "Unknown Owner"
        budget = self.owner.available_minutes_per_day if self.owner else "N/A"

        lines = [
            f"Plan for {pet_name}",
            f"Owner: {owner_name}",
            f"Total minutes: {self.total_minutes}/{budget}",
            "",
        ]

        if self.tasks:
            lines.append("Tasks:")
            for i, task in enumerate(self.tasks, 1):
                lines.append(
                    f"{i}. {task.name} | {task.duration_minutes} min | "
                    f"{task.priority.value} | {task.display_time_frame()} | {task.status.value}"
                )
        else:
            lines.append("No tasks scheduled.")

        if self.explanation:
            lines.extend(["", self.explanation])

        return "\n".join(lines)

    def remove_task(self, task_name: str) -> bool:
        for i, task in enumerate(self.tasks):
            if task.name == task_name:
                self.total_minutes -= task.duration_minutes
                del self.tasks[i]
                return True
        return False


class Scheduler:
    def detect_schedule_conflicts(self, owner: Owner) -> list[tuple[Task, Task, str, str]]:
        """Find all pairs of overlapping pending tasks across all pets."""
        conflicts: list[tuple[Task, Task, str, str]] = []
        seen_pairs = set()

        for pet1 in owner.pets:
            for task1 in pet1.tasks:
                if task1.status != TaskStatus.PENDING:
                    continue

                for pet2 in owner.pets:
                    for task2 in pet2.tasks:
                        if task2.status != TaskStatus.PENDING:
                            continue

                        if task1 is task2:
                            continue

                        pair_key = tuple(sorted([id(task1), id(task2)]))
                        if pair_key in seen_pairs:
                            continue

                        if task1.overlaps_with(task2):
                            seen_pairs.add(pair_key)
                            conflicts.append((task1, task2, pet1.name, pet2.name))

        return conflicts

    def get_conflict_report(self, owner: Owner) -> str:
        """Generate a human-readable report of all scheduling conflicts."""
        conflicts = self.detect_schedule_conflicts(owner)

        if not conflicts:
            return "No scheduling conflicts detected."

        lines = [f"Found {len(conflicts)} schedule conflict(s):\n"]
        for i, (task1, task2, pet1_name, pet2_name) in enumerate(conflicts, 1):
            lines.append(
                f"{i}. CONFLICT: '{task1.name}' ({pet1_name}) "
                f"@ {task1.display_time_frame()} overlaps with "
                f"'{task2.name}' ({pet2_name}) @ {task2.display_time_frame()}"
            )

        return "\n".join(lines)

    def mark_task_completed(self, pet: Pet, task_name: str) -> Task | None:
        for task in pet.tasks:
            if task.name == task_name and task.status == TaskStatus.PENDING:
                task.mark_completed()
                next_task = task.create_next_occurrence()
                if next_task is not None:
                    pet.add_task(next_task)
                return next_task
        return None

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        return sorted(tasks, key=lambda task: self._parse_hhmm(self._task_time_value(task)))

    def _task_time_value(self, task: Task) -> str:
        # Prefer an explicit "time" attribute if present, else use custom start time.
        explicit_time = getattr(task, "time", "")
        if isinstance(explicit_time, str) and explicit_time:
            return explicit_time
        if task.custom_time_frame_start:
            return task.custom_time_frame_start
        return "23:59"

    def _parse_hhmm(self, value: str) -> tuple[int, int]:
        try:
            hour_str, minute_str = value.split(":", 1)
            hour = int(hour_str)
            minute = int(minute_str)
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return hour, minute
        except (ValueError, AttributeError):
            pass
        return 23, 59

    def generate_daily_plans(
        self,
        owner: Owner,
        current_window: TimeWindow = TimeWindow.ANY,
    ) -> list[Plan]:
        plans: list[Plan] = []
        remaining_minutes = owner.available_minutes_per_day

        for pet in owner.pets:
            pet_tasks = [task for task in pet.tasks if task.status == TaskStatus.PENDING]
            plan, remaining_minutes = self._generate_plan_for_pet(
                owner,
                pet,
                pet_tasks,
                current_window,
                remaining_minutes,
            )
            plans.append(plan)

        return plans

    def _generate_plan_for_pet(
        self,
        owner: Owner,
        pet: Pet,
        available_tasks: list[Task],
        current_window: TimeWindow,
        remaining_minutes: int,
    ) -> tuple[Plan, int]:
        plan = Plan(owner=owner, pet=pet)

        if not available_tasks:
            plan.explanation = "No tasks available to schedule."
            return plan, remaining_minutes

        selected_tasks: list[Task] = []
        skipped_tasks: list[Task] = []

        mandatory_tasks = [t for t in available_tasks if t.mandatory]
        optional_tasks = [t for t in available_tasks if not t.mandatory]

        for task in sorted(
            mandatory_tasks,
            key=lambda t: self._task_sort_key(t, owner, current_window),
        ):
            if task.is_feasible(remaining_minutes):
                plan.add_task(task)
                selected_tasks.append(task)
                remaining_minutes -= task.duration_minutes
            else:
                skipped_tasks.append(task)

        chosen_optional = self._select_optional_tasks_knapsack(
            optional_tasks,
            remaining_minutes,
            owner,
            current_window,
        )
        chosen_optional_ids = {id(t) for t in chosen_optional}

        for task in sorted(chosen_optional, key=lambda t: self._task_sort_key(t, owner, current_window)):
            plan.add_task(task)
            selected_tasks.append(task)
            remaining_minutes -= task.duration_minutes

        for task in optional_tasks:
            if id(task) not in chosen_optional_ids:
                skipped_tasks.append(task)

        plan.explanation = self._build_explanation(selected_tasks, skipped_tasks, remaining_minutes)
        return plan, remaining_minutes

    def _task_sort_key(self, task: Task, owner: Owner, current_window: TimeWindow) -> tuple:
        window_rank = 0 if task.matches_window(current_window) else 1
        value_density = self._task_value(task, owner, current_window) / max(task.duration_minutes, 1)

        return (
            window_rank,
            -value_density,
            task.duration_minutes,
            task.name.lower(),
        )

    def _task_value(self, task: Task, owner: Owner, current_window: TimeWindow) -> int:
        priority_weight = {
            Priority.CRITICAL: 100,
            Priority.HIGH: 75,
            Priority.MEDIUM: 50,
            Priority.LOW: 25,
        }.get(task.priority, 0)

        preference_bonus = task.score_for_owner(owner.preferences) - (
            {
                Priority.CRITICAL: 4,
                Priority.HIGH: 3,
                Priority.MEDIUM: 2,
                Priority.LOW: 1,
            }.get(task.priority, 0)
            + (2 if task.mandatory else 0)
        )
        preference_bonus *= 8

        mandatory_bonus = 30 if task.mandatory else 0
        window_bonus = 10 if task.matches_window(current_window) else 0
        duration_penalty = task.duration_minutes // 10

        return max(1, priority_weight + mandatory_bonus + window_bonus + preference_bonus - duration_penalty)

    def _select_optional_tasks_knapsack(
        self,
        optional_tasks: list[Task],
        capacity: int,
        owner: Owner,
        current_window: TimeWindow,
    ) -> list[Task]:
        if capacity <= 0 or not optional_tasks:
            return []

        n = len(optional_tasks)
        dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]

        for i in range(1, n + 1):
            task = optional_tasks[i - 1]
            weight = task.duration_minutes
            value = self._task_value(task, owner, current_window)

            for cap in range(capacity + 1):
                best_without = dp[i - 1][cap]
                best_with = best_without
                if weight <= cap:
                    best_with = value + dp[i - 1][cap - weight]
                dp[i][cap] = max(best_without, best_with)

        selected: list[Task] = []
        cap = capacity
        for i in range(n, 0, -1):
            if dp[i][cap] != dp[i - 1][cap]:
                task = optional_tasks[i - 1]
                selected.append(task)
                cap -= task.duration_minutes

        selected.reverse()
        return selected

    def _build_explanation(self, selected: list[Task], skipped: list[Task], remaining_minutes: int) -> str:
        parts: list[str] = []

        if selected:
            parts.append(f"Selected {len(selected)} task(s):")
            for task in selected:
                parts.append(
                    f"- {task.name} ({task.duration_minutes} min, "
                    f"{task.priority.value}, {task.display_time_frame()})"
                )

        if skipped:
            parts.append(f"Skipped {len(skipped)} task(s) due to time constraints:")
            for task in skipped:
                parts.append(
                    f"- {task.name} ({task.duration_minutes} min, "
                    f"{task.priority.value}, {task.display_time_frame()})"
                )

        parts.append(f"Remaining daily minutes after this plan: {remaining_minutes}")

        if not parts:
            return "No tasks to schedule."

        return "\n".join(parts)

    def get_schedule_report(self, owner: Owner) -> str:
        plans = self.generate_daily_plans(owner)
        lines = ["Schedule Report", "=" * 20]
        for plan in plans:
            lines.append(plan.summarize())
            lines.append("-" * 20)
        return "\n".join(lines)