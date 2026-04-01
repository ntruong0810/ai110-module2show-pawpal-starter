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

During implementation, I made a key change to simplify the interaction between classes. Initially, I planned for the Scheduler to directly manage all logic, including filtering, sorting, and explanation generation. However, this made the Scheduler too complex and harder to maintain.

To improve this, I refactored part of the logic by adding helper methods (or lightweight internal functions) to handle specific tasks such as sorting tasks by priority and checking time constraints. This made the Scheduler more modular and easier to test.

This change was important because it improved code readability, made debugging easier, and allowed me to test individual parts of the scheduling logic more effectively.

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
