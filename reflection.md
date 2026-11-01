# PawPal+ Reflection

## 1. System Design

### Three main user actions

- Add a pet to the household.
- Schedule a feeding, walk, medication reminder, or appointment.
- Check the schedule and mark tasks complete.

### 1a. Initial design

The app uses four classes: Owner, Pet, Task, and Scheduler. Owner keeps track of the pets. Pet stores each pet's information and tasks. Task holds the details of a care activity. Scheduler handles sorting, filtering, recurring tasks, and conflict warnings.

Keeping these jobs separate makes the code easier to follow. The Streamlit interface uses the same backend as the terminal demo, so the scheduling rules only need to be written in one place.

### 1b. Design changes

The first design only gave tasks a time. Adding a due date made it possible to tell today's tasks apart from tomorrow's tasks. Each task also has its own ID so the app can complete the right task even when descriptions match.

Recurring tasks are handled through the scheduler because it knows which pet should receive the next task. The final UML diagram was updated to match these changes.

## 2. Algorithmic Layer

### 2a. Scheduling decisions

Tasks are sorted by date and then time. Filters let the owner choose a pet, completion status, or date. Conflict warnings appear when pending tasks share the same date and time, including tasks for different pets.

Completing a daily task creates a new task for the next day. A weekly task creates one seven days later. The next date is based on the completion date. Completing the same task again does not create another copy.

### 2b. Tradeoffs

The conflict check only looks for exact time matches. It does not check how long an activity lasts, so it could miss an overlap between a long appointment and a later walk.

The app also keeps data in session memory instead of a database. This is enough for the exercise, but saving the data permanently would make it more useful. Recurring tasks create one next occurrence instead of filling an entire future calendar.

## 3. Testing and Verification

The terminal demo shows two pets and five tasks added out of order. It displays the sorted schedule, filters, a conflict warning, and daily and weekly recurrence.

The finished project passes 25 tests. These check task completion, adding tasks, sorting, filtering, recurrence, conflicts, input validation, and Streamlit interactions.

The review found a few details that the original tests missed. A pet named "All pets" caused a filtering problem, loading the demo left the old owner name in the edit field, and early completion used the wrong date rule for recurrence. Those were fixed and checked with tests.

This shows why testing needs more than normal examples. A feature can look correct and still behave differently with an unusual input.

## 4. AI Collaboration

### What helped most

I used Codex to help with the design, code, tests, and review. Having the code and test results checked together was useful because it made problems easier to spot. The tests gave a way to check whether the suggested fixes actually worked.

### An AI suggestion that was changed

The original AI-assisted interface used "All pets" as a special filter value. That caused a problem because someone could also give their pet that name. The review changed the special value to None and gave actual pets separate labels. A test checked that filtering returned only the selected pet's tasks.

### Separate chats

The original build stayed in one chat. A separate follow-up chat reviewed the finished project and found issues that needed another look. That review helped keep the focus on checking the requirements and testing the finished app. I would use separate chats earlier next time to keep design and testing questions easier to follow.

### Main takeaway

My main takeaway is that using AI still requires checking how the whole application fits together. The design, code, interface, tests, and documentation all need to agree. AI can help produce the files, but the results still need to be reviewed and tested instead of assuming they work.
