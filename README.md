# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Testing PawPal+

### Running Tests

To run the complete test suite:

```bash
python -m pytest test/test_pawpal.py -v
```

Or for a quick summary:

```bash
python -m pytest test/test_pawpal.py -q
```

### Test Coverage

The test suite includes **41 tests** covering:

- **Task Completion** (6 tests) — task status transitions, feasibility checks
- **Pet Task Management** (8 tests) — adding/removing tasks, pending task filtering, time overlap detection
- **Scheduler Logic** (15 tests) — conflict detection across pets, recurring task creation, time-based sorting, priority scoring, knapsack optimization, daily planning
- **Owner Task Access** (7 tests) — cross-pet filtering, global overlap detection, task aggregation
- **Plan Management** (3 tests) — plan task management, summarization

**Key behaviors verified:**

- ✅ Recurring tasks (daily/weekly) automatically generate next occurrence on completion
- ✅ Time overlaps detected within same pet and across different pets
- ✅ Global schedule shared across all pets (no double-booking owner's time)
- ✅ Mandatory tasks prioritized before optional tasks
- ✅ 0/1 knapsack optimization for optional tasks within time budget
- ✅ Task sorting by HH:MM custom time windows
- ✅ Owner preferences affect task scoring

### Confidence Level

**⭐⭐⭐⭐ (4/5 stars)**

**Why confident:**

- All 41 tests pass with no failures
- Core scheduling logic is well-tested (mandatory vs optional, knapsack, scoring)
- Time overlap detection works correctly at owner level (cross-pet)
- Recurring task generation with timedelta is properly tested

**What could improve confidence to 5 stars:**

- Integration tests between Streamlit UI and core logic
- Edge cases: very long task names, extreme time windows, empty owner scenarios
- Performance tests with 50+ tasks
- Timezone handling for recurring tasks
