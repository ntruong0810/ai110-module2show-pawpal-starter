# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
  In my initial UML design, I structured the system around a few core classes: Owner, Pet, Task, Scheduler, and Plan. The Owner class stores basic information about the user, such as available time and preferences. The Pet class represents the pet being cared for, including its type and needs.
  The Task class is central to the system, representing individual care activities like feeding, walking, or giving medication. Each task includes attributes such as duration and priority. The Scheduler class is responsible for generating a daily plan by selecting and organizing tasks based on constraints like available time and priority. Finally, the Plan class stores the resulting schedule and provides a way to display or explain it.
  Overall, I aimed to separate responsibilities clearly: data representation (Owner, Pet, Task) and decision-making logic (Scheduler), with Plan acting as the output container.
  **b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, I made several important changes during implementation:

1. **Added Owner-Pet relationship**: Originally, `Owner` was standalone. I added `pet: Pet | None` to create a direct link between Owner and their Pet. This eliminates the need to pass Pet separately and makes the relationship explicit in the code.

2. **Enhanced Task with time windows and scoring**: I added `preferred_window` (e.g., "morning", "evening") and `mandatory` flag to Task, plus a new `score_for_owner()` method. This matches the UML better and supports more flexible scheduling logic based on user preferences.

3. **Plan now references Owner and Pet**: Added `owner` and `pet` fields to Plan so that a generated schedule knows exactly whose plan it is. This simplifies context when displaying or explaining the plan.

4. **Eliminated logic duplication in Scheduler**: The `_fits_time_budget()` method now delegates to `Task.is_feasible()` instead of duplicating the logic. This applies the DRY principle and ensures a single source of truth for feasibility checks.

5. **Added docstrings to methods**: Clarified the purpose of key methods like `add_task()`, `summarize()`, and `is_feasible()` to improve code maintainability.

These changes were made to reduce coupling, improve testability (each method has a single responsibility), and align the skeleton more closely with the UML design while keeping it clean and maintainable.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
